"""
core/compat.py ― Streamlitのバージョン差異を吸収するラッパー

st.components.v1.html は Streamlit 1.56 で非推奨になり、後継は st.iframe。
本番（常に最新版）とローカル/旧環境の両方で動くよう、ここで吸収する。
"""

from __future__ import annotations

import streamlit as st


def html_embed(html: str, height: int = 150, scrolling: bool = False) -> None:
    """HTML文字列をiframeとして埋め込む。

    Streamlit 1.56+ では st.iframe、それ未満では components.html を使う。
    （st.iframe に scrolling 引数はなく常にスクロール可能）
    """
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=height, scrolling=scrolling)
