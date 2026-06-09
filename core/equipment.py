"""core/equipment.py — 装備アイテム定義・SVGオーバーレイ"""
from __future__ import annotations

# 帽子SVGオーバーレイ（キャラクターSVG内側末尾に追加）
# viewBox="0 0 80 100"、頭 cy≈22 r≈15
HAT_OVERLAYS: dict[str, str] = {
    "leather_cap": (
        '<ellipse cx="40" cy="16" rx="19" ry="4.5" fill="#6a4820"/>'
        '<ellipse cx="40" cy="11" rx="13" ry="7" fill="#8b6240"/>'
        '<ellipse cx="37" cy="9" rx="6" ry="3" fill="#aa7a55" opacity="0.5"/>'
    ),
    "ranger_hat": (
        '<ellipse cx="40" cy="17" rx="22" ry="5" fill="#6a4820"/>'
        '<ellipse cx="40" cy="12" rx="14" ry="7" fill="#8b6240"/>'
        '<rect x="35" y="10" width="10" height="3" fill="#ffe066" rx="1"/>'
    ),
    "iron_helm": (
        '<ellipse cx="40" cy="16" rx="18" ry="5" fill="#778899"/>'
        '<ellipse cx="40" cy="10" rx="14" ry="10" fill="#aabbcc"/>'
        '<ellipse cx="36" cy="8" rx="6" ry="3.5" fill="#ccdded" opacity="0.5"/>'
        '<rect x="37" y="19" width="6" height="7" fill="#667788" rx="1"/>'
    ),
    "mage_hat": (
        '<polygon points="40,-2 27,18 53,18" fill="#7733dd"/>'
        '<polygon points="40,-2 33,12 47,12" fill="#9944ee"/>'
        '<rect x="25" y="16" width="30" height="5" fill="#5511bb" rx="2"/>'
        '<circle cx="40" cy="0" r="2.5" fill="#cc88ff"/>'
        '<circle cx="40" cy="0" r="1.2" fill="white"/>'
    ),
    "crown": (
        '<rect x="28" y="11" width="24" height="8" fill="#ffe066"/>'
        '<polygon points="28,11 31,4 34,11" fill="#ffcc00"/>'
        '<polygon points="37,11 40,3 43,11" fill="#ffee44"/>'
        '<polygon points="46,11 49,4 52,11" fill="#ffcc00"/>'
        '<circle cx="31" cy="8" r="1.5" fill="#ff4444"/>'
        '<circle cx="40" cy="6" r="1.5" fill="#4488ff"/>'
        '<circle cx="49" cy="8" r="1.5" fill="#44cc44"/>'
    ),
}

# アイテムメタデータ（全種）
ITEMS: dict[str, dict] = {
    # 帽子
    "leather_cap":   {"name": "革の帽子",         "type": "hat",    "tier": 1, "icon": "🎩"},
    "ranger_hat":    {"name": "レンジャーハット",  "type": "hat",    "tier": 2, "icon": "🪖"},
    "iron_helm":     {"name": "鉄の兜",            "type": "hat",    "tier": 2, "icon": "⛑️"},
    "mage_hat":      {"name": "魔法使いの帽子",    "type": "hat",    "tier": 2, "icon": "🎓"},
    "crown":         {"name": "王冠",              "type": "hat",    "tier": 3, "icon": "👑"},
    # 武器
    "wooden_sword":  {"name": "木の剣",            "type": "weapon", "tier": 1, "icon": "🗡️"},
    "iron_sword":    {"name": "鉄の剣",            "type": "weapon", "tier": 2, "icon": "⚔️"},
    "magic_staff":   {"name": "魔法の杖",          "type": "weapon", "tier": 2, "icon": "🪄"},
    "holy_staff":    {"name": "聖なる杖",          "type": "weapon", "tier": 2, "icon": "✨"},
    "battle_axe":    {"name": "戦斧",              "type": "weapon", "tier": 2, "icon": "🪓"},
    "dark_wand":     {"name": "闇の魔杖",          "type": "weapon", "tier": 2, "icon": "🌑"},
    "lute":          {"name": "リュート",          "type": "weapon", "tier": 1, "icon": "🎵"},
    "flame_sword":   {"name": "炎の剣",            "type": "weapon", "tier": 3, "icon": "🔥"},
    # 防具
    "leather_armor": {"name": "革の鎧",            "type": "armor",  "tier": 1, "icon": "🛡️"},
    "iron_armor":    {"name": "鉄の鎧",            "type": "armor",  "tier": 2, "icon": "⚙️"},
    "mage_robe":     {"name": "魔法使いのローブ",  "type": "armor",  "tier": 2, "icon": "🔮"},
    "holy_robe":     {"name": "聖なるローブ",      "type": "armor",  "tier": 2, "icon": "✝️"},
    "dragon_scale":  {"name": "竜鱗の鎧",          "type": "armor",  "tier": 3, "icon": "🐉"},
    # マント
    "wool_cloak":    {"name": "羊毛のマント",      "type": "cloak",  "tier": 1, "icon": "🧥"},
    "silk_cloak":    {"name": "絹のマント",        "type": "cloak",  "tier": 2, "icon": "🎀"},
    "hero_cloak":    {"name": "勇者のマント",      "type": "cloak",  "tier": 3, "icon": "🏆"},
    "dark_cloak":    {"name": "闇のマント",        "type": "cloak",  "tier": 3, "icon": "🌑"},
}

# デイリークエスト報酬テーブル
QUEST_REWARDS: dict[str, str] = {
    "correct10": "wooden_sword",
    "streak5":   "leather_cap",
    "weak3":     "leather_armor",
    "hard5":     "wool_cloak",
}

# 連続ログインボーナステーブル
LOGIN_BONUS_REWARDS: dict[int, str] = {
    1:  "wooden_sword",
    3:  "leather_cap",
    7:  "iron_sword",
    14: "mage_hat",
    30: "crown",
}

LOGIN_BONUS_THRESHOLDS: list[int] = [1, 3, 7, 14, 30]


def apply_hat_overlay(svg_inner: str, hat_id: str | None) -> str:
    """帽子オーバーレイをキャラクターSVG内容に追加する"""
    if not hat_id or hat_id not in HAT_OVERLAYS:
        return svg_inner
    return svg_inner + HAT_OVERLAYS[hat_id]


def equipment_badges_html(equipment: dict | None) -> str:
    """武器・防具・マントのアイコンバッジHTML（サイドバー用）"""
    if not equipment:
        return ""
    parts = []
    for slot in ("weapon", "armor", "cloak"):
        item_id = equipment.get(slot)
        if item_id and item_id in ITEMS:
            item = ITEMS[item_id]
            parts.append(
                f'<span title="{item["name"]}" style="font-size:.9rem;margin:0 2px;">{item["icon"]}</span>'
            )
    if not parts:
        return ""
    return '<div style="text-align:center;margin-top:3px;">' + "".join(parts) + "</div>"
