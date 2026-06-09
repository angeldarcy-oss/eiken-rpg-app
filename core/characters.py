"""core/characters.py — キャラクター定義（10種類）"""

from __future__ import annotations

CHARACTER_ORDER = [
    "allen", "liria", "gares", "shia", "erwin",
    "noah", "drake", "luna", "finn", "sera",
]


def _svg(inner: str) -> str:
    return '<svg viewBox="0 0 80 100" xmlns="http://www.w3.org/2000/svg">' + inner + '</svg>'


# ─────────────────────────────────────────
# 1. アレン（勇者）- 青テーマ
# ─────────────────────────────────────────
_ALLEN = _svg(
    # 足・ブーツ
    '<rect x="27" y="70" width="11" height="22" fill="#1a4fcc" rx="2"/>'
    '<rect x="42" y="70" width="11" height="22" fill="#1a4fcc" rx="2"/>'
    '<rect x="25" y="80" width="15" height="12" fill="#0d2d88" rx="2"/>'
    '<rect x="40" y="80" width="15" height="12" fill="#0d2d88" rx="2"/>'
    # 胴体（青い鎧）
    '<rect x="21" y="40" width="38" height="30" fill="#1a4fcc" rx="4"/>'
    '<path d="M21 40 L40 35 L59 40 L59 46 L40 41 L21 46Z" fill="#3377ff"/>'
    '<polygon points="40,47 43,53 49,53 45,57 47,62 40,58 33,62 35,57 31,53 37,53" fill="#ffe066"/>'
    '<rect x="21" y="68" width="38" height="4" fill="#0a2070" rx="1"/>'
    '<rect x="36" y="66" width="8" height="7" fill="#ffe066" rx="1"/>'
    # 肩アーマー
    '<ellipse cx="21" cy="42" rx="7" ry="6" fill="#2255ee"/>'
    '<ellipse cx="59" cy="42" rx="7" ry="6" fill="#2255ee"/>'
    # 腕
    '<rect x="5" y="42" width="17" height="10" fill="#1a4fcc" rx="3"/>'
    '<rect x="58" y="42" width="17" height="10" fill="#1a4fcc" rx="3"/>'
    # 盾（左）
    '<rect x="-2" y="46" width="13" height="20" fill="#0d2d88" rx="3"/>'
    '<rect x="-1" y="47" width="11" height="18" fill="#1a4fcc" rx="2"/>'
    '<polygon points="5.5,50 9,56 5.5,63 2,56" fill="#ffe066"/>'
    # 剣（右）
    '<rect x="70" y="7" width="4" height="46" fill="#c8deff" rx="1"/>'
    '<polygon points="72,1 76,11 68,11" fill="#e8f0ff"/>'
    '<rect x="63" y="26" width="18" height="4" fill="#ffe066" rx="1"/>'
    # 首
    '<rect x="33" y="35" width="14" height="7" fill="#f5c5a3" rx="2"/>'
    # 頭
    '<circle cx="40" cy="22" r="15" fill="#f5c5a3"/>'
    # 金髪スパイク
    '<ellipse cx="40" cy="11" rx="14" ry="9" fill="#ffdd22"/>'
    '<polygon points="30,13 27,-1 34,11" fill="#ffcc00"/>'
    '<polygon points="39,10 38,-3 44,8" fill="#ffee44"/>'
    '<polygon points="48,12 49,-1 54,11" fill="#ffcc00"/>'
    '<path d="M25 19 C23 11 27 4 31 8" stroke="#ffdd22" stroke-width="5" fill="none" stroke-linecap="round"/>'
    '<path d="M55 19 C57 11 53 4 49 8" stroke="#ddbb00" stroke-width="5" fill="none" stroke-linecap="round"/>'
    # 目（大・青）
    '<ellipse cx="33" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="47" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="33" cy="24" rx="3.5" ry="4.5" fill="#2288ff"/>'
    '<ellipse cx="47" cy="24" rx="3.5" ry="4.5" fill="#2288ff"/>'
    '<ellipse cx="33" cy="26" rx="3.5" ry="2" fill="#0044cc"/>'
    '<ellipse cx="47" cy="26" rx="3.5" ry="2" fill="#0044cc"/>'
    '<ellipse cx="33" cy="24" rx="1.5" ry="2" fill="#050d1a"/>'
    '<ellipse cx="47" cy="24" rx="1.5" ry="2" fill="#050d1a"/>'
    '<circle cx="30.5" cy="21" r="1.8" fill="white"/>'
    '<circle cx="44.5" cy="21" r="1.8" fill="white"/>'
    '<path d="M28 19 Q33 15 38 19" stroke="#221100" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M42 19 Q47 15 52 19" stroke="#221100" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 眉
    '<path d="M27 14 Q33 10 39 13" stroke="#cc9900" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    '<path d="M41 13 Q47 10 53 14" stroke="#cc9900" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    # 口
    '<path d="M35 30 Q40 35 45 30" stroke="#cc7755" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 頬
    '<circle cx="28" cy="27" r="4" fill="#ff9977" opacity="0.35"/>'
    '<circle cx="52" cy="27" r="4" fill="#ff9977" opacity="0.35"/>'
)

# ─────────────────────────────────────────
# 2. リリア（魔法使い）- 紫テーマ
# ─────────────────────────────────────────
_LIRIA = _svg(
    # 足・ローブ裾
    '<path d="M26 72 L22 94 L37 85 L40 94 L43 85 L58 94 L54 72Z" fill="#6622cc"/>'
    # 胴体（紫ローブ）
    '<rect x="19" y="40" width="42" height="34" fill="#7733dd" rx="5"/>'
    '<rect x="19" y="40" width="4" height="34" fill="#5511bb" rx="2"/>'
    '<rect x="57" y="40" width="4" height="34" fill="#5511bb" rx="2"/>'
    '<path d="M19 40 L40 35 L61 40 L61 46 L40 41 L19 46Z" fill="#9955ff"/>'
    # 星紋様
    '<circle cx="40" cy="55" r="5" fill="none" stroke="#cc99ff" stroke-width="1.5"/>'
    '<polygon points="40,49 41.5,53.5 46,53.5 42.5,56.5 43.5,61 40,58 36.5,61 37.5,56.5 34,53.5 38.5,53.5" fill="#cc99ff" opacity="0.6"/>'
    # 腕
    '<rect x="6" y="42" width="14" height="9" fill="#7733dd" rx="3"/>'
    '<rect x="60" y="42" width="14" height="9" fill="#7733dd" rx="3"/>'
    # 杖（左）
    '<rect x="4" y="26" width="3" height="32" fill="#8866aa" rx="1"/>'
    '<circle cx="5.5" cy="22" r="7" fill="#cc88ff" opacity="0.4"/>'
    '<circle cx="5.5" cy="22" r="5" fill="#bb66ff"/>'
    '<circle cx="5.5" cy="22" r="3" fill="#eeccff"/>'
    '<circle cx="5.5" cy="22" r="1.5" fill="white"/>'
    # 右手の光
    '<circle cx="72" cy="50" r="5" fill="#9944ff" opacity="0.3"/>'
    '<circle cx="72" cy="50" r="3" fill="#cc88ff" opacity="0.5"/>'
    # 首
    '<rect x="34" y="35" width="12" height="7" fill="#f0c0e0" rx="2"/>'
    # 頭
    '<circle cx="40" cy="22" r="14" fill="#f0c0e0"/>'
    # 尖り帽子
    '<polygon points="40,-6 24,27 56,27" fill="#6622cc"/>'
    '<polygon points="40,-6 31,12 49,12" fill="#8833ee"/>'
    '<rect x="22" y="25" width="36" height="6" fill="#5511bb" rx="3"/>'
    '<circle cx="40" cy="-2" r="3" fill="#cc88ff"/>'
    '<circle cx="40" cy="-2" r="1.5" fill="white"/>'
    # シルバーピンクの髪
    '<path d="M27 22 C24 14 26 7 30 9 C27 14 26 20 25 30 C24 38 22 46 20 52 L22 52 C24 46 26 38 27 30Z" fill="#ddbbee"/>'
    '<path d="M53 22 C56 14 54 7 50 9 C53 14 54 20 55 30 C56 38 58 46 60 52 L58 52 C56 46 54 38 53 30Z" fill="#ccaae0"/>'
    '<ellipse cx="40" cy="14" rx="12" ry="6" fill="#ddbbee"/>'
    # 目（大・紫）
    '<ellipse cx="33" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="47" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="33" cy="24" rx="3.5" ry="4.5" fill="#9933cc"/>'
    '<ellipse cx="47" cy="24" rx="3.5" ry="4.5" fill="#9933cc"/>'
    '<ellipse cx="33" cy="26" rx="3.5" ry="2" fill="#6611aa"/>'
    '<ellipse cx="47" cy="26" rx="3.5" ry="2" fill="#6611aa"/>'
    '<ellipse cx="33" cy="24" rx="1.5" ry="2" fill="#110022"/>'
    '<ellipse cx="47" cy="24" rx="1.5" ry="2" fill="#110022"/>'
    '<circle cx="30.5" cy="21" r="1.8" fill="white"/>'
    '<circle cx="44.5" cy="21" r="1.8" fill="white"/>'
    '<path d="M28 19 Q33 15 38 19" stroke="#330066" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M42 19 Q47 15 52 19" stroke="#330066" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 眉
    '<path d="M28 14 Q33 10 38 13" stroke="#7733aa" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    '<path d="M42 13 Q47 10 52 14" stroke="#7733aa" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    # 口
    '<path d="M36 30 Q40 34 44 30" stroke="#cc88bb" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
    # 頬
    '<circle cx="28" cy="27" r="3.5" fill="#ff99cc" opacity="0.3"/>'
    '<circle cx="52" cy="27" r="3.5" fill="#ff99cc" opacity="0.3"/>'
)

# ─────────────────────────────────────────
# 3. ガレス（騎士）- シルバーテーマ（フルアーマー）
# ─────────────────────────────────────────
_GARES = _svg(
    # 足・グリーブ
    '<rect x="26" y="70" width="12" height="22" fill="#9aa8b8" rx="2"/>'
    '<rect x="42" y="70" width="12" height="22" fill="#9aa8b8" rx="2"/>'
    '<rect x="24" y="80" width="16" height="12" fill="#6a7888" rx="2"/>'
    '<rect x="40" y="80" width="16" height="12" fill="#6a7888" rx="2"/>'
    '<rect x="24" y="80" width="16" height="3" fill="#bbccdd" rx="1"/>'
    '<rect x="40" y="80" width="16" height="3" fill="#bbccdd" rx="1"/>'
    # 胴体（重厚な銀鎧）
    '<rect x="18" y="39" width="44" height="31" fill="#aabbcc" rx="4"/>'
    '<path d="M18 39 L40 33 L62 39 L62 46 L40 40 L18 46Z" fill="#ccdded"/>'
    '<path d="M34 48 L40 44 L46 48 L46 58 L40 62 L34 58Z" fill="#3355cc"/>'
    '<path d="M35 49 L40 46 L45 49 L45 57 L40 60 L35 57Z" fill="#4466ee"/>'
    '<polygon points="40,49 41.5,53 43,53 41.5,55 42,58 40,56 38,58 38.5,55 37,53 38.5,53" fill="#ffe066"/>'
    '<rect x="18" y="68" width="44" height="4" fill="#6a7888" rx="1"/>'
    # 肩鎧
    '<ellipse cx="18" cy="41" rx="9" ry="7" fill="#bbccdd"/>'
    '<ellipse cx="62" cy="41" rx="9" ry="7" fill="#bbccdd"/>'
    '<ellipse cx="18" cy="41" rx="6" ry="4" fill="#ccdded"/>'
    '<ellipse cx="62" cy="41" rx="6" ry="4" fill="#ccdded"/>'
    # 腕
    '<rect x="4" y="41" width="15" height="11" fill="#aabbcc" rx="3"/>'
    '<rect x="61" y="41" width="15" height="11" fill="#aabbcc" rx="3"/>'
    # 大盾（左）
    '<rect x="-4" y="44" width="14" height="24" fill="#778899" rx="3"/>'
    '<rect x="-3" y="45" width="12" height="22" fill="#99aacc" rx="2"/>'
    '<polygon points="3,48 8,52 8,62 3,67 -2,62 -2,52" fill="#aabbdd"/>'
    '<polygon points="3,52 6,56 3,62 0,56" fill="#ffe066" opacity="0.7"/>'
    # 槍（右）
    '<rect x="70" y="2" width="5" height="64" fill="#c0c8d8" rx="2"/>'
    '<polygon points="72.5,-4 77,10 68,10" fill="#e0e8f8"/>'
    '<rect x="67" y="24" width="11" height="5" fill="#ffe066" rx="1"/>'
    # フルフェイス兜
    '<ellipse cx="40" cy="24" rx="17" ry="16" fill="#aabbcc"/>'
    '<ellipse cx="40" cy="24" rx="16" ry="15" fill="#bbccdd"/>'
    '<path d="M23 24 Q23 15 40 12 Q57 15 57 24" fill="#ccdded"/>'
    '<rect x="24" y="25" width="32" height="8" fill="#778899" rx="2"/>'
    '<rect x="25" y="26" width="14" height="5" fill="#1133aa" rx="1"/>'
    '<rect x="41" y="26" width="14" height="5" fill="#1133aa" rx="1"/>'
    '<rect x="26" y="27" width="12" height="3" fill="#3366ff" rx="1" opacity="0.7"/>'
    '<rect x="42" y="27" width="12" height="3" fill="#3366ff" rx="1" opacity="0.7"/>'
    '<rect x="37" y="33" width="6" height="5" fill="#9aa8b8" rx="2"/>'
    # 青いプルーム
    '<path d="M40 8 C37 -2 32 -6 34 2 C36 -4 39 2 40 8Z" fill="#2255cc"/>'
    '<path d="M40 8 C43 -2 48 -6 46 2 C44 -4 41 2 40 8Z" fill="#3366ee"/>'
    '<path d="M40 8 C38 0 35 -4 37 2 C38 -2 39 3 40 8Z" fill="#4488ff"/>'
    '<path d="M40 8 C42 0 45 -4 43 2 C42 -2 41 3 40 8Z" fill="#1144bb"/>'
)

# ─────────────────────────────────────────
# 4. シア（盗賊）- 緑テーマ
# ─────────────────────────────────────────
_SHIA = _svg(
    # 足・ブーツ
    '<rect x="27" y="71" width="11" height="21" fill="#2d5522" rx="2"/>'
    '<rect x="42" y="71" width="11" height="21" fill="#2d5522" rx="2"/>'
    '<rect x="25" y="81" width="15" height="11" fill="#1a2e11" rx="2"/>'
    '<rect x="40" y="81" width="15" height="11" fill="#1a2e11" rx="2"/>'
    # 体（革鎧・ダークグリーン）
    '<rect x="22" y="40" width="36" height="31" fill="#3d6e2d" rx="4"/>'
    '<path d="M22 40 L40 35 L58 40 L58 46 L40 41 L22 46Z" fill="#5a9945"/>'
    '<path d="M22 42 C20 36 22 30 40 28 C58 30 60 36 58 42Z" fill="#2d5522"/>'
    '<rect x="22" y="65" width="36" height="5" fill="#1a2e11" rx="1"/>'
    '<rect x="34" y="62" width="12" height="10" fill="#2d4011" rx="1"/>'
    '<rect x="23" y="55" width="8" height="9" fill="#4a3011" rx="2"/>'
    '<rect x="49" y="55" width="8" height="9" fill="#4a3011" rx="2"/>'
    # 腕
    '<rect x="9" y="41" width="14" height="9" fill="#3d6e2d" rx="3"/>'
    '<rect x="57" y="41" width="14" height="9" fill="#3d6e2d" rx="3"/>'
    # 短剣（両側）
    '<rect x="4" y="52" width="3" height="18" fill="#c8c8c8" rx="1" transform="rotate(-15 5 60)"/>'
    '<rect x="2" y="56" width="8" height="3" fill="#5a3a11" rx="1" transform="rotate(-15 5 60)"/>'
    '<rect x="66" y="52" width="3" height="18" fill="#c8c8c8" rx="1" transform="rotate(15 68 60)"/>'
    '<rect x="63" y="56" width="8" height="3" fill="#5a3a11" rx="1" transform="rotate(15 68 60)"/>'
    # 首
    '<rect x="34" y="35" width="12" height="7" fill="#c8906a" rx="2"/>'
    # 頭
    '<circle cx="40" cy="22" r="14" fill="#c8906a"/>'
    # ダークグリーンフード
    '<ellipse cx="40" cy="16" rx="18" ry="13" fill="#2d5522"/>'
    '<path d="M22 22 C22 14 28 8 40 6 C52 8 58 14 58 22 C54 16 47 12 40 12 C33 12 26 16 22 22Z" fill="#3d6e2d"/>'
    '<path d="M22 22 C22 32 24 40 20 46 C18 40 18 31 22 22Z" fill="#2d5522"/>'
    '<path d="M58 22 C58 32 56 40 60 46 C62 40 62 31 58 22Z" fill="#2d5522"/>'
    # 目（大・緑）
    '<ellipse cx="33" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="47" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="33" cy="24" rx="3.5" ry="4.5" fill="#33aa44"/>'
    '<ellipse cx="47" cy="24" rx="3.5" ry="4.5" fill="#33aa44"/>'
    '<ellipse cx="33" cy="26" rx="3.5" ry="2" fill="#116622"/>'
    '<ellipse cx="47" cy="26" rx="3.5" ry="2" fill="#116622"/>'
    '<ellipse cx="33" cy="24" rx="1.5" ry="2" fill="#081100"/>'
    '<ellipse cx="47" cy="24" rx="1.5" ry="2" fill="#081100"/>'
    '<circle cx="30.5" cy="21" r="1.8" fill="white"/>'
    '<circle cx="44.5" cy="21" r="1.8" fill="white"/>'
    '<path d="M28 19 Q33 15 38 19" stroke="#112200" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M42 19 Q47 15 52 19" stroke="#112200" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 眉（鋭い）
    '<path d="M28 14 Q33 11 38 14" stroke="#3d2211" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    '<path d="M42 14 Q47 11 52 14" stroke="#3d2211" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    # 口（ニヤリ）
    '<path d="M35 30 Q38 28 40 30 Q42 28 45 30" stroke="#9a5533" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
)

# ─────────────────────────────────────────
# 5. エルウィン（弓使い）- 茶色テーマ
# ─────────────────────────────────────────
_ERWIN = _svg(
    # 足・ブーツ
    '<rect x="27" y="71" width="11" height="21" fill="#7a5533" rx="2"/>'
    '<rect x="42" y="71" width="11" height="21" fill="#7a5533" rx="2"/>'
    '<rect x="25" y="81" width="15" height="11" fill="#4a2e11" rx="2"/>'
    '<rect x="40" y="81" width="15" height="11" fill="#4a2e11" rx="2"/>'
    # 体（茶色レンジャー服）
    '<rect x="22" y="40" width="36" height="31" fill="#8b6240" rx="4"/>'
    '<path d="M22 40 L40 35 L58 40 L58 46 L40 41 L22 46Z" fill="#aa7a55"/>'
    '<rect x="34" y="40" width="12" height="2" fill="#6a4820" rx="1"/>'
    '<rect x="22" y="55" width="36" height="3" fill="#6a4820" rx="1"/>'
    '<path d="M22 48 L16 72 L28 64Z" fill="#6a4820" opacity="0.8"/>'
    '<rect x="22" y="66" width="36" height="5" fill="#4a2e11" rx="1"/>'
    # 腕
    '<rect x="9" y="41" width="14" height="9" fill="#8b6240" rx="3"/>'
    '<rect x="57" y="41" width="14" height="9" fill="#8b6240" rx="3"/>'
    # 弓（右側）
    '<path d="M68 14 C78 24 78 52 68 62" stroke="#8b6240" stroke-width="4" fill="none" stroke-linecap="round"/>'
    '<path d="M68 14 C74 24 74 52 68 62" stroke="#aa8855" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<line x1="68" y1="14" x2="68" y2="62" stroke="#c8a878" stroke-width="1.2" stroke-dasharray="3,2"/>'
    '<line x1="58" y1="38" x2="76" y2="38" stroke="#aa8855" stroke-width="1.5"/>'
    '<polygon points="76,38 72,36 72,40" fill="#8b6240"/>'
    '<rect x="57" y="36" width="4" height="4" fill="#cc3333" rx="1"/>'
    # 首
    '<rect x="33" y="35" width="14" height="7" fill="#e8d0a0" rx="2"/>'
    # 頭
    '<circle cx="40" cy="22" r="15" fill="#e8d0a0"/>'
    # 銀白髪
    '<ellipse cx="40" cy="11" rx="14" ry="9" fill="#dde8f0"/>'
    '<path d="M25 19 C23 11 26 4 30 8" stroke="#dde8f0" stroke-width="6" fill="none" stroke-linecap="round"/>'
    '<path d="M55 19 C57 11 54 4 50 8" stroke="#c8d8e8" stroke-width="6" fill="none" stroke-linecap="round"/>'
    '<rect x="28" y="9" width="4" height="10" fill="#c8d8e8" rx="2" transform="rotate(-8 30 14)"/>'
    '<rect x="48" y="9" width="4" height="10" fill="#dde8f0" rx="2" transform="rotate(8 50 14)"/>'
    # ヘアバンド
    '<rect x="25" y="16" width="30" height="4" fill="#8b6240" rx="2"/>'
    # 目（大・灰青）
    '<ellipse cx="33" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="47" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="33" cy="24" rx="3.5" ry="4.5" fill="#6688aa"/>'
    '<ellipse cx="47" cy="24" rx="3.5" ry="4.5" fill="#6688aa"/>'
    '<ellipse cx="33" cy="26" rx="3.5" ry="2" fill="#446688"/>'
    '<ellipse cx="47" cy="26" rx="3.5" ry="2" fill="#446688"/>'
    '<ellipse cx="33" cy="24" rx="1.5" ry="2" fill="#0a1020"/>'
    '<ellipse cx="47" cy="24" rx="1.5" ry="2" fill="#0a1020"/>'
    '<circle cx="30.5" cy="21" r="1.8" fill="white"/>'
    '<circle cx="44.5" cy="21" r="1.8" fill="white"/>'
    '<path d="M28 19 Q33 15 38 19" stroke="#331100" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
    '<path d="M42 19 Q47 15 52 19" stroke="#331100" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
    # 眉（細い）
    '<path d="M28 14 Q33 11 38 14" stroke="#9a9090" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M42 14 Q47 11 52 14" stroke="#9a9090" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 口（冷静）
    '<line x1="36" y1="31" x2="44" y2="31" stroke="#bb8855" stroke-width="1.8" stroke-linecap="round"/>'
)

# ─────────────────────────────────────────
# 6. ノア（僧侶）- 白/金テーマ
# ─────────────────────────────────────────
_NOAH = _svg(
    # 足・ローブ裾
    '<path d="M26 72 L23 94 L38 86 L40 92 L42 86 L57 94 L54 72Z" fill="#eeeecc"/>'
    # 胴体（白金ローブ）
    '<rect x="19" y="40" width="42" height="33" fill="#eeeecc" rx="5"/>'
    '<rect x="19" y="40" width="5" height="33" fill="#ffe066" rx="2"/>'
    '<rect x="56" y="40" width="5" height="33" fill="#ffe066" rx="2"/>'
    '<path d="M19 40 L40 34 L61 40 L61 47 L40 41 L19 47Z" fill="#fafae8"/>'
    # 胸の十字紋章
    '<rect x="37" y="48" width="6" height="14" fill="#ffe066" rx="2"/>'
    '<rect x="32" y="53" width="16" height="6" fill="#ffe066" rx="2"/>'
    '<rect x="38" y="49" width="4" height="12" fill="#ffcc00" rx="1"/>'
    '<rect x="33" y="54" width="14" height="4" fill="#ffcc00" rx="1"/>'
    # 腕
    '<rect x="6" y="42" width="14" height="9" fill="#eeeecc" rx="3"/>'
    '<rect x="60" y="42" width="14" height="9" fill="#eeeecc" rx="3"/>'
    # 聖なる杖（左）
    '<rect x="3" y="24" width="4" height="36" fill="#aa8833" rx="2"/>'
    '<circle cx="5" cy="20" r="8" fill="#ffe066" opacity="0.4"/>'
    '<circle cx="5" cy="20" r="6" fill="#ffe066" opacity="0.6"/>'
    '<circle cx="5" cy="20" r="4" fill="#ffcc00"/>'
    '<circle cx="5" cy="20" r="2.5" fill="#ffffaa"/>'
    '<circle cx="5" cy="20" r="1" fill="white"/>'
    # 右手の光輪
    '<circle cx="73" cy="49" r="6" fill="#ffe066" opacity="0.3"/>'
    '<circle cx="73" cy="49" r="4" fill="#ffe066" opacity="0.5"/>'
    # 首
    '<rect x="34" y="35" width="12" height="7" fill="#f0c07a" rx="2"/>'
    # 頭
    '<circle cx="40" cy="22" r="15" fill="#f0c07a"/>'
    # 金色ウェーブヘア
    '<ellipse cx="40" cy="11" rx="14" ry="9" fill="#ffe033"/>'
    '<path d="M25 19 C23 12 26 5 30 8 C27 13 26 19 25 22Z" fill="#ffe033"/>'
    '<path d="M55 19 C57 12 54 5 50 8 C53 13 54 19 55 22Z" fill="#ddcc22"/>'
    '<path d="M25 22 C23 28 24 38 22 46 L24 46 C26 38 25 28 26 22Z" fill="#ddcc22"/>'
    '<path d="M55 22 C57 28 56 38 58 46 L56 46 C54 38 55 28 54 22Z" fill="#ddcc22"/>'
    # 目（大・温かみのある茶色）
    '<ellipse cx="33" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="47" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="33" cy="24" rx="3.5" ry="4.5" fill="#aa6633"/>'
    '<ellipse cx="47" cy="24" rx="3.5" ry="4.5" fill="#aa6633"/>'
    '<ellipse cx="33" cy="26" rx="3.5" ry="2" fill="#774422"/>'
    '<ellipse cx="47" cy="26" rx="3.5" ry="2" fill="#774422"/>'
    '<ellipse cx="33" cy="24" rx="1.5" ry="2" fill="#1a0800"/>'
    '<ellipse cx="47" cy="24" rx="1.5" ry="2" fill="#1a0800"/>'
    '<circle cx="30.5" cy="21" r="1.8" fill="white"/>'
    '<circle cx="44.5" cy="21" r="1.8" fill="white"/>'
    '<path d="M28 19 Q33 15 38 19" stroke="#221100" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M42 19 Q47 15 52 19" stroke="#221100" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 眉（優しい）
    '<path d="M28 14 Q33 11 38 14" stroke="#aa7722" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    '<path d="M42 14 Q47 11 52 14" stroke="#aa7722" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    # 口（優しい笑顔）
    '<path d="M35 30 Q40 35 45 30" stroke="#cc8855" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 頬
    '<circle cx="27" cy="27" r="4" fill="#ffaa66" opacity="0.35"/>'
    '<circle cx="53" cy="27" r="4" fill="#ffaa66" opacity="0.35"/>'
)

# ─────────────────────────────────────────
# 7. ドラク（ドラゴン戦士）- 赤テーマ
# ─────────────────────────────────────────
_DRAKE = _svg(
    # 尻尾
    '<path d="M54 72 C66 68 76 76 72 90 C68 98 60 96 56 88" stroke="#cc2211" stroke-width="8" fill="none" stroke-linecap="round"/>'
    '<path d="M54 72 C66 68 76 76 72 90" stroke="#ff4433" stroke-width="4" fill="none" stroke-linecap="round"/>'
    # 足・ブーツ
    '<rect x="27" y="70" width="11" height="22" fill="#cc2211" rx="2"/>'
    '<rect x="42" y="70" width="11" height="22" fill="#cc2211" rx="2"/>'
    '<rect x="25" y="80" width="15" height="12" fill="#881100" rx="2"/>'
    '<rect x="40" y="80" width="15" height="12" fill="#881100" rx="2"/>'
    '<polygon points="26,92 28,99 30,92" fill="#440000"/>'
    '<polygon points="32,92 34,99 36,92" fill="#440000"/>'
    '<polygon points="42,92 44,99 46,92" fill="#440000"/>'
    '<polygon points="48,92 50,99 52,92" fill="#440000"/>'
    # 胴体（赤い鱗鎧）
    '<rect x="20" y="39" width="40" height="31" fill="#cc2211" rx="4"/>'
    '<path d="M20 39 L40 33 L60 39 L60 46 L40 41 L20 46Z" fill="#ee4433"/>'
    '<ellipse cx="28" cy="48" rx="6" ry="3.5" fill="#991100" opacity="0.7"/>'
    '<ellipse cx="36" cy="48" rx="6" ry="3.5" fill="#991100" opacity="0.7"/>'
    '<ellipse cx="44" cy="48" rx="6" ry="3.5" fill="#991100" opacity="0.7"/>'
    '<ellipse cx="52" cy="48" rx="6" ry="3.5" fill="#991100" opacity="0.7"/>'
    '<ellipse cx="32" cy="56" rx="6" ry="3.5" fill="#991100" opacity="0.6"/>'
    '<ellipse cx="40" cy="56" rx="6" ry="3.5" fill="#991100" opacity="0.6"/>'
    '<ellipse cx="48" cy="56" rx="6" ry="3.5" fill="#991100" opacity="0.6"/>'
    '<rect x="20" y="68" width="40" height="4" fill="#881100" rx="1"/>'
    # 肩（棘付き）
    '<ellipse cx="20" cy="42" rx="8" ry="6" fill="#dd3322"/>'
    '<polygon points="14,38 12,30 18,36" fill="#cc2211"/>'
    '<polygon points="20,36 18,26 24,34" fill="#cc2211"/>'
    '<ellipse cx="60" cy="42" rx="8" ry="6" fill="#dd3322"/>'
    '<polygon points="66,38 68,30 62,36" fill="#cc2211"/>'
    '<polygon points="60,36 62,26 56,34" fill="#cc2211"/>'
    # 腕
    '<rect x="5" y="41" width="16" height="11" fill="#cc2211" rx="3"/>'
    '<rect x="59" y="41" width="16" height="11" fill="#cc2211" rx="3"/>'
    # 大斧（右）
    '<rect x="70" y="20" width="5" height="50" fill="#888880" rx="2"/>'
    '<path d="M72.5 8 C82 10 84 24 74 26 C82 20 80 10 72.5 8Z" fill="#a0a8a0"/>'
    '<path d="M72.5 8 C63 10 61 24 71 26 C63 20 65 10 72.5 8Z" fill="#c0c8c0"/>'
    '<ellipse cx="72.5" cy="17" rx="4" ry="2" fill="#ffe066"/>'
    # 首（鱗）
    '<rect x="33" y="34" width="14" height="7" fill="#a85040" rx="2"/>'
    # 頭（ドラゴン肌）
    '<circle cx="40" cy="22" r="15" fill="#a85040"/>'
    # ドラゴンの角
    '<path d="M31 14 C27 4 22 0 24 8 C26 3 30 10 32 16Z" fill="#770000"/>'
    '<path d="M49 14 C53 4 58 0 56 8 C54 3 50 10 48 16Z" fill="#770000"/>'
    '<path d="M31 14 C29 6 25 3 27 9 C28 5 30 10 32 16Z" fill="#aa1100" opacity="0.6"/>'
    '<path d="M49 14 C51 6 55 3 53 9 C52 5 50 10 48 16Z" fill="#aa1100" opacity="0.6"/>'
    # スパイク赤髪
    '<ellipse cx="40" cy="11" rx="13" ry="8" fill="#cc2211"/>'
    '<polygon points="34,12 31,-2 36,10" fill="#dd3322"/>'
    '<polygon points="40,9 39,-3 44,8" fill="#ee4433"/>'
    '<polygon points="46,12 48,-2 52,11" fill="#cc2211"/>'
    # 目（縦長瞳孔・オレンジ）
    '<ellipse cx="33" cy="23" rx="4.5" ry="5" fill="white"/>'
    '<ellipse cx="47" cy="23" rx="4.5" ry="5" fill="white"/>'
    '<ellipse cx="33" cy="23" rx="3.5" ry="4" fill="#ff8811"/>'
    '<ellipse cx="47" cy="23" rx="3.5" ry="4" fill="#ff8811"/>'
    '<ellipse cx="33" cy="23" rx="1.2" ry="3.5" fill="#110000"/>'
    '<ellipse cx="47" cy="23" rx="1.2" ry="3.5" fill="#110000"/>'
    '<ellipse cx="33" cy="26" rx="3.5" ry="1.5" fill="#cc5500"/>'
    '<ellipse cx="47" cy="26" rx="3.5" ry="1.5" fill="#cc5500"/>'
    '<circle cx="30.5" cy="21" r="1.5" fill="white" opacity="0.8"/>'
    '<circle cx="44.5" cy="21" r="1.5" fill="white" opacity="0.8"/>'
    '<path d="M28 19 Q33 15 38 19" stroke="#330000" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M42 19 Q47 15 52 19" stroke="#330000" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 眉（怒り気味）
    '<path d="M28 14 Q33 11 37 14" stroke="#770000" stroke-width="3" fill="none" stroke-linecap="round" transform="rotate(6 33 14)"/>'
    '<path d="M43 14 Q47 11 52 14" stroke="#770000" stroke-width="3" fill="none" stroke-linecap="round" transform="rotate(-6 47 14)"/>'
    # 口（牙）
    '<path d="M34 30 Q40 35 46 30" stroke="#771100" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<rect x="38" y="30" width="2.5" height="5" fill="#f0eed8" rx="1"/>'
    '<rect x="41.5" y="30" width="2.5" height="5" fill="#f0eed8" rx="1"/>'
)

# ─────────────────────────────────────────
# 8. ルナ（闇魔法使い）- 黒/紫テーマ
# ─────────────────────────────────────────
_LUNA = _svg(
    # 魔法の粒子（背景）
    '<circle cx="12" cy="20" r="3" fill="#9933ff" opacity="0.4"/>'
    '<circle cx="8" cy="35" r="2" fill="#cc66ff" opacity="0.3"/>'
    '<circle cx="68" cy="25" r="3" fill="#9933ff" opacity="0.4"/>'
    '<circle cx="72" cy="40" r="2" fill="#cc66ff" opacity="0.3"/>'
    # 足
    '<rect x="29" y="74" width="10" height="18" fill="#1a0a2e" rx="2"/>'
    '<rect x="41" y="74" width="10" height="18" fill="#1a0a2e" rx="2"/>'
    '<rect x="27" y="82" width="14" height="10" fill="#110022" rx="2"/>'
    '<rect x="39" y="82" width="14" height="10" fill="#110022" rx="2"/>'
    # 黒いローブ（紫縁取り）
    '<rect x="18" y="40" width="44" height="35" fill="#1a0a2e" rx="5"/>'
    '<rect x="18" y="40" width="5" height="35" fill="#7722cc" rx="2"/>'
    '<rect x="57" y="40" width="5" height="35" fill="#7722cc" rx="2"/>'
    '<path d="M18 40 L40 34 L62 40 L62 47 L40 41 L18 47Z" fill="#2d1155"/>'
    '<path d="M18 64 L14 92 L32 78Z" fill="#110022"/>'
    '<path d="M62 64 L66 92 L48 78Z" fill="#110022"/>'
    # 三日月紋章
    '<circle cx="40" cy="55" r="7" fill="none" stroke="#9933ff" stroke-width="1.5"/>'
    '<circle cx="44" cy="53" r="6" fill="#1a0a2e"/>'
    '<circle cx="40" cy="48" r="3" fill="#9933ff" opacity="0.5"/>'
    # 腕
    '<rect x="5" y="42" width="14" height="9" fill="#1a0a2e" rx="3"/>'
    '<rect x="61" y="42" width="14" height="9" fill="#1a0a2e" rx="3"/>'
    # 両手の闇の球
    '<circle cx="7" cy="56" r="6" fill="#9933ff" opacity="0.3"/>'
    '<circle cx="7" cy="56" r="4" fill="#bb55ff" opacity="0.5"/>'
    '<circle cx="7" cy="56" r="2" fill="#cc88ff"/>'
    '<circle cx="73" cy="56" r="6" fill="#9933ff" opacity="0.3"/>'
    '<circle cx="73" cy="56" r="4" fill="#bb55ff" opacity="0.5"/>'
    '<circle cx="73" cy="56" r="2" fill="#cc88ff"/>'
    # 首
    '<rect x="34" y="35" width="12" height="7" fill="#e0c0e8" rx="2"/>'
    # 頭（青白い肌）
    '<circle cx="40" cy="22" r="15" fill="#e0c0e8"/>'
    # 白髪（長い）
    '<ellipse cx="40" cy="11" rx="13" ry="8" fill="#e8e0f8"/>'
    '<path d="M26 19 C23 11 25 4 29 7 C27 12 26 18 25 28 C24 38 22 50 20 58 L22 58 C24 50 26 38 27 28 C27 18 26 19 26 19Z" fill="#ddd8f0"/>'
    '<path d="M54 19 C57 11 55 4 51 7 C53 12 54 18 55 28 C56 38 58 50 60 58 L58 58 C56 50 54 38 53 28 C53 18 54 19 54 19Z" fill="#ddd8f0"/>'
    '<circle cx="30" cy="8" r="2" fill="#aa66ff" opacity="0.8"/>'
    '<circle cx="50" cy="8" r="2" fill="#aa66ff" opacity="0.8"/>'
    '<circle cx="24" cy="4" r="1.2" fill="#8844cc" opacity="0.6"/>'
    '<circle cx="56" cy="4" r="1.2" fill="#8844cc" opacity="0.6"/>'
    # 目（大・紫）
    '<ellipse cx="33" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="47" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="33" cy="24" rx="3.5" ry="4.5" fill="#8833cc"/>'
    '<ellipse cx="47" cy="24" rx="3.5" ry="4.5" fill="#8833cc"/>'
    '<ellipse cx="33" cy="26" rx="3.5" ry="2" fill="#5511aa"/>'
    '<ellipse cx="47" cy="26" rx="3.5" ry="2" fill="#5511aa"/>'
    '<ellipse cx="33" cy="24" rx="1.5" ry="2" fill="#110022"/>'
    '<ellipse cx="47" cy="24" rx="1.5" ry="2" fill="#110022"/>'
    '<circle cx="30.5" cy="21" r="1.8" fill="white"/>'
    '<circle cx="44.5" cy="21" r="1.8" fill="white"/>'
    # 半眼（ミステリアス）
    '<path d="M28 20 Q33 19.5 38 20" stroke="#1a0a2e" stroke-width="4" fill="none" stroke-linecap="round"/>'
    '<path d="M42 20 Q47 19.5 52 20" stroke="#1a0a2e" stroke-width="4" fill="none" stroke-linecap="round"/>'
    '<path d="M28 20 Q33 16.5 38 20" stroke="#331155" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M42 20 Q47 16.5 52 20" stroke="#331155" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 眉
    '<path d="M29 14 Q33 11 37 13" stroke="#6622aa" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M43 13 Q47 11 51 14" stroke="#6622aa" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 口
    '<path d="M36 30 Q40 33 44 30" stroke="#cc88ee" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
)

# ─────────────────────────────────────────
# 9. フィン（吟遊詩人）- オレンジテーマ
# ─────────────────────────────────────────
_FINN = _svg(
    # 足・ブーツ
    '<rect x="27" y="71" width="11" height="21" fill="#cc5500" rx="2"/>'
    '<rect x="42" y="71" width="11" height="21" fill="#cc5500" rx="2"/>'
    '<rect x="25" y="81" width="15" height="11" fill="#882200" rx="2"/>'
    '<rect x="40" y="81" width="15" height="11" fill="#882200" rx="2"/>'
    # 体（カラフルな詩人服）
    '<rect x="21" y="40" width="38" height="31" fill="#ff7722" rx="4"/>'
    '<path d="M21 40 L40 35 L59 40 L59 46 L40 41 L21 46Z" fill="#ffaa44"/>'
    '<rect x="21" y="50" width="38" height="5" fill="#ffcc44" rx="1"/>'
    '<rect x="21" y="58" width="38" height="4" fill="#ee6600" rx="1"/>'
    '<rect x="21" y="66" width="38" height="5" fill="#662200" rx="1"/>'
    '<rect x="35" y="64" width="10" height="8" fill="#ffe066" rx="2"/>'
    # 腕
    '<rect x="9" y="41" width="13" height="9" fill="#ff7722" rx="3"/>'
    '<rect x="58" y="41" width="13" height="9" fill="#ff7722" rx="3"/>'
    # リュート（右側）
    '<ellipse cx="66" cy="58" rx="9" ry="11" fill="#aa7733"/>'
    '<ellipse cx="66" cy="58" rx="7" ry="9" fill="#cc9944"/>'
    '<circle cx="66" cy="58" r="3" fill="#885522"/>'
    '<rect x="65" y="42" width="2" height="20" fill="#775533" rx="1"/>'
    '<line x1="63" y1="44" x2="66" y2="54" stroke="#ddc888" stroke-width="0.8"/>'
    '<line x1="65" y1="43" x2="66" y2="54" stroke="#ddc888" stroke-width="0.8"/>'
    '<line x1="67" y1="43" x2="66" y2="54" stroke="#ddc888" stroke-width="0.8"/>'
    '<line x1="69" y1="44" x2="66" y2="54" stroke="#ddc888" stroke-width="0.8"/>'
    # 首
    '<rect x="34" y="35" width="12" height="7" fill="#f0c07a" rx="2"/>'
    # 頭
    '<circle cx="40" cy="22" r="14" fill="#f0c07a"/>'
    # 赤オレンジの髪
    '<ellipse cx="40" cy="12" rx="13" ry="8" fill="#ee4411"/>'
    '<path d="M26 18 C24 11 27 4 31 8" stroke="#ee4411" stroke-width="5" fill="none" stroke-linecap="round"/>'
    '<path d="M54 18 C56 11 53 4 49 8" stroke="#dd3300" stroke-width="5" fill="none" stroke-linecap="round"/>'
    # 羽飾りの帽子
    '<ellipse cx="40" cy="14" rx="22" ry="7" fill="#882200"/>'
    '<ellipse cx="40" cy="13" rx="16" ry="9" fill="#aa3311"/>'
    '<path d="M52 8 C58 -2 64 -6 62 2 C60 -4 56 0 53 6 C57 0 60 -2 58 4 C56 2 54 6 52 10Z" fill="#3366cc"/>'
    '<path d="M52 10 C56 2 60 -2 58 4 C56 0 53 5 52 10Z" fill="#5588ff"/>'
    '<path d="M52 10 C54 4 58 2 57 7 C56 4 53 8 52 10Z" fill="#88aaff"/>'
    # 目（大・明るい茶色）
    '<ellipse cx="33" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="47" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="33" cy="24" rx="3.5" ry="4.5" fill="#bb6622"/>'
    '<ellipse cx="47" cy="24" rx="3.5" ry="4.5" fill="#bb6622"/>'
    '<ellipse cx="33" cy="26" rx="3.5" ry="2" fill="#884411"/>'
    '<ellipse cx="47" cy="26" rx="3.5" ry="2" fill="#884411"/>'
    '<ellipse cx="33" cy="24" rx="1.5" ry="2" fill="#110800"/>'
    '<ellipse cx="47" cy="24" rx="1.5" ry="2" fill="#110800"/>'
    '<circle cx="30.5" cy="21" r="1.8" fill="white"/>'
    '<circle cx="44.5" cy="21" r="1.8" fill="white"/>'
    '<path d="M28 19 Q33 15 38 19" stroke="#221100" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M42 19 Q47 15 52 19" stroke="#221100" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 眉
    '<path d="M27 14 Q33 10 39 13" stroke="#882200" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    '<path d="M41 13 Q47 10 53 14" stroke="#882200" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    # 大きな笑顔
    '<path d="M34 30 Q40 36 46 30" stroke="#cc6633" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    # 頬紅
    '<circle cx="27" cy="27" r="5" fill="#ff6633" opacity="0.3"/>'
    '<circle cx="53" cy="27" r="5" fill="#ff6633" opacity="0.3"/>'
)

# ─────────────────────────────────────────
# 10. セラ（精霊使い）- 水色テーマ
# ─────────────────────────────────────────
_SERA = _svg(
    # 妖精の羽（透明感）
    '<ellipse cx="18" cy="50" rx="14" ry="22" fill="#88eeff" opacity="0.25" transform="rotate(-20 18 50)"/>'
    '<ellipse cx="18" cy="50" rx="10" ry="16" fill="#aaeeff" opacity="0.2" transform="rotate(-20 18 50)"/>'
    '<ellipse cx="62" cy="50" rx="14" ry="22" fill="#88eeff" opacity="0.25" transform="rotate(20 62 50)"/>'
    '<ellipse cx="62" cy="50" rx="10" ry="16" fill="#aaeeff" opacity="0.2" transform="rotate(20 62 50)"/>'
    '<ellipse cx="14" cy="44" rx="6" ry="12" fill="none" stroke="#66ccff" stroke-width="1.5" opacity="0.5" transform="rotate(-20 14 44)"/>'
    '<ellipse cx="66" cy="44" rx="6" ry="12" fill="none" stroke="#66ccff" stroke-width="1.5" opacity="0.5" transform="rotate(20 66 44)"/>'
    # 精霊の光
    '<circle cx="10" cy="28" r="4" fill="#88ffee" opacity="0.5"/>'
    '<circle cx="10" cy="28" r="2.5" fill="#aafff0" opacity="0.7"/>'
    '<circle cx="10" cy="28" r="1" fill="white"/>'
    '<circle cx="70" cy="32" r="3.5" fill="#88ffcc" opacity="0.5"/>'
    '<circle cx="70" cy="32" r="2" fill="#aaffd8" opacity="0.7"/>'
    '<circle cx="70" cy="32" r="1" fill="white"/>'
    # 足・ブーツ
    '<rect x="28" y="74" width="10" height="18" fill="#88ccee" rx="2"/>'
    '<rect x="42" y="74" width="10" height="18" fill="#88ccee" rx="2"/>'
    '<rect x="26" y="82" width="14" height="10" fill="#5599bb" rx="2"/>'
    '<rect x="40" y="82" width="14" height="10" fill="#5599bb" rx="2"/>'
    # 水色のドレス
    '<rect x="19" y="41" width="42" height="34" fill="#88ccee" rx="5"/>'
    '<path d="M19 64 L15 92 L34 78Z" fill="#77bbdd"/>'
    '<path d="M61 64 L65 92 L46 78Z" fill="#77bbdd"/>'
    '<path d="M19 41 L40 35 L61 41 L61 48 L40 42 L19 48Z" fill="#aadeee"/>'
    '<circle cx="30" cy="54" r="4" fill="#66bbdd" opacity="0.5"/>'
    '<circle cx="50" cy="54" r="4" fill="#66bbdd" opacity="0.5"/>'
    '<circle cx="40" cy="60" r="3.5" fill="#55aacc" opacity="0.5"/>'
    # 腕
    '<rect x="6" y="42" width="14" height="9" fill="#88ccee" rx="3"/>'
    '<rect x="60" y="42" width="14" height="9" fill="#88ccee" rx="3"/>'
    # 首
    '<rect x="34" y="35" width="12" height="8" fill="#f5d0b8" rx="2"/>'
    # 頭
    '<circle cx="40" cy="22" r="15" fill="#f5d0b8"/>'
    # ミントグリーンの髪
    '<ellipse cx="40" cy="11" rx="14" ry="9" fill="#77cc99"/>'
    '<path d="M25 20 C23 12 26 5 30 8" stroke="#77cc99" stroke-width="6" fill="none" stroke-linecap="round"/>'
    '<path d="M55 20 C57 12 54 5 50 8" stroke="#66bb88" stroke-width="6" fill="none" stroke-linecap="round"/>'
    # 花冠
    '<circle cx="32" cy="11" r="3.5" fill="#ff88aa"/>'
    '<circle cx="39" cy="8" r="3.5" fill="#ffaa44"/>'
    '<circle cx="46" cy="9" r="3.5" fill="#ff88cc"/>'
    '<circle cx="53" cy="12" r="3" fill="#ff7799"/>'
    '<circle cx="32" cy="11" r="2" fill="#ffffaa"/>'
    '<circle cx="39" cy="8" r="2" fill="#ffffff"/>'
    '<circle cx="46" cy="9" r="2" fill="#ffeecc"/>'
    '<circle cx="53" cy="12" r="1.7" fill="#ffddcc"/>'
    '<ellipse cx="25" cy="17" rx="5" ry="3" fill="#77cc99" opacity="0.6" transform="rotate(-30 25 17)"/>'
    '<ellipse cx="55" cy="17" rx="5" ry="3" fill="#66bb88" opacity="0.6" transform="rotate(30 55 17)"/>'
    # 目（大・アクア）
    '<ellipse cx="33" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="47" cy="23" rx="4.5" ry="5.5" fill="white"/>'
    '<ellipse cx="33" cy="24" rx="3.5" ry="4.5" fill="#22aacc"/>'
    '<ellipse cx="47" cy="24" rx="3.5" ry="4.5" fill="#22aacc"/>'
    '<ellipse cx="33" cy="26" rx="3.5" ry="2" fill="#117799"/>'
    '<ellipse cx="47" cy="26" rx="3.5" ry="2" fill="#117799"/>'
    '<ellipse cx="33" cy="24" rx="1.5" ry="2" fill="#040f14"/>'
    '<ellipse cx="47" cy="24" rx="1.5" ry="2" fill="#040f14"/>'
    '<circle cx="30.5" cy="21" r="1.8" fill="white"/>'
    '<circle cx="44.5" cy="21" r="1.8" fill="white"/>'
    '<path d="M28 19 Q33 15 38 19" stroke="#112233" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M42 19 Q47 15 52 19" stroke="#112233" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 眉
    '<path d="M28 14 Q33 11 38 14" stroke="#448866" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M42 14 Q47 11 52 14" stroke="#448866" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 口
    '<path d="M35 30 Q40 35 45 30" stroke="#cc8877" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 頬
    '<circle cx="27" cy="27" r="4" fill="#88ccff" opacity="0.4"/>'
    '<circle cx="53" cy="27" r="4" fill="#88ccff" opacity="0.4"/>'
)


CHARACTERS: dict[str, dict] = {
    "allen": {
        "id": "allen",
        "name": "アレン",
        "title": "勇者",
        "story": "辺境の村で生まれた若者。剣と盾で世界を守る王道の主人公。バランス型でどんな状況にも冷静に対応できる。",
        "color": "#1a4fcc",
        "svg": _ALLEN,
    },
    "liria": {
        "id": "liria",
        "name": "リリア",
        "title": "魔法使い",
        "story": "古の魔法書を読み解いた天才少女。知識こそが最強の武器と信じ、言葉の魔法で英知の扉を開く。",
        "color": "#7733dd",
        "svg": _LIRIA,
    },
    "gares": {
        "id": "gares",
        "name": "ガレス",
        "title": "騎士",
        "story": "王国騎士団の重鎮。重装備の守り手として仲間を守り抜く。不屈の意志と鋼の盾が彼の誇り。",
        "color": "#aabbcc",
        "svg": _GARES,
    },
    "shia": {
        "id": "shia",
        "name": "シア",
        "title": "盗賊",
        "story": "影に生きる素早き者。正確無比な短剣さばきで難題を切り抜ける。誰よりも鋭く、誰よりも速い。",
        "color": "#3d6e2d",
        "svg": _SHIA,
    },
    "erwin": {
        "id": "erwin",
        "name": "エルウィン",
        "title": "弓使い",
        "story": "遠距離から冷静に的を射る銀髪の射手。感情を乱さず、どんな難問も精密に攻略する。",
        "color": "#8b6240",
        "svg": _ERWIN,
    },
    "noah": {
        "id": "noah",
        "name": "ノア",
        "title": "僧侶",
        "story": "回復と支援の達人。仲間の挫けそうな心を癒し、どんな困難も乗り越えさせる光の体現者。",
        "color": "#ffe066",
        "svg": _NOAH,
    },
    "drake": {
        "id": "drake",
        "name": "ドラク",
        "title": "ドラゴン戦士",
        "story": "半竜の血を引く孤高の戦士。強靭な鱗と炎の意志で英単語の試練に真正面から挑む。",
        "color": "#cc2211",
        "svg": _DRAKE,
    },
    "luna": {
        "id": "luna",
        "name": "ルナ",
        "title": "闇魔法使い",
        "story": "謎めいた力を操る月の魔法使い。暗闇から星の言葉を呼び起こし、未知の英知を解き明かす。",
        "color": "#7722cc",
        "svg": _LUNA,
    },
    "finn": {
        "id": "finn",
        "name": "フィン",
        "title": "吟遊詩人",
        "story": "言葉と音楽で世界を旅する詩人。英語の韻律を奏でながら、言葉の力で敵を魅了し打ち破る。",
        "color": "#ff7722",
        "svg": _FINN,
    },
    "sera": {
        "id": "sera",
        "name": "セラ",
        "title": "精霊使い",
        "story": "自然と共に生きる精霊の使い手。花と風が語りかける声を英知に変え、世界と調和しながら戦う。",
        "color": "#88ccee",
        "svg": _SERA,
    },
}


def get_character(char_id: str | None) -> dict:
    if not char_id or char_id not in CHARACTERS:
        return CHARACTERS["allen"]
    return CHARACTERS[char_id]


def sidebar_avatar_html(char_id: str | None, equipment: dict | None = None) -> str:
    if not char_id or char_id not in CHARACTERS:
        return '<div style="font-size:3rem;text-align:center;line-height:1;">⚔️</div>'
    c = CHARACTERS[char_id]
    # SVG内側コンテンツを取り出して帽子オーバーレイを適用
    svg_full = c["svg"]
    tag_end = svg_full.index('>') + 1
    close_start = svg_full.rindex('</')
    svg_inner = svg_full[tag_end:close_start]
    if equipment:
        from core.equipment import apply_hat_overlay, apply_ring_overlay, apply_necklace_overlay, equipment_badges_html
        svg_inner = apply_hat_overlay(svg_inner, equipment.get("hat"))
        svg_inner = apply_ring_overlay(svg_inner, equipment.get("ring"))
        svg_inner = apply_necklace_overlay(svg_inner, equipment.get("necklace"))
        badges = equipment_badges_html(equipment)
    else:
        badges = ""
    svg_with_overlay = '<svg viewBox="0 0 80 100" xmlns="http://www.w3.org/2000/svg">' + svg_inner + '</svg>'
    return (
        '<div style="width:70px;height:88px;margin:0 auto;overflow:hidden;">' + svg_with_overlay + '</div>'
        '<div style="font-size:.72rem;color:#aa88ff;text-align:center;margin-top:2px;">' + c["title"] + '</div>'
        + badges
    )
