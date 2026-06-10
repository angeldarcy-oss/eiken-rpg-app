"""core/nav.py — 言語対応カスタムサイドバーナビゲーション"""
from __future__ import annotations
import streamlit as st
from core.i18n import t

HIDE_NAV_CSS = (
    '<style>[data-testid="stSidebarNav"]>ul{display:none!important;}</style>'
)

_NAV_PAGES: list[tuple[str, str]] = [
    ("app.py",               "nav_home"),
    ("pages/01_quest.py",    "nav_quest"),
    ("pages/02_dungeon.py",  "nav_dungeon"),
    ("pages/03_daily.py",    "nav_daily"),
    ("pages/04_wordbook.py", "nav_wordbook"),
    ("pages/05_ranking.py",  "nav_ranking"),
    ("pages/06_party.py",    "nav_party"),
    ("pages/07_guild.py",    "nav_guild"),
    ("pages/08_shop.py",     "nav_shop"),
    ("pages/09_event.py",    "nav_event"),
    ("pages/10_settings.py", "nav_settings"),
]


def render_nav(lang: str = "ja") -> None:
    """サイドバーナビゲーションリンクを描画する（with st.sidebar: 内で呼ぶこと）。"""
    st.markdown(HIDE_NAV_CSS, unsafe_allow_html=True)
    nav_label = "ページ移動" if lang == "ja" else "頁面導覽"
    st.markdown(
        f'<div style="font-size:.66rem;color:#666;letter-spacing:.07em;'
        f'padding:4px 0 2px;">{nav_label}</div>',
        unsafe_allow_html=True,
    )
    for path, key in _NAV_PAGES:
        st.page_link(path, label=t(key, lang))
