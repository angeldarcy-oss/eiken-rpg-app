"""
core/pwa.py ― スマホの「ホーム画面に追加」対応

Streamlitは<head>を直接編集できないため、iframe内のスクリプトから
親ページの<head>にPWAマニフェストとiOS用メタタグを注入する。

Streamlit Cloudのエッジは /app/static/ や /component/ への直接アクセスを
アプリに転送しない（実ブラウザでもHTMLフォールバックが返る）ことが
実測で確認されたため、アイコンの配信はURLに依存しない方式を採る:
  - マニフェスト: アイコンをbase64で埋め込み、マニフェスト自体も
    data: URLとして<link>に直接埋め込む（外部取得ゼロ）
  - iOSのapple-touch-icon: st.imageと同じメディア配信機構（/media/）で
    アイコンPNGを配信する。失敗時はdata: URLにフォールバック
"""

from __future__ import annotations
import base64
import json
from functools import lru_cache
from pathlib import Path

from core.compat import html_embed

_ASSETS_DIR = Path(__file__).parent / "pwa_assets"


@lru_cache(maxsize=8)
def _icon_b64(filename: str) -> str:
    return base64.b64encode((_ASSETS_DIR / filename).read_bytes()).decode()


@lru_cache(maxsize=1)
def _manifest_data_uri() -> str:
    """アイコンをdata URLで内包したマニフェストを、data URLとして返す。"""
    manifest = {
        "name": "英検Quest",
        "short_name": "英検Quest",
        "description": "英単語を制して、伝説の勇者へ",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#0e1117",
        "theme_color": "#1a1a2e",
        "icons": [
            {"src": "data:image/png;base64," + _icon_b64("icon-192.png"),
             "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "data:image/png;base64," + _icon_b64("icon-512.png"),
             "sizes": "512x512", "type": "image/png", "purpose": "any"},
        ],
    }
    payload = base64.b64encode(
        json.dumps(manifest, ensure_ascii=False).encode("utf-8")).decode()
    return "data:application/manifest+json;base64," + payload


def _touch_icon_url() -> str:
    """apple-touch-icon用のURLを返す。

    Streamlitのメディアファイルマネージャ（st.imageが使う /media/ 配信）に
    登録できればそのURLを、できなければ data: URLを返す。
    """
    try:
        from streamlit.runtime import get_instance
        mgr = get_instance().media_file_mgr
        url = mgr.add(
            (_ASSETS_DIR / "icon-180.png").read_bytes(),
            "image/png",
            "eiken-pwa-touch-icon",
        )
        if url:
            return url
    except Exception:
        pass
    return "data:image/png;base64," + _icon_b64("icon-180.png")


def inject_pwa_tags() -> None:
    """親ページに PWA 用の <link>/<meta> タグを注入する。

    ブラウザは「文書内で最初に見つかった manifest」を採用するため、
    Streamlit / Streamlit Cloud が先に入れている manifest や
    apple-touch-icon を取り除いてから自分のタグを挿入する。
    後からホスティング側がタグを再注入してもMutationObserverで排除する。
    """
    manifest_href = _manifest_data_uri()
    icon_href = _touch_icon_url()
    html_embed(
        '<script>(function(){'
        'var d=window.parent.document;'
        'var MF=' + json.dumps(manifest_href) + ';'
        'var IC=' + json.dumps(icon_href) + ';'
        'function apply(){'
        # 自分のもの以外の manifest / apple-touch-icon を排除
        'd.querySelectorAll(\'link[rel="manifest"],link[rel~="apple-touch-icon"]\')'
        '.forEach(function(el){'
        'if(!el.id||el.id.indexOf("eiken-pwa")!==0)el.remove();'
        '});'
        'var tags=['
        '["link",{rel:"manifest",href:MF,id:"eiken-pwa"}],'
        '["link",{rel:"apple-touch-icon",sizes:"180x180",href:IC,id:"eiken-pwa-icon"}],'
        '["meta",{name:"apple-mobile-web-app-capable",content:"yes"}],'
        '["meta",{name:"mobile-web-app-capable",content:"yes"}],'
        '["meta",{name:"apple-mobile-web-app-status-bar-style",content:"black-translucent"}],'
        '["meta",{name:"apple-mobile-web-app-title",content:"英検Quest"}],'
        '["meta",{name:"theme-color",content:"#1a1a2e"}]'
        '];'
        'tags.forEach(function(t){'
        'var sel=t[0]+(t[1].id?"#"+t[1].id:\'[name="\'+t[1].name+\'"]\');'
        'var ex=d.head.querySelector(sel);'
        'if(ex){if(t[1].href)ex.setAttribute("href",t[1].href);return;}'
        'var el=d.createElement(t[0]);'
        'for(var k in t[1])el.setAttribute(k,t[1][k]);'
        'd.head.appendChild(el);'
        '});'
        '}'
        'apply();'
        # ホスティング側が後からタグを注入しても常に排除する
        'if(!window.parent.__eikenPwaObserver){'
        'var obs=new MutationObserver(function(){apply();});'
        'obs.observe(d.head,{childList:true});'
        'window.parent.__eikenPwaObserver=obs;'
        '}'
        '})();</script>',
        height=1, scrolling=False)
