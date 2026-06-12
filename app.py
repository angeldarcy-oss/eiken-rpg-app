import sys
from pathlib import Path
_root = Path(__file__).parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
from core.save_manager import (
    load_player, save_player,
    register_user, verify_login, user_exists, is_username_taken,
    get_registered_users,
)
from core.i18n import t
from core.characters import CHARACTERS, CHARACTER_ORDER
from core.daily_quest import get_login_streak
from core.pwa import inject_pwa_tags

st.set_page_config(page_title="英検Quest", page_icon="⚔️", layout="centered", initial_sidebar_state="expanded")
inject_pwa_tags()

st.markdown("""<style>
html,body,[class*="css"]{font-family:'Noto Sans JP',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460);}
[data-testid="stSidebar"] *{color:#e0e0e0 !important;}
.hp-bar-outer{background:#2a0a0a;border-radius:8px;height:18px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a1a1a;}
.hp-bar-inner{background:linear-gradient(90deg,#e05252,#ff8080);height:100%;border-radius:8px;}
.exp-bar-outer{background:#1a1500;border-radius:8px;height:14px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a4a00;}
.exp-bar-inner{background:linear-gradient(90deg,#c8a000,#ffe066);height:100%;border-radius:8px;}
.stat-label{font-size:11px;color:#aaaacc !important;}
.info-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;border-radius:12px;padding:20px 24px;margin-bottom:16px;}
.char-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:2px solid #3a3a6a;border-radius:16px;padding:16px 12px;text-align:center;cursor:pointer;transition:all .2s;}
.char-card:hover{border-color:#7766cc;background:linear-gradient(135deg,#2a2a4a,#3a3a6a);}
.char-card-selected{border-color:#ffe066 !important;background:linear-gradient(135deg,#2a2000,#3a3000) !important;}
</style>""", unsafe_allow_html=True)


def init_session():
    for k, v in [("logged_in", False), ("username", ""), ("player", None),
                 ("total_correct", 0), ("total_questions", 0), ("streak", 0)]:
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─────────────────────────────────────────
# ログイン画面
# ─────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown(
        '<div style="text-align:center;padding:40px 0 20px;">'
        '<div style="font-size:4rem;">⚔️</div>'
        '<div style="font-size:2.5rem;font-weight:700;background:linear-gradient(135deg,#ffe066,#ffaa00);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">'
        '英検Quest</div>'
        '<div style="color:#888;margin-top:8px;">英単語を制して、伝説の勇者へ</div>'
        '</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔑 ログイン", "🆕 新規登録"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        login_user = st.text_input("ユーザー名", key="login_user", placeholder="登録したユーザー名")
        login_pass = st.text_input("パスワード", key="login_pass", type="password", placeholder="登録したパスワード")
        if st.button("ログイン", use_container_width=True, type="primary"):
            if not login_user or not login_pass:
                st.error("ユーザー名とパスワードを入力してください")
            elif not user_exists(login_user):
                st.error("このユーザー名は登録されていません")
            elif not verify_login(login_user, login_pass):
                st.error("パスワードが違います")
            else:
                st.session_state.logged_in = True
                st.session_state.username = login_user.strip()
                st.session_state.player = load_player(login_user.strip())
                st.session_state.total_correct = 0
                st.session_state.total_questions = 0
                st.session_state.streak = 0
                get_login_streak(st.session_state.player)
                save_player(st.session_state.player, login_user.strip())
                st.rerun()

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        reg_user = st.text_input("ユーザー名", key="reg_user", placeholder="2〜20文字", max_chars=20)
        reg_pass = st.text_input("パスワード", key="reg_pass", type="password", placeholder="4文字以上で入力")
        st.caption("🔒 パスワードは4文字以上で設定してください")
        reg_pass2 = st.text_input("パスワード（確認）", key="reg_pass2", type="password", placeholder="もう一度入力してください")
        st.caption("✅ 上のパスワードをもう一度入力してください")
        if st.button("新規登録", use_container_width=True, type="primary"):
            name = reg_user.strip()
            if not name or not reg_pass:
                st.error("全ての項目を入力してください")
            elif len(name) < 2:
                st.error("ユーザー名は2文字以上にしてください")
            elif len(reg_pass) < 4:
                st.error("パスワードは4文字以上にしてください")
            elif reg_pass != reg_pass2:
                st.error("パスワードが一致しません")
            elif is_username_taken(name):
                st.error("このユーザー名は既に使われています")
            else:
                if register_user(name, reg_pass):
                    st.session_state.logged_in = True
                    st.session_state.username = name
                    st.session_state.player = load_player(name)
                    st.session_state.total_correct = 0
                    st.session_state.total_questions = 0
                    st.session_state.streak = 0
                    get_login_streak(st.session_state.player)
                    save_player(st.session_state.player, name)
                    st.success("登録完了！ようこそ " + name + " さん！")
                    st.rerun()

    users = get_registered_users()
    if users:
        st.markdown(
            '<div style="text-align:center;color:#666;font-size:.85rem;margin-top:24px;">'
            '現在 <b>' + str(len(users)) + '</b> 人の勇者が冒険中！'
            '</div>', unsafe_allow_html=True)

    # PWA（ホーム画面アイコン）の動作診断。実ブラウザ内から配信とタグ注入を検査する
    with st.expander("🔧 アイコン診断"):
        from core.compat import html_embed
        html_embed(
            '<div id="r" style="font-family:monospace;font-size:12px;color:#333;'
            'white-space:pre-wrap;line-height:1.7;">検査中...</div>'
            '<script>(async function(){'
            'var out=[];'
            'try{'
            'var d=window.parent.document;'
            'var mf=d.querySelector(\'link[rel="manifest"]\');'
            'var ic=d.querySelector(\'link[rel~="apple-touch-icon"]\');'
            'var tt=d.querySelector(\'meta[name="apple-mobile-web-app-title"]\');'
            'var mh=mf?mf.getAttribute("href"):"";'
            'var ih=ic?ic.getAttribute("href"):"";'
            'out.push((mh.indexOf("data:application/manifest")===0?"✓":"✗")'
            '+" manifest: "+(mh?mh.slice(0,42)+"...":"なし"));'
            'if(ih){'
            'try{var r=await fetch(ih);'
            'var ct=r.headers.get("content-type")||"";'
            'out.push((ct.indexOf("image")>=0?"✓":"✗")+" touch-icon("+ih.slice(0,30)+"...) → "+r.status+" "+ct);'
            '}catch(e){out.push("✗ touch-icon fetch ERROR "+e);}'
            '}else{out.push("✗ touch-icon: なし");}'
            'out.push((tt&&tt.content==="\\u82f1\\u691cQuest"?"✓":"✗")+" app-title: "+(tt?tt.content:"なし"));'
            '}catch(e){out.push("✗ 親ページ参照: 不可 "+e);}'
            'out.push("ビルド: 2026-06-12-E");'
            'document.getElementById("r").innerText=out.join("\\n");'
            '})();</script>',
            height=170)
    st.stop()


# ─────────────────────────────────────────
# キャラクター選択画面
# ─────────────────────────────────────────
def show_character_select(is_change: bool = False):
    p = st.session_state.player
    current_char = p.get("character", "")

    st.markdown(
        '<div style="text-align:center;padding:24px 0 8px;">'
        '<div style="font-size:2rem;font-weight:700;background:linear-gradient(135deg,#ffe066,#ffaa00);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">'
        + ("冒険の仲間を選ぼう" if not is_change else "キャラクターを変更する") +
        '</div>'
        '<div style="color:#888;font-size:.9rem;margin-top:6px;">'
        'あなたと共に英知の試練を乗り越えるキャラクターを選んでください'
        '</div>'
        '</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    cols_per_row = 2
    char_ids = CHARACTER_ORDER
    rows = [char_ids[i:i+cols_per_row] for i in range(0, len(char_ids), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, char_id in zip(cols, row):
            c = CHARACTERS[char_id]
            is_selected = (char_id == current_char)
            border_color = "#ffe066" if is_selected else "#3a3a6a"
            bg = "linear-gradient(135deg,#2a2000,#3a3000)" if is_selected else "linear-gradient(135deg,#1e1e3a,#2a2a4a)"
            with col:
                st.markdown(
                    f'<div style="background:{bg};border:2px solid {border_color};border-radius:16px;'
                    f'padding:16px 10px;text-align:center;margin-bottom:4px;">'
                    f'<div style="width:80px;height:100px;margin:0 auto;">{c["svg"]}</div>'
                    f'<div style="font-size:1.1rem;font-weight:700;color:#ffe066;margin-top:8px;">{c["name"]}</div>'
                    f'<div style="font-size:.75rem;color:#aa88ff;margin-bottom:6px;">{c["title"]}</div>'
                    f'<div style="font-size:.75rem;color:#aaaacc;line-height:1.5;margin-bottom:10px;">{c["story"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True)
                btn_label = "✓ 選択中" if is_selected else "選択する"
                btn_type = "primary" if not is_selected else "secondary"
                if st.button(btn_label, key=f"select_char_{char_id}", use_container_width=True, type=btn_type):
                    st.session_state.player["character"] = char_id
                    save_player(st.session_state.player, st.session_state.get("username", ""))
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    if not is_change:
        st.markdown(
            '<div style="text-align:center;color:#666;font-size:.82rem;margin-top:8px;">'
            'キャラクターは後で設定ページからいつでも変更できます'
            '</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# 初回キャラクター選択（未選択なら強制表示）
# ─────────────────────────────────────────
if not st.session_state.player.get("character"):
    show_character_select(is_change=False)
    st.stop()


# ─────────────────────────────────────────
# ログイン後：サイドバー
# ─────────────────────────────────────────
_lang = (st.session_state.get("player") or {}).get("language", "ja")
pg = st.navigation(
    [
        st.Page("pages/00_home.py",     title="英検Quest",                              default=True),
        st.Page("pages/01_quest.py",    title=t("pt_quest",    _lang) + " | 英検Quest"),
        st.Page("pages/02_dungeon.py",  title=t("pt_dungeon",  _lang) + " | 英検Quest"),
        st.Page("pages/03_daily.py",    title=t("pt_daily",    _lang) + " | 英検Quest"),
        st.Page("pages/04_wordbook.py", title=t("pt_wordbook", _lang) + " | 英検Quest"),
        st.Page("pages/05_ranking.py",  title=t("pt_ranking",  _lang) + " | 英検Quest"),
        st.Page("pages/11_progress.py", title=t("pt_progress", _lang) + " | 英検Quest"),
        st.Page("pages/06_party.py",    title=t("pt_party",    _lang) + " | 英検Quest"),
        st.Page("pages/07_guild.py",    title=t("pt_guild",    _lang) + " | 英検Quest"),
        st.Page("pages/08_shop.py",     title=t("pt_shop",     _lang) + " | 英検Quest"),
        st.Page("pages/09_event.py",    title=t("pt_event",    _lang) + " | 英検Quest"),
        st.Page("pages/10_settings.py", title=t("pt_settings", _lang) + " | 英検Quest"),
    ],
    position="hidden",
)
pg.run()
