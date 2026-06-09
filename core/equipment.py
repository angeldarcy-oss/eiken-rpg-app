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
    # レア帽子
    "dark_crown": (
        '<rect x="27" y="11" width="26" height="9" fill="#220033"/>'
        '<polygon points="27,11 30,3 33,11" fill="#440055"/>'
        '<polygon points="37,11 40,2 43,11" fill="#330044"/>'
        '<polygon points="47,11 50,3 53,11" fill="#440055"/>'
        '<circle cx="30" cy="6" r="2" fill="#cc00ff"/>'
        '<circle cx="40" cy="4" r="2" fill="#ff0088"/>'
        '<circle cx="50" cy="6" r="2" fill="#cc00ff"/>'
        '<rect x="27" y="18" width="26" height="2" fill="#330044" rx="1"/>'
        '<ellipse cx="40" cy="5" rx="12" ry="3" fill="#550066" opacity="0.4"/>'
    ),
}

# 指輪SVGオーバーレイ（右手首付近 cx≈70, cy≈52、viewBox="0 0 80 100"）
RING_OVERLAYS: dict[str, str] = {
    "fire_ring": (
        '<circle cx="70" cy="52" r="4.5" fill="none" stroke="#ff4400" stroke-width="2"/>'
        '<circle cx="70" cy="47.5" r="2.8" fill="#ff6600"/>'
        '<circle cx="70" cy="47.5" r="1.4" fill="#ffcc00"/>'
    ),
    "ice_ring": (
        '<circle cx="70" cy="52" r="4.5" fill="none" stroke="#88ccff" stroke-width="2"/>'
        '<circle cx="70" cy="47.5" r="2.8" fill="#aaddff"/>'
        '<circle cx="70" cy="47.5" r="1.4" fill="#ffffff" opacity="0.8"/>'
    ),
    "dragon_ring": (
        '<circle cx="70" cy="52" r="4.5" fill="none" stroke="#44bb44" stroke-width="2"/>'
        '<polygon points="70,44.5 72.5,49.5 67.5,49.5" fill="#44bb44"/>'
        '<circle cx="70" cy="52" r="1.5" fill="#88ff88"/>'
    ),
}

# ネックレスSVGオーバーレイ（胸・首元 y≈40–55、viewBox="0 0 80 100"）
NECKLACE_OVERLAYS: dict[str, str] = {
    "hero_necklace": (
        '<path d="M30,42 Q40,50 50,42" stroke="#ffcc00" stroke-width="1.8" fill="none"/>'
        '<circle cx="40" cy="52" r="4" fill="#ffcc00"/>'
        '<circle cx="40" cy="52" r="2.5" fill="#ff8800"/>'
        '<circle cx="40" cy="52" r="1.2" fill="#ffee88"/>'
    ),
    "crystal_necklace": (
        '<path d="M30,42 Q40,50 50,42" stroke="#88ccff" stroke-width="1.8" fill="none"/>'
        '<polygon points="40,48 37,54 40,60 43,54" fill="#aaddff" stroke="#66aaff" stroke-width="0.8"/>'
    ),
    "moon_pendant": (
        '<path d="M30,42 Q40,50 50,42" stroke="#ccaaee" stroke-width="1.8" fill="none"/>'
        '<path d="M36,54 Q40,49 44,54 Q40,51 36,54Z" fill="#cc88ee"/>'
        '<circle cx="40" cy="57" r="2.2" fill="#ddaaff"/>'
        '<circle cx="40" cy="57" r="1" fill="#ffffff" opacity="0.6"/>'
    ),
}

# アイテムメタデータ（全種）
ITEMS: dict[str, dict] = {
    # 帽子
    "leather_cap":      {"name": "革の帽子",           "type": "hat",      "tier": 1, "icon": "🎩"},
    "ranger_hat":       {"name": "レンジャーハット",    "type": "hat",      "tier": 2, "icon": "🪖"},
    "iron_helm":        {"name": "鉄の兜",              "type": "hat",      "tier": 2, "icon": "⛑️"},
    "mage_hat":         {"name": "魔法使いの帽子",      "type": "hat",      "tier": 2, "icon": "🎓"},
    "crown":            {"name": "王冠",                "type": "hat",      "tier": 3, "icon": "👑"},
    "dark_crown":       {"name": "暗黒の王冠",          "type": "hat",      "tier": 4, "icon": "💜", "rare": True},
    # 武器
    "wooden_sword":     {"name": "木の剣",              "type": "weapon",   "tier": 1, "icon": "🗡️"},
    "iron_sword":       {"name": "鉄の剣",              "type": "weapon",   "tier": 2, "icon": "⚔️"},
    "magic_staff":      {"name": "魔法の杖",            "type": "weapon",   "tier": 2, "icon": "🪄"},
    "holy_staff":       {"name": "聖なる杖",            "type": "weapon",   "tier": 2, "icon": "✨"},
    "battle_axe":       {"name": "戦斧",                "type": "weapon",   "tier": 2, "icon": "🪓"},
    "dark_wand":        {"name": "闇の魔杖",            "type": "weapon",   "tier": 2, "icon": "🌑"},
    "lute":             {"name": "リュート",            "type": "weapon",   "tier": 1, "icon": "🎵"},
    "flame_sword":      {"name": "炎の剣",              "type": "weapon",   "tier": 3, "icon": "🔥"},
    "golden_sword":     {"name": "黄金の剣",            "type": "weapon",   "tier": 4, "icon": "🌟", "rare": True},
    "rainbow_staff":    {"name": "虹の魔杖",            "type": "weapon",   "tier": 4, "icon": "🌈", "rare": True},
    # 防具
    "leather_armor":    {"name": "革の鎧",              "type": "armor",    "tier": 1, "icon": "🛡️"},
    "iron_armor":       {"name": "鉄の鎧",              "type": "armor",    "tier": 2, "icon": "⚙️"},
    "mage_robe":        {"name": "魔法使いのローブ",    "type": "armor",    "tier": 2, "icon": "🔮"},
    "holy_robe":        {"name": "聖なるローブ",        "type": "armor",    "tier": 2, "icon": "✝️"},
    "dragon_scale":     {"name": "竜鱗の鎧",            "type": "armor",    "tier": 3, "icon": "🐉"},
    "phoenix_armor":    {"name": "フェニックスアーマー","type": "armor",    "tier": 4, "icon": "🔥", "rare": True},
    # マント
    "wool_cloak":       {"name": "羊毛のマント",        "type": "cloak",    "tier": 1, "icon": "🧥"},
    "silk_cloak":       {"name": "絹のマント",          "type": "cloak",    "tier": 2, "icon": "🎀"},
    "hero_cloak":       {"name": "勇者のマント",        "type": "cloak",    "tier": 3, "icon": "🏆"},
    "dark_cloak":       {"name": "闇のマント",          "type": "cloak",    "tier": 3, "icon": "🌑"},
    "rainbow_cloak":    {"name": "虹のマント",          "type": "cloak",    "tier": 4, "icon": "🌈", "rare": True},
    # 指輪（アクセサリ）
    "fire_ring":        {"name": "炎の指輪",            "type": "ring",     "tier": 3, "icon": "💍"},
    "ice_ring":         {"name": "氷の指輪",            "type": "ring",     "tier": 3, "icon": "💎"},
    "dragon_ring":      {"name": "ドラゴンリング",      "type": "ring",     "tier": 4, "icon": "🐉", "rare": True},
    # ネックレス（アクセサリ）
    "hero_necklace":    {"name": "勇者のネックレス",    "type": "necklace", "tier": 3, "icon": "📿"},
    "crystal_necklace": {"name": "クリスタルネックレス","type": "necklace", "tier": 3, "icon": "💎"},
    "moon_pendant":     {"name": "月のペンダント",      "type": "necklace", "tier": 4, "icon": "🌙", "rare": True},
    # ギルドボス限定ドロップ
    "guild_pendant":        {"name": "ギルドの勲章ペンダント", "type": "necklace", "tier": 5, "icon": "🏅", "rare": True},
    "guild_crest_ring":     {"name": "ギルド紋章の指輪",       "type": "ring",     "tier": 5, "icon": "💠", "rare": True},
    "guild_badge_necklace": {"name": "ギルドの証",             "type": "necklace", "tier": 5, "icon": "🎖️", "rare": True},
    # 季節イベント限定
    "sakura_sword":           {"name": "桜の刀",              "type": "weapon",   "tier": 4, "icon": "🌸", "rare": True,  "season": "spring"},
    "spring_cloak":           {"name": "花見のマント",         "type": "cloak",    "tier": 3, "icon": "🌸",               "season": "spring"},
    "ocean_ring":             {"name": "海の輝き",            "type": "ring",     "tier": 3, "icon": "🌊",               "season": "summer"},
    "summer_hat":             {"name": "麦わら帽子",          "type": "hat",      "tier": 3, "icon": "👒",               "season": "summer"},
    "maple_staff":            {"name": "紅葉の杖",            "type": "weapon",   "tier": 4, "icon": "🍁", "rare": True,  "season": "autumn"},
    "halloween_hat":          {"name": "かぼちゃの帽子",      "type": "hat",      "tier": 3, "icon": "🎃",               "season": "autumn"},
    "snow_crystal_necklace":  {"name": "雪の結晶ネックレス",  "type": "necklace", "tier": 4, "icon": "❄️", "rare": True,  "season": "winter"},
    "santa_hat":              {"name": "サンタ帽子",          "type": "hat",      "tier": 3, "icon": "🎅",               "season": "winter"},
}

# ボス専用レアドロッププール
BOSS_RARE_DROPS: list[str] = [
    "golden_sword", "rainbow_staff", "phoenix_armor", "dark_crown",
    "rainbow_cloak", "dragon_ring", "moon_pendant",
]

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
    if not hat_id or hat_id not in HAT_OVERLAYS:
        return svg_inner
    return svg_inner + HAT_OVERLAYS[hat_id]


def apply_ring_overlay(svg_inner: str, ring_id: str | None) -> str:
    if not ring_id or ring_id not in RING_OVERLAYS:
        return svg_inner
    return svg_inner + RING_OVERLAYS[ring_id]


def apply_necklace_overlay(svg_inner: str, necklace_id: str | None) -> str:
    if not necklace_id or necklace_id not in NECKLACE_OVERLAYS:
        return svg_inner
    return svg_inner + NECKLACE_OVERLAYS[necklace_id]


def equipment_badges_html(equipment: dict | None) -> str:
    """武器・防具・マント・アクセサリのアイコンバッジHTML（サイドバー用）"""
    if not equipment:
        return ""
    parts = []
    for slot in ("weapon", "armor", "cloak", "ring", "necklace"):
        item_id = equipment.get(slot)
        if item_id and item_id in ITEMS:
            item = ITEMS[item_id]
            color = ' style="filter:drop-shadow(0 0 3px #ffcc00);"' if item.get("rare") else ""
            parts.append(
                f'<span title="{item["name"]}" style="font-size:.9rem;margin:0 2px;"{color}>{item["icon"]}</span>'
            )
    if not parts:
        return ""
    return '<div style="text-align:center;margin-top:3px;">' + "".join(parts) + "</div>"
