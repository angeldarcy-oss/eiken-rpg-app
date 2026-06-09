"""core/shop.py — ショップ商品カタログ・購入ロジック"""
from __future__ import annotations
import hashlib
from datetime import date

from core.equipment import ITEMS as _EQUIP_ITEMS
from core.pets import PET_DEFS, add_egg

# ─── 商品カタログ ──────────────────────────────────────────────────
# rare=True → レア入荷枠（週替わり3種のみ販売）
# limited=True → 週替わりセール対象外（レアはすでに週替わり）
SHOP_CATALOG: list[dict] = [
    # 武器
    {"id": "wooden_sword",  "category": "weapon",   "price": 0,     "desc": "初心者向けの頼もしい一本"},
    {"id": "lute",          "category": "weapon",   "price": 200,   "desc": "音楽で仲間を励ます弦楽器"},
    {"id": "iron_sword",    "category": "weapon",   "price": 800,   "desc": "鍛え上げられた頑丈な剣"},
    {"id": "magic_staff",   "category": "weapon",   "price": 1000,  "desc": "魔法の力を秘めた杖"},
    {"id": "holy_staff",    "category": "weapon",   "price": 1200,  "desc": "聖なる光を放つ神秘の杖"},
    {"id": "battle_axe",    "category": "weapon",   "price": 1000,  "desc": "強力な一撃を与える戦斧"},
    {"id": "dark_wand",     "category": "weapon",   "price": 1500,  "desc": "闇の魔力が宿る禁断の杖"},
    {"id": "flame_sword",   "category": "weapon",   "price": 3000,  "desc": "炎をまとう伝説の剣"},
    {"id": "golden_sword",  "category": "weapon",   "price": 8000,  "desc": "純金で造られた究極の剣",          "rare": True},
    {"id": "rainbow_staff", "category": "weapon",   "price": 9000,  "desc": "七色の魔力をもつ至高の杖",        "rare": True},
    # 防具
    {"id": "leather_armor", "category": "armor",    "price": 0,     "desc": "軽くて動きやすい革の鎧"},
    {"id": "iron_armor",    "category": "armor",    "price": 1000,  "desc": "頑丈な鉄で造られた鎧"},
    {"id": "mage_robe",     "category": "armor",    "price": 1200,  "desc": "魔法使いが愛用する長衣"},
    {"id": "holy_robe",     "category": "armor",    "price": 1500,  "desc": "聖なる加護をもたらすローブ"},
    {"id": "dragon_scale",  "category": "armor",    "price": 3500,  "desc": "竜の鱗で作られた最強の鎧"},
    {"id": "phoenix_armor", "category": "armor",    "price": 10000, "desc": "不死鳥の羽から作られた伝説の鎧",  "rare": True},
    # 帽子
    {"id": "leather_cap",   "category": "hat",      "price": 0,     "desc": "シンプルで使いやすい革帽子"},
    {"id": "ranger_hat",    "category": "hat",      "price": 600,   "desc": "旅人に愛される風格のある帽子"},
    {"id": "iron_helm",     "category": "hat",      "price": 800,   "desc": "頭部を守る頑丈な鉄の兜"},
    {"id": "mage_hat",      "category": "hat",      "price": 1000,  "desc": "魔力を高める尖り帽子"},
    {"id": "crown",         "category": "hat",      "price": 4000,  "desc": "英雄の証たる輝く王冠"},
    {"id": "dark_crown",    "category": "hat",      "price": 9000,  "desc": "闇の王者が持つ禁断の冠",          "rare": True},
    # マント
    {"id": "wool_cloak",    "category": "cloak",    "price": 200,   "desc": "あたたかい羊毛のマント"},
    {"id": "silk_cloak",    "category": "cloak",    "price": 800,   "desc": "なめらかな絹のマント"},
    {"id": "dark_cloak",    "category": "cloak",    "price": 2500,  "desc": "闇に紛れる漆黒のマント"},
    {"id": "hero_cloak",    "category": "cloak",    "price": 3000,  "desc": "勇者だけが身に付けられるマント"},
    {"id": "rainbow_cloak", "category": "cloak",    "price": 9000,  "desc": "七色に輝く究極のマント",          "rare": True},
    # ネックレス
    {"id": "crystal_necklace","category": "necklace","price": 2000, "desc": "クリスタルが輝くネックレス"},
    {"id": "hero_necklace", "category": "necklace", "price": 2500,  "desc": "勇者の証のゴールドネックレス"},
    {"id": "moon_pendant",  "category": "necklace", "price": 7000,  "desc": "月の加護を受けるペンダント",      "rare": True},
    # 指輪
    {"id": "fire_ring",     "category": "ring",     "price": 2500,  "desc": "炎の力を宿す指輪"},
    {"id": "ice_ring",      "category": "ring",     "price": 2500,  "desc": "氷の加護をもたらす指輪"},
    {"id": "dragon_ring",   "category": "ring",     "price": 8000,  "desc": "ドラゴンの力が宿る指輪",          "rare": True},
    # ペットたまご
    {"id": "egg_slime",     "category": "egg",      "price": 1000,  "desc": "愛らしいスライムが生まれる"},
    {"id": "egg_cat",       "category": "egg",      "price": 1500,  "desc": "かわいいネコが生まれる"},
    {"id": "egg_dragon",    "category": "egg",      "price": 3000,  "desc": "強力なドラゴンが生まれる"},
    {"id": "egg_phoenix",   "category": "egg",      "price": 3500,  "desc": "伝説のフェニックスが生まれる"},
    {"id": "egg_unicorn",   "category": "egg",      "price": 4000,  "desc": "神秘のユニコーンが生まれる"},
]

CATEGORY_LABELS: dict[str, str] = {
    "weapon":   "⚔️ 武器",
    "armor":    "🛡️ 防具",
    "hat":      "🎩 帽子",
    "cloak":    "🧥 マント",
    "necklace": "📿 ネックレス",
    "ring":     "💍 指輪",
    "egg":      "🥚 ペットたまご",
}

_CATALOG_BY_ID: dict[str, dict] = {s["id"]: s for s in SHOP_CATALOG}


def _week_seed() -> str:
    y, w, _ = date.today().isocalendar()
    return hashlib.md5(f"{y}-{w}".encode()).hexdigest()


def get_weekly_sale_ids() -> set[str]:
    """今週のセール商品ID（4種、30%オフ）— 無料・レア以外から選出"""
    seed = _week_seed()
    eligible = [s["id"] for s in SHOP_CATALOG if s["price"] > 0 and not s.get("rare")]
    rng = int(seed, 16)
    pool = eligible[:]
    chosen: list[str] = []
    for _ in range(min(4, len(pool))):
        idx = rng % len(pool)
        chosen.append(pool.pop(idx))
        rng >>= 4
    return set(chosen)


def get_weekly_rare_ids() -> set[str]:
    """今週のレア入荷商品ID（3種）"""
    seed = _week_seed() + "rare"
    seed = hashlib.md5(seed.encode()).hexdigest()
    rares = [s["id"] for s in SHOP_CATALOG if s.get("rare")]
    rng = int(seed, 16)
    pool = rares[:]
    chosen: list[str] = []
    for _ in range(min(3, len(pool))):
        idx = rng % len(pool)
        chosen.append(pool.pop(idx))
        rng >>= 4
    return set(chosen)


def get_available_exp(player: dict) -> int:
    return max(0, player.get("total_exp_earned", 0) - player.get("exp_spent", 0))


def is_owned(player: dict, item_id: str) -> bool:
    if item_id.startswith("egg_"):
        pet_type = item_id[4:]
        return (
            player.get("active_pet") == pet_type
            or any(e.get("type") == pet_type for e in player.get("eggs", []))
            or player.get("pets", {}).get(pet_type, False)
        )
    inv = player.get("inventory", [])
    equip = player.get("equipment", {})
    return item_id in inv or item_id in equip.values()


def get_final_price(item_id: str, sale_ids: set[str]) -> int:
    """セール適用後の価格"""
    base = _CATALOG_BY_ID.get(item_id, {}).get("price", 0)
    if item_id in sale_ids:
        return max(0, int(base * 0.7))
    return base


def purchase(player: dict, item_id: str, final_price: int) -> bool:
    """購入処理。成功=True"""
    if get_available_exp(player) < final_price:
        return False
    if is_owned(player, item_id) and not item_id.startswith("egg_"):
        return False
    player["exp_spent"] = player.get("exp_spent", 0) + final_price
    if item_id.startswith("egg_"):
        add_egg(player, item_id[4:])  # egg_dragon → dragon
    else:
        player.setdefault("inventory", []).append(item_id)
    return True


def get_item_display(item_id: str) -> dict:
    """ショップカード表示に必要な情報を返す"""
    catalog = _CATALOG_BY_ID.get(item_id, {})
    equip_meta = _EQUIP_ITEMS.get(item_id, {})
    pet_key = item_id[4:] if item_id.startswith("egg_") else None
    pet_meta = PET_DEFS.get(pet_key, {}) if pet_key else {}
    return {
        "id": item_id,
        "name": equip_meta.get("name") or pet_meta.get("egg_name") or catalog.get("id", item_id),
        "icon": equip_meta.get("icon") or ("🥚" if pet_key else "📦"),
        "desc": catalog.get("desc", ""),
        "price": catalog.get("price", 0),
        "rare": catalog.get("rare", False),
        "category": catalog.get("category", ""),
        "tier": equip_meta.get("tier", 1),
        "egg_svg": pet_meta.get("egg_svg", "") if pet_key else "",
    }
