"""
core/save_manager.py ― Supabaseによるプレイヤーデータの永続化

テーブル構成（supabase_schema.sql 参照）:
  - users    : アカウント（username / password_hash）
  - players  : プレイヤーデータ本体（JSONB）+ 苦手単語
  - history  : 学習履歴（1セッション1行）
  - rankings : 週間ランキング（1ユーザー1行）

関数のシグネチャは旧ファイル保存版と同一なので、呼び出し側の変更は不要。
"""

from __future__ import annotations
from typing import List, Optional
import hashlib
from datetime import date, datetime, timedelta, timezone

from core.player import new_player, exp_to_next_level
from core.supabase_client import get_client


def _hash_password(password: str) -> str:
    """パスワードをSHA-256でハッシュ化する"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────
# ユーザー検索ヘルパー
# ─────────────────────────────────────────

def _get_user_row(username: str) -> Optional[dict]:
    """usernameからusersテーブルの行を取得（大文字小文字を無視）"""
    if not username or not username.strip():
        return None
    try:
        res = (
            get_client().table("users")
            .select("id, username, password_hash")
            .eq("username_lower", username.strip().lower())
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None
    except Exception as e:
        print("[SaveManager] ユーザー取得失敗: " + str(e))
        return None


def _get_user_id(username: str) -> Optional[str]:
    row = _get_user_row(username)
    return row["id"] if row else None


# ─────────────────────────────────────────
# アカウント管理
# ─────────────────────────────────────────

def get_registered_users() -> List[str]:
    try:
        res = get_client().table("users").select("username").execute()
        return [r["username"] for r in res.data]
    except Exception as e:
        print("[SaveManager] ユーザー一覧取得失敗: " + str(e))
        return []


def is_username_taken(username: str) -> bool:
    return _get_user_row(username) is not None


def register_user(username: str, password: str) -> bool:
    """新規ユーザー登録。成功したらTrue、既に存在したらFalseを返す"""
    if is_username_taken(username):
        return False
    try:
        client = get_client()
        name = username.strip()
        res = client.table("users").insert({
            "username": name,
            "password_hash": _hash_password(password),
        }).execute()
        user_id = res.data[0]["id"]
        # 初期プレイヤーデータを作成
        player = new_player(name=name)
        client.table("players").insert({
            "user_id": user_id,
            "data": player,
            "weak_words": [],
            "last_saved": _now_iso(),
        }).execute()
        return True
    except Exception as e:
        print("[SaveManager] 登録失敗: " + str(e))
        return False


def verify_login(username: str, password: str) -> bool:
    """ユーザー名とパスワードを検証する"""
    row = _get_user_row(username)
    if not row:
        return False
    return row.get("password_hash") == _hash_password(password)


def user_exists(username: str) -> bool:
    return is_username_taken(username)


# ─────────────────────────────────────────
# プレイヤーデータ
# ─────────────────────────────────────────

def load_player(username: str = "") -> dict:
    if not username:
        return new_player()
    player = load_player_if_exists(username)
    if player is None:
        return new_player(name=username)
    return player


def load_player_if_exists(username: str) -> Optional[dict]:
    """保存済みプレイヤーデータを返す。存在しなければNone（パーティー表示などに使う）"""
    user_id = _get_user_id(username)
    if not user_id:
        return None
    try:
        res = (
            get_client().table("players")
            .select("data")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not res.data:
            return None
        return _validate_and_fill(res.data[0].get("data") or {})
    except Exception as e:
        print("[SaveManager] 読み込み失敗: " + str(e))
        return None


def save_player(player: dict, username: str = "") -> bool:
    try:
        name = username or player.get("name", "player")
        user_id = _get_user_id(name)
        if not user_id:
            print("[SaveManager] 保存失敗: ユーザーが存在しません: " + str(name))
            return False
        get_client().table("players").upsert({
            "user_id": user_id,
            "data": player,
            "last_saved": _now_iso(),
        }).execute()
        return True
    except Exception as e:
        print("[SaveManager] 保存失敗: " + str(e))
        return False


def save_exists(username: str = "") -> bool:
    if not username:
        return False
    user_id = _get_user_id(username)
    if not user_id:
        return False
    try:
        res = (
            get_client().table("players")
            .select("user_id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return bool(res.data)
    except Exception:
        return False


def delete_save(username: str = "") -> bool:
    """アカウントとプレイヤーデータを削除する（履歴・ランキングもCASCADEで消える）"""
    try:
        if username:
            user_id = _get_user_id(username)
            if user_id:
                get_client().table("users").delete().eq("id", user_id).execute()
        return True
    except Exception as e:
        print("[SaveManager] 削除失敗: " + str(e))
        return False


# ─────────────────────────────────────────
# 苦手単語
# ─────────────────────────────────────────

def save_weak_words(weak_words: list, username: str = "") -> bool:
    try:
        name = username or "player"
        user_id = _get_user_id(name)
        if not user_id:
            return False
        get_client().table("players").upsert({
            "user_id": user_id,
            "weak_words": weak_words,
            "last_saved": _now_iso(),
        }).execute()
        return True
    except Exception as e:
        print("[SaveManager] 苦手単語保存失敗: " + str(e))
        return False


def load_weak_words(username: str = "") -> list:
    if not username:
        return []
    user_id = _get_user_id(username)
    if not user_id:
        return []
    try:
        res = (
            get_client().table("players")
            .select("weak_words")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not res.data:
            return []
        return res.data[0].get("weak_words") or []
    except Exception as e:
        print("[SaveManager] 苦手単語読み込み失敗: " + str(e))
        return []


# ─────────────────────────────────────────
# 学習履歴
# ─────────────────────────────────────────

def append_history(session_stats: dict, username: str = "") -> bool:
    try:
        name = username or "player"
        user_id = _get_user_id(name)
        if not user_id:
            return False
        get_client().table("history").insert({
            "user_id": user_id,
            "played_on": date.today().isoformat(),
            "played_at": _now_iso(),
            "grade": session_stats.get("grade_target", ""),
            "total": session_stats.get("total", 0),
            "correct": session_stats.get("correct", 0),
            "accuracy": float(session_stats.get("accuracy", 0.0)),
            "exp_gained": session_stats.get("total_exp", 0),
            "damage_taken": session_stats.get("total_damage", 0),
        }).execute()
        return True
    except Exception as e:
        print("[SaveManager] 履歴保存失敗: " + str(e))
        return False


def load_history(username: str = "") -> list:
    """学習履歴を新しい順に最大180件返す（旧JSON形式と同じキー構成）"""
    if not username:
        return []
    user_id = _get_user_id(username)
    if not user_id:
        return []
    try:
        res = (
            get_client().table("history")
            .select("played_on, played_at, grade, total, correct, accuracy, exp_gained, damage_taken")
            .eq("user_id", user_id)
            .order("played_at", desc=True)
            .limit(180)
            .execute()
        )
        return [
            {
                "date": r["played_on"],
                "timestamp": r["played_at"],
                "grade": r["grade"],
                "total": r["total"],
                "correct": r["correct"],
                "accuracy": r["accuracy"],
                "exp_gained": r["exp_gained"],
                "damage_taken": r["damage_taken"],
            }
            for r in res.data
        ]
    except Exception as e:
        print("[SaveManager] 履歴読み込み失敗: " + str(e))
        return []


# ─────────────────────────────────────────
# セーブデータ検証
# ─────────────────────────────────────────

def _validate_and_fill(player: dict) -> dict:
    # 旧セーブのフィールドを補完（defaults適用より前に行う）
    if "best_streak" not in player:
        player["best_streak"] = player.get("max_streak", 0)
    if "boss_defeats" not in player:
        player["boss_defeats"] = 0
    defaults = new_player()
    for key, val in defaults.items():
        if key not in player:
            player[key] = val
    player["exp_to_next"] = exp_to_next_level(player["level"])
    # ネストした辞書のキーも補完
    for slot in ("weapon", "armor", "hat", "cloak", "ring", "necklace"):
        player["equipment"].setdefault(slot, None)
    if "last_login" not in player.get("login_streak", {}):
        player["login_streak"] = {"last_login": "", "streak_days": 0, "claimed_milestones": []}
    if "party_code" not in player:
        player["party_code"] = ""
    if "guild_code" not in player:
        player["guild_code"] = ""
    if "event_quests_claimed" not in player:
        player["event_quests_claimed"] = []
    if "event_boss_last_attempt" not in player:
        player["event_boss_last_attempt"] = ""
    if "phoenix_revival_used" not in player:
        player["phoenix_revival_used"] = ""
    if "unicorn_heal_used" not in player:
        player["unicorn_heal_used"] = ""
    if "dungeons" not in player:
        player["dungeons"] = {}
    if "exp_spent" not in player:
        player["exp_spent"] = 0
    return player


# ─────────────────────────────────────────
# ランキング管理
# ─────────────────────────────────────────

def _iso_week_start() -> str:
    """今週の月曜日の日付文字列を返す"""
    today = date.today()
    return (today - timedelta(days=today.weekday())).isoformat()


def update_ranking(player: dict, username: str):
    """プレイヤーのランキングデータを更新する"""
    if not username:
        return
    try:
        user_id = _get_user_id(username)
        if not user_id:
            return
        get_client().table("rankings").upsert({
            "user_id": user_id,
            "username": username,
            "name": player.get("name", username),
            "character": player.get("character", ""),
            "level": player.get("level", 1),
            "total_exp": player.get("total_exp_earned", 0),
            "grade_target": player.get("grade_target", "grade_5"),
            "weekly_correct": player.get("weekly_correct", 0),
            "weekly_total": player.get("weekly_total", 0),
            "max_streak": player.get("max_streak", 0),
            "best_streak": player.get("best_streak", player.get("max_streak", 0)),
            "boss_defeats": player.get("boss_defeats", 0),
            "active_title": player.get("active_title"),
            "titles": player.get("titles", []),
            "week_start": _iso_week_start(),
            "updated_at": _now_iso(),
        }).execute()
    except Exception as e:
        print("[SaveManager] ランキング更新失敗: " + str(e))


def load_rankings() -> dict:
    """ランキングデータを読み込む（全ユーザー、旧JSON形式と同じ構造）"""
    current_week = _iso_week_start()
    try:
        res = get_client().table("rankings").select("*").execute()
        users = {}
        for r in res.data:
            # 週が変わっていたら週間データを0として扱う
            stale = str(r.get("week_start", "")) != current_week
            users[r["username"]] = {
                "name": r.get("name", ""),
                "character": r.get("character", ""),
                "level": r.get("level", 1),
                "total_exp": r.get("total_exp", 0),
                "grade_target": r.get("grade_target", "grade_5"),
                "weekly_correct": 0 if stale else r.get("weekly_correct", 0),
                "weekly_total": 0 if stale else r.get("weekly_total", 0),
                "max_streak": r.get("max_streak", 0),
                "best_streak": r.get("best_streak", 0),
                "boss_defeats": r.get("boss_defeats", 0),
                "active_title": r.get("active_title"),
                "titles": r.get("titles") or [],
                "updated_at": r.get("updated_at", ""),
            }
        return {"users": users, "week_start": current_week}
    except Exception as e:
        print("[SaveManager] ランキング読み込み失敗: " + str(e))
        return {"users": {}, "week_start": current_week}
