"""
core/supabase_client.py ― Supabase接続クライアント

SUPABASE_URL / SUPABASE_KEY を .env から読み込み、
アプリ全体で共有するクライアントを1つだけ生成する。
"""

from __future__ import annotations
import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import create_client, Client


def _get_setting(name: str) -> str:
    """環境変数(.env) → st.secrets の順に設定値を探す"""
    value = os.environ.get(name, "").strip()
    if value:
        return value
    # Streamlit Cloudでは .env の代わりに Secrets (st.secrets) を使う
    try:
        import streamlit as st
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


@lru_cache(maxsize=1)
def get_client() -> Client:
    """Supabaseクライアントを返す（初回のみ生成、以降はキャッシュ）"""
    load_dotenv()
    url = _get_setting("SUPABASE_URL")
    key = _get_setting("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_KEY が設定されていません。"
            "ローカルでは .env に、Streamlit CloudではSecretsに設定してください。"
        )
    return create_client(url, key)
