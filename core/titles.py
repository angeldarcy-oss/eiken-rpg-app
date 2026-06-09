"""core/titles.py — 称号システム"""
from __future__ import annotations

TITLE_DEFS: list[dict] = [
    {
        "id": "dragon_slayer",
        "name": "ドラゴンスレイヤー",
        "icon": "🐉",
        "desc": "ボスを3体撃破",
        "check": lambda p: p.get("boss_defeats", 0) >= 3,
    },
    {
        "id": "eiken_master",
        "name": "英検マスター",
        "icon": "🎓",
        "desc": "正答率90%以上（100問以上）",
        "check": lambda p: (
            p.get("total_questions_ever", 0) >= 100
            and p.get("total_correct_ever", 0) / max(p.get("total_questions_ever", 1), 1) >= 0.9
        ),
    },
    {
        "id": "streak_master",
        "name": "連続の達人",
        "icon": "🔥",
        "desc": "最高連続30問以上",
        "check": lambda p: p.get("best_streak", 0) >= 30,
    },
    {
        "id": "diligent_scholar",
        "name": "勤勉な学者",
        "icon": "📚",
        "desc": "累計1000問正解",
        "check": lambda p: p.get("total_correct_ever", 0) >= 1000,
    },
    # ダンジョン称号
    {
        "id": "dungeon_rookie",
        "name": "洞窟の探検家",
        "icon": "🏚️",
        "desc": "初心者の洞窟をクリア",
        "check": lambda p: p.get("dungeons", {}).get("cave", {}).get("clears", 0) >= 1,
    },
    {
        "id": "dungeon_explorer",
        "name": "草原の勇者",
        "icon": "🌿",
        "desc": "草原の迷宮をクリア",
        "check": lambda p: p.get("dungeons", {}).get("prairie", {}).get("clears", 0) >= 1,
    },
    {
        "id": "dungeon_mage",
        "name": "森の賢者",
        "icon": "🌲",
        "desc": "魔法の森をクリア",
        "check": lambda p: p.get("dungeons", {}).get("forest", {}).get("clears", 0) >= 1,
    },
    {
        "id": "dungeon_knight",
        "name": "氷の騎士",
        "icon": "❄️",
        "desc": "氷の城をクリア",
        "check": lambda p: p.get("dungeons", {}).get("ice_castle", {}).get("clears", 0) >= 1,
    },
    {
        "id": "dungeon_conqueror",
        "name": "竜の征服者",
        "icon": "🐲",
        "desc": "竜の巣窟をクリア",
        "check": lambda p: p.get("dungeons", {}).get("dragon_lair", {}).get("clears", 0) >= 1,
    },
    {
        "id": "dungeon_champion",
        "name": "ダンジョンチャンピオン",
        "icon": "🏆",
        "desc": "全5ダンジョンをクリア",
        "check": lambda p: all(
            p.get("dungeons", {}).get(d, {}).get("clears", 0) >= 1
            for d in ["cave", "prairie", "forest", "ice_castle", "dragon_lair"]
        ),
    },
]

_TITLE_MAP: dict[str, dict] = {d["id"]: d for d in TITLE_DEFS}


def evaluate_titles(player: dict) -> list[str]:
    """新たに解除された称号IDリストを返し、player["titles"]を更新する"""
    current = set(player.setdefault("titles", []))
    newly_unlocked: list[str] = []
    for tdef in TITLE_DEFS:
        if tdef["id"] not in current:
            try:
                if tdef["check"](player):
                    player["titles"].append(tdef["id"])
                    current.add(tdef["id"])
                    newly_unlocked.append(tdef["id"])
            except Exception:
                pass
    if newly_unlocked and not player.get("active_title"):
        player["active_title"] = player["titles"][0]
    return newly_unlocked


def get_active_title_def(player: dict) -> dict | None:
    tid = player.get("active_title") or (player.get("titles") or [None])[0]
    return _TITLE_MAP.get(tid) if tid else None


def title_badge_html(player: dict, style: str = "sidebar") -> str:
    """称号バッジHTML。style='sidebar' or 'ranking'"""
    tdef = get_active_title_def(player)
    if not tdef:
        return ""
    if style == "sidebar":
        return (
            '<div style="text-align:center;margin-top:3px;">'
            '<span style="background:linear-gradient(135deg,#2a1800,#4a2e00);'
            'border:1px solid #aa7700;border-radius:12px;padding:2px 10px;'
            'font-size:.7rem;color:#ffcc44;">'
            + tdef["icon"] + " " + tdef["name"] +
            "</span></div>"
        )
    return (
        '<span style="background:linear-gradient(135deg,#2a1800,#3a2800);'
        'border:1px solid #886600;border-radius:8px;padding:1px 7px;'
        'font-size:.65rem;color:#ffcc44;white-space:nowrap;">'
        + tdef["icon"] + " " + tdef["name"] +
        "</span>"
    )
