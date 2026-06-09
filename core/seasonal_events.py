"""core/seasonal_events.py — 季節イベントシステム"""
from __future__ import annotations
import json
import random
from datetime import date, datetime
from pathlib import Path

EVENTS_DIR = Path("data/events")
EVENT_BOSS_QUESTIONS = 5  # 1回の挑戦で出る問題数


# ── 季節ボスSVG ────────────────────────────────────────────────
_EVENT_BOSS_SVG: dict[str, str] = {
    "sakura_spirit": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<ellipse cx="40" cy="22" rx="13" ry="12" fill="#ee88cc"/>'
        '<circle cx="34" cy="21" r="3" fill="#fff"/><circle cx="34" cy="21" r="1.6" fill="#cc0066"/>'
        '<circle cx="46" cy="21" r="3" fill="#fff"/><circle cx="46" cy="21" r="1.6" fill="#cc0066"/>'
        '<path d="M36,27 Q40,30 44,27" stroke="#aa0044" stroke-width="1.5" fill="none"/>'
        '<ellipse cx="40" cy="48" rx="14" ry="17" fill="#dd66bb"/>'
        '<path d="M26,44 Q40,68 54,44" fill="#cc44aa" opacity=".7"/>'
        '<ellipse cx="20" cy="36" rx="8" ry="5" fill="#ff99cc" opacity=".8" transform="rotate(-25 20 36)"/>'
        '<ellipse cx="60" cy="36" rx="8" ry="5" fill="#ff99cc" opacity=".8" transform="rotate(25 60 36)"/>'
        '<circle cx="27" cy="14" r="4" fill="#ffbbdd"/><circle cx="53" cy="14" r="4" fill="#ffbbdd"/>'
        '<circle cx="29" cy="12" r="1.8" fill="#ff44aa"/><circle cx="55" cy="12" r="1.8" fill="#ff44aa"/>'
        '<ellipse cx="40" cy="12" rx="4" ry="5" fill="#ff88cc"/>'
        '</svg>'
    ),
    "wave_demon": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M8,55 Q20,40 32,52 Q40,58 48,52 Q60,40 72,55 Q66,70 40,72 Q14,70 8,55Z" fill="#0066cc"/>'
        '<path d="M14,50 Q26,37 36,48 Q40,53 44,48 Q54,37 66,50 Q60,62 40,64 Q20,62 14,50Z" fill="#0088ee"/>'
        '<ellipse cx="40" cy="28" rx="15" ry="14" fill="#0077dd"/>'
        '<ellipse cx="40" cy="26" rx="13" ry="12" fill="#0099ff"/>'
        '<circle cx="34" cy="24" r="4" fill="#eeffff"/><circle cx="34" cy="24" r="2.2" fill="#0033aa"/>'
        '<circle cx="46" cy="24" r="4" fill="#eeffff"/><circle cx="46" cy="24" r="2.2" fill="#0033aa"/>'
        '<path d="M35,32 Q40,36 45,32" stroke="#005599" stroke-width="1.8" fill="none"/>'
        '<polygon points="34,32 36,37 38,32" fill="white" opacity=".7"/>'
        '<polygon points="42,32 44,37 46,32" fill="white" opacity=".7"/>'
        '<path d="M14,16 Q22,8 30,16" stroke="#44aaff" stroke-width="3" fill="none" stroke-linecap="round"/>'
        '<path d="M50,16 Q58,8 66,16" stroke="#44aaff" stroke-width="3" fill="none" stroke-linecap="round"/>'
        '</svg>'
    ),
    "pumpkin_king": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="30" y="56" width="20" height="16" rx="3" fill="#1a1a1a"/>'
        '<ellipse cx="40" cy="56" rx="22" ry="6" fill="#1a1a1a"/>'
        '<ellipse cx="26" cy="44" rx="12" ry="15" fill="#dd6600"/>'
        '<ellipse cx="40" cy="42" rx="14" ry="17" fill="#ff8800"/>'
        '<ellipse cx="54" cy="44" rx="12" ry="15" fill="#dd6600"/>'
        '<ellipse cx="40" cy="41" rx="12" ry="15" fill="#ffaa00"/>'
        '<polygon points="32,32 34,22 38,32" fill="#ff6600"/>'
        '<polygon points="42,32 46,22 48,32" fill="#ff6600"/>'
        '<polygon points="34,36 30,42 38,39" fill="#111"/>'
        '<polygon points="46,36 50,42 42,39" fill="#111"/>'
        '<rect x="36" y="44" width="8" height="3" rx="1" fill="#111"/>'
        '<path d="M34,50 L40,55 L46,50" stroke="#111" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        '<path d="M36,32 Q40,28 44,32" stroke="#cc5500" stroke-width="2" fill="none"/>'
        '</svg>'
    ),
    "snow_king": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="28" y="12" width="24" height="8" rx="4" fill="#cc0000"/>'
        '<polygon points="28,12 31,4 34,12" fill="#cc0000"/>'
        '<polygon points="37,12 40,3 43,12" fill="#cc0000"/>'
        '<polygon points="46,12 49,4 52,12" fill="#cc0000"/>'
        '<circle cx="38" cy="8" r="1.5" fill="#ffdd00"/>'
        '<circle cx="42" cy="5" r="1.5" fill="#ffdd00"/>'
        '<ellipse cx="40" cy="28" rx="14" ry="13" fill="#ddeeff"/>'
        '<circle cx="35" cy="26" r="4" fill="#fff"/><circle cx="35" cy="26" r="2.2" fill="#0066cc"/>'
        '<circle cx="45" cy="26" r="4" fill="#fff"/><circle cx="45" cy="26" r="2.2" fill="#0066cc"/>'
        '<path d="M35,33 Q40,37 45,33" stroke="#6699cc" stroke-width="1.8" fill="none"/>'
        '<ellipse cx="40" cy="52" rx="20" ry="19" fill="#cce0ff"/>'
        '<ellipse cx="40" cy="50" rx="18" ry="17" fill="#ddeeff"/>'
        '<path d="M28,50 L52,50 M40,38 L40,62 M30,42 L50,58 M30,58 L50,42" stroke="#aaccee" stroke-width="2.5"/>'
        '<ellipse cx="22" cy="52" rx="10" ry="9" fill="#cce0ff"/>'
        '<ellipse cx="58" cy="52" rx="10" ry="9" fill="#cce0ff"/>'
        '</svg>'
    ),
}

# ── 季節定義 ────────────────────────────────────────────────────
SEASONS: list[dict] = [
    {
        "id": "spring",
        "name": "春の英検祭り",
        "icon": "🌸",
        "months": [3, 4, 5],
        "description": "桜が舞う季節に英語の力を磨こう！季節限定装備と称号をゲット！",
        "theme": {
            "bg": "linear-gradient(135deg,#1a0a1a,#2a0a2a,#1a0010)",
            "border": "#ff66bb",
            "accent": "#ffbbee",
            "primary": "#ff44aa",
            "secondary": "#ffaadd",
            "banner_bg": "linear-gradient(135deg,#2a001a,#3a1030)",
            "tab_color": "#ff88cc",
            "glow": "0 0 18px #ff44aa88",
        },
        "boss": {
            "id": "sakura_spirit",
            "name": "桜の精霊",
            "emoji": "🌸",
            "desc": "桜の花びらで全てを覆い尽くす幻の精霊",
            "svg": _EVENT_BOSS_SVG["sakura_spirit"],
            "score_per_correct": 20,
            "bonus_score": 50,
        },
        "quests": [
            {
                "id": "spring_q1",
                "name": "🌸 桜吹雪クエスト",
                "desc": "今週20問正解しよう",
                "condition_type": "weekly_correct",
                "condition_value": 20,
                "reward_exp": 300,
                "reward_item": "sakura_sword",
                "reward_title": None,
                "icon": "⚔️",
            },
            {
                "id": "spring_q2",
                "name": "🌷 花見チャレンジ",
                "desc": "最高連続正解数5問以上達成",
                "condition_type": "best_streak",
                "condition_value": 5,
                "reward_exp": 200,
                "reward_item": None,
                "reward_title": None,
                "icon": "🔥",
            },
            {
                "id": "spring_q3",
                "name": "🎋 春の大冒険",
                "desc": "ボスを1体倒す",
                "condition_type": "boss_defeats",
                "condition_value": 1,
                "reward_exp": 400,
                "reward_item": "spring_cloak",
                "reward_title": "spring_adventurer",
                "icon": "👑",
            },
        ],
        "archive_note": "桜の刀・花見のマント・桜の冒険者称号が入手可能",
    },
    {
        "id": "summer",
        "name": "真夏の英語大作戦",
        "icon": "🌊",
        "months": [6, 7, 8],
        "description": "熱い夏に英語力を爆上げしよう！海と花火の季節限定イベント！",
        "theme": {
            "bg": "linear-gradient(135deg,#000a1a,#001a2a,#001030)",
            "border": "#00aaff",
            "accent": "#aae0ff",
            "primary": "#0088ff",
            "secondary": "#44ccff",
            "banner_bg": "linear-gradient(135deg,#000a1a,#001a2a)",
            "tab_color": "#44aaff",
            "glow": "0 0 18px #0088ff88",
        },
        "boss": {
            "id": "wave_demon",
            "name": "波の魔王",
            "emoji": "🌊",
            "desc": "夏の海から現れた伝説の魔王",
            "svg": _EVENT_BOSS_SVG["wave_demon"],
            "score_per_correct": 20,
            "bonus_score": 50,
        },
        "quests": [
            {
                "id": "summer_q1",
                "name": "🌊 海の勇者",
                "desc": "今週20問正解しよう",
                "condition_type": "weekly_correct",
                "condition_value": 20,
                "reward_exp": 300,
                "reward_item": "ocean_ring",
                "reward_title": None,
                "icon": "💍",
            },
            {
                "id": "summer_q2",
                "name": "🎆 花火大会",
                "desc": "ダンジョンを1つクリアする",
                "condition_type": "dungeon_clear",
                "condition_value": 1,
                "reward_exp": 250,
                "reward_item": None,
                "reward_title": None,
                "icon": "🏚️",
            },
            {
                "id": "summer_q3",
                "name": "🏖️ 真夏の猛特訓",
                "desc": "累計正解数100問達成",
                "condition_type": "total_correct",
                "condition_value": 100,
                "reward_exp": 400,
                "reward_item": "summer_hat",
                "reward_title": "summer_hero",
                "icon": "🏆",
            },
        ],
        "archive_note": "海の指輪・麦わら帽子・夏の英雄称号が入手可能",
    },
    {
        "id": "autumn",
        "name": "紅葉とハロウィンの宴",
        "icon": "🍁",
        "months": [9, 10, 11],
        "description": "秋の夜長に英語の魔法を学ぼう！ハロウィン限定ボスが出現！",
        "theme": {
            "bg": "linear-gradient(135deg,#1a0a00,#2a1000,#1a0a00)",
            "border": "#ff8800",
            "accent": "#ffdd88",
            "primary": "#ff6600",
            "secondary": "#ffaa44",
            "banner_bg": "linear-gradient(135deg,#2a0a00,#3a1500)",
            "tab_color": "#ff9944",
            "glow": "0 0 18px #ff660088",
        },
        "boss": {
            "id": "pumpkin_king",
            "name": "カボチャ魔王",
            "emoji": "🎃",
            "desc": "ハロウィンの夜に現れる伝説の魔王",
            "svg": _EVENT_BOSS_SVG["pumpkin_king"],
            "score_per_correct": 20,
            "bonus_score": 50,
        },
        "quests": [
            {
                "id": "autumn_q1",
                "name": "🍁 紅葉狩りクエスト",
                "desc": "今週20問正解しよう",
                "condition_type": "weekly_correct",
                "condition_value": 20,
                "reward_exp": 300,
                "reward_item": "maple_staff",
                "reward_title": None,
                "icon": "🪄",
            },
            {
                "id": "autumn_q2",
                "name": "🎃 ハロウィンチャレンジ",
                "desc": "最高連続正解数7問以上達成",
                "condition_type": "best_streak",
                "condition_value": 7,
                "reward_exp": 350,
                "reward_item": None,
                "reward_title": None,
                "icon": "🔥",
            },
            {
                "id": "autumn_q3",
                "name": "🏆 秋の収穫祭",
                "desc": "ボスを2体倒す",
                "condition_type": "boss_defeats",
                "condition_value": 2,
                "reward_exp": 500,
                "reward_item": "halloween_hat",
                "reward_title": "autumn_sage",
                "icon": "👑",
            },
        ],
        "archive_note": "紅葉の杖・かぼちゃの帽子・秋の賢者称号が入手可能",
    },
    {
        "id": "winter",
        "name": "雪と光のウィンターフェスト",
        "icon": "❄️",
        "months": [12, 1, 2],
        "description": "クリスマス・お正月・冬の英語フェスタ！雪の魔王に挑め！",
        "theme": {
            "bg": "linear-gradient(135deg,#00081a,#000a22,#00061a)",
            "border": "#88ccff",
            "accent": "#ddeeff",
            "primary": "#44aaff",
            "secondary": "#aaddff",
            "banner_bg": "linear-gradient(135deg,#000a1a,#001530)",
            "tab_color": "#66bbff",
            "glow": "0 0 18px #44aaff88",
        },
        "boss": {
            "id": "snow_king",
            "name": "雪の魔王",
            "emoji": "☃️",
            "desc": "真冬の猛吹雪を操る古の魔王",
            "svg": _EVENT_BOSS_SVG["snow_king"],
            "score_per_correct": 20,
            "bonus_score": 50,
        },
        "quests": [
            {
                "id": "winter_q1",
                "name": "❄️ 雪の結晶チャレンジ",
                "desc": "今週20問正解しよう",
                "condition_type": "weekly_correct",
                "condition_value": 20,
                "reward_exp": 300,
                "reward_item": "snow_crystal_necklace",
                "reward_title": None,
                "icon": "📿",
            },
            {
                "id": "winter_q2",
                "name": "🎄 クリスマスクエスト",
                "desc": "最高連続正解数10問以上達成",
                "condition_type": "best_streak",
                "condition_value": 10,
                "reward_exp": 400,
                "reward_item": None,
                "reward_title": None,
                "icon": "🔥",
            },
            {
                "id": "winter_q3",
                "name": "🎍 お正月大修行",
                "desc": "累計正解数300問達成",
                "condition_type": "total_correct",
                "condition_value": 300,
                "reward_exp": 500,
                "reward_item": "santa_hat",
                "reward_title": "winter_knight",
                "icon": "🏆",
            },
        ],
        "archive_note": "雪の結晶ネックレス・サンタ帽子・冬の騎士称号が入手可能",
    },
]

_SEASON_MAP: dict[str, dict] = {s["id"]: s for s in SEASONS}


# ── ユーティリティ ─────────────────────────────────────────────
def _ensure_dir() -> None:
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _today() -> str:
    return date.today().isoformat()


def _event_file(season_id: str, year: int) -> Path:
    return EVENTS_DIR / f"{season_id}_{year}.json"


# ── 季節判定 ───────────────────────────────────────────────────
def get_current_season(target_date: date | None = None) -> dict | None:
    """現在の季節イベントを返す。オフシーズンなら None"""
    d = target_date or date.today()
    m = d.month
    for s in SEASONS:
        if m in s["months"]:
            return s
    return None


def get_season_end_date(season: dict, target_date: date | None = None) -> date:
    """季節の終了日（その季節の最終月の最終日）を返す"""
    d = target_date or date.today()
    months = season["months"]
    last_month = months[-1]
    year = d.year
    if last_month < d.month and last_month in [1, 2]:
        year += 1
    import calendar
    last_day = calendar.monthrange(year, last_month)[1]
    return date(year, last_month, last_day)


def days_remaining(season: dict) -> int:
    end = get_season_end_date(season)
    delta = (end - date.today()).days
    return max(0, delta)


def get_season_year(season: dict, target_date: date | None = None) -> int:
    """イベントランキングに使う年（冬季は月をまたぐため調整）"""
    d = target_date or date.today()
    if season["id"] == "winter" and d.month in [1, 2]:
        return d.year - 1
    return d.year


# ── イベントランキング ──────────────────────────────────────────
def _load_event_data(season_id: str, year: int) -> dict:
    f = _event_file(season_id, year)
    if not f.exists():
        return {"season": season_id, "year": year, "players": {}}
    try:
        with open(f, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"season": season_id, "year": year, "players": {}}


def _save_event_data(data: dict) -> None:
    _ensure_dir()
    f = _event_file(data["season"], data["year"])
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def add_event_score(season_id: str, year: int, username: str,
                    player_name: str, character: str, level: int,
                    score: int, quest_completed: bool = False) -> None:
    """プレイヤーのイベントスコアを加算し、ランキングを更新"""
    data = _load_event_data(season_id, year)
    players = data.setdefault("players", {})
    entry = players.get(username, {
        "name": player_name, "character": character, "level": level,
        "score": 0, "boss_attempts": 0, "quests_completed": 0,
        "updated_at": _now(),
    })
    entry["score"] = entry.get("score", 0) + score
    entry["name"] = player_name
    entry["character"] = character
    entry["level"] = level
    if quest_completed:
        entry["quests_completed"] = entry.get("quests_completed", 0) + 1
    entry["updated_at"] = _now()
    players[username] = entry
    data["players"] = players
    _save_event_data(data)


def add_boss_attempt_score(season_id: str, year: int, username: str,
                           player_name: str, character: str, level: int,
                           correct: int, total: int) -> int:
    """ボス挑戦スコアを記録し、獲得スコアを返す"""
    season = _SEASON_MAP.get(season_id, {})
    boss = season.get("boss", {})
    per = boss.get("score_per_correct", 20)
    bonus = boss.get("bonus_score", 50) if correct == total else 0
    score = per * correct + bonus

    data = _load_event_data(season_id, year)
    players = data.setdefault("players", {})
    entry = players.get(username, {
        "name": player_name, "character": character, "level": level,
        "score": 0, "boss_attempts": 0, "quests_completed": 0,
        "updated_at": _now(),
    })
    entry["score"] = entry.get("score", 0) + score
    entry["boss_attempts"] = entry.get("boss_attempts", 0) + 1
    entry["name"] = player_name
    entry["character"] = character
    entry["level"] = level
    entry["updated_at"] = _now()
    players[username] = entry
    data["players"] = players
    _save_event_data(data)
    return score


def get_event_ranking(season_id: str, year: int) -> list[dict]:
    """スコア順のランキングリスト（最大20件）"""
    data = _load_event_data(season_id, year)
    entries = [
        {"username": u, **v}
        for u, v in data.get("players", {}).items()
    ]
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)
    return entries[:20]


def get_player_rank(season_id: str, year: int, username: str) -> int | None:
    """プレイヤーの順位を返す（1始まり）。未参加なら None"""
    ranking = get_event_ranking(season_id, year)
    for i, e in enumerate(ranking):
        if e.get("username") == username:
            return i + 1
    return None


# ── イベントクエスト ────────────────────────────────────────────
def _quest_key(season_id: str, year: int, quest_id: str) -> str:
    return f"{season_id}_{year}_{quest_id}"


def get_quest_progress(quest: dict, player: dict) -> tuple[int, int]:
    """(current, target) を返す"""
    ct = quest["condition_type"]
    target = quest["condition_value"]
    if ct == "weekly_correct":
        return player.get("weekly_correct", 0), target
    if ct == "best_streak":
        return player.get("best_streak", 0), target
    if ct == "boss_defeats":
        return player.get("boss_defeats", 0), target
    if ct == "dungeon_clear":
        cleared = sum(
            1 for v in player.get("dungeons", {}).values()
            if v.get("clears", 0) >= 1
        )
        return cleared, target
    if ct == "total_correct":
        return player.get("total_correct_ever", 0), target
    return 0, target


def is_quest_complete(quest: dict, player: dict) -> bool:
    cur, target = get_quest_progress(quest, player)
    return cur >= target


def is_quest_claimed(season_id: str, year: int, quest_id: str, player: dict) -> bool:
    key = _quest_key(season_id, year, quest_id)
    return key in player.get("event_quests_claimed", [])


def claim_quest(season_id: str, year: int, quest: dict, player: dict,
                username: str, player_name: str, character: str) -> dict:
    """クエスト報酬を適用して返す: {"exp": int, "item": str|None, "title": str|None}"""
    key = _quest_key(season_id, year, quest["id"])
    if key in player.get("event_quests_claimed", []):
        return {}
    if not is_quest_complete(quest, player):
        return {}

    player.setdefault("event_quests_claimed", []).append(key)

    reward_item = quest.get("reward_item")
    if reward_item:
        inv = player.setdefault("inventory", [])
        if reward_item not in inv:
            inv.append(reward_item)

    reward_title = quest.get("reward_title")
    if reward_title:
        titles = player.setdefault("titles", [])
        if reward_title not in titles:
            titles.append(reward_title)
        if not player.get("active_title"):
            player["active_title"] = reward_title

    # イベントスコアに反映
    add_event_score(
        season_id, year, username, player_name, character,
        player.get("level", 1), quest["reward_exp"], quest_completed=True,
    )

    return {
        "exp": quest["reward_exp"],
        "item": reward_item,
        "title": reward_title,
    }


# ── イベントボス（1日1回チャレンジ） ───────────────────────────
def can_challenge_boss_today(player: dict) -> bool:
    """今日のボス挑戦権があるか"""
    return player.get("event_boss_last_attempt", "") != _today()


def record_boss_attempt(player: dict) -> None:
    """ボス挑戦日を記録（1日1回制限）"""
    player["event_boss_last_attempt"] = _today()
