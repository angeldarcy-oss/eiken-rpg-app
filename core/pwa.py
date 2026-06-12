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
    """親ページに PWA 用の <link>/<meta> タグを注入する。

    ブラウザは「文書内で最初に見つかった manifest」を採用するため、
    Streamlit / Streamlit Cloud が先に入れている manifest や
    apple-touch-icon を取り除いてから自分のタグを挿入する。
    後からホスティング側が再注入するケースに備えて、数秒間は
    定期的に競合タグを排除し続ける。
    """
    components.html(
        '<script>(function(){'
        'var d=window.parent.document;'
        'function apply(){'
        # 自分のもの以外の manifest / apple-touch-icon を排除
        'd.querySelectorAll(\'link[rel="manifest"],link[rel~="apple-touch-icon"]\')'
        '.forEach(function(el){'
        'if(!el.id||el.id.indexOf("eiken-pwa")!==0)el.remove();'
        '});'
        'var tags=['
        '["link",{rel:"manifest",href:"/app/static/manifest.json",id:"eiken-pwa"}],'
        '["link",{rel:"apple-touch-icon",sizes:"180x180",href:"/app/static/icon-180.png",id:"eiken-pwa-icon"}],'
        '["meta",{name:"apple-mobile-web-app-capable",content:"yes"}],'
        '["meta",{name:"mobile-web-app-capable",content:"yes"}],'
        '["meta",{name:"apple-mobile-web-app-status-bar-style",content:"black-translucent"}],'
        '["meta",{name:"apple-mobile-web-app-title",content:"英検Quest"}],'
        '["meta",{name:"theme-color",content:"#1a1a2e"}]'
        '];'
        'tags.forEach(function(t){'
        'var sel=t[0]+(t[1].id?"#"+t[1].id:\'[name="\'+t[1].name+\'"]\');'
        'if(d.head.querySelector(sel))return;'
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
