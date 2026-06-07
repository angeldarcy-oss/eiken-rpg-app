import sys
from pathlib import Path
_root = Path(__file__).parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
from core.save_manager import (
    load_player, save_player, delete_save,
    register_user, verify_login, user_exists, is_username_taken,
    get_registered_users
)

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
</style>""", unsafe_allow_html=True)


def _grade_label(k):
    return {"grade_5":"5級","grade_4":"4級","grade_3":"3級","grade_pre2":"準2級","grade_2":"2級"}.get(k,k)


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
                st.rerun()

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        reg_user = st.text_input("ユーザー名", key="reg_user", placeholder="2〜20文字", max_chars=20)
        reg_pass = st.text_input("パスワード", key="reg_pass", type="password", placeholder="4文字以上")
        reg_pass2 = st.text_input("パスワード（確認）", key="reg_pass2", type="password", placeholder="もう一度入力")
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
# ログイン後：サイドバー
# ─────────────────────────────────────────
def render_sidebar():
    p = st.session_state.player
    from core.player import PlayerManager, streak_multiplier, STREAK_BONUS_TABLE
    pm = PlayerManager(p)
    hp_pct = pm.hp_percent() * 100
    exp_pct = pm.exp_percent() * 100
    streak = st.session_state.streak
    total = st.session_state.total_questions
    correct = st.session_state.total_correct
    accuracy = str(round(correct/total*100)) + "%" if total > 0 else "---"
    current_mult = streak_multiplier(streak)
    next_thresh = next((t for t in sorted(STREAK_BONUS_TABLE) if t > streak), None)
    bonus_html = ""
    if current_mult > 1.0:
        bonus_html = '<b style="color:#ffe066;">EXP x' + str(current_mult) + '</b>'
    elif next_thresh:
        bonus_html = '<span style="color:#888;">あと' + str(next_thresh - streak) + '問でボーナス！</span>'

    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:16px 0 8px;">'
            '<div style="font-size:3rem;">⚔️</div>'
            '<div style="font-size:1.3rem;font-weight:700;color:#ffe066;margin-top:8px;">' + p["name"] + '</div>'
            '<div style="font-size:.85rem;color:#aaaacc;">Lv. ' + str(p["level"]) + ' | 英検' + _grade_label(p["grade_target"]) + '</div>'
            '</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="stat-label">HP ' + str(p["hp"]) + ' / ' + str(p["hp_max"]) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="hp-bar-outer"><div class="hp-bar-inner" style="width:' + str(round(hp_pct,1)) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">EXP ' + str(p["exp"]) + ' / ' + str(p["exp_to_next"]) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="exp-bar-outer"><div class="exp-bar-inner" style="width:' + str(round(exp_pct,1)) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(
            '<div style="font-size:.82rem;line-height:2.1;color:#ccccee;">'
            '🔥 連続正解 <b style="color:#ffe066;">' + str(streak) + '</b> 問 ' + bonus_html + '<br>'
            '📊 正答率 <b style="color:#ffe066;">' + accuracy + '</b><br>'
            '📝 累計 <b style="color:#ffe066;">' + str(total) + '</b> 問'
            '</div>', unsafe_allow_html=True)
        st.markdown("---")
        if p["hp"] <= 0:
            st.error("HPが0！正解するとHP回復します")
        if st.button("💾 セーブ", use_container_width=True):
            save_player(st.session_state.player, st.session_state.username)
            st.success("セーブしました！")
        if st.button("🚪 ログアウト", use_container_width=True):
            save_player(st.session_state.player, st.session_state.username)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        with st.expander("開発者メニュー"):
            if st.button("データ削除", use_container_width=True):
                delete_save(st.session_state.username)
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

render_sidebar()


# ─────────────────────────────────────────
# ホーム画面
# ─────────────────────────────────────────
p = st.session_state.player
st.markdown(
    '<div style="font-size:2.5rem;font-weight:700;text-align:center;'
    'background:linear-gradient(135deg,#ffe066,#ffaa00,#ff6600);'
    '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
    'background-clip:text;margin-bottom:4px;">⚔️ 英検Quest ⚔️</div>'
    '<div style="text-align:center;color:#888;margin-bottom:24px;">英単語を制して、伝説の勇者へ</div>',
    unsafe_allow_html=True)

st.markdown(
    '<div class="info-card">'
    '<div style="font-size:.9rem;color:#ccccee;line-height:1.9;">'
    '⚔️ おかえり、<b style="color:#ffe066;">' + p["name"] + '</b>！<br>'
    '現在 <b style="color:#fff;">Lv. ' + str(p["level"]) + '</b> | '
    '英検<b style="color:#fff;">' + _grade_label(p["grade_target"]) + '</b>に挑戦中'
    '</div></div>',
    unsafe_allow_html=True)

st.markdown(
    '<div class="info-card">'
    '<div style="font-size:1.05rem;font-weight:700;color:#ffe066;margin-bottom:10px;">📜 今日のミッション</div>'
    '<div style="font-size:.9rem;color:#ccccee;line-height:1.9;">'
    '✅ クイズを <b style="color:#fff;">10問</b> 解く<br>'
    '✅ 正答率 <b style="color:#fff;">80%</b> 以上を目指す<br>'
    '✅ HPを <b style="color:#fff;">0</b> にしないで完走する'
    '</div></div>'
    '<div class="info-card">'
    '<div style="font-size:1.05rem;font-weight:700;color:#ffe066;margin-bottom:10px;">🗺️ 使い方</div>'
    '<div style="font-size:.9rem;color:#ccccee;line-height:1.9;">'
    '👈 左のサイドバーから <b style="color:#fff;">quest</b> を選んでクイズ開始！<br>'
    '⚔️ 正解すると <b style="color:#ffe066;">EXP獲得</b> → レベルアップ<br>'
    '💔 不正解すると <b style="color:#ff8080;">HPが減少</b><br>'
    '🔥 連続正解で <b style="color:#ffe066;">EXPボーナス</b>（3連続x1.2、5連続x1.5、10連続x2.0）'
    '</div></div>',
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.page_link("pages/01_quest.py", label="⚔️ クエスト開始！", icon="🗡️")
