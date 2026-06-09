from __future__ import annotations
from typing import Dict, List, Optional
import json
import hashlib
import os
from datetime import date, datetime
from pathlib import Path

from core.player import new_player, exp_to_next_level

SAVE_DIR = Path("data/saves")
RANKINGS_FILE = SAVE_DIR / "rankings.json"
USERS_FILE = SAVE_DIR / "users.json"
SAVE_FILE = SAVE_DIR / "player_data.json"  # 後方互換


def _hash_password(password: str) -> str:
    """パスワードをSHA-256でハッシュ化する"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_user_save_path(username: str) -> Path:
    safe_name = "".join(c for c in username if c.isalnum() or c in "-_")
    return SAVE_DIR / ("user_" + safe_name + ".json")


def _load_users() -> dict:
    if not USERS_FILE.exists():
        return {}
    try:
        with open(USERS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_users(users_data: dict) -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)


def get_registered_users() -> List[str]:
    data = _load_users()
    return list(data.get("accounts", {}).keys())


def is_username_taken(username: str) -> bool:
    data = _load_users()
    accounts = data.get("accounts", {})
    return username.strip().lower() in [u.lower() for u in accounts.keys()]


def register_user(username: str, password: str) -> bool:
    """新規ユーザー登録。成功したらTrue、既に存在したらFalseを返す"""
    if is_username_taken(username):
        return False
    try:
        data = _load_users()
        accounts = data.get("accounts", {})
        accounts[username.strip()] = {
            "password_hash": _hash_password(password),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        data["accounts"] = accounts
        _save_users(data)
        # 初期プレイヤーデータを作成
        player = new_player(name=username.strip())
        save_path = get_user_save_path(username)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump({
                "player": player,
                "history": [],
                "last_saved": datetime.now().isoformat(timespec="seconds")
            }, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("[SaveManager] 登録失敗: " + str(e))
        return False


def verify_login(username: str, password: str) -> bool:
    """ユーザー名とパスワードを検証する"""
    data = _load_users()
    accounts = data.get("accounts", {})
    for name, info in accounts.items():
        if name.lower() == username.strip().lower():
            return info.get("password_hash") == _hash_password(password)
    return False


def user_exists(username: str) -> bool:
    return is_username_taken(username)


def load_player(username: str = "") -> dict:
    if not username:
        return new_player()
    save_path = get_user_save_path(username)
    if not save_path.exists():
        return new_player(name=username)
    try:
        with open(save_path, encoding="utf-8") as f:
            data = json.load(f)
        return _validate_and_fill(data.get("player", {}))
    except Exception:
        return new_player(name=username)


def save_player(player: dict, username: str = "") -> bool:
    try:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        name = username or player.get("name", "player")
        save_path = get_user_save_path(name)
        existing: dict = {}
        if save_path.exists():
            try:
                with open(save_path, encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass
        existing["player"] = player
        existing["last_saved"] = datetime.now().isoformat(timespec="seconds")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("[SaveManager] 保存失敗: " + str(e))
        return False


def append_history(session_stats: dict, username: str = "") -> bool:
    try:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        name = username or "player"
        save_path = get_user_save_path(name)
        existing: dict = {}
        if save_path.exists():
            try:
                with open(save_path, encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass
        history = existing.get("history", [])
        history.append({
            "date": date.today().isoformat(),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "grade": session_stats.get("grade_target", ""),
            "total": session_stats.get("total", 0),
            "correct": session_stats.get("correct", 0),
            "accuracy": session_stats.get("accuracy", 0.0),
            "exp_gained": session_stats.get("total_exp", 0),
            "damage_taken": session_stats.get("total_damage", 0),
        })
        existing["history"] = history[-180:]
        existing["last_saved"] = datetime.now().isoformat(timespec="seconds")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("[SaveManager] 履歴保存失敗: " + str(e))
        return False


def save_weak_words(weak_words: list, username: str = "") -> bool:
    try:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        name = username or "player"
        save_path = get_user_save_path(name)
        existing: dict = {}
        if save_path.exists():
            try:
                with open(save_path, encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass
        existing["weak_words"] = weak_words
        existing["last_saved"] = datetime.now().isoformat(timespec="seconds")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("[SaveManager] 苦手単語保存失敗: " + str(e))
        return False


def load_history(username: str = "") -> list:
    if not username:
        return []
    save_path = get_user_save_path(username)
    if not save_path.exists():
        return []
    try:
        with open(save_path, encoding="utf-8") as f:
            data = json.load(f)
        return list(reversed(data.get("history", [])))
    except Exception:
        return []


def save_exists(username: str = "") -> bool:
    if not username:
        return False
    return get_user_save_path(username).exists()


def delete_save(username: str = "") -> bool:
    try:
        if username:
            save_path = get_user_save_path(username)
            if save_path.exists():
                save_path.unlink()
            data = _load_users()
            accounts = data.get("accounts", {})
            accounts = {k: v for k, v in accounts.items() if k.lower() != username.lower()}
            data["accounts"] = accounts
            _save_users(data)
        return True
    except Exception as e:
        print("[SaveManager] 削除失敗: " + str(e))
        return False


def _validate_and_fill(player: dict) -> dict:
    defaults = new_player()
    for key, val in defaults.items():
        if key not in player:
            player[key] = val
    player["exp_to_next"] = exp_to_next_level(player["level"])
    # ネストした辞書のキーも補完
    for slot in ("weapon", "armor", "hat", "cloak"):
        player["equipment"].setdefault(slot, None)
    if "last_login" not in player.get("login_streak", {}):
        player["login_streak"] = {"last_login": "", "streak_days": 0, "claimed_milestones": []}
    return player


# ─────────────────────────────────────────
# ランキング管理
# ─────────────────────────────────────────

def _iso_week_start() -> str:
    """今週の月曜日の日付文字列を返す"""
    today = date.today()
    return (today - __import__("datetime").timedelta(days=today.weekday())).isoformat()


def _load_rankings() -> dict:
    if not RANKINGS_FILE.exists():
        return {"users": {}, "week_start": _iso_week_start()}
    try:
        with open(RANKINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}, "week_start": _iso_week_start()}


def _save_rankings(data: dict):
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(RANKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_ranking(player: dict, username: str):
    """プレイヤーのランキングデータを更新する"""
    if not username:
        return
    try:
        data = _load_rankings()
        current_week = _iso_week_start()
        # 週が変わっていたら全ユーザーの週間データをリセット
        if data.get("week_start") != current_week:
            for u in data.get("users", {}).values():
                u["weekly_correct"] = 0
                u["weekly_total"] = 0
            data["week_start"] = current_week
        users = data.setdefault("users", {})
        users[username] = {
            "name": player.get("name", username),
            "character": player.get("character", ""),
            "level": player.get("level", 1),
            "total_exp": player.get("total_exp_earned", 0),
            "grade_target": player.get("grade_target", "grade_5"),
            "weekly_correct": player.get("weekly_correct", 0),
            "weekly_total": player.get("weekly_total", 0),
            "max_streak": player.get("max_streak", 0),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        _save_rankings(data)
    except Exception as e:
        print("[SaveManager] ランキング更新失敗: " + str(e))


def load_rankings() -> dict:
    """ランキングデータを読み込む（全ユーザー）"""
    data = _load_rankings()
    current_week = _iso_week_start()
    if data.get("week_start") != current_week:
        for u in data.get("users", {}).values():
            u["weekly_correct"] = 0
            u["weekly_total"] = 0
        data["week_start"] = current_week
    return data
