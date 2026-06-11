"""
core/sound.py ― モバイル対応の効果音再生ヘルパー

モバイルブラウザ（iOS Safari / Android Chrome）は「ユーザー操作を伴わない
音声再生」をブロックするため、Streamlitのrerun後に挿入されるiframe内で
audio.play() を自動実行してもスマホでは鳴らない。

対策（オーディオアンロック方式）:
  1. render_sound_bootstrap() で効果音のAudioオブジェクトを親ページ
     （rerunでも破棄されないドキュメント）に登録し、ユーザーの最初の
     タップ時に無音で一度再生してブラウザの再生制限を解除する
  2. play_sound() / play_js() は解除済みの親ページのAudioを再生する。
     一度ユーザー操作で再生された要素は、以後プログラムから再生できる
  3. 親ページにアクセスできない場合は従来どおりiframe内の
     new Audio() にフォールバックする（PCはこれでも鳴る）
"""

from __future__ import annotations
import json

import streamlit.components.v1 as components


def render_sound_bootstrap(sounds: dict) -> None:
    """効果音を親ページに登録し、初回タップでのアンロックを仕込む。

    ページ描画のたびに呼んでよい（親ページ側のフラグで多重登録を防ぐ）。

    Args:
        sounds: {効果音名: WAVデータのbase64文字列}
    """
    components.html(
        '<script>(function(){'
        'var P=window.parent;'
        'var DATA=' + json.dumps(sounds) + ';'
        'var reg=P.__sfxReg=P.__sfxReg||{};'
        'for(var k in DATA){'
        'if(!reg[k]){'
        'var a=new P.Audio("data:audio/wav;base64,"+DATA[k]);'
        'a.preload="auto";'
        'reg[k]=a;'
        '}}'
        'if(!P.__sfxUnlockInstalled){'
        'P.__sfxUnlockInstalled=true;'
        'var unlock=function(){'
        'if(P.__sfxUnlocked)return;'
        'P.__sfxUnlocked=true;'
        'var r=P.__sfxReg;'
        'for(var k in r){(function(a){'
        'a.muted=true;'
        'var pr=a.play();'
        'var done=function(){a.pause();a.currentTime=0;a.muted=false;};'
        'if(pr&&pr.then){pr.then(done).catch(function(){a.muted=false;});}'
        'else{done();}'
        '})(r[k]);}'
        'P.document.removeEventListener("touchend",unlock,true);'
        'P.document.removeEventListener("click",unlock,true);'
        '};'
        'P.document.addEventListener("touchend",unlock,true);'
        'P.document.addEventListener("click",unlock,true);'
        '}'
        '})();</script>',
        height=1, scrolling=False)


def play_js(name: str, b64: str, volume: float = 0.65) -> str:
    """効果音を再生する<script>タグ文字列を返す（他のHTMLに埋め込む用）。"""
    v = str(volume)
    return (
        '<script>(function(){'
        'function fb(){'
        'var a=new Audio("data:audio/wav;base64,' + b64 + '");'
        'a.volume=' + v + ';'
        'var p=a.play();if(p&&p.catch)p.catch(function(){});'
        '}'
        'try{'
        'var reg=window.parent.__sfxReg;'
        'var a=reg&&reg[' + json.dumps(name) + '];'
        'if(a){'
        'a.muted=false;a.volume=' + v + ';a.currentTime=0;'
        'var p=a.play();if(p&&p.catch)p.catch(fb);'
        '}else{fb();}'
        '}catch(e){fb();}'
        '})();</script>'
    )


def play_sound(name: str, b64: str, volume: float = 0.65) -> None:
    """効果音を再生する。render_sound_bootstrap() で登録済みの名前を渡すこと。"""
    components.html(play_js(name, b64, volume), height=1, scrolling=False)
