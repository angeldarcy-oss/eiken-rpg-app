"""core/pets.py — ペットシステム（たまご・孵化・EXPボーナス）"""
from __future__ import annotations
import random

HATCH_THRESHOLD = 100  # 正解100問で孵化


def _svg(inner: str) -> str:
    return '<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">' + inner + '</svg>'


def _egg_svg(shell: str, spot: str) -> str:
    return _svg(
        '<ellipse cx="20" cy="23" rx="13" ry="16" fill="' + shell + '"/>'
        '<ellipse cx="20" cy="17" rx="9" ry="8" fill="' + spot + '" opacity="0.5"/>'
        '<ellipse cx="15" cy="14" rx="4" ry="3" fill="#ffffff" opacity="0.35"/>'
        '<ellipse cx="25" cy="27" rx="3" ry="2" fill="' + spot + '" opacity="0.35"/>'
    )


PET_DEFS: dict[str, dict] = {
    "dragon": {
        "name": "ドラゴン", "egg_name": "ドラゴンのたまご", "emoji": "🐉",
        "color": "#44aa44", "egg_svg": _egg_svg("#cc3322", "#ff6644"),
        "svg": _svg(
            '<polygon points="8,22 1,11 16,24" fill="#338833" opacity="0.85"/>'
            '<polygon points="32,22 39,11 24,24" fill="#338833" opacity="0.85"/>'
            '<ellipse cx="20" cy="28" rx="11" ry="9" fill="#44aa44"/>'
            '<rect x="17" y="17" width="6" height="9" fill="#44aa44" rx="2"/>'
            '<ellipse cx="20" cy="15" rx="9" ry="7" fill="#55bb55"/>'
            '<ellipse cx="16" cy="13" rx="4" ry="3" fill="#88dd88" opacity="0.5"/>'
            '<circle cx="15" cy="13" r="2.2" fill="#ff8800"/>'
            '<circle cx="15.6" cy="13.5" r="1.1" fill="#1a1a00"/>'
            '<circle cx="25" cy="13" r="2.2" fill="#ff8800"/>'
            '<circle cx="25.6" cy="13.5" r="1.1" fill="#1a1a00"/>'
            '<circle cx="17.5" cy="17.5" r="1" fill="#338833"/>'
            '<circle cx="22.5" cy="17.5" r="1" fill="#338833"/>'
            '<path d="M30,31 Q37,36 33,39 Q30,40 28,37" stroke="#44aa44" stroke-width="3" fill="none" stroke-linecap="round"/>'
            '<polygon points="20,8 18,1 22,8" fill="#ccaa00"/>'
        ),
    },
    "phoenix": {
        "name": "フェニックス", "egg_name": "フェニックスのたまご", "emoji": "🔥",
        "color": "#ff6600", "egg_svg": _egg_svg("#ff8800", "#ff2200"),
        "svg": _svg(
            '<path d="M13,36 Q9,29 11,23" stroke="#ff2200" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
            '<path d="M20,39 Q19,31 20,25" stroke="#ff6600" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
            '<path d="M27,36 Q31,29 29,23" stroke="#ffaa00" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
            '<path d="M9,22 Q5,14 13,12 Q10,19 17,19Z" fill="#ff6600"/>'
            '<path d="M31,22 Q35,14 27,12 Q30,19 23,19Z" fill="#ff6600"/>'
            '<path d="M10,20 Q7,16 13,13" stroke="#ffaa00" stroke-width="1.2" fill="none"/>'
            '<path d="M30,20 Q33,16 27,13" stroke="#ffaa00" stroke-width="1.2" fill="none"/>'
            '<ellipse cx="20" cy="24" rx="9" ry="7" fill="#ff8800"/>'
            '<circle cx="20" cy="15" r="7" fill="#ffaa00"/>'
            '<polygon points="16,9 20,2 24,9" fill="#ff2200"/>'
            '<polygon points="20,8 20,2 22,8" fill="#ff7700"/>'
            '<circle cx="17" cy="14" r="2" fill="#fff"/>'
            '<circle cx="23" cy="14" r="2" fill="#fff"/>'
            '<circle cx="17.5" cy="14" r="1" fill="#ff2200"/>'
            '<circle cx="23.5" cy="14" r="1" fill="#ff2200"/>'
            '<polygon points="19,18 21,18 20,21" fill="#ff6600"/>'
        ),
    },
    "unicorn": {
        "name": "ユニコーン", "egg_name": "ユニコーンのたまご", "emoji": "🦄",
        "color": "#ddaaff", "egg_svg": _egg_svg("#eeccff", "#cc88ee"),
        "svg": _svg(
            '<ellipse cx="23" cy="30" rx="13" ry="8" fill="#fff5f8"/>'
            '<polygon points="15,22 22,24 20,32 13,30" fill="#fff5f8"/>'
            '<ellipse cx="13" cy="19" rx="9" ry="8" fill="#fff8fc"/>'
            '<polygon points="9,14 12,8 15,14" fill="#ffbbdd"/>'
            '<polygon points="10,13 12,9 14,13" fill="#ffddee"/>'
            '<polygon points="13,12 11,2 15,12" fill="#cc88ff"/>'
            '<polygon points="12.5,9 13,2 13.5,9" fill="#eeccff"/>'
            '<ellipse cx="10" cy="19" rx="2" ry="2.5" fill="#7766bb"/>'
            '<ellipse cx="10.6" cy="18.4" rx="0.8" ry="1" fill="#fff"/>'
            '<path d="M13,13 Q19,18 21,25" stroke="#ffaadd" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
            '<path d="M15,12 Q22,17 24,25" stroke="#cc88ee" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
            '<rect x="13" y="35" width="3.5" height="5" fill="#ffeeee" rx="1.5"/>'
            '<rect x="20" y="35" width="3.5" height="5" fill="#ffeeee" rx="1.5"/>'
            '<rect x="28" y="35" width="3.5" height="5" fill="#ffeeee" rx="1.5"/>'
            '<path d="M35,27 Q39,32 37,37" stroke="#ffaadd" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
            '<path d="M35,29 Q40,35 38,39" stroke="#cc88ee" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        ),
    },
    "slime": {
        "name": "スライム", "egg_name": "スライムのたまご", "emoji": "💧",
        "color": "#44aaff", "egg_svg": _egg_svg("#66ccff", "#2288dd"),
        "svg": _svg(
            '<ellipse cx="20" cy="26" rx="15" ry="12" fill="#44aaff"/>'
            '<ellipse cx="20" cy="16" rx="11" ry="10" fill="#66ccff"/>'
            '<ellipse cx="14" cy="13" rx="5" ry="4" fill="#aaddff" opacity="0.7"/>'
            '<line x1="20" y1="7" x2="20" y2="4" stroke="#44aaff" stroke-width="2"/>'
            '<circle cx="20" cy="3" r="2.5" fill="#66ccff"/>'
            '<ellipse cx="15.5" cy="20" rx="3" ry="3.5" fill="#fff"/>'
            '<ellipse cx="24.5" cy="20" rx="3" ry="3.5" fill="#fff"/>'
            '<circle cx="16" cy="20.5" r="1.5" fill="#1a4488"/>'
            '<circle cx="25" cy="20.5" r="1.5" fill="#1a4488"/>'
            '<circle cx="16.6" cy="19.9" r="0.6" fill="#fff"/>'
            '<circle cx="25.6" cy="19.9" r="0.6" fill="#fff"/>'
            '<path d="M15 25 Q20 29 25 25" stroke="#2266aa" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
        ),
    },
    "cat": {
        "name": "ネコ", "egg_name": "ネコのたまご", "emoji": "🐱",
        "color": "#ff9966", "egg_svg": _egg_svg("#ffcc99", "#ff9966"),
        "svg": _svg(
            '<ellipse cx="20" cy="30" rx="13" ry="9" fill="#ffcc99"/>'
            '<path d="M32,30 Q38,26 36,20 Q34,15 30,22" stroke="#ffaa77" stroke-width="3" fill="none" stroke-linecap="round"/>'
            '<circle cx="20" cy="18" r="12" fill="#ffcc99"/>'
            '<polygon points="9,13 12,5 17,13" fill="#ffcc99"/>'
            '<polygon points="23,13 28,5 31,13" fill="#ffcc99"/>'
            '<polygon points="10,12 13,7 16,12" fill="#ffaacc"/>'
            '<polygon points="24,12 27,7 30,12" fill="#ffaacc"/>'
            '<ellipse cx="15" cy="18" rx="3" ry="3.5" fill="#66bb44"/>'
            '<ellipse cx="25" cy="18" rx="3" ry="3.5" fill="#66bb44"/>'
            '<ellipse cx="15" cy="18" rx="1.2" ry="2" fill="#222"/>'
            '<ellipse cx="25" cy="18" rx="1.2" ry="2" fill="#222"/>'
            '<circle cx="15.5" cy="17" r="0.7" fill="#fff"/>'
            '<circle cx="25.5" cy="17" r="0.7" fill="#fff"/>'
            '<polygon points="20,23 18,24.5 22,24.5" fill="#ff7799"/>'
            '<path d="M18,24.5 Q20,27 22,24.5" stroke="#dd5588" stroke-width="0.8" fill="none"/>'
            '<line x1="4" y1="22" x2="14" y2="23" stroke="#ddbbaa" stroke-width="0.8"/>'
            '<line x1="4" y1="24.5" x2="14" y2="24.5" stroke="#ddbbaa" stroke-width="0.8"/>'
            '<line x1="26" y1="23" x2="36" y2="22" stroke="#ddbbaa" stroke-width="0.8"/>'
            '<line x1="26" y1="24.5" x2="36" y2="24.5" stroke="#ddbbaa" stroke-width="0.8"/>'
        ),
    },
}

EGG_POOL = list(PET_DEFS.keys())


def get_random_egg() -> str:
    return random.choice(EGG_POOL)


def get_pet_exp_bonus(player: dict) -> float:
    """ペットがいる場合のEXPボーナス率（0.1 = +10%）"""
    return 0.1 if player.get("active_pet") else 0.0


def add_egg(player: dict, egg_type: str) -> None:
    player.setdefault("eggs", []).append({"type": egg_type, "hatch_gauge": 0})


def update_hatch_gauge(player: dict, amount: int = 1) -> list[str]:
    """孵化ゲージを更新し、孵化したペット種類リストを返す"""
    hatched: list[str] = []
    remaining: list[dict] = []
    for egg in player.get("eggs", []):
        egg["hatch_gauge"] = egg.get("hatch_gauge", 0) + amount
        if egg["hatch_gauge"] >= HATCH_THRESHOLD:
            pet_type = egg["type"]
            player.setdefault("pets", {})[pet_type] = True
            player["active_pet"] = pet_type
            hatched.append(pet_type)
        else:
            remaining.append(egg)
    player["eggs"] = remaining
    return hatched


def pet_sidebar_html(player: dict) -> str:
    """サイドバー用ペット表示HTML（ペットまたはたまご）"""
    pet_id = player.get("active_pet")
    if pet_id and pet_id in PET_DEFS:
        pet = PET_DEFS[pet_id]
        return (
            '<div style="text-align:center;padding:6px 0 2px;">'
            '<div style="font-size:.65rem;color:#88ccff;margin-bottom:2px;">🐾 ' + pet["emoji"] + ' ' + pet["name"] + '</div>'
            '<div style="width:40px;height:40px;margin:0 auto;">' + pet["svg"] + '</div>'
            '<div style="font-size:.58rem;color:#66aacc;margin-top:2px;">EXP +10%</div>'
            '</div>'
        )
    eggs = player.get("eggs", [])
    if not eggs:
        return ""
    egg = eggs[0]
    pet_def = PET_DEFS.get(egg["type"], {})
    gauge = egg.get("hatch_gauge", 0)
    pct = min(100, round(gauge / HATCH_THRESHOLD * 100))
    return (
        '<div style="text-align:center;padding:6px 0 2px;">'
        '<div style="font-size:.65rem;color:#aa88cc;margin-bottom:2px;">🥚 ' + pet_def.get("egg_name", "たまご") + '</div>'
        '<div style="width:36px;height:36px;margin:0 auto;">' + pet_def.get("egg_svg", "") + '</div>'
        '<div style="background:#1a1020;border-radius:4px;height:6px;width:60px;margin:4px auto 0;'
        'overflow:hidden;border:1px solid #553366;">'
        '<div style="background:linear-gradient(90deg,#cc44ff,#ff88cc);height:100%;border-radius:4px;width:' + str(pct) + '%;"></div>'
        '</div>'
        '<div style="font-size:.58rem;color:#8855aa;margin-top:2px;">' + str(gauge) + ' / ' + str(HATCH_THRESHOLD) + '</div>'
        '</div>'
    )
