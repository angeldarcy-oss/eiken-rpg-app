import sys
from pathlib import Path
_root = Path(__file__).parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
from core.save_manager import load_player, save_player, save_exists, delete_save

st.set_page_config(page_title="英検Quest", page_icon="⚔️", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Kaisei+Decol:wght@400;700&family=Noto+Sans+JP:wght@400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans JP', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460); }
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
.hp-bar-outer { background:#2a0a0a; border-radius:8px; height:18px; width:100%; margin:4px 0 12px; overflow:hidden; border:1px solid #5a1a1a; }
.hp-bar-inner { background:linear-gradient(90deg,#e05252,#ff8080); height:100%; border-radius:8px; }
.exp-bar-outer { background:#1a1500; border-radius:8px; height:14px; width:100%; margin:4px 0 12px; overflow:hidden; border:1px solid #5a4a00; }
.exp-bar-inner { background:linear-gradient(90deg,#c8a000,#ffe066); height:100%; border-radius:8px; }
.stat-label { font-size:11px; letter-spacing:.08em; color:#aaaacc !important; text-transform:uppercase; }
.home-title { font-family:'Kaisei Decol',serif; font-size:2.8rem; font-weight:700; text-align:center; background:linear-gradient(135deg,#ffe066,#ffaa00,#ff6600); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; line-height:1.2; margin-bottom:0.2em; }
.home-subtitle { text-align:center; color:#888; font-size:0.95rem; margin-bottom:2rem; }
.info-card { background:linear-gradient(135deg,#1e1e3a,#2a2a4a); border:1px solid #3a3a6a; border-radius:12px; padding:20px 24px; margin-bottom:16px; }
</style>
""", unsafe_allow_html=True)

def _grade_label(k):
    return {"grade_5":"5級","grade_4":"4級","grade_3":"3級","grade_pre2":"準2級","grade_2":"2級"}.get(k, k)

def init_session():
    if "player" not in st.session_state:
        st.session_state.player = load_player()
    if "total_correct" not in st.session_state:
        st.session_state.total_correct = 0
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0
    if "streak" not in st.session_state:
        st.session_state.streak = 0

init_session()

def render_sidebar():
    p = st.session_state.player
    hp_pct = max(0, p["hp"] / p["hp_max"] * 100) if p["hp_max"] > 0 else 0
    exp_pct = min(100, p["exp"] / p["exp_to_next"] * 100) if p["exp_to_next"] > 0 else 0
    streak = st.session_state.streak
    total = st.session_state.total_questions
    correct = st.session_state.total_correct
    accuracy = f"{correct/total*100:.0f}%" if total > 0 else "---"
    name = p['name']
    level = p['level']
    grade = _grade_label(p['grade_target'])
    hp = p['hp']
    hp_max = p['hp_max']
    exp = p['exp']
    exp_to_next = p['exp_to_next']
    total_exp = p.get('total_exp_earned', 0)

    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:16px 0 8px;">'
            '<div style="font-size:3rem;">⚔️</div>'
            '<div style="font-family:serif;font-size:1.3rem;font-weight:700;color:#ffe066;margin-top:8px;">' + name + '</div>'
            '<div style="font-size:.85rem;color:#aaaacc;margin-top:2px;">Lv. ' + str(level) + ' | 英検' + grade + '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown("---")
        st.markdown('<div class="stat-label">HP  ' + str(hp) + ' / ' + str(hp_max) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="hp-bar-outer"><div class="hp-bar-inner" style="width:' + str(hp_pct) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">EXP  ' + str(exp) + ' / ' + str(exp_to_next) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="exp-bar-outer"><div class="exp-bar-inner" style="width:' + str(exp_pct) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(
            '<div style="font-size:.82rem;line-height:2.1;color:#ccccee;">'
            '🔥 連続正解 <b style="color:#ffe066;">' + str(streak) + '</b> 問<br>'
            '📊 累計正答率 <b style="color:#ffe066;">' + accuracy + '</b><br>'
            '📝 累計問題数 <b style="color:#ffe066;">' + str(total) + '</b> 問<br>'
            '💰 累計EXP <b style="color:#ffe066;">' + str(total_exp) + '</b>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown("---")
        if p["hp"] <= 0:
            st.error("HPが0！クエストで正解するとHP回復します。")
        if st.button("💾 セーブする", use_container_width=True):
            save_player(st.session_state.player)
            st.success("セーブしました！")
        with st.expander("開発者メニュー"):
            if st.button("セーブデータ削除", use_container_width=True):
                delete_save()
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

render_sidebar()

st.markdown('<div class="home-title">⚔️ 英検Quest ⚔️</div>', unsafe_allow_html=True)
st.markdown('<div class="home-subtitle">英単語を制して、伝説の勇者へ</div>', unsafe_allow_html=True)

if save_exists():
    p = st.session_state.player
    grade_str = _grade_label(p['grade_target'])
    st.markdown(
        '<div class="info-card"><div style="font-size:.9rem;color:#ccccee;line-height:1.9;">'
        '⚔️ おかえり、<b style="color:#ffe066;">' + p['name'] + '</b>！<br>'
        '現在 <b style="color:#fff;">Lv. ' + str(p['level']) + '</b> | '
        '英検<b style="color:#fff;">' + grade_str + '</b>に挑戦中'
        '</div></div>',
        unsafe_allow_html=True
    )

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
    '👈 左のサイドバーから <b style="color:#fff;">01_quest</b> を選んでクイズ開始！<br>'
    '⚔️ 正解すると <b style="color:#ffe066;">EXP獲得</b> → レベルアップ<br>'
    '💔 不正解すると <b style="color:#ff8080;">HPが減少</b><br>'
    '🔥 連続正解で <b style="color:#ffe066;">EXPボーナス</b>（3連続x1.2、5連続x1.5、10連続x2.0）'
    '</div></div>',
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)
st.page_link("pages/01_quest.py", label="⚔️ クエスト開始！", icon="🗡️")