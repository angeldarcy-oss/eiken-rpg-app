"""core/characters.py — キャラクター定義（10種類）"""

from __future__ import annotations

CHARACTER_ORDER = [
    "allen", "liria", "gares", "shia", "erwin",
    "noah", "drake", "luna", "finn", "sera",
]

def _svg(inner: str) -> str:
    return '<svg viewBox="0 0 80 100" xmlns="http://www.w3.org/2000/svg">' + inner + '</svg>'


# ─────────────────────────────────────────
# 1. アレン（勇者）- 赤い鎧、金髪、剣と盾
# ─────────────────────────────────────────
_ALLEN = _svg(
    # 足・ブーツ
    '<rect x="27" y="71" width="11" height="23" fill="#3355aa" rx="2"/>'
    '<rect x="42" y="71" width="11" height="23" fill="#3355aa" rx="2"/>'
    '<rect x="26" y="82" width="13" height="12" fill="#221100" rx="2"/>'
    '<rect x="41" y="82" width="13" height="12" fill="#221100" rx="2"/>'
    # マント
    '<path d="M22 47 L7 96 L26 79Z" fill="#aa2200"/>'
    '<path d="M58 47 L73 96 L54 79Z" fill="#aa2200"/>'
    # 体（赤い鎧）
    '<rect x="21" y="42" width="38" height="31" fill="#cc3333" rx="4"/>'
    '<rect x="31" y="42" width="18" height="5" fill="#aa2222" rx="1"/>'
    '<polygon points="40,48 44,57 40,54 36,57" fill="#ffe066"/>'
    # 腕
    '<rect x="8" y="43" width="14" height="9" fill="#cc3333" rx="3"/>'
    '<rect x="58" y="43" width="14" height="9" fill="#cc3333" rx="3"/>'
    # 盾（左）
    '<rect x="2" y="49" width="12" height="18" fill="#2244bb" rx="2"/>'
    '<rect x="4" y="51" width="8" height="14" fill="#3366cc" rx="1"/>'
    '<circle cx="8" cy="58" r="3" fill="#ffe066" opacity="0.6"/>'
    # 剣（右）
    '<rect x="68" y="14" width="4" height="37" fill="#dddddd" rx="1"/>'
    '<rect x="62" y="28" width="16" height="4" fill="#886600" rx="1"/>'
    '<polygon points="70,4 73,18 67,18" fill="#eeeeee"/>'
    # 首
    '<rect x="33" y="36" width="14" height="8" fill="#f0c07a" rx="2"/>'
    # 頭
    '<circle cx="40" cy="23" r="14" fill="#f0c07a"/>'
    # 金色の髪（上向きスパイク）
    '<ellipse cx="40" cy="12" rx="11" ry="7" fill="#ffdd22"/>'
    '<rect x="36" y="3" width="3" height="8" fill="#ffdd22" rx="1" transform="rotate(-10 37 7)"/>'
    '<rect x="40" y="2" width="3" height="9" fill="#ffdd22" rx="1"/>'
    '<rect x="43" y="3" width="3" height="8" fill="#ffdd22" rx="1" transform="rotate(10 44 7)"/>'
    '<path d="M28 20 C25 11 31 6 37 9 C33 13 29 17 28 20Z" fill="#ffdd22"/>'
    '<path d="M52 20 C55 11 49 6 43 9 C47 13 51 17 52 20Z" fill="#ffdd22"/>'
    # 目（青）
    '<ellipse cx="35" cy="23" rx="3" ry="2.5" fill="#2244aa"/>'
    '<ellipse cx="45" cy="23" rx="3" ry="2.5" fill="#2244aa"/>'
    '<circle cx="36" cy="22" r="1" fill="#fff"/>'
    '<circle cx="46" cy="22" r="1" fill="#fff"/>'
    # 眉
    '<path d="M32 18 Q35 16 38 18" stroke="#886600" stroke-width="1.5" fill="none"/>'
    '<path d="M42 18 Q45 16 48 18" stroke="#886600" stroke-width="1.5" fill="none"/>'
    # 口（微笑み）
    '<path d="M37 29 Q40 32 43 29" stroke="#cc8855" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
)

# ─────────────────────────────────────────
# 2. リリア（魔法使い）- 紫の尖り帽子、杖
# ─────────────────────────────────────────
_LIRIA = _svg(
    # 足・靴
    '<rect x="29" y="76" width="10" height="18" fill="#5533aa" rx="2"/>'
    '<rect x="41" y="76" width="10" height="18" fill="#5533aa" rx="2"/>'
    '<rect x="28" y="84" width="12" height="10" fill="#221133" rx="2"/>'
    '<rect x="40" y="84" width="12" height="10" fill="#221133" rx="2"/>'
    # ローブ（長い）
    '<rect x="19" y="42" width="42" height="36" fill="#7744cc" rx="5"/>'
    '<path d="M19 60 L15 94 L35 80Z" fill="#6633bb"/>'
    '<path d="M61 60 L65 94 L45 80Z" fill="#6633bb"/>'
    # ローブ装飾
    '<rect x="34" y="42" width="12" height="4" fill="#9966ee" rx="2"/>'
    '<path d="M33 56 Q40 62 47 56" stroke="#bb88ff" stroke-width="1.5" fill="none"/>'
    # 腕
    '<rect x="7" y="43" width="13" height="8" fill="#7744cc" rx="3"/>'
    '<rect x="60" y="43" width="13" height="8" fill="#7744cc" rx="3"/>'
    # 魔法の杖（左）星型
    '<rect x="5" y="32" width="3" height="30" fill="#886644" rx="1"/>'
    '<circle cx="6" cy="28" r="6" fill="#aa77ff" opacity="0.3"/>'
    '<circle cx="6" cy="28" r="4" fill="#cc99ff"/>'
    '<circle cx="6" cy="28" r="2" fill="#ffffff"/>'
    # 首
    '<rect x="34" y="36" width="12" height="8" fill="#f0c0e0" rx="2"/>'
    # 頭
    '<circle cx="40" cy="23" r="14" fill="#f0c0e0"/>'
    # 銀紫の長髪（両サイド）
    '<path d="M27 20 C24 14 26 8 30 8 C28 14 27 20 26 34 C24 38 22 42 21 50 C22 40 24 28 27 20Z" fill="#ccbbee"/>'
    '<path d="M53 20 C56 14 54 8 50 8 C52 14 53 20 54 34 C56 38 58 42 59 50 C58 40 56 28 53 20Z" fill="#ccbbee"/>'
    # 尖り帽子（大きく上へ）
    '<polygon points="40,-4 26,27 54,27" fill="#7744cc"/>'
    '<polygon points="40,-4 30,15 50,15" fill="#9955dd"/>'
    '<rect x="24" y="26" width="32" height="5" fill="#5533aa" rx="2"/>'
    # 目（紫）
    '<ellipse cx="35" cy="23" rx="2.5" ry="2" fill="#663399"/>'
    '<ellipse cx="45" cy="23" rx="2.5" ry="2" fill="#663399"/>'
    '<circle cx="36" cy="22" r="0.8" fill="#fff"/>'
    '<circle cx="46" cy="22" r="0.8" fill="#fff"/>'
    # 眉
    '<path d="M33 18 Q35 17 37 18" stroke="#553388" stroke-width="1.2" fill="none"/>'
    '<path d="M43 18 Q45 17 47 18" stroke="#553388" stroke-width="1.2" fill="none"/>'
    # 口
    '<path d="M37 29 Q40 31 43 29" stroke="#cc88bb" stroke-width="1.2" fill="none" stroke-linecap="round"/>'
)

# ─────────────────────────────────────────
# 3. ガレス（騎士）- 銀の鎧、青い盾
# ─────────────────────────────────────────
_GARES = _svg(
    # 足・グリーブ
    '<rect x="27" y="71" width="11" height="23" fill="#8899bb" rx="2"/>'
    '<rect x="42" y="71" width="11" height="23" fill="#8899bb" rx="2"/>'
    '<rect x="26" y="80" width="13" height="14" fill="#778899" rx="2"/>'
    '<rect x="41" y="80" width="13" height="14" fill="#778899" rx="2"/>'
    # 体（重厚な鎧）
    '<rect x="18" y="40" width="44" height="33" fill="#aabbcc" rx="4"/>'
    '<rect x="26" y="40" width="28" height="6" fill="#99aacc" rx="2"/>'
    '<rect x="30" y="46" width="20" height="3" fill="#778899"/>'
    # 胸の紋章
    '<polygon points="40,50 44,58 40,55 36,58" fill="#2255cc"/>'
    # 腕（プレートアーマー）
    '<rect x="6" y="41" width="13" height="11" fill="#aabbcc" rx="3"/>'
    '<rect x="61" y="41" width="13" height="11" fill="#aabbcc" rx="3"/>'
    # 大きな盾（左）
    '<rect x="-2" y="46" width="16" height="24" fill="#2244aa" rx="3"/>'
    '<polygon points="6,49 14,49 14,65 6,70 -2,65 -2,49" fill="#3355bb"/>'
    '<polygon points="6,52 11,58 6,64 1,58" fill="#ffe066" opacity="0.7"/>'
    # 槍（右）
    '<rect x="70" y="8" width="4" height="60" fill="#aaaaaa" rx="1"/>'
    '<polygon points="72,-2 75,12 69,12" fill="#cccccc"/>'
    '<rect x="68" y="28" width="8" height="3" fill="#886600" rx="1"/>'
    # 首（兜のカバー）
    '<rect x="31" y="35" width="18" height="8" fill="#aabbcc" rx="2"/>'
    # 頭（兜）
    '<ellipse cx="40" cy="24" rx="16" ry="14" fill="#aabbcc"/>'
    '<rect x="24" y="26" width="32" height="10" fill="#99aacc" rx="1"/>'
    # 目のスリット
    '<rect x="30" y="27" width="8" height="4" fill="#112244" rx="1"/>'
    '<rect x="42" y="27" width="8" height="4" fill="#112244" rx="1"/>'
    '<rect x="31" y="28" width="6" height="2" fill="#4477cc" rx="1"/>'
    '<rect x="43" y="28" width="6" height="2" fill="#4477cc" rx="1"/>'
    # 青いプルーム（羽飾り）
    '<path d="M40 10 C38 0 34 -4 36 2 C38-2 40 4 40 10Z" fill="#3366cc"/>'
    '<path d="M40 10 C42 0 46 -4 44 2 C42-2 40 4 40 10Z" fill="#5588ee"/>'
    '<path d="M40 10 C36 2 30 -2 33 4 C36 0 38 5 40 10Z" fill="#2255bb"/>'
)

# ─────────────────────────────────────────
# 4. シア（盗賊）- 暗緑のフード、短剣
# ─────────────────────────────────────────
_SHIA = _svg(
    # 足・靴
    '<rect x="28" y="72" width="10" height="22" fill="#334422" rx="2"/>'
    '<rect x="42" y="72" width="10" height="22" fill="#334422" rx="2"/>'
    '<rect x="27" y="82" width="12" height="12" fill="#1a1100" rx="2"/>'
    '<rect x="41" y="82" width="12" height="12" fill="#1a1100" rx="2"/>'
    # 体（革鎧）
    '<rect x="22" y="42" width="36" height="32" fill="#554422" rx="4"/>'
    '<rect x="30" y="42" width="20" height="4" fill="#443311" rx="1"/>'
    # ベルト
    '<rect x="22" y="61" width="36" height="5" fill="#332211" rx="1"/>'
    '<rect x="36" y="60" width="8" height="7" fill="#775533" rx="1"/>'
    # 腕
    '<rect x="10" y="43" width="13" height="8" fill="#554422" rx="3"/>'
    '<rect x="57" y="43" width="13" height="8" fill="#554422" rx="3"/>'
    # 短剣（腰に）
    '<rect x="14" y="59" width="3" height="14" fill="#aaaaaa" rx="1" transform="rotate(-20 15 65)"/>'
    '<rect x="12" y="62" width="7" height="2" fill="#663300" rx="1" transform="rotate(-20 15 65)"/>'
    '<rect x="58" y="59" width="3" height="14" fill="#aaaaaa" rx="1" transform="rotate(20 60 65)"/>'
    '<rect x="55" y="62" width="7" height="2" fill="#663300" rx="1" transform="rotate(20 60 65)"/>'
    # 首（フードで隠れる）
    '<rect x="33" y="35" width="14" height="9" fill="#c4884a" rx="2"/>'
    # 頭（フード）
    '<circle cx="40" cy="24" r="14" fill="#c4884a"/>'
    # 暗緑のフード
    '<ellipse cx="40" cy="17" rx="17" ry="12" fill="#335522"/>'
    '<path d="M23 24 C22 16 28 10 40 8 C52 10 58 16 57 24 C54 18 46 14 40 14 C34 14 26 18 23 24Z" fill="#446633"/>'
    '<path d="M23 24 C24 34 26 42 22 46 C20 40 20 32 23 24Z" fill="#335522"/>'
    '<path d="M57 24 C56 34 54 42 58 46 C60 40 60 32 57 24Z" fill="#335522"/>'
    # 目（鋭い）
    '<ellipse cx="35" cy="25" rx="2.5" ry="2" fill="#336611"/>'
    '<ellipse cx="45" cy="25" rx="2.5" ry="2" fill="#336611"/>'
    '<circle cx="36" cy="24" r="0.8" fill="#fff"/>'
    '<circle cx="46" cy="24" r="0.8" fill="#fff"/>'
    # 口（ニヤリ）
    '<path d="M36 31 Q40 30 44 31" stroke="#cc8855" stroke-width="1.2" fill="none"/>'
    '<path d="M36 31 Q36 33 37 31" stroke="#cc8855" stroke-width="1" fill="none"/>'
)

# ─────────────────────────────────────────
# 5. エルウィン（弓使い）- 銀髪、青緑の服、弓
# ─────────────────────────────────────────
_ERWIN = _svg(
    # 足・靴
    '<rect x="28" y="72" width="10" height="22" fill="#335544" rx="2"/>'
    '<rect x="42" y="72" width="10" height="22" fill="#335544" rx="2"/>'
    '<rect x="27" y="82" width="12" height="12" fill="#442211" rx="2"/>'
    '<rect x="41" y="82" width="12" height="12" fill="#442211" rx="2"/>'
    # 体（青緑のチュニック）
    '<rect x="22" y="42" width="36" height="32" fill="#227766" rx="4"/>'
    '<rect x="30" y="42" width="20" height="4" fill="#115544" rx="1"/>'
    # クローク的装飾
    '<path d="M22 50 L18 75 L28 65Z" fill="#115544" opacity="0.7"/>'
    # 腕
    '<rect x="10" y="43" width="13" height="8" fill="#227766" rx="3"/>'
    '<rect x="57" y="43" width="13" height="8" fill="#227766" rx="3"/>'
    # 弓（右側、曲線）
    '<path d="M70 18 C78 30 78 50 70 62" stroke="#886644" stroke-width="3" fill="none" stroke-linecap="round"/>'
    '<line x1="70" y1="18" x2="70" y2="62" stroke="#aaaaaa" stroke-width="1" stroke-dasharray="2,2"/>'
    # 矢
    '<line x1="62" y1="40" x2="78" y2="40" stroke="#886644" stroke-width="1.5"/>'
    '<polygon points="78,40 74,38 74,42" fill="#886644"/>'
    # 首
    '<rect x="34" y="36" width="12" height="8" fill="#e8d0a0" rx="2"/>'
    # 頭
    '<circle cx="40" cy="24" r="14" fill="#e8d0a0"/>'
    # 銀白色の長髪
    '<path d="M27 20 C24 13 26 6 30 8 C28 13 27 20 26 36 C25 44 24 52 22 58 L24 58 C26 52 27 44 28 36 C27 20 27 20 27 20Z" fill="#dde8f0"/>'
    '<path d="M53 20 C56 13 54 6 50 8 C52 13 53 20 54 36 C55 44 56 52 58 58 L56 58 C54 52 53 44 52 36 C53 20 53 20 53 20Z" fill="#dde8f0"/>'
    '<ellipse cx="40" cy="13" rx="11" ry="7" fill="#dde8f0"/>'
    # 目（灰青）
    '<ellipse cx="35" cy="24" rx="2.5" ry="2" fill="#5577aa"/>'
    '<ellipse cx="45" cy="24" rx="2.5" ry="2" fill="#5577aa"/>'
    '<circle cx="36" cy="23" r="0.8" fill="#fff"/>'
    '<circle cx="46" cy="23" r="0.8" fill="#fff"/>'
    # 眉（細い）
    '<path d="M33 19 Q35 18 37 19" stroke="#aaaaaa" stroke-width="1.2" fill="none"/>'
    '<path d="M43 19 Q45 18 47 19" stroke="#aaaaaa" stroke-width="1.2" fill="none"/>'
    # 口（冷静）
    '<line x1="37" y1="30" x2="43" y2="30" stroke="#cc9966" stroke-width="1.2" stroke-linecap="round"/>'
)

# ─────────────────────────────────────────
# 6. ノア（僧侶）- 白いローブ、回復のオーブ
# ─────────────────────────────────────────
_NOAH = _svg(
    # 足・靴
    '<rect x="28" y="76" width="10" height="18" fill="#ddd8c0" rx="2"/>'
    '<rect x="42" y="76" width="10" height="18" fill="#ddd8c0" rx="2"/>'
    '<rect x="27" y="84" width="12" height="10" fill="#998855" rx="2"/>'
    '<rect x="41" y="84" width="12" height="10" fill="#998855" rx="2"/>'
    # 白いローブ（長い）
    '<rect x="19" y="41" width="42" height="37" fill="#eeeecc" rx="5"/>'
    '<path d="M19 60 L17 94 L34 78Z" fill="#e8e8c0"/>'
    '<path d="M61 60 L63 94 L46 78Z" fill="#e8e8c0"/>'
    # ローブの金の縁取り
    '<rect x="33" y="41" width="14" height="4" fill="#ddcc88" rx="2"/>'
    '<rect x="19" y="41" width="4" height="37" fill="#ddcc88" rx="2"/>'
    '<rect x="57" y="41" width="4" height="37" fill="#ddcc88" rx="2"/>'
    # 胸の十字
    '<rect x="38" y="48" width="4" height="12" fill="#ffe066" rx="1"/>'
    '<rect x="34" y="53" width="12" height="4" fill="#ffe066" rx="1"/>'
    # 腕
    '<rect x="7" y="42" width="13" height="8" fill="#eeeecc" rx="3"/>'
    '<rect x="60" y="42" width="13" height="8" fill="#eeeecc" rx="3"/>'
    # 回復のオーブ（左手に輝く）
    '<circle cx="8" cy="56" r="7" fill="#ffe066" opacity="0.3"/>'
    '<circle cx="8" cy="56" r="5" fill="#ffe066" opacity="0.5"/>'
    '<circle cx="8" cy="56" r="3" fill="#ffffff"/>'
    '<circle cx="8" cy="56" r="1.5" fill="#ffee88"/>'
    # 首
    '<rect x="34" y="36" width="12" height="7" fill="#f0c07a" rx="2"/>'
    # 頭
    '<circle cx="40" cy="24" r="14" fill="#f0c07a"/>'
    # 温かみのある金髪
    '<ellipse cx="40" cy="13" rx="12" ry="8" fill="#ddcc66"/>'
    '<path d="M28 20 C26 12 30 6 34 9 C30 13 28 18 28 20Z" fill="#ddcc66"/>'
    '<path d="M52 20 C54 12 50 6 46 9 C50 13 52 18 52 20Z" fill="#ddcc66"/>'
    # 目（温かい茶色）
    '<ellipse cx="35" cy="24" rx="2.5" ry="2" fill="#885522"/>'
    '<ellipse cx="45" cy="24" rx="2.5" ry="2" fill="#885522"/>'
    '<circle cx="36" cy="23" r="0.8" fill="#fff"/>'
    '<circle cx="46" cy="23" r="0.8" fill="#fff"/>'
    # 眉（優しい曲線）
    '<path d="M33 19 Q35 17 37 19" stroke="#885522" stroke-width="1.2" fill="none"/>'
    '<path d="M43 19 Q45 17 47 19" stroke="#885522" stroke-width="1.2" fill="none"/>'
    # 口（優しい微笑み）
    '<path d="M36 29 Q40 33 44 29" stroke="#cc8855" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
)

# ─────────────────────────────────────────
# 7. ドラク（ドラゴン戦士）- 角、鱗の鎧、尻尾
# ─────────────────────────────────────────
_DRAKE = _svg(
    # 尻尾
    '<path d="M58 74 C68 70 76 80 72 90 C68 96 62 94 58 88" stroke="#2d6e22" stroke-width="6" fill="none" stroke-linecap="round"/>'
    # 足・爪
    '<rect x="27" y="71" width="11" height="23" fill="#336622" rx="2"/>'
    '<rect x="42" y="71" width="11" height="23" fill="#336622" rx="2"/>'
    '<polygon points="27,94 29,100 31,94" fill="#224411"/>'
    '<polygon points="33,94 35,100 37,94" fill="#224411"/>'
    '<polygon points="43,94 45,100 47,94" fill="#224411"/>'
    '<polygon points="49,94 51,100 53,94" fill="#224411"/>'
    # 体（鱗の鎧）
    '<rect x="20" y="41" width="40" height="32" fill="#2d6e22" rx="4"/>'
    # 鱗模様
    '<ellipse cx="28" cy="48" rx="5" ry="3" fill="#224411" opacity="0.6"/>'
    '<ellipse cx="36" cy="48" rx="5" ry="3" fill="#224411" opacity="0.6"/>'
    '<ellipse cx="44" cy="48" rx="5" ry="3" fill="#224411" opacity="0.6"/>'
    '<ellipse cx="52" cy="48" rx="5" ry="3" fill="#224411" opacity="0.6"/>'
    '<ellipse cx="32" cy="55" rx="5" ry="3" fill="#224411" opacity="0.6"/>'
    '<ellipse cx="40" cy="55" rx="5" ry="3" fill="#224411" opacity="0.6"/>'
    '<ellipse cx="48" cy="55" rx="5" ry="3" fill="#224411" opacity="0.6"/>'
    '<ellipse cx="28" cy="62" rx="5" ry="3" fill="#224411" opacity="0.5"/>'
    '<ellipse cx="36" cy="62" rx="5" ry="3" fill="#224411" opacity="0.5"/>'
    '<ellipse cx="44" cy="62" rx="5" ry="3" fill="#224411" opacity="0.5"/>'
    '<ellipse cx="52" cy="62" rx="5" ry="3" fill="#224411" opacity="0.5"/>'
    # 腕（爪付き）
    '<rect x="8" y="42" width="13" height="10" fill="#2d6e22" rx="3"/>'
    '<rect x="59" y="42" width="13" height="10" fill="#2d6e22" rx="3"/>'
    '<polygon points="8,52 10,58 12,52" fill="#224411"/>'
    '<polygon points="13,52 15,58 17,52" fill="#224411"/>'
    # 首（鱗）
    '<rect x="33" y="35" width="14" height="8" fill="#3d8e32" rx="2"/>'
    # 頭（緑がかった肌）
    '<circle cx="40" cy="23" r="14" fill="#5da84a"/>'
    # ドラゴンの角（2本）
    '<path d="M33 14 C30 6 26 2 28 8 C30 4 34 10 34 16Z" fill="#2a5020"/>'
    '<path d="M47 14 C50 6 54 2 52 8 C50 4 46 10 46 16Z" fill="#2a5020"/>'
    # 頭部の鱗
    '<ellipse cx="35" cy="18" rx="4" ry="2" fill="#3d8020" opacity="0.5"/>'
    '<ellipse cx="45" cy="18" rx="4" ry="2" fill="#3d8020" opacity="0.5"/>'
    # 目（縦長の瞳孔・ドラゴン目）
    '<ellipse cx="35" cy="23" rx="3" ry="3" fill="#dd6600"/>'
    '<ellipse cx="45" cy="23" rx="3" ry="3" fill="#dd6600"/>'
    '<ellipse cx="35" cy="23" rx="1" ry="2.5" fill="#221100"/>'
    '<ellipse cx="45" cy="23" rx="1" ry="2.5" fill="#221100"/>'
    '<circle cx="35.5" cy="22" r="0.7" fill="#fff" opacity="0.5"/>'
    '<circle cx="45.5" cy="22" r="0.7" fill="#fff" opacity="0.5"/>'
    # 鼻孔
    '<circle cx="38" cy="27" r="1" fill="#3a6030"/>'
    '<circle cx="42" cy="27" r="1" fill="#3a6030"/>'
    # 口（牙あり）
    '<path d="M35 31 Q40 35 45 31" stroke="#2a5020" stroke-width="2" fill="none"/>'
    '<rect x="38" y="31" width="2" height="4" fill="#f0f0e0" rx="1"/>'
    '<rect x="42" y="31" width="2" height="4" fill="#f0f0e0" rx="1"/>'
)

# ─────────────────────────────────────────
# 8. ルナ（闇魔法使い）- 黒いローブ、紫の月
# ─────────────────────────────────────────
_LUNA = _svg(
    # 足・靴
    '<rect x="29" y="76" width="10" height="18" fill="#221133" rx="2"/>'
    '<rect x="41" y="76" width="10" height="18" fill="#221133" rx="2"/>'
    '<rect x="28" y="84" width="12" height="10" fill="#110022" rx="2"/>'
    '<rect x="40" y="84" width="12" height="10" fill="#110022" rx="2"/>'
    # 黒いローブ（紫の縁）
    '<rect x="18" y="41" width="44" height="37" fill="#221133" rx="5"/>'
    '<rect x="18" y="41" width="4" height="37" fill="#6622aa" rx="2"/>'
    '<rect x="58" y="41" width="4" height="37" fill="#6622aa" rx="2"/>'
    '<path d="M18 62 L14 94 L32 79Z" fill="#1a0f28"/>'
    '<path d="M62 62 L66 94 L48 79Z" fill="#1a0f28"/>'
    # 胸の三日月紋章
    '<path d="M38 52 C36 48 38 44 42 44 C38 44 36 48 38 52Z" fill="#aa66ff"/>'
    '<circle cx="41" cy="48" r="5" fill="none" stroke="#aa66ff" stroke-width="1.5"/>'
    '<circle cx="44" cy="47" r="4" fill="#221133"/>'
    # 腕
    '<rect x="6" y="42" width="13" height="8" fill="#221133" rx="3"/>'
    '<rect x="61" y="42" width="13" height="8" fill="#221133" rx="3"/>'
    # 魔法の光（両手）
    '<circle cx="8" cy="56" r="5" fill="#9933ff" opacity="0.4"/>'
    '<circle cx="8" cy="56" r="3" fill="#cc88ff" opacity="0.6"/>'
    '<circle cx="72" cy="56" r="5" fill="#9933ff" opacity="0.4"/>'
    '<circle cx="72" cy="56" r="3" fill="#cc88ff" opacity="0.6"/>'
    # 首
    '<rect x="34" y="35" width="12" height="8" fill="#d0a8d0" rx="2"/>'
    # 頭（青白い肌）
    '<circle cx="40" cy="23" r="14" fill="#d8b8d8"/>'
    # 暗紫色の長い髪（両サイドに流れる）
    '<path d="M27 17 C24 10 25 4 29 5 C27 10 26 18 25 28 C24 38 22 48 20 56 L22 57 C24 48 26 38 27 28 C27 18 27 17 27 17Z" fill="#553388"/>'
    '<path d="M53 17 C56 10 55 4 51 5 C53 10 54 18 55 28 C56 38 58 48 60 56 L58 57 C56 48 54 38 53 28 C53 18 53 17 53 17Z" fill="#553388"/>'
    '<ellipse cx="40" cy="12" rx="11" ry="7" fill="#553388"/>'
    # 目（神秘的な紫）
    '<ellipse cx="35" cy="24" rx="3" ry="2.5" fill="#8833cc"/>'
    '<ellipse cx="45" cy="24" rx="3" ry="2.5" fill="#8833cc"/>'
    '<circle cx="36" cy="23" r="0.8" fill="#ffffff" opacity="0.7"/>'
    '<circle cx="46" cy="23" r="0.8" fill="#ffffff" opacity="0.7"/>'
    # まつ毛（半眼）
    '<path d="M32 21 L32 23" stroke="#553388" stroke-width="1.2"/>'
    '<path d="M34 20 L34 22" stroke="#553388" stroke-width="1.2"/>'
    '<path d="M46 20 L46 22" stroke="#553388" stroke-width="1.2"/>'
    '<path d="M48 21 L48 23" stroke="#553388" stroke-width="1.2"/>'
    # 口（ミステリアス）
    '<path d="M37 30 Q40 32 43 30" stroke="#cc88cc" stroke-width="1.2" fill="none" stroke-linecap="round"/>'
    # 星の飾り
    '<circle cx="28" cy="9" r="1.5" fill="#aa66ff" opacity="0.8"/>'
    '<circle cx="52" cy="9" r="1.5" fill="#aa66ff" opacity="0.8"/>'
    '<circle cx="20" cy="6" r="1" fill="#8833cc" opacity="0.6"/>'
    '<circle cx="60" cy="6" r="1" fill="#8833cc" opacity="0.6"/>'
)

# ─────────────────────────────────────────
# 9. フィン（吟遊詩人）- 羽飾りの帽子、リュート
# ─────────────────────────────────────────
_FINN = _svg(
    # 足・靴
    '<rect x="28" y="72" width="10" height="22" fill="#cc7722" rx="2"/>'
    '<rect x="42" y="72" width="10" height="22" fill="#cc7722" rx="2"/>'
    '<rect x="27" y="82" width="12" height="12" fill="#332200" rx="2"/>'
    '<rect x="41" y="82" width="12" height="12" fill="#332200" rx="2"/>'
    # リュート（背中）
    '<ellipse cx="63" cy="60" rx="8" ry="10" fill="#886633"/>'
    '<ellipse cx="63" cy="60" rx="6" ry="8" fill="#aa8844"/>'
    '<circle cx="63" cy="60" r="2" fill="#664422"/>'
    '<rect x="62" y="45" width="2" height="18" fill="#665533" rx="1"/>'
    '<line x1="60" y1="46" x2="63" y2="55" stroke="#ccbb88" stroke-width="0.8"/>'
    '<line x1="62" y1="46" x2="63" y2="55" stroke="#ccbb88" stroke-width="0.8"/>'
    '<line x1="64" y1="46" x2="63" y2="55" stroke="#ccbb88" stroke-width="0.8"/>'
    # 体（カラフルな服）
    '<rect x="22" y="42" width="36" height="32" fill="#ff9933" rx="4"/>'
    '<rect x="30" y="42" width="20" height="4" fill="#ee7700" rx="2"/>'
    # 縞模様
    '<rect x="22" y="50" width="36" height="4" fill="#ffcc44" rx="1"/>'
    '<rect x="22" y="58" width="36" height="4" fill="#ee7700" rx="1"/>'
    # 腕
    '<rect x="10" y="43" width="13" height="8" fill="#ff9933" rx="3"/>'
    '<rect x="57" y="43" width="13" height="8" fill="#ff9933" rx="3"/>'
    # 首
    '<rect x="34" y="36" width="12" height="8" fill="#f0c07a" rx="2"/>'
    # 頭
    '<circle cx="40" cy="24" r="14" fill="#f0c07a"/>'
    # 羽飾りのある帽子（つばが広い）
    '<ellipse cx="40" cy="15" rx="20" ry="6" fill="#cc4422"/>'
    '<ellipse cx="40" cy="14" rx="14" ry="8" fill="#dd5533"/>'
    '<path d="M52 10 C56 2 60 -2 58 4 C56 0 54 4 52 8 C54 4 56 0 56 6 C54 4 53 8 52 10Z" fill="#3355cc"/>'
    '<path d="M52 10 C55 4 58 2 56 8 C54 6 52 10 52 10Z" fill="#5577ee"/>'
    # 目（楽しげ）
    '<ellipse cx="35" cy="24" rx="3" ry="2.5" fill="#884422"/>'
    '<ellipse cx="45" cy="24" rx="3" ry="2.5" fill="#884422"/>'
    '<circle cx="36" cy="23" r="1" fill="#fff"/>'
    '<circle cx="46" cy="23" r="1" fill="#fff"/>'
    # 眉（明るい表情）
    '<path d="M32 19 Q35 17 38 19" stroke="#664422" stroke-width="1.5" fill="none"/>'
    '<path d="M42 19 Q45 17 48 19" stroke="#664422" stroke-width="1.5" fill="none"/>'
    # 大きな笑顔
    '<path d="M35 29 Q40 35 45 29" stroke="#cc6633" stroke-width="2" fill="none" stroke-linecap="round"/>'
    # 頬紅
    '<circle cx="32" cy="28" r="4" fill="#ff8866" opacity="0.3"/>'
    '<circle cx="48" cy="28" r="4" fill="#ff8866" opacity="0.3"/>'
)

# ─────────────────────────────────────────
# 10. セラ（精霊使い）- 花冠、精霊の光
# ─────────────────────────────────────────
_SERA = _svg(
    # 精霊の光（浮遊するオーブ）
    '<circle cx="12" cy="30" r="5" fill="#88ff88" opacity="0.4"/>'
    '<circle cx="12" cy="30" r="3" fill="#aaffaa" opacity="0.6"/>'
    '<circle cx="12" cy="30" r="1.5" fill="#ffffff"/>'
    '<circle cx="68" cy="35" r="4" fill="#88ffaa" opacity="0.4"/>'
    '<circle cx="68" cy="35" r="2.5" fill="#aaffcc" opacity="0.6"/>'
    '<circle cx="68" cy="35" r="1.2" fill="#ffffff"/>'
    '<circle cx="15" cy="65" r="3.5" fill="#66ff99" opacity="0.35"/>'
    '<circle cx="15" cy="65" r="2" fill="#99ffbb" opacity="0.5"/>'
    '<circle cx="15" cy="65" r="1" fill="#ffffff"/>'
    # 足・靴
    '<rect x="28" y="76" width="10" height="18" fill="#88cc88" rx="2"/>'
    '<rect x="42" y="76" width="10" height="18" fill="#88cc88" rx="2"/>'
    '<rect x="27" y="84" width="12" height="10" fill="#556644" rx="2"/>'
    '<rect x="41" y="84" width="12" height="10" fill="#556644" rx="2"/>'
    # 白緑のドレス（長い）
    '<rect x="19" y="41" width="42" height="37" fill="#cceecc" rx="5"/>'
    '<path d="M19 63 L15 94 L34 80Z" fill="#bbddbb"/>'
    '<path d="M61 63 L65 94 L46 80Z" fill="#bbddbb"/>'
    # ドレス装飾（葉と花）
    '<ellipse cx="30" cy="52" rx="4" ry="6" fill="#88bb88" opacity="0.5" transform="rotate(-20 30 52)"/>'
    '<ellipse cx="50" cy="52" rx="4" ry="6" fill="#88bb88" opacity="0.5" transform="rotate(20 50 52)"/>'
    '<circle cx="40" cy="50" r="3" fill="#ffeeaa" opacity="0.7"/>'
    # ベルト（葉っぱモチーフ）
    '<rect x="26" y="62" width="28" height="4" fill="#6a9a6a" rx="2"/>'
    # 腕
    '<rect x="7" y="42" width="13" height="8" fill="#cceecc" rx="3"/>'
    '<rect x="60" y="42" width="13" height="8" fill="#cceecc" rx="3"/>'
    # 首
    '<rect x="34" y="35" width="12" height="8" fill="#f0d0c0" rx="2"/>'
    # 頭
    '<circle cx="40" cy="23" r="14" fill="#f0d0c0"/>'
    # 緑がかった髪（ウェーブ）
    '<ellipse cx="40" cy="13" rx="11" ry="7" fill="#88cc66"/>'
    '<path d="M28 20 C25 12 28 6 32 8 C29 13 28 18 28 20Z" fill="#88cc66"/>'
    '<path d="M52 20 C55 12 52 6 48 8 C51 13 52 18 52 20Z" fill="#88cc66"/>'
    # 花冠
    '<circle cx="33" cy="12" r="3" fill="#ff88aa"/>'
    '<circle cx="40" cy="9" r="3" fill="#ffaa44"/>'
    '<circle cx="47" cy="12" r="3" fill="#ff88aa"/>'
    '<circle cx="36" cy="10" r="2.5" fill="#ffcc66"/>'
    '<circle cx="44" cy="10" r="2.5" fill="#ff99bb"/>'
    '<circle cx="33" cy="12" r="1.5" fill="#ffffaa"/>'
    '<circle cx="40" cy="9" r="1.5" fill="#ffffff"/>'
    '<circle cx="47" cy="12" r="1.5" fill="#ffffaa"/>'
    # 目（緑）
    '<ellipse cx="35" cy="24" rx="2.5" ry="2" fill="#336633"/>'
    '<ellipse cx="45" cy="24" rx="2.5" ry="2" fill="#336633"/>'
    '<circle cx="36" cy="23" r="0.8" fill="#fff"/>'
    '<circle cx="46" cy="23" r="0.8" fill="#fff"/>'
    # 眉（柔らかい）
    '<path d="M33 19 Q35 17 37 19" stroke="#668844" stroke-width="1.2" fill="none"/>'
    '<path d="M43 19 Q45 17 47 19" stroke="#668844" stroke-width="1.2" fill="none"/>'
    # 口（穏やか）
    '<path d="M37 29 Q40 32 43 29" stroke="#cc9977" stroke-width="1.3" fill="none" stroke-linecap="round"/>'
)


CHARACTERS: dict[str, dict] = {
    "allen": {
        "id": "allen",
        "name": "アレン",
        "title": "勇者",
        "story": "辺境の村で生まれた若者。剣と盾で世界を守る王道の主人公。バランス型でどんな状況にも冷静に対応できる。",
        "color": "#cc3333",
        "svg": _ALLEN,
    },
    "liria": {
        "id": "liria",
        "name": "リリア",
        "title": "魔法使い",
        "story": "古の魔法書を読み解いた天才少女。知識こそが最強の武器と信じ、言葉の魔法で英知の扉を開く。",
        "color": "#7744cc",
        "svg": _LIRIA,
    },
    "gares": {
        "id": "gares",
        "name": "ガレス",
        "title": "騎士",
        "story": "王国騎士団の重鎮。重装備の守り手として仲間を守り抜く。不屈の意志と鋼の盾が彼の誇り。",
        "color": "#7799cc",
        "svg": _GARES,
    },
    "shia": {
        "id": "shia",
        "name": "シア",
        "title": "盗賊",
        "story": "影に生きる素早き者。正確無比な短剣さばきで難題を切り抜ける。誰よりも鋭く、誰よりも速い。",
        "color": "#446633",
        "svg": _SHIA,
    },
    "erwin": {
        "id": "erwin",
        "name": "エルウィン",
        "title": "弓使い",
        "story": "遠距離から冷静に的を射る銀髪の射手。感情を乱さず、どんな難問も精密に攻略する。",
        "color": "#227766",
        "svg": _ERWIN,
    },
    "noah": {
        "id": "noah",
        "name": "ノア",
        "title": "僧侶",
        "story": "回復と支援の達人。仲間の挫けそうな心を癒し、どんな困難も乗り越えさせる光の体現者。",
        "color": "#bb9933",
        "svg": _NOAH,
    },
    "drake": {
        "id": "drake",
        "name": "ドラク",
        "title": "ドラゴン戦士",
        "story": "半竜の血を引く孤高の戦士。強靭な鱗と炎の意志で英単語の試練に真正面から挑む。",
        "color": "#3d8022",
        "svg": _DRAKE,
    },
    "luna": {
        "id": "luna",
        "name": "ルナ",
        "title": "闇魔法使い",
        "story": "謎めいた力を操る月の魔法使い。暗闇から星の言葉を呼び起こし、未知の英知を解き明かす。",
        "color": "#7733aa",
        "svg": _LUNA,
    },
    "finn": {
        "id": "finn",
        "name": "フィン",
        "title": "吟遊詩人",
        "story": "言葉と音楽で世界を旅する詩人。英語の韻律を奏でながら、言葉の力で敵を魅了し打ち破る。",
        "color": "#cc6611",
        "svg": _FINN,
    },
    "sera": {
        "id": "sera",
        "name": "セラ",
        "title": "精霊使い",
        "story": "自然と共に生きる精霊の使い手。花と風が語りかける声を英知に変え、世界と調和しながら戦う。",
        "color": "#4a9944",
        "svg": _SERA,
    },
}


def get_character(char_id: str | None) -> dict:
    if not char_id or char_id not in CHARACTERS:
        return CHARACTERS["allen"]
    return CHARACTERS[char_id]


def sidebar_avatar_html(char_id: str | None) -> str:
    if not char_id or char_id not in CHARACTERS:
        return '<div style="font-size:3rem;text-align:center;line-height:1;">⚔️</div>'
    c = CHARACTERS[char_id]
    svg = c["svg"]
    return (
        '<div style="width:70px;height:88px;margin:0 auto;overflow:hidden;">' + svg + '</div>'
        '<div style="font-size:.72rem;color:#aa88ff;text-align:center;margin-top:2px;">' + c["title"] + '</div>'
    )
