import sys
import streamlit as st
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.save_manager import load_player, save_player, delete_save
from core.player import PlayerManager, new_player

st.set_page_config(page_title="設定 | 英検Quest", page_icon="⚙️", layout="centered", initial_sidebar_state="expanded")

st.markdown("""<style>
html,body,[class*="css"]{font-family:'Noto Sans JP',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460);}
[data-testid="stSidebar"] *{color:#e0e0e0 !important;}
.hp-bar-outer{background:#2a0a0a;border-radius:8px;height:18px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a1a1a;}
.hp-bar-inner{background:linear-gradient(90deg,#e05252,#ff8080);height:100%;border-radius:8px;}
.exp-bar-outer{background:#1a1500;border-radius:8px;height:14px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a4a00;}
.exp-bar-inner{background:linear-gradient(90deg,#c8a000,#ffe066);height:100%;border-radius:8px;}
.stat-label{font-size:11px;color:#aaaacc !important;}
.setting-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;border-radius:12px;padding:24px;margin-bottom:16px;}
</style>""", unsafe_allow_html=True)

GRADE_OPTIONS = {
    "grade_5": "英検5級",
    "grade_4": "英検4級",
    "grade_3": "英検3級",
    "grade_pre2": "英検準2級",
    "grade_2": "英検2級",
}


def _grade_label(k):
    return {"grade_5":"5級","grade_4":"4級","grade_3":"3級","grade_pre2":"準2級","grade_2":"2級"}.get(k,k)


def init_session():
    if "player" not in st.session_state:
        st.session_state.player = load_player(st.session_state.get("username", ""))
    if "total_correct" not in st.session_state:
        st.session_state.total_correct = 0
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0
    if "streak" not in st.session_state:
        st.session_state.streak = 0

init_session()


def render_sidebar():
    p = st.session_state.player
    pm = PlayerManager(p)
    hp_pct = pm.hp_percent() * 100
    exp_pct = pm.exp_percent() * 100
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

render_sidebar()


# ─────────────────────────────────────────
# メイン画面
# ─────────────────────────────────────────
st.markdown(
    '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">⚙️ 設定</div>'
    '<div style="font-size:.9rem;color:#888;margin-bottom:24px;">プレイヤー情報や挑戦級を変更できます</div>',
    unsafe_allow_html=True)

p = st.session_state.player

# ── 現在のステータス表示 ──
st.markdown(
    '<div class="setting-card">'
    '<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:16px;">👤 現在のプレイヤー情報</div>'
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">'
    '<div style="background:#1a1a3a;border-radius:8px;padding:12px;">'
    '<div style="font-size:.75rem;color:#888;">名前</div>'
    '<div style="font-size:1.1rem;color:#fff;font-weight:700;">' + p["name"] + '</div>'
    '</div>'
    '<div style="background:#1a1a3a;border-radius:8px;padding:12px;">'
    '<div style="font-size:.75rem;color:#888;">レベル</div>'
    '<div style="font-size:1.1rem;color:#ffe066;font-weight:700;">Lv. ' + str(p["level"]) + '</div>'
    '</div>'
    '<div style="background:#1a1a3a;border-radius:8px;padding:12px;">'
    '<div style="font-size:.75rem;color:#888;">挑戦級</div>'
    '<div style="font-size:1.1rem;color:#88aaff;font-weight:700;">英検' + _grade_label(p["grade_target"]) + '</div>'
    '</div>'
    '<div style="background:#1a1a3a;border-radius:8px;padding:12px;">'
    '<div style="font-size:.75rem;color:#888;">累計EXP</div>'
    '<div style="font-size:1.1rem;color:#ffcc44;font-weight:700;">' + str(p.get("total_exp_earned", 0)) + '</div>'
    '</div>'
    '</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 名前変更 ──
st.markdown('<div class="setting-card">', unsafe_allow_html=True)
st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:12px;">✏️ 名前を変更する</div>', unsafe_allow_html=True)

new_name = st.text_input("新しい名前", value=p["name"], max_chars=10, placeholder="10文字以内で入力")

if st.button("💾 名前を保存", use_container_width=True):
    if new_name.strip():
        st.session_state.player["name"] = new_name.strip()
        save_player(st.session_state.player, st.session_state.get("username", ""))
        st.success("✅ 名前を「" + new_name.strip() + "」に変更しました！")
        st.rerun()
    else:
        st.error("名前を入力してください")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 挑戦級変更 ──
st.markdown('<div class="setting-card">', unsafe_allow_html=True)
st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:4px;">📚 挑戦する英検の級を変更する</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.85rem;color:#888;margin-bottom:12px;">※ 級を変えると出題単語が切り替わります（レベルは維持されます）</div>', unsafe_allow_html=True)

grade_keys = list(GRADE_OPTIONS.keys())
grade_labels = list(GRADE_OPTIONS.values())
current_index = grade_keys.index(p["grade_target"]) if p["grade_target"] in grade_keys else 1

selected_grade_label = st.selectbox("挑戦する級", grade_labels, index=current_index)
selected_grade_key = grade_keys[grade_labels.index(selected_grade_label)]

if st.button("💾 級を保存", use_container_width=True):
    st.session_state.player["grade_target"] = selected_grade_key
    # クイズエンジンをリセット（新しい級で再生成）
    if "engine" in st.session_state:
        del st.session_state["engine"]
    if "current_question" in st.session_state:
        del st.session_state["current_question"]
    save_player(st.session_state.player, st.session_state.get("username", ""))
    st.success("✅ 挑戦級を「" + selected_grade_label + "」に変更しました！")
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 危険ゾーン ──
st.markdown('<div style="background:linear-gradient(135deg,#2a0a0a,#3a1010);border:1px solid #7a2a2a;border-radius:12px;padding:24px;margin-bottom:16px;">', unsafe_allow_html=True)
st.markdown('<div style="font-size:1rem;font-weight:700;color:#ff8080;margin-bottom:4px;">⚠️ データリセット</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.85rem;color:#cc8888;margin-bottom:16px;">レベル・EXP・学習履歴が全て削除されます。この操作は取り消せません。</div>', unsafe_allow_html=True)

confirm = st.checkbox("リセットすることを理解しました")
if confirm:
    if st.button("🗑️ 全データをリセットする", use_container_width=True):
        delete_save(st.session_state.get("username", ""))
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("リセットしました。ホーム画面に戻ってください。")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
