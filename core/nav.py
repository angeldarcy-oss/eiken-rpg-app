"""core/nav.py — 言語対応カスタムサイドバーナビゲーション"""
from __future__ import annotations
import streamlit as st
from core.i18n import t

# Streamlit自動生成ナビを非表示
HIDE_NAV_CSS = (
    '<style>[data-testid="stSidebarNav"]{display:none!important;}</style>'
)

# (file path for st.switch_page, i18n key)
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
    """サイドバーナビゲーションを描画する（with st.sidebar: 内で呼ぶこと）。
    st.button + st.switch_page を使用。stSidebarNav に依存しない。
    """
    st.markdown(HIDE_NAV_CSS, unsafe_allow_html=True)
    nav_label = "ページ移動" if lang == "ja" else "頁面導覽"
    st.caption(nav_label)
    for path, key in _NAV_PAGES:
        btn_key = "nav_" + path.replace("/", "_").replace(".", "_")
        if st.button(t(key, lang), key=btn_key, use_container_width=True):
            st.switch_page(path)
