import sys
from pathlib import Path
_root = Path(__file__).parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
from core.save_manager import (
    load_player, save_player, delete_save,
    register_user, verify_login, user_exists, is_username_taken,
    get_registered_users, update_ranking
)
from core.player import PlayerManager, streak_multiplier, STREAK_BONUS_TABLE
from core.i18n import t, grade_label, LANG_OPTIONS
from core.characters import CHARACTERS, CHARACTER_ORDER, get_character, sidebar_avatar_html
from core.daily_quest import get_login_streak

st.set_page_config(page_title="英検Quest", page_icon="⚔️", layout="centered", initial_sidebar_state="expanded")

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
def render_sidebar():
    p = st.session_state.player
    lang = p.get("language", "ja")
    pm = PlayerManager(p)
    hp_pct = pm.hp_percent() * 100
    exp_pct = pm.exp_percent() * 100
    streak = st.session_state.streak
    total = st.session_state.total_questions
    correct = st.session_state.total_correct
    accuracy = str(round(correct / total * 100)) + "%" if total > 0 else "---"
    current_mult = streak_multiplier(streak)
    next_thresh = next((t_v for t_v in sorted(STREAK_BONUS_TABLE) if t_v > streak), None)
    bonus_html = ""
    if current_mult > 1.0:
        bonus_html = '<b style="color:#ffe066;">EXP x' + str(current_mult) + '</b>'
    elif next_thresh:
        bonus_html = '<span style="color:#888;">あと' + str(next_thresh - streak) + '問でボーナス！</span>'

    char_id = p.get("character", "")
    c = get_character(char_id)
    equip = p.get("equipment")

    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:12px 0 6px;">'
            + sidebar_avatar_html(char_id, equip) +
            '<div style="font-size:1.2rem;font-weight:700;color:#ffe066;margin-top:6px;">' + p["name"] + '</div>'
            '<div style="font-size:.8rem;color:#aaaacc;">'
            + t("level", lang) + ' ' + str(p["level"]) + ' | ' + grade_label(p["grade_target"], lang) +
            '</div>'
            '</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="stat-label">' + t("hp", lang) + ' ' + str(p["hp"]) + ' / ' + str(p["hp_max"]) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="hp-bar-outer"><div class="hp-bar-inner" style="width:' + str(round(hp_pct, 1)) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">' + t("exp", lang) + ' ' + str(p["exp"]) + ' / ' + str(p["exp_to_next"]) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="exp-bar-outer"><div class="exp-bar-inner" style="width:' + str(round(exp_pct, 1)) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(
            '<div style="font-size:.82rem;line-height:2.1;color:#ccccee;">'
            '🔥 ' + t("streak", lang) + ' <b style="color:#ffe066;">' + str(streak) + '</b> ' + t("questions", lang) + ' ' + bonus_html + '<br>'
            '📊 ' + t("accuracy", lang) + ' <b style="color:#ffe066;">' + accuracy + '</b><br>'
            '📝 ' + t("total_q", lang) + ' <b style="color:#ffe066;">' + str(total) + '</b> ' + t("questions", lang) +
            '</div>', unsafe_allow_html=True)
        st.markdown("---")
        if p["hp"] <= 0:
            st.error(t("hp0_msg", lang))
        if st.button(t("save", lang), use_container_width=True):
            save_player(st.session_state.player, st.session_state.username)
            update_ranking(st.session_state.player, st.session_state.username)
            st.success("セーブしました！" if lang == "ja" else "已儲存！")
        if st.button(t("logout", lang), use_container_width=True):
            save_player(st.session_state.player, st.session_state.username)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        with st.expander(t("dev_menu", lang)):
            if st.button(t("data_delete", lang), use_container_width=True):
                delete_save(st.session_state.username)
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

render_sidebar()


# ─────────────────────────────────────────
# ホーム画面
# ─────────────────────────────────────────
p = st.session_state.player
lang = p.get("language", "ja")
c = get_character(p.get("character", ""))

st.markdown(
    '<div style="font-size:2.5rem;font-weight:700;text-align:center;'
    'background:linear-gradient(135deg,#ffe066,#ffaa00,#ff6600);'
    '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
    'background-clip:text;margin-bottom:4px;">⚔️ 英検Quest ⚔️</div>'
    '<div style="text-align:center;color:#888;margin-bottom:24px;">' + t("app_subtitle", lang) + '</div>',
    unsafe_allow_html=True)

st.markdown(
    '<div class="info-card">'
    '<div style="display:flex;align-items:center;gap:20px;">'
    '<div style="flex-shrink:0;width:70px;height:88px;">' + c["svg"] + '</div>'
    '<div style="font-size:.9rem;color:#ccccee;line-height:1.9;">'
    '<b style="color:#ffe066;">' + c["name"] + '</b>（' + c["title"] + '）と共に冒険中！<br>'
    '⚔️ ' + t("home_welcome", lang) + '<b style="color:#ffe066;">' + p["name"] + '</b>！<br>'
    + t("level", lang) + ' <b style="color:#fff;">' + str(p["level"]) + '</b> | '
    + t("home_challenge", lang) + '<b style="color:#fff;">' + grade_label(p["grade_target"], lang) + '</b>' + t("home_challenge_sub", lang) +
    '</div></div></div>',
    unsafe_allow_html=True)

st.markdown(
    '<div class="info-card">'
    '<div style="font-size:1.05rem;font-weight:700;color:#ffe066;margin-bottom:10px;">' + t("mission_title", lang) + '</div>'
    '<div style="font-size:.9rem;color:#ccccee;line-height:1.9;">' + t("mission_body", lang) + '</div>'
    '</div>'
    '<div class="info-card">'
    '<div style="font-size:1.05rem;font-weight:700;color:#ffe066;margin-bottom:10px;">' + t("howto_title", lang) + '</div>'
    '<div style="font-size:.9rem;color:#ccccee;line-height:1.9;">' + t("howto_body", lang) + '</div>'
    '</div>',
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.page_link("pages/01_quest.py", label=t("start_quest", lang), icon="🗡️")
