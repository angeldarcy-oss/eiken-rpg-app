"""core/gacha.py — ガチャシステム"""
from __future__ import annotations
import random

# ── レアリティ定義 ─────────────────────────────────────────────────
# (star, weight%, label_ja, color)
RARITY_TABLE: list[tuple[int, int, str, str]] = [
    (1, 60, "★1 コモン",       "#888888"),
    (2, 30, "★2 レア",         "#4499ff"),
    (3,  8, "★3 スーパーレア", "#cc44ff"),
    (4,  2, "★4 ウルトラレア", "#ffaa00"),
]

# ── ガチャ種別 ─────────────────────────────────────────────────────
GACHA_TYPES: dict[str, dict] = {
    "normal": {
        "name": "ノーマルガチャ", "name_zh": "普通扭蛋",
        "cost": 500,
        "icon": "🎯",
        "ball_top": "#cc3322", "ball_bot": "#eeeeee",
        "desc": "武器・防具・帽子・マントがランダム！",
        "desc_zh": "武器・防具・帽子・披風隨機出現！",
        "pool": {
            1: ["wooden_sword", "lute", "leather_armor", "leather_cap", "wool_cloak"],
            2: ["iron_sword", "magic_staff", "holy_staff", "battle_axe", "dark_wand",
                "iron_armor", "mage_robe", "holy_robe", "ranger_hat", "iron_helm",
                "mage_hat", "silk_cloak"],
            3: ["flame_sword", "dragon_scale", "crown", "hero_cloak", "dark_cloak",
                "summer_hat", "halloween_hat", "santa_hat", "spring_cloak"],
            4: ["golden_sword", "rainbow_staff", "phoenix_armor", "dark_crown",
                "rainbow_cloak", "sakura_sword", "maple_staff"],
        },
    },
    "rare": {
        "name": "レアガチャ", "name_zh": "稀有扭蛋",
        "cost": 1500,
        "icon": "💎",
        "ball_top": "#7722cc", "ball_bot": "#ddbbff",
        "desc": "レア装備・アクセサリがランダム！",
        "desc_zh": "稀有裝備・飾品隨機出現！",
        "pool": {
            1: ["fire_ring", "ice_ring", "hero_necklace", "crystal_necklace"],
            2: ["ocean_ring", "moon_pendant", "snow_crystal_necklace",
                "flame_sword", "dragon_scale"],
            3: ["dragon_ring", "rainbow_staff", "phoenix_armor", "dark_crown"],
            4: ["guild_crest_ring", "guild_badge_necklace", "guild_pendant",
                "golden_sword"],
        },
    },
    "premium": {
        "name": "プレミアムガチャ", "name_zh": "高級扭蛋",
        "cost": 3000,
        "icon": "🌟",
        "ball_top": "#cc8800", "ball_bot": "#fff3aa",
        "desc": "超レア装備・ペットたまごがランダム！",
        "desc_zh": "超稀有裝備・寵物蛋隨機出現！",
        "pool": {
            1: ["egg_slime", "egg_cat"],
            2: ["egg_unicorn", "egg_phoenix", "rainbow_cloak", "sakura_sword"],
            3: ["egg_dragon", "maple_staff", "golden_sword"],
            4: ["rainbow_staff", "guild_crest_ring", "guild_badge_necklace",
                "guild_pendant"],
        },
    },
}


def _roll_rarity() -> int:
    stars = [r[0] for r in RARITY_TABLE]
    weights = [r[1] for r in RARITY_TABLE]
    return random.choices(stars, weights=weights, k=1)[0]


def roll_gacha(gacha_type: str) -> tuple[str, int]:
    """ガチャを1回引いて (item_id, rarity) を返す。"""
    pool = GACHA_TYPES[gacha_type]["pool"]
    rarity = _roll_rarity()
    # 対象レアリティにアイテムがない場合は近いレアリティへ
    for star in sorted(pool, key=lambda s: abs(s - rarity)):
        if pool[star]:
            return random.choice(pool[star]), rarity
    return "wooden_sword", 1


def gacha_pull(player: dict, gacha_type: str) -> dict | None:
    """ガチャを引き、アイテムを付与する。
    成功したら {"item_id", "rarity", "duplicate"} を返す。
    EXP不足なら None。
    """
    from core.pets import add_egg
    gacha = GACHA_TYPES[gacha_type]
    cost = gacha["cost"]
    available = player.get("total_exp_earned", 0) - player.get("exp_spent", 0)
    if available < cost:
        return None

    item_id, rarity = roll_gacha(gacha_type)
    player["exp_spent"] = player.get("exp_spent", 0) + cost

    duplicate = False
    if item_id.startswith("egg_"):
        add_egg(player, item_id[4:])
    else:
        inv = player.setdefault("inventory", [])
        equip_vals = list((player.get("equipment") or {}).values())
        if item_id in inv or item_id in equip_vals:
            duplicate = True
        else:
            inv.append(item_id)

    return {"item_id": item_id, "rarity": rarity, "duplicate": duplicate}


def rarity_label(rarity: int) -> str:
    for star, _, label, _ in RARITY_TABLE:
        if star == rarity:
            return label
    return "★1"


def rarity_color(rarity: int) -> str:
    for star, _, _, color in RARITY_TABLE:
        if star == rarity:
            return color
    return "#888888"


def gacha_animation_html(item_icon: str, item_name: str, rarity: int,
                          ball_top: str, ball_bot: str) -> str:
    """ガチャ演出HTML（components.html用）を返す。"""
    r_color = rarity_color(rarity)
    r_label = rarity_label(rarity)
    is_flash = rarity >= 3
    flash_style = f"background:radial-gradient(circle,{r_color}88 0%,transparent 70%);" if is_flash else ""
    glow_style = f"filter:drop-shadow(0 0 12px {r_color});" if rarity >= 3 else ""
    sound_js = _sound_js(rarity)

    return f"""
<style>
@keyframes spin {{
  from {{ transform: rotate(0deg); }}
  to   {{ transform: rotate(360deg); }}
}}
@keyframes pop {{
  0%   {{ transform: scale(0.2); opacity: 0; }}
  60%  {{ transform: scale(1.15); opacity: 1; }}
  80%  {{ transform: scale(0.95); }}
  100% {{ transform: scale(1); }}
}}
@keyframes star-flash {{
  0%,100% {{ opacity: 1; transform: scale(1); }}
  50%     {{ opacity: 0.7; transform: scale(1.05); }}
}}
body {{ margin:0; background:transparent; font-family:'Noto Sans JP',sans-serif; }}
</style>
<div id="wrap" style="
  background:linear-gradient(135deg,#1a1a2e,#2a2a4a);
  border-radius:16px; padding:24px 16px; text-align:center;
  position:relative; overflow:hidden; min-height:220px;
">
  <!-- フラッシュ背景 -->
  <div id="flash-bg" style="
    position:absolute; inset:0; border-radius:16px;
    {flash_style}
    opacity:0; transition:opacity .25s; pointer-events:none;
  "></div>

  <!-- Phase1: ボール回転 -->
  <div id="phase1">
    <div style="font-size:.75rem;color:#888;margin-bottom:14px;letter-spacing:.08em;">
      ガチャ回転中…
    </div>
    <div id="ball" style="width:80px;height:80px;margin:0 auto;
      animation:spin .45s linear infinite;">
      <svg viewBox="0 0 100 100" width="80" height="80">
        <defs>
          <radialGradient id="bg" cx="40%" cy="35%" r="60%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <ellipse cx="50" cy="94" rx="28" ry="5" fill="#000" opacity=".3"/>
        <circle cx="50" cy="48" r="44" fill="{ball_bot}"/>
        <path d="M6,48 A44,44 0 0,1 94,48 Z" fill="{ball_top}"/>
        <circle cx="50" cy="48" r="44" fill="url(#bg)"/>
        <rect x="5" y="44" width="90" height="8" fill="#fff" rx="4" opacity=".75"/>
        <circle cx="50" cy="48" r="44" fill="none" stroke="#555" stroke-width="1.5"/>
      </svg>
    </div>
  </div>

  <!-- Phase2: 結果 -->
  <div id="phase2" style="display:none; animation:pop .5s ease-out;">
    <div style="font-size:3.2rem; {glow_style} margin-bottom:8px;">{item_icon}</div>
    <div style="font-size:1.15rem;font-weight:700;color:#ffe066;margin-bottom:8px;">
      {item_name}
    </div>
    <div style="
      display:inline-block;
      background:linear-gradient(135deg,#1a1a1a,#2a2a2a);
      border:2px solid {r_color};
      border-radius:20px; padding:4px 18px;
      font-size:.95rem; font-weight:700;
      color:{r_color};
      animation:star-flash 1.2s ease-in-out infinite;
    ">{r_label}</div>
  </div>
</div>

<script>
{sound_js}
var phase1 = document.getElementById('phase1');
var phase2 = document.getElementById('phase2');
var flashBg = document.getElementById('flash-bg');

// 1400ms後: フラッシュ演出（★3以上）
setTimeout(function() {{
  {'flashBg.style.opacity = "0.55";' if is_flash else ''}
  playSound({rarity});
  setTimeout(function() {{
    {'flashBg.style.opacity = "0";' if is_flash else ''}
  }}, 350);
}}, 1400);

// 1700ms後: 結果表示
setTimeout(function() {{
  phase1.style.display = 'none';
  phase2.style.display = 'block';
}}, 1700);
</script>
"""


def _sound_js(rarity: int) -> str:
    """レアリティに応じた効果音JS（Web Audio API）を返す。"""
    if rarity == 4:
        # ウルトラレア: ファンファーレ
        notes = "[523,659,784,1047,1319]"
        gap = 120
        dur = 0.22
        vol = 0.35
    elif rarity == 3:
        # スーパーレア: 3音上昇
        notes = "[523,784,1047]"
        gap = 140
        dur = 0.28
        vol = 0.30
    elif rarity == 2:
        # レア: 2音
        notes = "[440,660]"
        gap = 150
        dur = 0.22
        vol = 0.22
    else:
        # コモン: 短いビープ
        notes = "[440]"
        gap = 0
        dur = 0.18
        vol = 0.18
    return f"""
function playSound(r) {{
  try {{
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    var ctx = new AC();
    var freqs = {notes};
    freqs.forEach(function(freq, i) {{
      setTimeout(function() {{
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = r >= 3 ? 'triangle' : 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime({vol}, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + {dur});
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + {dur});
      }}, i * {gap});
    }});
  }} catch(e) {{}}
}}
"""
