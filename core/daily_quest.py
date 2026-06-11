"""core/daily_quest.py — デイリークエスト・ログインボーナス管理"""
from __future__ import annotations
from datetime import date, timedelta


QUEST_DEFS = [
    {"id": "correct10", "title": "今日10問正解する",          "title_zh": "今日答對10題",        "target": 10, "icon": "⭐"},
    {"id": "streak5",   "title": "5問連続正解する",            "title_zh": "連續答對5題",          "target": 5,  "icon": "🔥"},
    {"id": "weak3",     "title": "苦手単語を3問正解する",      "title_zh": "正確答對3道弱點單字",  "target": 3,  "icon": "📚"},
    {"id": "hard5",     "title": "難問（3つ星）を5問正解する", "title_zh": "答對5道難題（3星）",  "target": 5,  "icon": "💎"},
]


def _today() -> str:
    return date.today().isoformat()


def get_or_reset_daily_quests(player: dict, weak_count: int | None = None) -> list[dict]:
    """今日のクエストを取得。日付が変わっていたらリセット。
    weak_count を渡すと「苦手単語」クエストの目標数を実際の苦手単語数に合わせて自動調整する。
    """
    dq = player.get("daily_quests", {})
    today = _today()
    if dq.get("date") != today:
        def _target(d: dict) -> int:
            if d["id"] == "weak3" and weak_count is not None and weak_count >= 1:
                return min(d["target"], weak_count)
            return d["target"]

        player["daily_quests"] = {
            "date": today,
            "quests": [
                {"id": d["id"], "progress": 0, "target": _target(d),
                 "completed": False, "claimed": False}
                for d in QUEST_DEFS
            ],
        }
    return player["daily_quests"]["quests"]


def update_quest_progress(player: dict, quest_id: str, amount: int = 1) -> bool:
    """クエスト進捗を更新。completedになったら True を返す。"""
    quests = get_or_reset_daily_quests(player)
    for q in quests:
        if q["id"] == quest_id and not q["completed"]:
            q["progress"] = min(q["progress"] + amount, q["target"])
            if q["progress"] >= q["target"]:
                q["completed"] = True
                return True
            return False
    return False


def get_login_streak(player: dict) -> dict:
    """ログイン連続日数を更新して返す。同日2回呼んでも加算しない。"""
    ls = player.setdefault("login_streak", {
        "last_login": "", "streak_days": 0, "claimed_milestones": []
    })
    today = _today()
    last = ls.get("last_login", "")
    if last == today:
        return ls
    if last:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        ls["streak_days"] = ls.get("streak_days", 0) + 1 if last == yesterday else 1
    else:
        ls["streak_days"] = 1
    ls["last_login"] = today
    return ls


# 毎日のログインEXPボーナス: 基本20 + 連続日数×5（10日目以降は上限）
LOGIN_EXP_BASE = 20
LOGIN_EXP_PER_DAY = 5
LOGIN_EXP_STREAK_CAP = 10


def daily_login_exp_amount(streak_days: int) -> int:
    """連続ログイン日数に応じた今日のボーナスEXP額を返す。"""
    streak = max(1, streak_days)
    return LOGIN_EXP_BASE + LOGIN_EXP_PER_DAY * (min(streak, LOGIN_EXP_STREAK_CAP) - 1)


def claim_daily_login_exp(player: dict) -> int:
    """1日1回、連続日数に応じたログインEXPを付与する。

    付与したEXP額を返す。今日すでに受け取り済みなら0を返す。
    """
    ls = player.setdefault("login_streak", {
        "last_login": "", "streak_days": 0, "claimed_milestones": []
    })
    today = _today()
    if ls.get("last_exp_claim") == today:
        return 0
    exp = daily_login_exp_amount(ls.get("streak_days", 1))
    ls["last_exp_claim"] = today
    from core.player import PlayerManager
    PlayerManager(player).gain_exp(exp)
    return exp


def get_claimable_login_bonuses(player: dict) -> list[int]:
    """受け取り可能なログインボーナスのしきい値リストを返す。"""
    from core.equipment import LOGIN_BONUS_THRESHOLDS
    ls = player.get("login_streak", {})
    streak = ls.get("streak_days", 0)
    claimed = set(ls.get("claimed_milestones", []))
    return [t for t in LOGIN_BONUS_THRESHOLDS if t <= streak and t not in claimed]


def claim_login_bonus(player: dict, days: int) -> str | None:
    """ログインボーナスを受け取り、付与したアイテムIDを返す。"""
    from core.equipment import LOGIN_BONUS_REWARDS
    ls = player.setdefault("login_streak", {"last_login": "", "streak_days": 0, "claimed_milestones": []})
    claimed = ls.setdefault("claimed_milestones", [])
    if days in claimed:
        return None
    item_id = LOGIN_BONUS_REWARDS.get(days)
    if item_id:
        claimed.append(days)
        _add_to_inventory(player, item_id)
    return item_id


def claim_quest_reward(player: dict, quest_id: str) -> str | None:
    """クエスト報酬を受け取り、付与したアイテムIDを返す。"""
    from core.equipment import QUEST_REWARDS
    quests = get_or_reset_daily_quests(player)
    for q in quests:
        if q["id"] == quest_id and q["completed"] and not q["claimed"]:
            item_id = QUEST_REWARDS.get(quest_id)
            if item_id:
                q["claimed"] = True
                _add_to_inventory(player, item_id)
                return item_id
    return None


def equip_item(player: dict, item_id: str) -> bool:
    """インベントリからアイテムを装備する。成功したら True を返す。"""
    from core.equipment import ITEMS
    if item_id not in player.get("inventory", []):
        return False
    item = ITEMS.get(item_id)
    if not item:
        return False
    equip = player.setdefault("equipment", {"weapon": None, "armor": None, "hat": None, "cloak": None, "ring": None, "necklace": None})
    equip[item["type"]] = item_id
    return True


def unequip_slot(player: dict, slot: str):
    """スロットの装備を外す。"""
    equip = player.setdefault("equipment", {"weapon": None, "armor": None, "hat": None, "cloak": None, "ring": None, "necklace": None})
    equip[slot] = None


def _add_to_inventory(player: dict, item_id: str):
    inv = player.setdefault("inventory", [])
    if item_id not in inv:
        inv.append(item_id)
