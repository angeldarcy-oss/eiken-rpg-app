"""core/monsters.py — RPGモンスターデータ定義（通常10種 + 週替わりボス5種）"""
from __future__ import annotations
import random
from datetime import date

# ─────────────────────────────────────────
# SVG イラスト
# ─────────────────────────────────────────

_SVG: dict[str, str] = {}

# ── スライム ──────────────────────────────
_SVG["slime"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="71" rx="24" ry="5" fill="#002266" opacity=".25"/>'
    '<ellipse cx="28" cy="57" rx="15" ry="11" fill="#2255dd"/>'
    '<ellipse cx="52" cy="57" rx="15" ry="11" fill="#2255dd"/>'
    '<ellipse cx="40" cy="49" rx="22" ry="20" fill="#3377ff"/>'
    '<ellipse cx="33" cy="38" rx="8" ry="5" fill="#88bbff" opacity=".55"/>'
    '<circle cx="33" cy="49" r="6.5" fill="white"/>'
    '<circle cx="47" cy="49" r="6.5" fill="white"/>'
    '<circle cx="34" cy="50" r="3.5" fill="#0011aa"/>'
    '<circle cx="48" cy="50" r="3.5" fill="#0011aa"/>'
    '<circle cx="32.5" cy="48" r="1.5" fill="white"/>'
    '<circle cx="46.5" cy="48" r="1.5" fill="white"/>'
    '<path d="M35 57 Q40 62 45 57" stroke="#0011aa" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
    '</svg>'
)

# ── コウモリ ──────────────────────────────
_SVG["bat"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M40 42 L5 22 L12 46 L26 50 Z" fill="#3a1855"/>'
    '<path d="M40 42 L75 22 L68 46 L54 50 Z" fill="#3a1855"/>'
    '<path d="M40 42 L16 30 L14 42" stroke="#52257a" stroke-width="1.2" fill="none" opacity=".5"/>'
    '<path d="M40 42 L64 30 L66 42" stroke="#52257a" stroke-width="1.2" fill="none" opacity=".5"/>'
    '<ellipse cx="40" cy="46" rx="13" ry="15" fill="#271240"/>'
    '<ellipse cx="40" cy="41" rx="9" ry="7" fill="#3a1855"/>'
    '<polygon points="30,26 24,9 36,21" fill="#3a1855"/>'
    '<polygon points="50,26 56,9 44,21" fill="#3a1855"/>'
    '<polygon points="30,26 27,15 35,22" fill="#ee88aa" opacity=".55"/>'
    '<polygon points="50,26 53,15 45,22" fill="#ee88aa" opacity=".55"/>'
    '<circle cx="33" cy="42" r="5.5" fill="#220011"/>'
    '<circle cx="47" cy="42" r="5.5" fill="#220011"/>'
    '<circle cx="33" cy="42" r="3.5" fill="#ee1100"/>'
    '<circle cx="47" cy="42" r="3.5" fill="#ee1100"/>'
    '<circle cx="34" cy="41" r="1.3" fill="#ff8844" opacity=".8"/>'
    '<circle cx="48" cy="41" r="1.3" fill="#ff8844" opacity=".8"/>'
    '<path d="M37 55 L36 62" stroke="white" stroke-width="2.5" stroke-linecap="round"/>'
    '<path d="M43 55 L44 62" stroke="white" stroke-width="2.5" stroke-linecap="round"/>'
    '</svg>'
)

# ── ゴブリン ──────────────────────────────
_SVG["goblin"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="77" rx="18" ry="4" fill="#000" opacity=".18"/>'
    '<rect x="30" y="50" width="20" height="22" rx="4" fill="#226622"/>'
    '<rect x="31" y="68" width="7" height="10" rx="3" fill="#1a5522"/>'
    '<rect x="42" y="68" width="7" height="10" rx="3" fill="#1a5522"/>'
    '<rect x="19" y="51" width="13" height="6" rx="3" fill="#226622"/>'
    '<rect x="48" y="51" width="13" height="6" rx="3" fill="#226622"/>'
    '<rect x="59" y="44" width="5" height="16" rx="2" fill="#553311"/>'
    '<ellipse cx="61" cy="43" rx="5" ry="4" fill="#774422"/>'
    '<circle cx="40" cy="38" r="16" fill="#33aa33"/>'
    '<ellipse cx="23" cy="37" rx="5" ry="8" fill="#33aa33"/>'
    '<ellipse cx="57" cy="37" rx="5" ry="8" fill="#33aa33"/>'
    '<ellipse cx="23" cy="37" rx="2.5" ry="5" fill="#ff7777" opacity=".55"/>'
    '<ellipse cx="57" cy="37" rx="2.5" ry="5" fill="#ff7777" opacity=".55"/>'
    '<ellipse cx="34" cy="37" rx="5" ry="5.5" fill="white"/>'
    '<ellipse cx="46" cy="37" rx="5" ry="5.5" fill="white"/>'
    '<circle cx="35" cy="38" r="3.5" fill="#cc0000"/>'
    '<circle cx="47" cy="38" r="3.5" fill="#cc0000"/>'
    '<circle cx="34" cy="37" r="1.5" fill="#330000"/>'
    '<circle cx="46" cy="37" r="1.5" fill="#330000"/>'
    '<ellipse cx="40" cy="42" rx="3" ry="2" fill="#228822"/>'
    '<circle cx="39" cy="42.5" r="1" fill="#006600"/>'
    '<circle cx="41" cy="42.5" r="1" fill="#006600"/>'
    '<path d="M34 46 Q40 51 46 46" stroke="#004400" stroke-width="1.5" fill="none"/>'
    '<rect x="37" y="46" width="2.5" height="3.5" rx="1" fill="white"/>'
    '<rect x="40.5" y="46" width="2.5" height="3.5" rx="1" fill="white"/>'
    '</svg>'
)

# ── ゾンビ ──────────────────────────────
_SVG["zombie"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="77" rx="18" ry="4" fill="#000" opacity=".18"/>'
    '<rect x="28" y="47" width="24" height="27" rx="4" fill="#3a6644"/>'
    '<path d="M28 58 L23 67 L28 65" fill="#2a5533"/>'
    '<path d="M52 61 L57 70 L52 68" fill="#2a5533"/>'
    '<rect x="29" y="68" width="10" height="12" rx="3" fill="#2a5533"/>'
    '<rect x="41" y="68" width="10" height="12" rx="3" fill="#2a5533"/>'
    '<rect x="4" y="47" width="26" height="8" rx="4" fill="#3a6644"/>'
    '<rect x="50" y="47" width="26" height="8" rx="4" fill="#3a6644"/>'
    '<path d="M10 48 L12 54" stroke="#2a4433" stroke-width="1.5"/>'
    '<path d="M61 48 L63 54" stroke="#2a4433" stroke-width="1.5"/>'
    '<circle cx="40" cy="33" r="18" fill="#44884a"/>'
    '<path d="M30 25 L36 32" stroke="#aa4444" stroke-width="2.5"/>'
    '<ellipse cx="33" cy="33" rx="5.5" ry="5" fill="#ccddaa"/>'
    '<ellipse cx="47" cy="33" rx="5.5" ry="5" fill="#ccddaa"/>'
    '<circle cx="33" cy="33" r="3" fill="#889955"/>'
    '<circle cx="47" cy="33" r="3" fill="#889955"/>'
    '<circle cx="33" cy="33" r="1.5" fill="#222211"/>'
    '<circle cx="47" cy="33" r="1.5" fill="#222211"/>'
    '<ellipse cx="40" cy="38" rx="2.5" ry="1.5" fill="#336644"/>'
    '<path d="M33 42 Q40 48 47 42" stroke="#2a4433" stroke-width="2" fill="#1a3322"/>'
    '<rect x="36" y="42" width="3" height="4" rx="1" fill="#bbbbaa" opacity=".8"/>'
    '<rect x="41" y="42" width="3" height="4" rx="1" fill="#bbbbaa" opacity=".8"/>'
    '</svg>'
)

# ── ウルフ ──────────────────────────────
_SVG["wolf"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="77" rx="24" ry="4" fill="#000" opacity=".2"/>'
    '<path d="M58 53 Q72 46 68 36 Q64 26 72 22" stroke="#778899" stroke-width="7" fill="none" stroke-linecap="round"/>'
    '<ellipse cx="42" cy="57" rx="21" ry="15" fill="#889aaa"/>'
    '<ellipse cx="40" cy="60" rx="13" ry="9" fill="#cccde0"/>'
    '<rect x="22" y="65" width="10" height="14" rx="5" fill="#778899"/>'
    '<rect x="48" y="65" width="10" height="14" rx="5" fill="#778899"/>'
    '<rect x="26" y="64" width="9" height="14" rx="4" fill="#889aaa"/>'
    '<rect x="45" y="64" width="9" height="14" rx="4" fill="#889aaa"/>'
    '<rect x="30" y="44" width="20" height="14" rx="8" fill="#889aaa"/>'
    '<ellipse cx="40" cy="34" rx="18" ry="16" fill="#889aaa"/>'
    '<ellipse cx="40" cy="44" rx="10" ry="7" fill="#aaaabc"/>'
    '<polygon points="24,20 20,5 32,18" fill="#889aaa"/>'
    '<polygon points="56,20 60,5 48,18" fill="#889aaa"/>'
    '<polygon points="25,19 22,10 31,18" fill="#cc9999" opacity=".6"/>'
    '<polygon points="55,19 58,10 49,18" fill="#cc9999" opacity=".6"/>'
    '<ellipse cx="33" cy="32" rx="5" ry="5.5" fill="white"/>'
    '<ellipse cx="47" cy="32" rx="5" ry="5.5" fill="white"/>'
    '<circle cx="33.5" cy="33" r="3.5" fill="#ccaa00"/>'
    '<circle cx="47.5" cy="33" r="3.5" fill="#ccaa00"/>'
    '<circle cx="33.5" cy="33" r="1.8" fill="#110000"/>'
    '<circle cx="47.5" cy="33" r="1.8" fill="#110000"/>'
    '<circle cx="32.5" cy="32" r="1" fill="white"/>'
    '<ellipse cx="40" cy="43" rx="4" ry="3" fill="#332233"/>'
    '<path d="M34 47 L40 51 L46 47" stroke="#778" stroke-width="1.5" fill="none"/>'
    '<path d="M37 48 L36 55" stroke="white" stroke-width="2.5" stroke-linecap="round"/>'
    '<path d="M43 48 L44 55" stroke="white" stroke-width="2.5" stroke-linecap="round"/>'
    '</svg>'
)

# ── ゴースト ──────────────────────────────
_SVG["ghost"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="44" rx="26" ry="29" fill="#9999ff" opacity=".12"/>'
    '<path d="M18 42 Q18 14 40 11 Q62 14 62 42 L62 70 Q56 63 51 70 Q46 63 40 70 Q34 63 29 70 Q24 63 18 70 Z" fill="#dde8ff" opacity=".9"/>'
    '<path d="M22 32 Q30 22 40 20" stroke="white" stroke-width="2" fill="none" opacity=".45"/>'
    '<ellipse cx="33" cy="40" rx="6" ry="7" fill="#222244"/>'
    '<ellipse cx="47" cy="40" rx="6" ry="7" fill="#222244"/>'
    '<ellipse cx="33" cy="41" rx="3" ry="3.5" fill="#6655ff" opacity=".85"/>'
    '<ellipse cx="47" cy="41" rx="3" ry="3.5" fill="#6655ff" opacity=".85"/>'
    '<circle cx="32" cy="39" r="1.2" fill="#aaaaff" opacity=".9"/>'
    '<circle cx="46" cy="39" r="1.2" fill="#aaaaff" opacity=".9"/>'
    '<path d="M35 51 Q40 56 45 51" stroke="#334466" stroke-width="2" fill="none"/>'
    '<circle cx="18" cy="30" r="2" fill="#aaaaff" opacity=".6"/>'
    '<circle cx="62" cy="26" r="1.5" fill="#aaaaff" opacity=".5"/>'
    '</svg>'
)

# ── オーク ──────────────────────────────
_SVG["orc"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="77" rx="22" ry="4" fill="#000" opacity=".2"/>'
    '<rect x="24" y="48" width="32" height="26" rx="5" fill="#556622"/>'
    '<rect x="27" y="48" width="26" height="18" rx="3" fill="#778833"/>'
    '<line x1="40" y1="48" x2="40" y2="66" stroke="#556622" stroke-width="2"/>'
    '<line x1="27" y1="57" x2="53" y2="57" stroke="#556622" stroke-width="2"/>'
    '<rect x="26" y="68" width="11" height="12" rx="4" fill="#445522"/>'
    '<rect x="43" y="68" width="11" height="12" rx="4" fill="#445522"/>'
    '<rect x="10" y="50" width="16" height="8" rx="4" fill="#556622"/>'
    '<rect x="54" y="50" width="16" height="8" rx="4" fill="#556622"/>'
    '<rect x="65" y="36" width="5" height="30" rx="2" fill="#774422"/>'
    '<polygon points="63,30 74,36 74,52 63,52" fill="#aaaaaa"/>'
    '<polygon points="63,30 53,36 63,52" fill="#cccccc"/>'
    '<circle cx="40" cy="34" r="20" fill="#668833"/>'
    '<ellipse cx="40" cy="20" rx="19" ry="8" fill="#888"/>'
    '<rect x="22" y="20" width="36" height="10" rx="2" fill="#999"/>'
    '<rect x="36" y="28" width="8" height="12" rx="2" fill="#888"/>'
    '<ellipse cx="34" cy="34" rx="5" ry="5" fill="white"/>'
    '<ellipse cx="46" cy="34" rx="5" ry="5" fill="white"/>'
    '<circle cx="35" cy="35" r="3" fill="#aa2200"/>'
    '<circle cx="47" cy="35" r="3" fill="#aa2200"/>'
    '<circle cx="34.5" cy="34" r="1.2" fill="#330000"/>'
    '<circle cx="46.5" cy="34" r="1.2" fill="#330000"/>'
    '<path d="M34 42 L31 49" stroke="white" stroke-width="3" stroke-linecap="round"/>'
    '<path d="M46 42 L49 49" stroke="white" stroke-width="3" stroke-linecap="round"/>'
    '</svg>'
)

# ── スケルトン ──────────────────────────────
_SVG["skeleton"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="77" rx="18" ry="3.5" fill="#000" opacity=".18"/>'
    '<rect x="29" y="62" width="8" height="16" rx="4" fill="#e5e5dd"/>'
    '<rect x="43" y="62" width="8" height="16" rx="4" fill="#e5e5dd"/>'
    '<ellipse cx="40" cy="62" rx="14" ry="6" fill="#d9d9d1"/>'
    '<rect x="30" y="41" width="20" height="22" rx="4" fill="#d9d9d1"/>'
    '<path d="M33 46 Q40 49 47 46" stroke="#bbb" stroke-width="1.5" fill="none"/>'
    '<path d="M33 51 Q40 54 47 51" stroke="#bbb" stroke-width="1.5" fill="none"/>'
    '<path d="M33 56 Q40 59 47 56" stroke="#bbb" stroke-width="1.5" fill="none"/>'
    '<line x1="40" y1="41" x2="40" y2="63" stroke="#ccc" stroke-width="2"/>'
    '<rect x="14" y="43" width="17" height="7" rx="3.5" fill="#d9d9d1"/>'
    '<rect x="49" y="43" width="17" height="7" rx="3.5" fill="#d9d9d1"/>'
    '<rect x="7" y="30" width="4" height="32" rx="2" fill="#aaaaaa"/>'
    '<rect x="3" y="42" width="13" height="3" rx="1" fill="#888"/>'
    '<rect x="8" y="28" width="2" height="5" rx="1" fill="#ddbb00"/>'
    '<rect x="37" y="36" width="6" height="7" rx="3" fill="#e0e0d8"/>'
    '<circle cx="40" cy="23" r="16" fill="#eeeee6"/>'
    '<path d="M36 14 L38 21" stroke="#ccc" stroke-width="1.5" fill="none"/>'
    '<ellipse cx="33" cy="24" rx="5.5" ry="6" fill="#1a1a2a"/>'
    '<ellipse cx="47" cy="24" rx="5.5" ry="6" fill="#1a1a2a"/>'
    '<circle cx="33" cy="25" r="2.5" fill="#4444ff" opacity=".7"/>'
    '<circle cx="47" cy="25" r="2.5" fill="#4444ff" opacity=".7"/>'
    '<path d="M38 31 L40 34 L42 31" stroke="#aaa" stroke-width="1.5" fill="none"/>'
    '<rect x="33" y="33" width="3" height="5" rx="1.5" fill="#ddd"/>'
    '<rect x="37" y="33" width="3" height="5" rx="1.5" fill="#ddd"/>'
    '<rect x="41" y="33" width="3" height="5" rx="1.5" fill="#ddd"/>'
    '</svg>'
)

# ── ミノタウロス ──────────────────────────────
_SVG["minotaur"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="77" rx="22" ry="4" fill="#000" opacity=".2"/>'
    '<rect x="24" y="46" width="32" height="28" rx="5" fill="#774422"/>'
    '<rect x="28" y="46" width="24" height="18" rx="3" fill="#886633"/>'
    '<rect x="25" y="67" width="12" height="12" rx="5" fill="#663311"/>'
    '<rect x="43" y="67" width="12" height="12" rx="5" fill="#663311"/>'
    '<rect x="8" y="47" width="18" height="10" rx="5" fill="#774422"/>'
    '<rect x="54" y="47" width="18" height="10" rx="5" fill="#774422"/>'
    '<rect x="65" y="28" width="5" height="34" rx="2" fill="#884422"/>'
    '<polygon points="64,24 76,29 76,46 64,42" fill="#bbbbbb"/>'
    '<polygon points="64,24 54,30 64,42" fill="#dddddd"/>'
    '<rect x="32" y="40" width="16" height="10" rx="5" fill="#774422"/>'
    '<ellipse cx="40" cy="29" rx="18" ry="16" fill="#885533"/>'
    '<path d="M23 21 Q12 11 18 4" stroke="#ccaa55" stroke-width="6" fill="none" stroke-linecap="round"/>'
    '<path d="M57 21 Q68 11 62 4" stroke="#ccaa55" stroke-width="6" fill="none" stroke-linecap="round"/>'
    '<ellipse cx="22" cy="29" rx="5" ry="8" fill="#885533"/>'
    '<ellipse cx="58" cy="29" rx="5" ry="8" fill="#885533"/>'
    '<ellipse cx="40" cy="38" rx="11" ry="8" fill="#996644"/>'
    '<circle cx="36" cy="38" r="2.5" fill="#663322"/>'
    '<circle cx="44" cy="38" r="2.5" fill="#663322"/>'
    '<ellipse cx="32" cy="27" rx="5" ry="5" fill="white"/>'
    '<ellipse cx="48" cy="27" rx="5" ry="5" fill="white"/>'
    '<circle cx="33" cy="28" r="3.5" fill="#cc3300"/>'
    '<circle cx="49" cy="28" r="3.5" fill="#cc3300"/>'
    '<circle cx="32.5" cy="27" r="1.5" fill="#110000"/>'
    '<circle cx="48.5" cy="27" r="1.5" fill="#110000"/>'
    '</svg>'
)

# ── ドラゴン（通常）──────────────────────────────
_SVG["dragon"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="77" rx="22" ry="4" fill="#000" opacity=".2"/>'
    '<path d="M57 58 Q70 64 72 54 Q74 43 63 41" stroke="#cc2200" stroke-width="7" fill="none" stroke-linecap="round"/>'
    '<path d="M30 40 Q14 20 7 28 Q4 36 20 43 Z" fill="#dd3300" opacity=".88"/>'
    '<path d="M50 40 Q66 20 73 28 Q76 36 60 43 Z" fill="#dd3300" opacity=".88"/>'
    '<path d="M30 40 Q13 24 9 30" stroke="#ee4411" stroke-width="1.2" fill="none" opacity=".5"/>'
    '<path d="M50 40 Q67 24 71 30" stroke="#ee4411" stroke-width="1.2" fill="none" opacity=".5"/>'
    '<ellipse cx="40" cy="57" rx="18" ry="16" fill="#cc2200"/>'
    '<ellipse cx="40" cy="60" rx="11" ry="10" fill="#ee8800" opacity=".7"/>'
    '<circle cx="36" cy="57" r="3" fill="#bb2200" opacity=".5"/>'
    '<circle cx="44" cy="57" r="3" fill="#bb2200" opacity=".5"/>'
    '<circle cx="40" cy="53" r="3" fill="#bb2200" opacity=".5"/>'
    '<path d="M28 67 L22 78" stroke="#cc2200" stroke-width="7" stroke-linecap="round"/>'
    '<path d="M52 67 L58 78" stroke="#cc2200" stroke-width="7" stroke-linecap="round"/>'
    '<rect x="32" y="40" width="16" height="16" rx="7" fill="#cc2200"/>'
    '<ellipse cx="40" cy="31" rx="16" ry="14" fill="#dd2200"/>'
    '<path d="M28 23 Q24 13 28 7" stroke="#ffaa00" stroke-width="4" fill="none" stroke-linecap="round"/>'
    '<path d="M52 23 Q56 13 52 7" stroke="#ffaa00" stroke-width="4" fill="none" stroke-linecap="round"/>'
    '<ellipse cx="40" cy="38" rx="9" ry="6" fill="#ee3300"/>'
    '<path d="M44 38 Q52 35 56 29 Q59 23 54 21" stroke="#ffcc00" stroke-width="3" fill="none" opacity=".85"/>'
    '<path d="M44 39 Q53 37 59 33" stroke="#ff8800" stroke-width="2" fill="none" opacity=".7"/>'
    '<circle cx="36.5" cy="38" r="2" fill="#aa1100"/>'
    '<circle cx="43.5" cy="38" r="2" fill="#aa1100"/>'
    '<ellipse cx="33" cy="28" rx="5" ry="5.5" fill="#ffcc00"/>'
    '<ellipse cx="47" cy="28" rx="5" ry="5.5" fill="#ffcc00"/>'
    '<ellipse cx="33" cy="29" rx="2" ry="3.5" fill="#110000"/>'
    '<ellipse cx="47" cy="29" rx="2" ry="3.5" fill="#110000"/>'
    '<circle cx="32" cy="27.5" r="1.2" fill="#ffeeaa" opacity=".8"/>'
    '<circle cx="46" cy="27.5" r="1.2" fill="#ffeeaa" opacity=".8"/>'
    '</svg>'
)

# ───────────────────────────── BOSS SVGs ─────────────────────────────

# ── 暗黒竜（ボス）──────────────────────────────
_SVG["dark_dragon"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="44" rx="36" ry="33" fill="#220033" opacity=".4"/>'
    '<path d="M57 58 Q74 66 76 53 Q78 40 63 36" stroke="#110022" stroke-width="9" fill="none" stroke-linecap="round"/>'
    '<path d="M28 42 Q7 18 1 26 Q-1 37 18 44 Z" fill="#110022" opacity=".95"/>'
    '<path d="M52 42 Q73 18 79 26 Q81 37 62 44 Z" fill="#110022" opacity=".95"/>'
    '<path d="M28 42 Q10 22 5 28" stroke="#3322aa" stroke-width="1.8" fill="none" opacity=".6"/>'
    '<path d="M28 42 Q15 30 9 36" stroke="#3322aa" stroke-width="1.2" fill="none" opacity=".4"/>'
    '<path d="M52 42 Q70 22 75 28" stroke="#3322aa" stroke-width="1.8" fill="none" opacity=".6"/>'
    '<path d="M52 42 Q65 30 71 36" stroke="#3322aa" stroke-width="1.2" fill="none" opacity=".4"/>'
    '<ellipse cx="40" cy="57" rx="20" ry="18" fill="#110022"/>'
    '<ellipse cx="40" cy="62" rx="12" ry="10" fill="#330044" opacity=".8"/>'
    '<circle cx="35" cy="57" r="4" fill="#220033" opacity=".7"/>'
    '<circle cx="45" cy="57" r="4" fill="#220033" opacity=".7"/>'
    '<circle cx="40" cy="52" r="4" fill="#220033" opacity=".7"/>'
    '<path d="M26 67 L17 79" stroke="#110022" stroke-width="8" stroke-linecap="round"/>'
    '<path d="M54 67 L63 79" stroke="#110022" stroke-width="8" stroke-linecap="round"/>'
    '<rect x="30" y="38" width="20" height="20" rx="9" fill="#110022"/>'
    '<ellipse cx="40" cy="27" rx="18" ry="16" fill="#1a0033"/>'
    '<path d="M25 19 Q17 7 22 1" stroke="#8800ff" stroke-width="5.5" fill="none" stroke-linecap="round"/>'
    '<path d="M55 19 Q63 7 58 1" stroke="#8800ff" stroke-width="5.5" fill="none" stroke-linecap="round"/>'
    '<path d="M32 17 Q28 9 30 4" stroke="#6600cc" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
    '<path d="M48 17 Q52 9 50 4" stroke="#6600cc" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
    '<ellipse cx="40" cy="35" rx="10" ry="7" fill="#220044"/>'
    '<path d="M44 36 Q54 30 58 21 Q62 14 55 11" stroke="#8800ff" stroke-width="3.5" fill="none" opacity=".9"/>'
    '<path d="M44 37 Q56 33 62 27" stroke="#cc44ff" stroke-width="2" fill="none" opacity=".65"/>'
    '<ellipse cx="32" cy="24" rx="6" ry="6.5" fill="#330066"/>'
    '<ellipse cx="48" cy="24" rx="6" ry="6.5" fill="#330066"/>'
    '<ellipse cx="32" cy="25" rx="3.5" ry="4.5" fill="#9900ff"/>'
    '<ellipse cx="48" cy="25" rx="3.5" ry="4.5" fill="#9900ff"/>'
    '<circle cx="32" cy="24" r="2" fill="#ffaaff" opacity=".75"/>'
    '<circle cx="48" cy="24" r="2" fill="#ffaaff" opacity=".75"/>'
    '<path d="M33 39 L31 46" stroke="#8800ff" stroke-width="2.5" stroke-linecap="round" opacity=".8"/>'
    '<path d="M47 39 L49 46" stroke="#8800ff" stroke-width="2.5" stroke-linecap="round" opacity=".8"/>'
    '</svg>'
)

# ── 魔王（ボス）──────────────────────────────
_SVG["demon_lord"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="44" rx="32" ry="34" fill="#330011" opacity=".5"/>'
    '<path d="M20 79 L18 50 Q20 44 40 43 Q60 44 62 50 L60 79 Z" fill="#220022"/>'
    '<path d="M26 79 L25 56 L40 54 L55 56 L54 79" fill="#110011" opacity=".5"/>'
    '<path d="M18 50 Q8 58 4 72 L18 73 Z" fill="#330033"/>'
    '<path d="M62 50 Q72 58 76 72 L62 73 Z" fill="#330033"/>'
    '<rect x="54" y="46" width="14" height="8" rx="4" fill="#220022"/>'
    '<rect x="66" y="22" width="4" height="38" rx="2" fill="#331133"/>'
    '<rect x="62" y="33" width="12" height="4" rx="2" fill="#440044"/>'
    '<path d="M68 22 L66 8 L70 8 Z" fill="#cc00cc"/>'
    '<ellipse cx="68" cy="24" rx="3" ry="3" fill="#9900aa"/>'
    '<rect x="12" y="46" width="14" height="8" rx="4" fill="#220022"/>'
    '<rect x="28" y="39" width="24" height="16" rx="6" fill="#2a0022"/>'
    '<path d="M40 42 L36 50 L40 48 L44 50 Z" fill="#ff0033" opacity=".8"/>'
    '<rect x="34" y="33" width="12" height="10" rx="5" fill="#2a0022"/>'
    '<ellipse cx="40" cy="23" rx="18" ry="18" fill="#1a0022"/>'
    '<path d="M22 15 Q14 3 20 -1" stroke="#ff2200" stroke-width="5.5" fill="none" stroke-linecap="round"/>'
    '<path d="M58 15 Q66 3 60 -1" stroke="#ff2200" stroke-width="5.5" fill="none" stroke-linecap="round"/>'
    '<path d="M30 13 Q26 5 28 1" stroke="#cc1100" stroke-width="3" fill="none" stroke-linecap="round"/>'
    '<path d="M50 13 Q54 5 52 1" stroke="#cc1100" stroke-width="3" fill="none" stroke-linecap="round"/>'
    '<rect x="22" y="14" width="36" height="7" rx="3" fill="#440022"/>'
    '<circle cx="32" cy="16" r="2" fill="#ff0033"/>'
    '<circle cx="40" cy="15" r="2.5" fill="#ff4444"/>'
    '<circle cx="48" cy="16" r="2" fill="#ff0033"/>'
    '<ellipse cx="32" cy="23" rx="6" ry="6" fill="#220011"/>'
    '<ellipse cx="48" cy="23" rx="6" ry="6" fill="#220011"/>'
    '<ellipse cx="32" cy="23" rx="4" ry="4" fill="#ff0000"/>'
    '<ellipse cx="48" cy="23" rx="4" ry="4" fill="#ff0000"/>'
    '<circle cx="32" cy="22" r="2" fill="#ffaa00" opacity=".8"/>'
    '<circle cx="48" cy="22" r="2" fill="#ffaa00" opacity=".8"/>'
    '<path d="M37 28 L40 31 L43 28" stroke="#550033" stroke-width="1.5" fill="none"/>'
    '<path d="M30 35 Q40 42 50 35" stroke="#440022" stroke-width="2.5" fill="#1a0011"/>'
    '<rect x="34" y="35" width="3" height="5" rx="1.5" fill="#880033"/>'
    '<rect x="38" y="35" width="4" height="5.5" rx="2" fill="#880033"/>'
    '<rect x="43" y="35" width="3" height="5" rx="1.5" fill="#880033"/>'
    '</svg>'
)

# ── リッチ（ボス）──────────────────────────────
_SVG["lich"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="44" rx="30" ry="34" fill="#001122" opacity=".4"/>'
    '<path d="M16 79 L20 46 Q24 41 40 39 Q56 41 60 46 L64 79 Z" fill="#0a1a2a"/>'
    '<path d="M24 79 L26 54 L40 52 L54 54 L56 79" fill="#060e18" opacity=".5"/>'
    '<rect x="12" y="41" width="16" height="7" rx="3.5" fill="#0a1a2a"/>'
    '<rect x="4" y="10" width="4" height="42" rx="2" fill="#442200"/>'
    '<circle cx="6" cy="9" r="7" fill="#001133"/>'
    '<circle cx="6" cy="9" r="5" fill="#0033aa"/>'
    '<circle cx="6" cy="9" r="3" fill="#4466ff"/>'
    '<circle cx="4.5" cy="7.5" r="1.5" fill="#aabbff"/>'
    '<path d="M6 2 L6 -1" stroke="#4466ff" stroke-width="1.5" opacity=".6"/>'
    '<path d="M1 9 L-1 9" stroke="#4466ff" stroke-width="1.5" opacity=".5"/>'
    '<path d="M2 4 L0 2" stroke="#4466ff" stroke-width="1.5" opacity=".5"/>'
    '<rect x="52" y="41" width="16" height="7" rx="3.5" fill="#0a1a2a"/>'
    '<rect x="10" y="45" width="5" height="7" rx="2" fill="#ddddcc"/>'
    '<rect x="12" y="50" width="2.5" height="6" rx="1" fill="#ccccbb"/>'
    '<rect x="65" y="45" width="5" height="7" rx="2" fill="#ddddcc"/>'
    '<rect x="26" y="37" width="28" height="16" rx="7" fill="#0a1a2a"/>'
    '<path d="M26 37 Q40 33 54 37" stroke="#224466" stroke-width="3" fill="none"/>'
    '<path d="M32 41 Q40 44 48 41" stroke="#224466" stroke-width="1.5" fill="none" opacity=".4"/>'
    '<path d="M32 46 Q40 49 48 46" stroke="#224466" stroke-width="1.5" fill="none" opacity=".4"/>'
    '<circle cx="40" cy="25" r="18" fill="#ddddd5"/>'
    '<ellipse cx="40" cy="19" rx="17" ry="14" fill="#0a1a2a" opacity=".72"/>'
    '<ellipse cx="40" cy="29" rx="12" ry="10" fill="#ddddd5"/>'
    '<ellipse cx="34" cy="28" rx="5.5" ry="6" fill="#0a1a2a"/>'
    '<ellipse cx="46" cy="28" rx="5.5" ry="6" fill="#0a1a2a"/>'
    '<circle cx="34" cy="29" r="3.5" fill="#0044ff"/>'
    '<circle cx="46" cy="29" r="3.5" fill="#0044ff"/>'
    '<circle cx="34" cy="29" r="2" fill="#4488ff"/>'
    '<circle cx="46" cy="29" r="2" fill="#4488ff"/>'
    '<circle cx="33" cy="28" r="1" fill="#aabbff"/>'
    '<circle cx="45" cy="28" r="1" fill="#aabbff"/>'
    '<path d="M38 34 L40 37 L42 34" stroke="#aaa" stroke-width="1.5" fill="none"/>'
    '<rect x="33.5" y="36" width="3" height="5" rx="1.5" fill="#ccccc0"/>'
    '<rect x="37.5" y="36" width="3" height="5" rx="1.5" fill="#ccccc0"/>'
    '<rect x="41.5" y="36" width="3" height="5" rx="1.5" fill="#ccccc0"/>'
    '<circle cx="60" cy="18" r="2" fill="#4466ff" opacity=".7"/>'
    '<circle cx="15" cy="29" r="1.5" fill="#4466ff" opacity=".6"/>'
    '</svg>'
)

# ── ゴーレム（ボス）──────────────────────────────
_SVG["golem"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="77" rx="28" ry="5" fill="#000" opacity=".28"/>'
    '<rect x="20" y="59" width="16" height="21" rx="3" fill="#556644"/>'
    '<rect x="44" y="59" width="16" height="21" rx="3" fill="#556644"/>'
    '<path d="M24 63 L26 73" stroke="#445533" stroke-width="1.5"/>'
    '<path d="M50 65 L52 75" stroke="#445533" stroke-width="1.5"/>'
    '<rect x="16" y="35" width="48" height="28" rx="5" fill="#667755"/>'
    '<path d="M30 39 L36 50 L30 56" stroke="#556644" stroke-width="2"/>'
    '<path d="M50 39 L44 48 L52 55" stroke="#556644" stroke-width="2"/>'
    '<path d="M38 41 L42 50" stroke="#556644" stroke-width="1.5"/>'
    '<ellipse cx="22" cy="47" rx="4" ry="3" fill="#448833" opacity=".7"/>'
    '<ellipse cx="58" cy="43" rx="3" ry="2.5" fill="#448833" opacity=".6"/>'
    '<rect x="2" y="37" width="16" height="20" rx="5" fill="#667755"/>'
    '<rect x="62" y="37" width="16" height="20" rx="5" fill="#667755"/>'
    '<path d="M5 43 L11 51" stroke="#556644" stroke-width="2"/>'
    '<path d="M66 41 L72 49" stroke="#556644" stroke-width="2"/>'
    '<circle cx="14" cy="37" r="8" fill="#778866"/>'
    '<circle cx="66" cy="37" r="8" fill="#778866"/>'
    '<rect x="30" y="27" width="20" height="12" rx="5" fill="#667755"/>'
    '<rect x="18" y="8" width="44" height="23" rx="4" fill="#778866"/>'
    '<path d="M36 11 L38 19 L34 23" stroke="#556644" stroke-width="2"/>'
    '<path d="M46 13 L44 21" stroke="#556644" stroke-width="1.5"/>'
    '<ellipse cx="28" cy="13" rx="5" ry="3" fill="#448833" opacity=".7"/>'
    '<ellipse cx="56" cy="11" rx="4" ry="2.5" fill="#448833" opacity=".6"/>'
    '<rect x="24" y="14" width="12" height="11" rx="3" fill="#221100"/>'
    '<rect x="44" y="14" width="12" height="11" rx="3" fill="#221100"/>'
    '<rect x="26" y="16" width="8" height="7" rx="2" fill="#ff6600"/>'
    '<rect x="46" y="16" width="8" height="7" rx="2" fill="#ff6600"/>'
    '<rect x="27" y="17" width="5" height="5" rx="1" fill="#ffaa00"/>'
    '<rect x="47" y="17" width="5" height="5" rx="1" fill="#ffaa00"/>'
    '<rect x="24" y="26" width="32" height="6" rx="2" fill="#221100"/>'
    '<rect x="26" y="26" width="4" height="5" rx="1" fill="#ccccaa"/>'
    '<rect x="32" y="26" width="4" height="5" rx="1" fill="#ccccaa"/>'
    '<rect x="38" y="26" width="4" height="5" rx="1" fill="#ccccaa"/>'
    '<rect x="44" y="26" width="4" height="5" rx="1" fill="#ccccaa"/>'
    '<rect x="50" y="26" width="4" height="5" rx="1" fill="#ccccaa"/>'
    '<text x="40" y="52" font-size="13" text-anchor="middle" fill="#88ffaa" opacity=".75" font-family="serif">Ω</text>'
    '</svg>'
)

# ── フェニックス（ボス）──────────────────────────────
_SVG["phoenix"] = (
    '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="44" rx="34" ry="32" fill="#ff6600" opacity=".14"/>'
    '<path d="M40 65 Q30 73 25 79 Q32 73 36 79 Q40 71 44 79 Q48 73 55 79 Q50 73 40 65 Z" fill="#ff4400" opacity=".8"/>'
    '<path d="M40 65 Q38 75 36 79" stroke="#ff8800" stroke-width="2" fill="none"/>'
    '<path d="M40 65 Q42 75 44 79" stroke="#ff8800" stroke-width="2" fill="none"/>'
    '<path d="M25 40 Q5 21 1 33 Q-1 44 20 46 Q10 51 8 62 L22 56 Q14 63 15 72 L28 61 Z" fill="#ff6600" opacity=".9"/>'
    '<path d="M25 40 Q7 25 3 36" stroke="#ffaa00" stroke-width="2" fill="none" opacity=".7"/>'
    '<path d="M25 42 Q9 33 6 43" stroke="#ffcc00" stroke-width="1.5" fill="none" opacity=".55"/>'
    '<path d="M24 47 Q11 45 9 53" stroke="#ffaa00" stroke-width="1.5" fill="none" opacity=".5"/>'
    '<path d="M55 40 Q75 21 79 33 Q81 44 60 46 Q70 51 72 62 L58 56 Q66 63 65 72 L52 61 Z" fill="#ff6600" opacity=".9"/>'
    '<path d="M55 40 Q73 25 77 36" stroke="#ffaa00" stroke-width="2" fill="none" opacity=".7"/>'
    '<path d="M55 42 Q71 33 74 43" stroke="#ffcc00" stroke-width="1.5" fill="none" opacity=".55"/>'
    '<path d="M56 47 Q69 45 71 53" stroke="#ffaa00" stroke-width="1.5" fill="none" opacity=".5"/>'
    '<ellipse cx="40" cy="51" rx="16" ry="18" fill="#ff4400"/>'
    '<ellipse cx="40" cy="55" rx="10" ry="12" fill="#ffcc00" opacity=".6"/>'
    '<path d="M32 38 Q40 32 48 38 L46 50 Q40 46 34 50 Z" fill="#ff5500"/>'
    '<circle cx="40" cy="27" r="14" fill="#ff4400"/>'
    '<path d="M40 13 Q36 5 32 1" stroke="#ffcc00" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
    '<path d="M40 13 Q40 3 40 -1" stroke="#ff8800" stroke-width="4" fill="none" stroke-linecap="round"/>'
    '<path d="M40 13 Q44 5 48 1" stroke="#ffcc00" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
    '<path d="M38 15 Q34 9 32 5" stroke="#ff6600" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    '<path d="M42 15 Q46 9 48 5" stroke="#ff6600" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    '<path d="M34 30 L28 35 L34 32 Z" fill="#ffcc00"/>'
    '<circle cx="34" cy="24" r="6" fill="#ffcc00"/>'
    '<circle cx="46" cy="24" r="6" fill="#ffcc00"/>'
    '<circle cx="34" cy="24" r="4" fill="#ff6600"/>'
    '<circle cx="46" cy="24" r="4" fill="#ff6600"/>'
    '<circle cx="34" cy="24" r="2" fill="#220000"/>'
    '<circle cx="46" cy="24" r="2" fill="#220000"/>'
    '<circle cx="33" cy="23" r="1" fill="#ffeeaa" opacity=".9"/>'
    '<circle cx="45" cy="23" r="1" fill="#ffeeaa" opacity=".9"/>'
    '<circle cx="18" cy="20" r="2" fill="#ffcc00" opacity=".8"/>'
    '<circle cx="62" cy="17" r="2.5" fill="#ffcc00" opacity=".7"/>'
    '</svg>'
)

# ─────────────────────────────────────────
# モンスターデータ
# ─────────────────────────────────────────

MONSTERS: dict[str, dict] = {
    "slime": {
        "id": "slime", "name": "スライム", "emoji": "🔵",
        "hp": 30, "attack": 5,
        "drop_rate": 0.15, "drop_items": ["wooden_sword", "leather_cap"],
        "svg": _SVG["slime"], "is_boss": False,
    },
    "bat": {
        "id": "bat", "name": "コウモリ", "emoji": "🦇",
        "hp": 38, "attack": 7,
        "drop_rate": 0.15, "drop_items": ["wooden_sword", "wool_cloak"],
        "svg": _SVG["bat"], "is_boss": False,
    },
    "goblin": {
        "id": "goblin", "name": "ゴブリン", "emoji": "👺",
        "hp": 52, "attack": 9,
        "drop_rate": 0.22, "drop_items": ["wooden_sword", "leather_cap", "leather_armor"],
        "svg": _SVG["goblin"], "is_boss": False,
    },
    "ghost": {
        "id": "ghost", "name": "ゴースト", "emoji": "👻",
        "hp": 46, "attack": 8,
        "drop_rate": 0.20, "drop_items": ["wool_cloak", "leather_cap"],
        "svg": _SVG["ghost"], "is_boss": False,
    },
    "zombie": {
        "id": "zombie", "name": "ゾンビ", "emoji": "🧟",
        "hp": 58, "attack": 9,
        "drop_rate": 0.22, "drop_items": ["leather_armor", "wool_cloak"],
        "svg": _SVG["zombie"], "is_boss": False,
    },
    "wolf": {
        "id": "wolf", "name": "ウルフ", "emoji": "🐺",
        "hp": 68, "attack": 12,
        "drop_rate": 0.22, "drop_items": ["iron_sword", "wool_cloak"],
        "svg": _SVG["wolf"], "is_boss": False,
    },
    "orc": {
        "id": "orc", "name": "オーク", "emoji": "🗡️",
        "hp": 84, "attack": 14,
        "drop_rate": 0.25, "drop_items": ["iron_sword", "iron_armor", "iron_helm"],
        "svg": _SVG["orc"], "is_boss": False,
    },
    "skeleton": {
        "id": "skeleton", "name": "スケルトン", "emoji": "💀",
        "hp": 72, "attack": 13,
        "drop_rate": 0.25, "drop_items": ["iron_sword", "iron_helm"],
        "svg": _SVG["skeleton"], "is_boss": False,
    },
    "minotaur": {
        "id": "minotaur", "name": "ミノタウロス", "emoji": "🐂",
        "hp": 104, "attack": 17,
        "drop_rate": 0.28, "drop_items": ["iron_armor", "iron_helm", "iron_sword"],
        "svg": _SVG["minotaur"], "is_boss": False,
    },
    "dragon": {
        "id": "dragon", "name": "ドラゴン", "emoji": "🐉",
        "hp": 124, "attack": 20,
        "drop_rate": 0.30, "drop_items": ["flame_sword", "dragon_scale", "iron_armor"],
        "svg": _SVG["dragon"], "is_boss": False,
    },
}

BOSS_MONSTERS: dict[str, dict] = {
    "dark_dragon": {
        "id": "dark_dragon", "name": "暗黒竜", "emoji": "🖤",
        "hp": 320, "attack": 28,
        "drop_rate": 1.0, "drop_items": ["dragon_scale", "flame_sword"],
        "svg": _SVG["dark_dragon"], "is_boss": True,
        "boss_title": "週替わりBOSS",
    },
    "demon_lord": {
        "id": "demon_lord", "name": "魔王", "emoji": "👿",
        "hp": 380, "attack": 32,
        "drop_rate": 1.0, "drop_items": ["dark_cloak", "hero_cloak"],
        "svg": _SVG["demon_lord"], "is_boss": True,
        "boss_title": "週替わりBOSS",
    },
    "lich": {
        "id": "lich", "name": "リッチ", "emoji": "🧙",
        "hp": 300, "attack": 26,
        "drop_rate": 1.0, "drop_items": ["mage_robe", "mage_hat"],
        "svg": _SVG["lich"], "is_boss": True,
        "boss_title": "週替わりBOSS",
    },
    "golem": {
        "id": "golem", "name": "ゴーレム", "emoji": "🗿",
        "hp": 360, "attack": 30,
        "drop_rate": 1.0, "drop_items": ["iron_armor", "iron_helm"],
        "svg": _SVG["golem"], "is_boss": True,
        "boss_title": "週替わりBOSS",
    },
    "phoenix": {
        "id": "phoenix", "name": "フェニックス", "emoji": "🔥",
        "hp": 290, "attack": 24,
        "drop_rate": 1.0, "drop_items": ["hero_cloak", "holy_robe"],
        "svg": _SVG["phoenix"], "is_boss": True,
        "boss_title": "週替わりBOSS",
    },
}

BOSS_ORDER = ["golem", "lich", "dark_dragon", "demon_lord", "phoenix"]

# 級ごとの出現モンスタープール
_GRADE_POOLS: dict[str, list[str]] = {
    "grade_5": ["slime", "bat", "goblin"],
    "grade_4": ["slime", "bat", "goblin", "ghost", "zombie"],
    "grade_3": ["goblin", "ghost", "zombie", "wolf", "orc"],
    "grade_pre2": ["wolf", "orc", "skeleton", "minotaur"],
    "grade_2": ["skeleton", "orc", "minotaur", "dragon"],
}


def get_weekly_boss() -> dict:
    """今週の曜日ボスを返す（ISO週番号でローテーション）"""
    week_num = date.today().isocalendar()[1]
    boss_id = BOSS_ORDER[week_num % len(BOSS_ORDER)]
    return dict(BOSS_MONSTERS[boss_id])


def get_monster_for_grade(grade: str) -> dict:
    """グレードに適したランダムモンスターを返す"""
    pool = _GRADE_POOLS.get(grade, ["slime", "goblin", "bat"])
    monster_id = random.choice(pool)
    return dict(MONSTERS[monster_id])


def calc_player_damage(difficulty: int) -> int:
    """問題の難易度に応じたモンスターへのダメージ量（1〜3星）"""
    base = {1: 18, 2: 26, 3: 38}.get(difficulty, 18)
    return base + random.randint(-4, 4)
