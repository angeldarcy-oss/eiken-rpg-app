"""core/nav.py — 言語対応カスタムサイドバーナビゲーション"""
from __future__ import annotations
import streamlit as st
from core.i18n import t

# Streamlit自動生成ナビを非表示（stSidebarNav コンテナごと消す）
HIDE_NAV_CSS = (
    '<style>[data-testid="stSidebarNav"]{display:none!important;}</style>'
)

# (URL path, i18n key)
_NAV_ITEMS: list[tuple[str, str]] = [
    ("/",          "nav_home"),
    ("/quest",     "nav_quest"),
    ("/dungeon",   "nav_dungeon"),
    ("/daily",     "nav_daily"),
    ("/wordbook",  "nav_wordbook"),
    ("/ranking",   "nav_ranking"),
    ("/party",     "nav_party"),
    ("/guild",     "nav_guild"),
    ("/shop",      "nav_shop"),
    ("/event",     "nav_event"),
    ("/settings",  "nav_settings"),
]

_NAV_CSS = """
<style>
.eiken-nav { margin: 2px 0 4px; }
.eiken-nav a {
    display: block;
    padding: 5px 10px;
    margin: 1px 0;
    border-radius: 6px;
    color: #ccccee !important;
    text-decoration: none !important;
    font-size: .85rem;
    line-height: 1.4;
}
.eiken-nav a:hover {
    background: rgba(255,255,255,0.1) !important;
    color: #ffffff !important;
}
.eiken-nav-label {
    font-size: .66rem;
    color: #666;
    letter-spacing: .07em;
    padding: 4px 0 2px;
}
</style>
"""


def render_nav(lang: str = "ja") -> None:
    """サイドバーナビゲーションリンクを描画する（with st.sidebar: 内で呼ぶこと）。
    st.page_link() は stSidebarNav 内に描画されるため HTML リンクを使用する。
    """
    nav_label = "ページ移動" if lang == "ja" else "頁面導覽"
    lines = [
        HIDE_NAV_CSS,
        _NAV_CSS,
        f'<div class="eiken-nav-label">{nav_label}</div>',
        '<div class="eiken-nav">',
    ]
    for url, key in _NAV_ITEMS:
        lines.append(f'<a href="{url}" target="_self">{t(key, lang)}</a>')
    lines.append("</div>")
    st.markdown("".join(lines), unsafe_allow_html=True)
