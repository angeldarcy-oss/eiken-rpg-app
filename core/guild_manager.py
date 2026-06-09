"""core/guild_manager.py — ギルド管理"""
from __future__ import annotations
import json
import random
import string
from datetime import date, datetime, timedelta
from pathlib import Path

GUILDS_DIR = Path("data/guilds")
MAX_MEMBERS = 20
MAX_BULLETIN = 30
MAX_BATTLE_LOG = 50

# ── ギルドボスSVG ─────────────────────────────────────────────

_GBOSS_SVG: dict[str, str] = {
    "guild_dragon": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M20,40 Q6,14 18,8 Q30,22 22,40 Z" fill="#6600aa" opacity=".85"/>'
        '<path d="M60,40 Q74,14 62,8 Q50,22 58,40 Z" fill="#6600aa" opacity=".85"/>'
        '<path d="M62,54 Q76,48 78,36 Q80,24 70,28" stroke="#8822aa" stroke-width="7" fill="none" stroke-linecap="round"/>'
        '<ellipse cx="40" cy="52" rx="22" ry="20" fill="#8822aa"/>'
        '<ellipse cx="40" cy="28" rx="14" ry="13" fill="#9933cc"/>'
        '<polygon points="31,20 27,6 34,17" fill="#6600aa"/>'
        '<polygon points="49,20 53,6 46,17" fill="#6600aa"/>'
        '<circle cx="34" cy="27" r="4.5" fill="#ffcc00"/><circle cx="35" cy="27" r="2.2" fill="#cc0000"/>'
        '<circle cx="46" cy="27" r="4.5" fill="#ffcc00"/><circle cx="47" cy="27" r="2.2" fill="#cc0000"/>'
        '<path d="M34,35 Q40,41 46,35" stroke="#440066" stroke-width="2" fill="none"/>'
        '<polygon points="35,35 37,40 39,35" fill="white" opacity=".8"/>'
        '<polygon points="41,35 43,40 45,35" fill="white" opacity=".8"/>'
        '<ellipse cx="28" cy="70" rx="10" ry="8" fill="#7711aa"/>'
        '<ellipse cx="52" cy="70" rx="10" ry="8" fill="#7711aa"/>'
        '</svg>'
    ),
    "shadow_titan": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<polygon points="32,14 30,4 35,12" fill="#222244"/>'
        '<polygon points="40,12 40,2 45,12" fill="#222244"/>'
        '<polygon points="48,14 50,4 45,12" fill="#222244"/>'
        '<rect x="26" y="14" width="28" height="26" rx="8" fill="#222244"/>'
        '<rect x="30" y="24" width="20" height="10" rx="5" fill="#000011"/>'
        '<ellipse cx="36" cy="29" rx="4" ry="3.5" fill="#ff0066"/>'
        '<ellipse cx="44" cy="29" rx="4" ry="3.5" fill="#ff0066"/>'
        '<ellipse cx="36" cy="29" rx="2" ry="1.8" fill="#ff88aa"/>'
        '<ellipse cx="44" cy="29" rx="2" ry="1.8" fill="#ff88aa"/>'
        '<rect x="10" y="36" width="15" height="9" rx="4" fill="#222244"/>'
        '<rect x="55" y="36" width="15" height="9" rx="4" fill="#222244"/>'
        '<rect x="8" y="43" width="9" height="22" rx="4" fill="#1a1a2e"/>'
        '<rect x="63" y="43" width="9" height="22" rx="4" fill="#1a1a2e"/>'
        '<rect x="22" y="40" width="36" height="30" rx="5" fill="#1a1a2e"/>'
        '<rect x="28" y="42" width="24" height="18" rx="3" fill="#2a2a4a" opacity=".9"/>'
        '<rect x="36" y="44" width="8" height="14" rx="2" fill="#ff0066" opacity=".5"/>'
        '<rect x="26" y="68" width="11" height="12" rx="3" fill="#1a1a2e"/>'
        '<rect x="43" y="68" width="11" height="12" rx="3" fill="#1a1a2e"/>'
        '</svg>'
    ),
    "chaos_golem": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<ellipse cx="40" cy="52" rx="21" ry="19" fill="#4a3a2a"/>'
        '<ellipse cx="40" cy="50" rx="19" ry="17" fill="#5a4a3a"/>'
        '<path d="M37,35 L35,43 L40,48 L37,57" stroke="#ff6600" stroke-width="2.2" fill="none" opacity=".85"/>'
        '<path d="M44,39 L47,46 L42,51" stroke="#ff6600" stroke-width="1.6" fill="none" opacity=".7"/>'
        '<ellipse cx="17" cy="47" rx="11" ry="9" fill="#4a3a2a"/>'
        '<ellipse cx="63" cy="47" rx="11" ry="9" fill="#4a3a2a"/>'
        '<ellipse cx="11" cy="58" rx="9" ry="11" fill="#3a2a1a"/>'
        '<ellipse cx="69" cy="58" rx="9" ry="11" fill="#3a2a1a"/>'
        '<ellipse cx="40" cy="28" rx="17" ry="15" fill="#5a4a3a"/>'
        '<ellipse cx="40" cy="26" rx="15" ry="13" fill="#6a5a4a"/>'
        '<circle cx="33" cy="25" r="5.5" fill="#111"/>'
        '<circle cx="47" cy="25" r="5.5" fill="#111"/>'
        '<circle cx="33" cy="25" r="3.2" fill="#ff4400"/>'
        '<circle cx="47" cy="25" r="3.2" fill="#ff4400"/>'
        '<circle cx="33" cy="25" r="1.6" fill="#ffaa00"/>'
        '<circle cx="47" cy="25" r="1.6" fill="#ffaa00"/>'
        '<rect x="32" y="32" width="16" height="5" rx="2" fill="#2a1a0a"/>'
        '<rect x="34" y="32" width="2.5" height="5" fill="#ff4400" opacity=".6"/>'
        '<rect x="38" y="32" width="2.5" height="5" fill="#ff4400" opacity=".6"/>'
        '<rect x="42" y="32" width="2.5" height="5" fill="#ff4400" opacity=".6"/>'
        '<ellipse cx="29" cy="70" rx="11" ry="9" fill="#3a2a1a"/>'
        '<ellipse cx="51" cy="70" rx="11" ry="9" fill="#3a2a1a"/>'
        '</svg>'
    ),
}

_GUILD_BOSSES = [
    {"id": "guild_dragon",  "name": "ギルドドラゴン",    "emoji": "🐉", "base_hp": 300, "svg": _GBOSS_SVG["guild_dragon"]},
    {"id": "shadow_titan",  "name": "シャドウタイタン",   "emoji": "👾", "base_hp": 420, "svg": _GBOSS_SVG["shadow_titan"]},
    {"id": "chaos_golem",   "name": "カオスゴーレム",     "emoji": "🗿", "base_hp": 560, "svg": _GBOSS_SVG["chaos_golem"]},
]

GUILD_BOSS_DROPS = ["guild_pendant", "guild_crest_ring", "guild_badge_necklace"]

WEEKLY_GOAL_OPTIONS = [
    {"type": "correct",  "label": "合計正解数",             "targets": [500, 1000, 1500, 2000]},
    {"type": "dungeon",  "label": "ダンジョンクリア数",     "targets": [5, 10, 15, 20]},
    {"type": "boss",     "label": "ボス撃破数",             "targets": [3, 5, 10, 20]},
]


# ── ユーティリティ ────────────────────────────────────────────

def _ensure_dir() -> None:
    GUILDS_DIR.mkdir(parents=True, exist_ok=True)


def _path(code: str) -> Path:
    return GUILDS_DIR / f"{code.upper()}.json"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _week_start() -> str:
    today = date.today()
    return (today - timedelta(days=today.weekday())).isoformat()


def generate_code() -> str:
    _ensure_dir()
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choices(chars, k=6))
        if not _path(code).exists():
            return code


# ── CRUD ─────────────────────────────────────────────────────

def get_guild(code: str) -> dict | None:
    p = _path(code)
    if not p.exists():
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_guild(guild: dict) -> bool:
    _ensure_dir()
    code = guild.get("code", "")
    if not code:
        return False
    try:
        with open(_path(code), "w", encoding="utf-8") as f:
            json.dump(guild, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def create_guild(username: str, player_name: str, guild_name: str,
                 description: str, icon: str, character: str = "") -> dict:
    code = generate_code()
    guild = {
        "code": code,
        "name": guild_name.strip()[:20],
        "description": description.strip()[:60],
        "icon": icon,
        "master": username,
        "created_at": _now(),
        "members": {
            username: {
                "name": player_name, "role": "master", "joined_at": _now(),
                "character": character, "level": 1,
                "weekly_correct": 0, "total_correct": 0,
                "boss_defeats": 0, "dungeon_clears": 0, "total_exp": 0,
            }
        },
        "stats": {"total_exp": 0, "boss_defeats": 0, "dungeon_clears": 0, "total_correct": 0},
        "weekly": {
            "week_start": _week_start(), "correct": 0, "dungeon": 0, "boss": 0,
            "goal_type": "correct", "goal_target": 1000,
            "goal_completed": False, "reward_claimed": [],
        },
        "bulletin": [],
        "guild_boss": {
            "active": False, "defeated": False,
            "boss_id": "", "boss_name": "", "boss_emoji": "", "boss_svg": "",
            "hp": 0, "hp_max": 0, "started_at": "", "defeated_at": "",
            "battle_log": [], "rewards_claimed": [],
        },
    }
    save_guild(guild)
    return guild


def join_guild(code: str, username: str, player_name: str,
               character: str = "") -> tuple[dict | None, str]:
    guild = get_guild(code)
    if guild is None:
        return None, "ギルドコードが見つかりません"
    if len(guild.get("members", {})) >= MAX_MEMBERS:
        return None, f"ギルドが満員です（最大{MAX_MEMBERS}人）"
    if username in guild.get("members", {}):
        return guild, ""
    guild.setdefault("members", {})[username] = {
        "name": player_name, "role": "member", "joined_at": _now(),
        "character": character, "level": 1,
        "weekly_correct": 0, "total_correct": 0,
        "boss_defeats": 0, "dungeon_clears": 0, "total_exp": 0,
    }
    save_guild(guild)
    return guild, ""


def leave_guild(code: str, username: str) -> bool:
    guild = get_guild(code)
    if guild is None:
        return False
    members = guild.get("members", {})
    members.pop(username, None)
    if not members:
        try:
            _path(code).unlink()
        except Exception:
            pass
        return True
    if guild.get("master") == username:
        new_master = next(iter(members))
        guild["master"] = new_master
        members[new_master]["role"] = "master"
    guild["members"] = members
    save_guild(guild)
    return True


def set_member_role(code: str, requester: str, target: str, role: str) -> tuple[bool, str]:
    """ギルドマスターがメンバーの役職を変更"""
    guild = get_guild(code)
    if guild is None:
        return False, "ギルドが見つかりません"
    if guild.get("master") != requester:
        return False, "ギルドマスターのみ操作できます"
    if target not in guild.get("members", {}):
        return False, "メンバーが見つかりません"
    if target == requester:
        return False, "自分自身の役職は変更できません"
    guild["members"][target]["role"] = role
    if role == "master":
        guild["members"][requester]["role"] = "member"
        guild["master"] = target
    save_guild(guild)
    return True, ""


# ── 統計同期 ────────────────────────────────────────────────

def sync_member_stats(code: str, username: str, player: dict) -> None:
    """プレイヤーの最新ステータスをギルドに同期（ページ訪問時に呼び出す）"""
    guild = get_guild(code)
    if guild is None:
        return
    members = guild.get("members", {})
    if username not in members:
        return

    weekly = guild.setdefault("weekly", {})
    cur_week = _week_start()
    if weekly.get("week_start") != cur_week:
        weekly.update({"week_start": cur_week, "correct": 0, "dungeon": 0, "boss": 0,
                       "goal_completed": False, "reward_claimed": []})
        for m in members.values():
            m["weekly_correct"] = 0

    m = members[username]
    old_wc = m.get("weekly_correct", 0)
    new_wc = player.get("weekly_correct", 0)

    m.update({
        "name": player.get("name", username),
        "character": player.get("character", ""),
        "level": player.get("level", 1),
        "total_exp": player.get("total_exp_earned", 0),
        "total_correct": player.get("total_correct_ever", 0),
        "boss_defeats": player.get("boss_defeats", 0),
        "dungeon_clears": sum(v.get("clears", 0) for v in player.get("dungeons", {}).values()),
        "weekly_correct": new_wc,
    })

    delta = max(0, new_wc - old_wc)
    weekly["correct"] = weekly.get("correct", 0) + delta

    # ダンジョンクリア・ボス撃破は全メンバーから再集計
    weekly["dungeon"] = sum(mem.get("dungeon_clears", 0) for mem in members.values())
    weekly["boss"] = sum(mem.get("boss_defeats", 0) for mem in members.values())

    stats = guild.setdefault("stats", {})
    stats["total_exp"] = sum(mem.get("total_exp", 0) for mem in members.values())
    stats["total_correct"] = sum(mem.get("total_correct", 0) for mem in members.values())
    stats["boss_defeats"] = sum(mem.get("boss_defeats", 0) for mem in members.values())
    stats["dungeon_clears"] = sum(mem.get("dungeon_clears", 0) for mem in members.values())

    goal_type = weekly.get("goal_type", "correct")
    goal_target = weekly.get("goal_target", 1000)
    goal_current = weekly.get(goal_type, 0)
    if goal_current >= goal_target and not weekly.get("goal_completed"):
        weekly["goal_completed"] = True

    guild["members"] = members
    guild["weekly"] = weekly
    guild["stats"] = stats
    save_guild(guild)


# ── 掲示板 ───────────────────────────────────────────────────

def post_bulletin(code: str, username: str, player_name: str, text: str) -> bool:
    text = text.strip()[:100]
    if not text:
        return False
    guild = get_guild(code)
    if guild is None or username not in guild.get("members", {}):
        return False
    bulletin = guild.setdefault("bulletin", [])
    bulletin.append({"username": username, "name": player_name, "text": text, "ts": _now()})
    guild["bulletin"] = bulletin[-MAX_BULLETIN:]
    save_guild(guild)
    return True


# ── 週間目標 ─────────────────────────────────────────────────

def set_weekly_goal(code: str, username: str, goal_type: str, goal_target: int) -> bool:
    guild = get_guild(code)
    if guild is None:
        return False
    member = guild.get("members", {}).get(username, {})
    if member.get("role") not in ("master", "officer"):
        return False
    weekly = guild.setdefault("weekly", {})
    weekly.update({"goal_type": goal_type, "goal_target": goal_target,
                   "goal_completed": False, "reward_claimed": []})
    guild["weekly"] = weekly
    save_guild(guild)
    return True


def claim_weekly_reward(code: str, username: str) -> int:
    """週間目標達成報酬（EXP量を返す）"""
    guild = get_guild(code)
    if guild is None:
        return 0
    weekly = guild.get("weekly", {})
    if not weekly.get("goal_completed"):
        return 0
    if username in weekly.get("reward_claimed", []):
        return 0
    if username not in guild.get("members", {}):
        return 0
    weekly.setdefault("reward_claimed", []).append(username)
    guild["weekly"] = weekly
    save_guild(guild)
    return 500


# ── ギルドボス ───────────────────────────────────────────────

def start_guild_boss(code: str, username: str) -> tuple[bool, str]:
    guild = get_guild(code)
    if guild is None:
        return False, "ギルドが見つかりません"
    member = guild.get("members", {}).get(username, {})
    if member.get("role") not in ("master", "officer"):
        return False, "ギルドマスターかオフィサーのみ召喚できます"
    boss_data = guild.get("guild_boss", {})
    if boss_data.get("active"):
        return False, "すでにギルドボスが出現中です"
    n = max(1, len(guild.get("members", {})))
    boss = _pick_guild_boss(n)
    guild["guild_boss"] = {
        "active": True, "defeated": False,
        "boss_id": boss["id"], "boss_name": boss["name"],
        "boss_emoji": boss["emoji"], "boss_svg": boss["svg"],
        "hp": boss["hp"], "hp_max": boss["hp"],
        "started_at": _now(), "defeated_at": "",
        "battle_log": [], "rewards_claimed": [],
    }
    save_guild(guild)
    return True, ""


def guild_boss_deal_damage(code: str, username: str, player_name: str,
                           damage: int) -> dict | None:
    guild = get_guild(code)
    if guild is None:
        return None
    boss = guild.get("guild_boss", {})
    if not boss.get("active"):
        return guild
    boss["hp"] = max(0, boss.get("hp", 0) - damage)
    log = boss.setdefault("battle_log", [])
    log.append({"name": player_name, "damage": damage, "hp_left": boss["hp"], "ts": _now()})
    boss["battle_log"] = log[-MAX_BATTLE_LOG:]
    if boss["hp"] <= 0:
        boss["active"] = False
        boss["defeated"] = True
        boss["defeated_at"] = _now()
        guild.setdefault("stats", {})["boss_defeats"] = (
            guild["stats"].get("boss_defeats", 0) + 1
        )
    guild["guild_boss"] = boss
    save_guild(guild)
    return guild


def claim_guild_boss_reward(code: str, username: str) -> list[str]:
    guild = get_guild(code)
    if guild is None:
        return []
    boss = guild.get("guild_boss", {})
    if not boss.get("defeated"):
        return []
    if username in boss.get("rewards_claimed", []):
        return []
    if username not in guild.get("members", {}):
        return []
    boss.setdefault("rewards_claimed", []).append(username)
    guild["guild_boss"] = boss
    save_guild(guild)
    return [random.choice(GUILD_BOSS_DROPS)]


def _pick_guild_boss(n_members: int) -> dict:
    boss = random.choice(_GUILD_BOSSES).copy()
    boss["hp"] = int(boss["base_hp"] * (1 + 0.25 * max(0, n_members - 1)))
    return boss


# ── ランキング ───────────────────────────────────────────────

def get_all_guilds() -> list[dict]:
    _ensure_dir()
    result = []
    for f in GUILDS_DIR.glob("*.json"):
        try:
            with open(f, encoding="utf-8") as fh:
                result.append(json.load(fh))
        except Exception:
            pass
    return result


def get_guild_rankings() -> dict:
    guilds = get_all_guilds()
    cur_week = _week_start()

    def _wc(g: dict) -> int:
        w = g.get("weekly", {})
        return w.get("correct", 0) if w.get("week_start") == cur_week else 0

    by_exp = sorted(guilds, key=lambda g: g.get("stats", {}).get("total_exp", 0), reverse=True)
    by_boss = sorted(guilds, key=lambda g: g.get("stats", {}).get("boss_defeats", 0), reverse=True)
    by_weekly = sorted(guilds, key=_wc, reverse=True)
    return {
        "by_exp": by_exp[:10],
        "by_boss": by_boss[:10],
        "by_weekly": by_weekly[:10],
        "week_start": cur_week,
    }
