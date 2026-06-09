"""core/party_manager.py — パーティー管理"""
from __future__ import annotations
import json
import random
import string
from datetime import datetime
from pathlib import Path

PARTIES_DIR = Path("data/parties")
MAX_MEMBERS = 4
MAX_MESSAGES = 50
MAX_LOG = 80


def _ensure_dir() -> None:
    PARTIES_DIR.mkdir(parents=True, exist_ok=True)


def _path(code: str) -> Path:
    return PARTIES_DIR / f"{code.upper()}.json"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def generate_code() -> str:
    _ensure_dir()
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choices(chars, k=6))
        if not _path(code).exists():
            return code


def get_party(code: str) -> dict | None:
    p = _path(code)
    if not p.exists():
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_party(party: dict) -> bool:
    _ensure_dir()
    code = party.get("code", "")
    if not code:
        return False
    try:
        with open(_path(code), "w", encoding="utf-8") as f:
            json.dump(party, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def create_party(username: str, player_name: str) -> dict:
    code = generate_code()
    party = {
        "code": code,
        "leader": username,
        "status": "waiting",
        "created_at": _now(),
        "boss_defeats": 0,
        "members": {
            username: {"name": player_name, "damage_dealt": 0, "joined_at": _now()},
        },
        "boss": None,
        "boss_hp": 0,
        "boss_hp_max": 0,
        "messages": [],
        "battle_log": [],
        "rewards_claimed": [],
    }
    save_party(party)
    return party


def join_party(code: str, username: str, player_name: str) -> tuple[dict | None, str]:
    party = get_party(code)
    if party is None:
        return None, "パーティーコードが見つかりません"
    if party.get("status") != "waiting":
        return None, "すでにバトルが始まっています"
    if len(party.get("members", {})) >= MAX_MEMBERS:
        return None, f"パーティーが満員です（最大{MAX_MEMBERS}人）"
    if username in party.get("members", {}):
        return party, ""
    party.setdefault("members", {})[username] = {
        "name": player_name, "damage_dealt": 0, "joined_at": _now()
    }
    save_party(party)
    return party, ""


def leave_party(code: str, username: str) -> bool:
    party = get_party(code)
    if party is None:
        return False
    party.setdefault("members", {}).pop(username, None)
    if not party["members"]:
        try:
            _path(code).unlink()
        except Exception:
            pass
        return True
    if party.get("leader") == username:
        party["leader"] = next(iter(party["members"]))
    save_party(party)
    return True


def start_battle(code: str, boss_info: dict) -> tuple[dict | None, str]:
    party = get_party(code)
    if party is None:
        return None, "パーティーが見つかりません"
    if party.get("status") != "waiting":
        return None, "すでに開始済みです"
    n = max(1, len(party.get("members", {})))
    hp = int(boss_info["hp"] * (1 + 0.5 * (n - 1)))
    party.update({
        "status": "battling",
        "battle_started_at": _now(),
        "boss": {
            "id": boss_info.get("id", ""),
            "name": boss_info.get("name", "BOSS"),
            "emoji": boss_info.get("emoji", "👾"),
        },
        "boss_hp": hp,
        "boss_hp_max": hp,
    })
    save_party(party)
    return party, ""


def deal_damage(code: str, username: str, damage: int) -> dict | None:
    party = get_party(code)
    if party is None or party.get("status") != "battling":
        return party
    party["boss_hp"] = max(0, party.get("boss_hp", 0) - damage)
    mdata = party.setdefault("members", {}).setdefault(username, {})
    mdata["damage_dealt"] = mdata.get("damage_dealt", 0) + damage
    mdata["last_active"] = _now()
    log = party.setdefault("battle_log", [])
    log.append({
        "name": mdata.get("name", username),
        "damage": damage,
        "hp_left": party["boss_hp"],
        "ts": _now(),
    })
    party["battle_log"] = log[-MAX_LOG:]
    if party["boss_hp"] <= 0:
        party["status"] = "completed"
        party["completed_at"] = _now()
        party["boss_defeats"] = party.get("boss_defeats", 0) + 1
    save_party(party)
    return party


def send_message(code: str, username: str, player_name: str, text: str) -> bool:
    text = text.strip()[:80]
    if not text:
        return False
    party = get_party(code)
    if party is None:
        return False
    msgs = party.setdefault("messages", [])
    msgs.append({"name": player_name, "text": text, "ts": _now()})
    party["messages"] = msgs[-MAX_MESSAGES:]
    save_party(party)
    return True


def claim_rewards(code: str, username: str) -> list[str]:
    party = get_party(code)
    if party is None or party.get("status") != "completed":
        return []
    if username in party.get("rewards_claimed", []):
        return []
    from core.equipment import BOSS_RARE_DROPS
    reward = random.choice(BOSS_RARE_DROPS)
    party.setdefault("rewards_claimed", []).append(username)
    save_party(party)
    return [reward]


def get_member_player(username: str) -> dict | None:
    from core.save_manager import get_user_save_path
    p = get_user_save_path(username)
    if not p.exists():
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f).get("player")
    except Exception:
        return None


def get_all_parties() -> list[dict]:
    _ensure_dir()
    result = []
    for f in PARTIES_DIR.glob("*.json"):
        try:
            with open(f, encoding="utf-8") as fh:
                result.append(json.load(fh))
        except Exception:
            pass
    return result
