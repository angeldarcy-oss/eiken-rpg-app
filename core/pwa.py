"""
core/pwa.py ― スマホの「ホーム画面に追加」対応

Streamlitは<head>を直接編集できないため、iframe内のスクリプトから
親ページの<head>にPWAマニフェストとiOS用メタタグを注入する。

必要な静的ファイル（.streamlit/config.toml の enableStaticServing で配信）:
  - static/manifest.json   … Android / Chrome 用
  - static/icon-192.png, icon-512.png … マニフェスト用アイコン
  - static/icon-180.png    … iOS の apple-touch-icon
"""

from __future__ import annotations
import streamlit.components.v1 as components


def inject_pwa_tags() -> None:
    """親ページに PWA 用の <link>/<meta> タグを一度だけ注入する。"""
    components.html(
        '<script>(function(){'
        'var d=window.parent.document;'
        'if(d.getElementById("eiken-pwa"))return;'
        'var tags=['
        '["link",{rel:"manifest",href:"/app/static/manifest.json",id:"eiken-pwa"}],'
        '["link",{rel:"apple-touch-icon",href:"/app/static/icon-180.png"}],'
        '["meta",{name:"apple-mobile-web-app-capable",content:"yes"}],'
        '["meta",{name:"mobile-web-app-capable",content:"yes"}],'
        '["meta",{name:"apple-mobile-web-app-status-bar-style",content:"black-translucent"}],'
        '["meta",{name:"apple-mobile-web-app-title",content:"英検Quest"}],'
        '["meta",{name:"theme-color",content:"#1a1a2e"}]'
        '];'
        'tags.forEach(function(t){'
        'var el=d.createElement(t[0]);'
        'for(var k in t[1])el.setAttribute(k,t[1][k]);'
        'd.head.appendChild(el);'
        '});'
        '})();</script>',
        height=1, scrolling=False)
