"""core/equipment_bonus.py — 装備・ペットのゲームプレイボーナス定義・計算"""
from __future__ import annotations

# 装備ボーナス定義
# exp_bonus_pct:      EXP獲得量アップ (武器)
# hp_reduction_pct:   ダメージ軽減 (防具)
# streak_bonus_pct:   連続正解EXP倍率アップ (帽子)
# hp_recovery:        モンスター撃破後HP回復 (マント)
# drop_bonus_pct:     ドロップ率アップ (指輪)
# daily_exp_bonus_pct: デイリークエスト報酬EXPボーナス (ネックレス)
EQUIPMENT_BONUSES: dict[str, dict] = {
    # ─── 武器 ───
    "wooden_sword":   {"exp_bonus_pct": 5},
    "lute":           {"exp_bonus_pct": 5},
    "iron_sword":     {"exp_bonus_pct": 10},
    "magic_staff":    {"exp_bonus_pct": 10},
    "holy_staff":     {"exp_bonus_pct": 10},
    "battle_axe":     {"exp_bonus_pct": 10},
    "dark_wand":      {"exp_bonus_pct": 10},
    "flame_sword":    {"exp_bonus_pct": 20},
    "golden_sword":   {"exp_bonus_pct": 35},
    "rainbow_staff":  {"exp_bonus_pct": 35},
    "sakura_sword":   {"exp_bonus_pct": 35},
    "maple_staff":    {"exp_bonus_pct": 35},
    # ─── 防具 ───
    "leather_armor":  {"hp_reduction_pct": 10},
    "iron_armor":     {"hp_reduction_pct": 20},
    "mage_robe":      {"hp_reduction_pct": 20},
    "holy_robe":      {"hp_reduction_pct": 20},
    "dragon_scale":   {"hp_reduction_pct": 40},
    "phoenix_armor":  {"hp_reduction_pct": 60},
    # ─── 帽子 ───
    "leather_cap":    {"streak_bonus_pct": 5},
    "ranger_hat":     {"streak_bonus_pct": 10},
    "iron_helm":      {"streak_bonus_pct": 10},
    "mage_hat":       {"streak_bonus_pct": 15},
    "crown":          {"streak_bonus_pct": 25},
    "summer_hat":     {"streak_bonus_pct": 25},
    "halloween_hat":  {"streak_bonus_pct": 25},
    "santa_hat":      {"streak_bonus_pct": 25},
    "dark_crown":     {"streak_bonus_pct": 30},
    # ─── マント ───
    "wool_cloak":     {"hp_recovery": 5},
    "silk_cloak":     {"hp_recovery": 10},
    "hero_cloak":     {"hp_recovery": 15},
    "dark_cloak":     {"hp_recovery": 15},
    "spring_cloak":   {"hp_recovery": 15},
    "rainbow_cloak":  {"hp_recovery": 30},
    # ─── 指輪 ───
    "fire_ring":         {"drop_bonus_pct": 20},
    "ice_ring":          {"drop_bonus_pct": 20},
    "ocean_ring":        {"drop_bonus_pct": 20},
    "dragon_ring":       {"drop_bonus_pct": 30},
    "guild_crest_ring":  {"drop_bonus_pct": 40},
    # ─── ネックレス ───
    "hero_necklace":         {"daily_exp_bonus_pct": 25},
    "crystal_necklace":      {"daily_exp_bonus_pct": 25},
    "moon_pendant":          {"daily_exp_bonus_pct": 35},
    "snow_crystal_necklace": {"daily_exp_bonus_pct": 35},
    "guild_pendant":         {"daily_exp_bonus_pct": 50},
    "guild_badge_necklace":  {"daily_exp_bonus_pct": 50},
}

# ペットボーナス定義
PET_BONUSES: dict[str, dict] = {
    "dragon":  {
        "boss_damage_pct": 30,
        "icon": "🐉", "name": "ドラゴン",
        "desc": "ボスへのダメージ+30%",
    },
    "phoenix": {
        "revival": True, "revival_hp_pct": 50,
        "icon": "🔥", "name": "フェニックス",
        "desc": "HP0で1回復活（HP50%で）",
    },
    "unicorn": {
        "daily_hp_full": True,
        "icon": "🦄", "name": "ユニコーン",
        "desc": "1日1回HP全回復",
    },
    "slime": {
        "hp_per_correct": 1,
        "icon": "💧", "name": "スライム",
        "desc": "正解するたびHP+1回復",
    },
    "cat": {
        "login_exp_bonus": 50,
        "icon": "🐱", "name": "ネコ",
        "desc": "毎日ログインEXP+50",
    },
}


def get_equipment_bonuses(equipment: dict) -> dict:
    """装備スロットから全ボーナスを集計して返す。"""
    totals: dict[str, int] = {
        "exp_bonus_pct": 0,
        "hp_reduction_pct": 0,
        "streak_bonus_pct": 0,
        "hp_recovery": 0,
        "drop_bonus_pct": 0,
        "daily_exp_bonus_pct": 0,
    }
    if not equipment:
        return totals
    for item_id in equipment.values():
        if item_id and item_id in EQUIPMENT_BONUSES:
            for k, v in EQUIPMENT_BONUSES[item_id].items():
                if k in totals:
                    totals[k] += v
    return totals


def get_pet_bonus(player: dict) -> dict:
    """アクティブペットのボーナスを返す。"""
    pet_id = player.get("active_pet")
    return PET_BONUSES.get(pet_id, {}) if pet_id else {}


def get_all_bonuses(player: dict) -> dict:
    """装備＋ペットの全ボーナスを統合して返す。"""
    bonuses = get_equipment_bonuses(player.get("equipment", {}))
    pet = get_pet_bonus(player)
    bonuses["boss_damage_pct"]        = pet.get("boss_damage_pct", 0)
    bonuses["phoenix_revival"]        = pet.get("revival", False)
    bonuses["phoenix_revival_hp_pct"] = pet.get("revival_hp_pct", 50)
    bonuses["unicorn_daily_hp"]       = pet.get("daily_hp_full", False)
    bonuses["slime_hp_per_correct"]   = pet.get("hp_per_correct", 0)
    bonuses["cat_login_exp"]          = pet.get("login_exp_bonus", 0)
    return bonuses


def get_bonus_description(item_id: str) -> str:
    """アイテムIDからボーナス説明文（1行）を返す。"""
    b = EQUIPMENT_BONUSES.get(item_id, {})
    if "exp_bonus_pct" in b:
        return f"⚔️ EXP獲得 +{b['exp_bonus_pct']}%"
    if "hp_reduction_pct" in b:
        return f"🛡️ ダメージ -{b['hp_reduction_pct']}%"
    if "streak_bonus_pct" in b:
        return f"🎩 連続ボーナス +{b['streak_bonus_pct']}%"
    if "hp_recovery" in b:
        return f"🧥 撃破後 HP+{b['hp_recovery']}"
    if "drop_bonus_pct" in b:
        return f"💍 ドロップ率 +{b['drop_bonus_pct']}%"
    if "daily_exp_bonus_pct" in b:
        return f"📿 デイリーEXP +{b['daily_exp_bonus_pct']}%"
    return ""


def sidebar_bonus_html(player: dict) -> str:
    """サイドバー用のボーナスサマリーHTML。ボーナスがなければ空文字を返す。"""
    equipment = player.get("equipment", {})
    pet_id = player.get("active_pet")
    lines: list[str] = []
    for item_id in equipment.values():
        if item_id:
            desc = get_bonus_description(item_id)
            if desc:
                lines.append(desc)
    if pet_id and pet_id in PET_BONUSES:
        pb = PET_BONUSES[pet_id]
        lines.append(f"{pb['icon']} {pb['name']}: {pb['desc']}")
    if not lines:
        return ""
    rows = "".join(
        f'<div style="font-size:.68rem;color:#aaccaa;padding:1px 0;'
        f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{ln}</div>'
        for ln in lines
    )
    return (
        '<div style="background:linear-gradient(135deg,#0a1a0a,#0a120a);'
        'border:1px solid #2a4a2a;border-radius:8px;padding:8px 10px;margin:4px 0 8px;">'
        '<div style="font-size:.7rem;font-weight:700;color:#66cc66;margin-bottom:4px;">✨ 装備ボーナス</div>'
        + rows + '</div>'
    )
