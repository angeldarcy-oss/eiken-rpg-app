"""core/mobile_css.py — モバイル最適化CSS（全ページ共通）"""

MOBILE_CSS: str = """<style>
/* ══════════════════════════════════════════
   英検Quest モバイル最適化 CSS
   対応: スマートフォン 375px〜428px / タブレット〜768px
   ══════════════════════════════════════════ */

/* ── 全デバイス共通: タッチ操作基盤 ── */
* {
    -webkit-tap-highlight-color: transparent;
}
.stButton > button {
    min-height: 44px !important;
    touch-action: manipulation !important;
    cursor: pointer !important;
}

/* iOS Safari: テキスト入力でのズーム防止（16px以上必須） */
input, textarea, select,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    font-size: 16px !important;
}

/* ══════════════════════════════════════════
   モバイル（幅 768px 以下）
   ══════════════════════════════════════════ */
@media screen and (max-width: 768px) {

    /* ─ レイアウト基盤 ─ */
    .main .block-container {
        padding: 1rem 0.7rem 2.5rem !important;
        max-width: 100% !important;
    }

    /* ─ ボタン: タップしやすいサイズ ─ */
    .stButton > button {
        min-height: 52px !important;
        font-size: 0.95rem !important;
        padding: 10px 14px !important;
        border-radius: 12px !important;
        white-space: normal !important;
        line-height: 1.35 !important;
        letter-spacing: 0.02em !important;
    }

    /* ─ カラム縦積み（選択肢ボタン・2列→1列化）─ */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0 !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex: 0 0 100% !important;
        min-width: 100% !important;
        width: 100% !important;
    }

    /* ─ クイズカード ─ */
    .quiz-card {
        padding: 14px 12px !important;
        border-radius: 12px !important;
        margin-bottom: 6px !important;
    }

    /* ─ 単語表示フォント縮小 ─ */
    .word-display {
        font-size: 2.1rem !important;
    }

    /* ─ ボス対戦レイアウト: 縦並び ─ */
    .boss-battle-layout {
        flex-direction: column !important;
        gap: 6px !important;
        padding: 4px 0 !important;
    }
    .char-battle-side, .boss-battle-side {
        align-self: center !important;
    }

    /* ─ モンスターSVGのサイズ制限 ─ */
    .m-svg-wrap {
        max-width: 100px !important;
        max-height: 100px !important;
    }
    .m-svg-wrap svg {
        width: 100% !important;
        height: auto !important;
        max-height: 100px !important;
    }
    .char-battle-side svg {
        max-width: 72px !important;
        max-height: 88px !important;
    }
    .boss-battle-side svg {
        max-width: 88px !important;
        max-height: 88px !important;
    }

    /* ─ タブのフォント調整 ─ */
    [data-testid="stTabs"] button[role="tab"] {
        font-size: 0.72rem !important;
        padding: 6px 7px !important;
        min-width: 0 !important;
        white-space: nowrap !important;
    }

    /* ─ expander タップ領域 ─ */
    [data-testid="stExpander"] summary {
        min-height: 48px !important;
        display: flex !important;
        align-items: center !important;
        padding: 10px 14px !important;
    }

    /* ─ フォーム要素の余白縮小 ─ */
    [data-testid="stTextInput"],
    [data-testid="stSelectbox"],
    [data-testid="stTextArea"] {
        margin-bottom: 0.4rem !important;
    }

    /* ─ サイドバー: コンパクト化 ─ */
    [data-testid="stSidebar"] {
        min-width: 240px !important;
        max-width: 280px !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding: 0.6rem 0.6rem 1.5rem !important;
    }
    /* キャラクターアバター縮小 */
    [data-testid="stSidebar"] div[style*="width:70px"] {
        width: 52px !important;
        height: 64px !important;
    }
    [data-testid="stSidebar"] div[style*="width:70px"] svg {
        width: 52px !important;
        height: 64px !important;
    }
    /* サイドバー内フォント縮小 */
    [data-testid="stSidebar"] .stat-label {
        font-size: 10px !important;
    }

    /* ─ ギルド・イベント系カードのパディング縮小 ─ */
    .guild-card {
        padding: 12px 14px !important;
    }

    /* ─ 水平仕切り線の余白縮小 ─ */
    hr {
        margin: 0.4rem 0 !important;
    }
}

/* ══════════════════════════════════════════
   小型モバイル（幅 480px 以下）
   ══════════════════════════════════════════ */
@media screen and (max-width: 480px) {

    .main .block-container {
        padding: 0.75rem 0.4rem 2.5rem !important;
    }

    .stButton > button {
        min-height: 56px !important;
        font-size: 0.88rem !important;
        padding: 12px 10px !important;
    }

    .word-display {
        font-size: 1.85rem !important;
    }

    .quiz-card {
        padding: 10px 8px !important;
    }

    /* タブをさらに小さく */
    [data-testid="stTabs"] button[role="tab"] {
        font-size: 0.62rem !important;
        padding: 5px 5px !important;
    }

    /* サイドバーアバターさらに縮小 */
    [data-testid="stSidebar"] div[style*="width:70px"] {
        width: 42px !important;
        height: 52px !important;
    }
}
</style>"""
