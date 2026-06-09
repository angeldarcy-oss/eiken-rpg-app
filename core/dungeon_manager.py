"""core/dungeon_manager.py — ダンジョン管理"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

DUNGEON_RANKINGS_FILE = Path("data/saves/dungeon_rankings.json")

# ─── マップSVG（180×110 viewBox） ────────────────────────────────
_MAP_SVG: dict[str, str] = {
    "cave": (
        '<svg viewBox="0 0 180 110" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="180" height="110" fill="#120a04"/>'
        '<ellipse cx="20" cy="0" rx="28" ry="22" fill="#1e1008"/>'
        '<ellipse cx="75" cy="0" rx="35" ry="28" fill="#180c04"/>'
        '<ellipse cx="140" cy="0" rx="32" ry="25" fill="#1e1008"/>'
        '<polygon points="22,0 30,38 14,38" fill="#2a1a0a"/>'
        '<polygon points="60,0 67,30 53,30" fill="#2a1a0a"/>'
        '<polygon points="108,0 115,42 101,42" fill="#221408"/>'
        '<polygon points="155,0 162,32 148,32" fill="#2a1a0a"/>'
        '<rect x="0" y="86" width="180" height="24" fill="#1a0e06"/>'
        '<path d="M5,98 Q60,82 120,94 Q150,100 175,90" stroke="#3a2010" stroke-width="14" fill="none" stroke-linecap="round"/>'
        '<rect x="36" y="52" width="5" height="16" fill="#6b3210"/>'
        '<ellipse cx="38" cy="51" rx="6" ry="8" fill="#ff8800" opacity="0.85"/>'
        '<ellipse cx="38" cy="49" rx="3" ry="5" fill="#ffdd00"/>'
        '<rect x="126" y="50" width="5" height="16" fill="#6b3210"/>'
        '<ellipse cx="128" cy="49" rx="6" ry="8" fill="#ff8800" opacity="0.85"/>'
        '<ellipse cx="128" cy="47" rx="3" ry="5" fill="#ffdd00"/>'
        '<rect x="153" y="72" width="18" height="13" rx="2" fill="#7a3a0a"/>'
        '<rect x="152" y="69" width="20" height="7" rx="2" fill="#9a5020"/>'
        '<rect x="159" y="74" width="6" height="8" rx="1" fill="#FFD700"/>'
        '<circle cx="48" cy="76" r="2" fill="#88aaff" opacity="0.7"/>'
        '<circle cx="88" cy="70" r="1.5" fill="#ff88aa" opacity="0.6"/>'
        '<text x="163" y="67" font-size="7" fill="#ff4444" font-weight="bold" text-anchor="middle">BOSS</text>'
        '</svg>'
    ),
    "prairie": (
        '<svg viewBox="0 0 180 110" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="180" height="72" fill="#87CEEB"/>'
        '<circle cx="155" cy="18" r="13" fill="#FFD700"/>'
        '<ellipse cx="38" cy="22" rx="26" ry="12" fill="white" opacity="0.9"/>'
        '<ellipse cx="54" cy="20" rx="20" ry="10" fill="white" opacity="0.9"/>'
        '<ellipse cx="125" cy="28" rx="22" ry="10" fill="white" opacity="0.85"/>'
        '<ellipse cx="0" cy="92" rx="62" ry="42" fill="#4CAF50"/>'
        '<ellipse cx="90" cy="97" rx="82" ry="38" fill="#66BB6A"/>'
        '<ellipse cx="180" cy="94" rx="62" ry="42" fill="#388E3C"/>'
        '<rect x="0" y="82" width="180" height="28" fill="#4CAF50"/>'
        '<path d="M5,106 Q60,88 120,100 Q152,106 175,96" stroke="#c8a000" stroke-width="10" fill="none" stroke-linecap="round"/>'
        '<rect x="16" y="58" width="5" height="22" fill="#7a5a20"/>'
        '<circle cx="18" cy="53" r="13" fill="#2E7D32"/>'
        '<rect x="157" y="55" width="5" height="25" fill="#7a5a20"/>'
        '<circle cx="159" cy="50" r="15" fill="#1B5E20"/>'
        '<circle cx="28" cy="84" r="4" fill="#FF6B6B"/>'
        '<circle cx="52" cy="80" r="3" fill="#FFD700"/>'
        '<circle cx="72" cy="86" r="4" fill="#FF6B6B"/>'
        '<circle cx="108" cy="82" r="3" fill="#ffffff"/>'
        '<circle cx="142" cy="85" r="4" fill="#FF6B6B"/>'
        '<rect x="148" y="70" width="26" height="14" rx="3" fill="#cc0000" opacity="0.85"/>'
        '<text x="161" y="80" font-size="7" fill="white" font-weight="bold" text-anchor="middle">BOSS</text>'
        '</svg>'
    ),
    "forest": (
        '<svg viewBox="0 0 180 110" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="180" height="110" fill="#060d06"/>'
        '<circle cx="148" cy="20" r="14" fill="#f5f5dc" opacity="0.88"/>'
        '<circle cx="153" cy="16" r="11" fill="#060d06"/>'
        '<circle cx="18" cy="10" r="1.2" fill="white" opacity="0.8"/>'
        '<circle cx="50" cy="16" r="1.5" fill="white" opacity="0.7"/>'
        '<circle cx="90" cy="8" r="1" fill="white"/>'
        '<circle cx="118" cy="18" r="1.2" fill="white" opacity="0.8"/>'
        '<rect x="6" y="8" width="10" height="68" fill="#0d1f08"/>'
        '<polygon points="0,42 11,6 22,42" fill="#174a08"/>'
        '<polygon points="0,58 11,22 22,58" fill="#1a5a0a"/>'
        '<rect x="28" y="14" width="8" height="62" fill="#0a1804"/>'
        '<polygon points="22,44 32,8 42,44" fill="#174a08"/>'
        '<rect x="142" y="6" width="10" height="70" fill="#0d1f08"/>'
        '<polygon points="135,40 147,4 159,40" fill="#174a08"/>'
        '<rect x="164" y="16" width="8" height="60" fill="#0a1804"/>'
        '<polygon points="160,42 168,10 176,42" fill="#1a5a0a"/>'
        '<rect x="0" y="75" width="180" height="35" fill="#0a1a06"/>'
        '<path d="M48,110 Q90,86 132,108" stroke="#2a1800" stroke-width="16" fill="none"/>'
        '<path d="M48,110 Q90,86 132,108" stroke="#3a2400" stroke-width="10" fill="none" opacity="0.6"/>'
        '<ellipse cx="58" cy="90" rx="9" ry="5" fill="#7a33cc" opacity="0.8"/>'
        '<rect x="55" y="90" width="6" height="10" fill="#5a22aa"/>'
        '<circle cx="58" cy="89" r="4" fill="#cc88ff" opacity="0.6"/>'
        '<ellipse cx="115" cy="87" rx="8" ry="4" fill="#3333cc" opacity="0.7"/>'
        '<rect x="112" y="87" width="5" height="9" fill="#2222aa"/>'
        '<circle cx="70" cy="77" r="2" fill="#aaffaa" opacity="0.8"/>'
        '<circle cx="95" cy="70" r="1.5" fill="#aaffff" opacity="0.7"/>'
        '<circle cx="112" cy="80" r="2" fill="#ffaaff" opacity="0.8"/>'
        '<text x="90" y="108" font-size="8" fill="#cc44ff" font-weight="bold" text-anchor="middle">⚠ BOSS</text>'
        '</svg>'
    ),
    "ice_castle": (
        '<svg viewBox="0 0 180 110" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="180" height="110" fill="#c0d8ee"/>'
        '<rect x="0" y="78" width="180" height="32" fill="#e4f2ff"/>'
        '<path d="M0,78 Q45,68 90,76 Q135,84 180,72" fill="#cce8ff"/>'
        '<rect x="62" y="28" width="56" height="55" rx="2" fill="#aad4f0" opacity="0.88"/>'
        '<polygon points="57,30 90,8 123,30" fill="#88c4e8"/>'
        '<polygon points="65,30 90,12 115,30" fill="#a8d8f5"/>'
        '<rect x="56" y="44" width="15" height="38" fill="#90c8ec"/>'
        '<polygon points="51,46 63,28 75,46" fill="#70b8e0"/>'
        '<rect x="109" y="44" width="15" height="38" fill="#90c8ec"/>'
        '<polygon points="104,46 116,28 128,46" fill="#70b8e0"/>'
        '<path d="M82,83 L82,60 Q90,53 98,60 L98,83" fill="#1a3a5a"/>'
        '<rect x="68" y="48" width="9" height="11" rx="4" fill="#88eeff" opacity="0.9"/>'
        '<rect x="103" y="48" width="9" height="11" rx="4" fill="#88eeff" opacity="0.9"/>'
        '<rect x="84" y="36" width="12" height="15" rx="6" fill="#aaffff" opacity="0.8"/>'
        '<path d="M10,106 Q60,88 110,102 Q140,109 170,98" stroke="#b0d8f0" stroke-width="12" fill="none"/>'
        '<polygon points="24,80 27,70 30,80" fill="#88ccff" opacity="0.8"/>'
        '<polygon points="140,78 143,68 146,78" fill="#88ccff" opacity="0.8"/>'
        '<polygon points="155,82 157,74 159,82" fill="#aaddff" opacity="0.7"/>'
        '<text x="90" y="22" font-size="8" fill="#0044aa" font-weight="bold" text-anchor="middle">👑 BOSS</text>'
        '</svg>'
    ),
    "dragon_lair": (
        '<svg viewBox="0 0 180 110" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="180" height="110" fill="#180800"/>'
        '<ellipse cx="90" cy="110" rx="110" ry="65" fill="#ff4400" opacity="0.18"/>'
        '<ellipse cx="18" cy="76" rx="32" ry="42" fill="#1f0e00"/>'
        '<ellipse cx="82" cy="82" rx="52" ry="46" fill="#160900"/>'
        '<ellipse cx="162" cy="72" rx="36" ry="44" fill="#1f0e00"/>'
        '<rect x="0" y="84" width="180" height="26" fill="#0f0500"/>'
        '<path d="M28,96 Q58,86 84,94 Q104,100 132,90" stroke="#ff4400" stroke-width="4" fill="none" opacity="0.8"/>'
        '<ellipse cx="60" cy="93" rx="9" ry="3" fill="#ff6600" opacity="0.6"/>'
        '<ellipse cx="120" cy="91" rx="7" ry="2.5" fill="#ff4400" opacity="0.5"/>'
        '<path d="M8,102 Q38,92 70,98" stroke="#ff3300" stroke-width="3" fill="none" opacity="0.7"/>'
        '<ellipse cx="130" cy="50" rx="30" ry="18" fill="#1a0a00" opacity="0.85"/>'
        '<path d="M104,50 Q80,22 76,46" fill="#0f0500" opacity="0.9"/>'
        '<path d="M156,50 Q176,24 178,46" fill="#0f0500" opacity="0.9"/>'
        '<ellipse cx="130" cy="40" rx="14" ry="11" fill="#200a00"/>'
        '<ellipse cx="144" cy="44" rx="11" ry="7" fill="#200a00"/>'
        '<circle cx="140" cy="39" r="3" fill="#ff2200" opacity="0.9"/>'
        '<circle cx="148" cy="42" r="2" fill="#ff4400" opacity="0.8"/>'
        '<path d="M153,43 Q168,36 178,41 Q166,46 178,53 Q168,51 153,46" fill="#ff4400" opacity="0.7"/>'
        '<path d="M8,108 Q58,90 110,103 Q142,108 172,97" stroke="#2a1200" stroke-width="10" fill="none"/>'
        '<ellipse cx="48" cy="89" rx="8" ry="6" fill="#2a1400"/>'
        '<ellipse cx="64" cy="91" rx="6" ry="5" fill="#1a0a00"/>'
        '<circle cx="86" cy="66" r="8" fill="#2a1200" opacity="0.4"/>'
        '<circle cx="82" cy="56" r="6" fill="#1a0800" opacity="0.3"/>'
        '<text x="130" y="30" font-size="9" fill="#ff4400" font-weight="bold" text-anchor="middle">👑 BOSS</text>'
        '</svg>'
    ),
}

# ─── ボスSVG（80×80 viewBox） ──────────────────────────────────────
_BOSS_SVG: dict[str, str] = {
    "goblin_king": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="58" y="13" width="4" height="52" rx="2" fill="#7a3a10"/>'
        '<circle cx="60" cy="10" r="7" fill="#ff6600"/><circle cx="60" cy="10" r="4" fill="#ffcc00"/>'
        '<ellipse cx="36" cy="54" rx="15" ry="17" fill="#2d8a2d"/>'
        '<ellipse cx="20" cy="52" rx="7" ry="5" fill="#2d8a2d" transform="rotate(-15 20 52)"/>'
        '<ellipse cx="54" cy="50" rx="8" ry="5" fill="#2d8a2d" transform="rotate(20 54 50)"/>'
        '<circle cx="36" cy="28" r="13" fill="#3aaa3a"/>'
        '<path d="M23,23 L26,11 L31,19 L36,8 L41,19 L46,11 L49,23 Z" fill="#FFD700"/>'
        '<circle cx="36" cy="11" r="3" fill="#ff4444"/>'
        '<circle cx="26" cy="18" r="2" fill="#4466ff"/>'
        '<circle cx="46" cy="18" r="2" fill="#44ff44"/>'
        '<circle cx="31" cy="27" r="3.5" fill="#ff2200"/><circle cx="32" cy="27" r="1.5" fill="black"/>'
        '<circle cx="41" cy="27" r="3.5" fill="#ff2200"/><circle cx="42" cy="27" r="1.5" fill="black"/>'
        '<ellipse cx="36" cy="33" rx="3" ry="2" fill="#228822"/>'
        '<path d="M30,37 Q36,42 42,37" stroke="#001100" stroke-width="2" fill="none"/>'
        '<ellipse cx="30" cy="68" rx="7" ry="6" fill="#2d8a2d"/>'
        '<ellipse cx="42" cy="68" rx="7" ry="6" fill="#2d8a2d"/>'
        '</svg>'
    ),
    "wolf_lord": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<ellipse cx="38" cy="50" rx="18" ry="20" fill="#7a7a88"/>'
        '<ellipse cx="16" cy="56" rx="7" ry="5" fill="#6a6a78" transform="rotate(-30 16 56)"/>'
        '<ellipse cx="60" cy="54" rx="7" ry="5" fill="#6a6a78" transform="rotate(30 60 54)"/>'
        '<ellipse cx="38" cy="28" rx="16" ry="14" fill="#8a8a98"/>'
        '<polygon points="26,20 30,7 34,20" fill="#7a7a88"/>'
        '<polygon points="42,20 46,7 50,20" fill="#7a7a88"/>'
        '<ellipse cx="38" cy="26" rx="10" ry="8" fill="#aaaaaa"/>'
        '<circle cx="32" cy="27" r="4" fill="#ffaa00"/><circle cx="33" cy="27" r="2" fill="black"/>'
        '<circle cx="44" cy="27" r="4" fill="#ffaa00"/><circle cx="45" cy="27" r="2" fill="black"/>'
        '<ellipse cx="38" cy="34" rx="5" ry="3" fill="#aaaaaa"/>'
        '<path d="M33,40 Q38,44 43,40" stroke="#333" stroke-width="2" fill="none"/>'
        '<rect x="35" y="38" width="6" height="4" fill="white" opacity="0.9"/>'
        '<ellipse cx="30" cy="68" rx="8" ry="7" fill="#6a6a78"/>'
        '<ellipse cx="46" cy="68" rx="8" ry="7" fill="#6a6a78"/>'
        '<ellipse cx="38" cy="15" rx="4" ry="6" fill="#aaaaaa" opacity="0.7"/>'
        '</svg>'
    ),
    "arch_mage": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="58" y="10" width="4" height="55" rx="2" fill="#4a228a"/>'
        '<circle cx="60" cy="8" r="8" fill="#aa44ff" opacity="0.9"/>'
        '<circle cx="60" cy="8" r="5" fill="#cc88ff"/><circle cx="60" cy="8" r="2" fill="white"/>'
        '<ellipse cx="36" cy="54" rx="14" ry="22" fill="#5a1a8a"/>'
        '<circle cx="36" cy="26" r="13" fill="#6622aa"/>'
        '<path d="M23,22 L36,12 L49,22 L43,28 L36,26 L29,28 Z" fill="#330066"/>'
        '<circle cx="30" cy="27" r="3.5" fill="#ccaaff"/><circle cx="31" cy="27" r="1.5" fill="black"/>'
        '<circle cx="42" cy="27" r="3.5" fill="#ccaaff"/><circle cx="43" cy="27" r="1.5" fill="black"/>'
        '<ellipse cx="36" cy="33" rx="3" ry="2" fill="#8855cc"/>'
        '<path d="M30,37 Q36,34 42,37" stroke="#220044" stroke-width="2" fill="none"/>'
        '<ellipse cx="28" cy="70" rx="7" ry="8" fill="#4a1a7a"/>'
        '<ellipse cx="44" cy="70" rx="7" ry="8" fill="#4a1a7a"/>'
        '<circle cx="25" cy="48" r="4" fill="#aa44ff" opacity="0.6"/>'
        '<circle cx="47" cy="46" r="3" fill="#aa44ff" opacity="0.6"/>'
        '</svg>'
    ),
    "ice_queen": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<ellipse cx="36" cy="56" rx="14" ry="20" fill="#88ccff"/>'
        '<ellipse cx="36" cy="70" rx="19" ry="10" fill="#aaddff"/>'
        '<circle cx="36" cy="24" r="13" fill="#ddeeff"/>'
        '<path d="M23,20 L27,9 L32,17 L36,7 L40,17 L45,9 L49,20 Z" fill="#88ccff"/>'
        '<polygon points="34,7 36,1 38,7" fill="#aaddff"/>'
        '<polygon points="29,9 27,3 31,7" fill="#88eeff"/>'
        '<polygon points="43,9 45,3 41,7" fill="#88eeff"/>'
        '<circle cx="30" cy="24" r="4" fill="#4488cc"/><circle cx="31" cy="24" r="2" fill="black"/>'
        '<circle cx="42" cy="24" r="4" fill="#4488cc"/><circle cx="43" cy="24" r="2" fill="black"/>'
        '<ellipse cx="36" cy="30" rx="3" ry="2" fill="#aaccee"/>'
        '<path d="M30,36 Q36,39 42,36" stroke="#3366aa" stroke-width="1.5" fill="none"/>'
        '<rect x="15" y="46" width="8" height="24" rx="2" fill="#88ccff" transform="rotate(-18 15 46)"/>'
        '<rect x="53" y="46" width="8" height="24" rx="2" fill="#88ccff" transform="rotate(18 53 46)"/>'
        '<circle cx="16" cy="43" r="5" fill="#aaeeff" opacity="0.8"/>'
        '<circle cx="56" cy="43" r="4" fill="#aaeeff" opacity="0.8"/>'
        '</svg>'
    ),
    "ancient_dragon": (
        '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M12,55 Q8,28 22,24 Q16,50 12,55 Z" fill="#cc2200" opacity="0.75"/>'
        '<path d="M64,55 Q68,28 54,24 Q60,50 64,55 Z" fill="#cc2200" opacity="0.75"/>'
        '<ellipse cx="38" cy="52" rx="20" ry="22" fill="#cc2200"/>'
        '<ellipse cx="38" cy="30" rx="16" ry="14" fill="#dd3300"/>'
        '<polygon points="27,22 31,9 35,20" fill="#cc2200"/>'
        '<polygon points="41,22 45,9 49,22" fill="#cc2200"/>'
        '<polygon points="38,14 35,7 41,7 38,14" fill="#ff6600"/>'
        '<circle cx="32" cy="30" r="4" fill="#ffaa00"/><circle cx="33" cy="30" r="2" fill="#ff2200"/>'
        '<circle cx="44" cy="30" r="4" fill="#ffaa00"/><circle cx="45" cy="30" r="2" fill="#ff2200"/>'
        '<path d="M30,40 Q38,36 46,40" stroke="#881100" stroke-width="2" fill="none"/>'
        '<polygon points="30,40 34,44 38,40 42,44 46,40" fill="white" opacity="0.9"/>'
        '<ellipse cx="27" cy="68" rx="10" ry="8" fill="#bb2200"/>'
        '<ellipse cx="49" cy="68" rx="10" ry="8" fill="#bb2200"/>'
        '<ellipse cx="17" cy="60" rx="6" ry="3" fill="#cc2200" transform="rotate(-20 17 60)"/>'
        '<ellipse cx="59" cy="60" rx="6" ry="3" fill="#cc2200" transform="rotate(20 59 60)"/>'
        '<path d="M38,72 Q48,76 56,74" stroke="#881100" stroke-width="3" fill="none"/>'
        '</svg>'
    ),
}

# ─── ダンジョン定義 ────────────────────────────────────────────────
DUNGEONS: list[dict] = [
    {
        "id": "cave",
        "name": "初心者の洞窟",
        "emoji": "🏚️",
        "grade": "grade_5",
        "difficulty": 1,
        "diff_label": "★☆☆☆☆",
        "theme_color": "#8B4513",
        "required_correct": 10,
        "monster_pool": ["slime", "bat", "goblin"],
        "boss_def": {
            "id": "goblin_king", "name": "ゴブリンキング", "emoji": "👑",
            "hp": 60, "attack": 12, "svg": _BOSS_SVG["goblin_king"],
        },
        "clear_rewards": ["iron_helm"],
        "first_clear_extra": ["flame_sword"],
        "first_clear_title": "dungeon_rookie",
        "map_svg": _MAP_SVG["cave"],
        "bg_color": "#120a04",
    },
    {
        "id": "prairie",
        "name": "草原の迷宮",
        "emoji": "🌿",
        "grade": "grade_4",
        "difficulty": 2,
        "diff_label": "★★☆☆☆",
        "theme_color": "#2E7D32",
        "required_correct": 10,
        "monster_pool": ["goblin", "ghost", "wolf"],
        "boss_def": {
            "id": "wolf_lord", "name": "ウルフロード", "emoji": "🐺",
            "hp": 80, "attack": 16, "svg": _BOSS_SVG["wolf_lord"],
        },
        "clear_rewards": ["iron_armor"],
        "first_clear_extra": ["hero_cloak"],
        "first_clear_title": "dungeon_explorer",
        "map_svg": _MAP_SVG["prairie"],
        "bg_color": "#0a1f0a",
    },
    {
        "id": "forest",
        "name": "魔法の森",
        "emoji": "🌲",
        "grade": "grade_3",
        "difficulty": 3,
        "diff_label": "★★★☆☆",
        "theme_color": "#7B1FA2",
        "required_correct": 10,
        "monster_pool": ["zombie", "orc", "skeleton"],
        "boss_def": {
            "id": "arch_mage", "name": "大魔法使い", "emoji": "🧙",
            "hp": 100, "attack": 20, "svg": _BOSS_SVG["arch_mage"],
        },
        "clear_rewards": ["mage_hat"],
        "first_clear_extra": ["mage_robe"],
        "first_clear_title": "dungeon_mage",
        "map_svg": _MAP_SVG["forest"],
        "bg_color": "#060d06",
    },
    {
        "id": "ice_castle",
        "name": "氷の城",
        "emoji": "❄️",
        "grade": "grade_pre2",
        "difficulty": 4,
        "diff_label": "★★★★☆",
        "theme_color": "#1565C0",
        "required_correct": 10,
        "monster_pool": ["minotaur", "orc", "skeleton"],
        "boss_def": {
            "id": "ice_queen", "name": "氷の女王", "emoji": "👸",
            "hp": 120, "attack": 24, "svg": _BOSS_SVG["ice_queen"],
        },
        "clear_rewards": ["ice_ring"],
        "first_clear_extra": ["moon_pendant"],
        "first_clear_title": "dungeon_knight",
        "map_svg": _MAP_SVG["ice_castle"],
        "bg_color": "#0a1a2a",
    },
    {
        "id": "dragon_lair",
        "name": "竜の巣窟",
        "emoji": "🐲",
        "grade": "grade_2",
        "difficulty": 5,
        "diff_label": "★★★★★",
        "theme_color": "#B71C1C",
        "required_correct": 10,
        "monster_pool": ["dragon", "minotaur", "skeleton"],
        "boss_def": {
            "id": "ancient_dragon", "name": "古代龍", "emoji": "🐉",
            "hp": 150, "attack": 30, "svg": _BOSS_SVG["ancient_dragon"],
        },
        "clear_rewards": ["dragon_scale"],
        "first_clear_extra": ["dragon_ring"],
        "first_clear_title": "dungeon_conqueror",
        "map_svg": _MAP_SVG["dragon_lair"],
        "bg_color": "#180800",
    },
]

_DUNGEON_MAP: dict[str, dict] = {d["id"]: d for d in DUNGEONS}


def get_dungeon(dungeon_id: str) -> dict | None:
    return _DUNGEON_MAP.get(dungeon_id)


def get_all_dungeons() -> list[dict]:
    return DUNGEONS


def get_player_dungeon_progress(player: dict, dungeon_id: str) -> dict:
    return player.get("dungeons", {}).get(dungeon_id, {
        "clears": 0, "best_time": None, "best_accuracy": None
    })


def record_clear(player: dict, dungeon_id: str, time_sec: float, accuracy: float) -> dict:
    """ダンジョンクリアを記録してplayer["dungeons"]を更新。付与報酬dictを返す。"""
    dungeons = player.setdefault("dungeons", {})
    prog = dungeons.setdefault(dungeon_id, {"clears": 0, "best_time": None, "best_accuracy": None})
    is_first_clear = prog["clears"] == 0
    prog["clears"] += 1
    if prog["best_time"] is None or time_sec < prog["best_time"]:
        prog["best_time"] = round(time_sec, 1)
    if prog["best_accuracy"] is None or accuracy > prog["best_accuracy"]:
        prog["best_accuracy"] = round(accuracy, 1)

    dungeon = get_dungeon(dungeon_id)
    if dungeon is None:
        return {"items": [], "first_clear": False}

    inv = player.setdefault("inventory", [])
    items_given = []
    for item_id in dungeon["clear_rewards"]:
        if item_id not in inv:
            inv.append(item_id)
            items_given.append(item_id)
    if is_first_clear:
        for item_id in dungeon["first_clear_extra"]:
            if item_id not in inv:
                inv.append(item_id)
                items_given.append(item_id)

    return {"items": items_given, "first_clear": is_first_clear}


# ─── ランキング管理 ────────────────────────────────────────────────
def _load_rankings() -> dict:
    if not DUNGEON_RANKINGS_FILE.exists():
        return {}
    try:
        with open(DUNGEON_RANKINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_rankings(data: dict) -> None:
    DUNGEON_RANKINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DUNGEON_RANKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_dungeon_ranking(username: str, player_name: str, dungeon_id: str,
                           time_sec: float, accuracy: float, character: str = "") -> None:
    data = _load_rankings()
    entries = data.setdefault(dungeon_id, [])
    # 同ユーザーの既存エントリを更新（ベストタイム更新のみ記録）
    existing = next((e for e in entries if e.get("username") == username), None)
    if existing is None or time_sec < existing.get("time", float("inf")):
        if existing:
            entries.remove(existing)
        entries.append({
            "username": username,
            "name": player_name,
            "character": character,
            "time": round(time_sec, 1),
            "accuracy": round(accuracy, 1),
            "date": datetime.now().strftime("%Y-%m-%d"),
        })
    entries.sort(key=lambda x: x.get("time", 9999))
    data[dungeon_id] = entries[:50]
    _save_rankings(data)


def get_dungeon_ranking(dungeon_id: str) -> list[dict]:
    data = _load_rankings()
    return data.get(dungeon_id, [])
