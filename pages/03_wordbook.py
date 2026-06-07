import sys
import streamlit as st
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.save_manager import load_player, save_player, get_user_save_path
from core.player import PlayerManager

st.set_page_config(page_title="単語帳 | 英検Quest", page_icon="📖", layout="centered", initial_sidebar_state="expanded")

st.markdown("""<style>
html,body,[class*="css"]{font-family:'Noto Sans JP',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460);}
[data-testid="stSidebar"] *{color:#e0e0e0 !important;}
.hp-bar-outer{background:#2a0a0a;border-radius:8px;height:18px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a1a1a;}
.hp-bar-inner{background:linear-gradient(90deg,#e05252,#ff8080);height:100%;border-radius:8px;}
.exp-bar-outer{background:#1a1500;border-radius:8px;height:14px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a4a00;}
.exp-bar-inner{background:linear-gradient(90deg,#c8a000,#ffe066);height:100%;border-radius:8px;}
.stat-label{font-size:11px;color:#aaaacc !important;}
.word-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;border-radius:12px;padding:20px 24px;margin-bottom:12px;}
.word-card-danger{background:linear-gradient(135deg,#2a0a0a,#3a1a1a);border:1px solid #7a2a2a;border-radius:12px;padding:20px 24px;margin-bottom:12px;}
</style>""", unsafe_allow_html=True)


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
    '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">📖 単語帳</div>'
    '<div style="font-size:.9rem;color:#888;margin-bottom:24px;">クエストで間違えた単語を復習しよう</div>',
    unsafe_allow_html=True)

# セーブデータから苦手単語を読み込む
import json

weak_words = []
username = st.session_state.get("username", "")
if username:
    save_path = get_user_save_path(username)
    if save_path.exists():
        try:
            with open(save_path, encoding="utf-8") as f:
                data = json.load(f)
            weak_words = data.get("weak_words", [])
        except Exception:
            weak_words = []

# engineがあればセッション中の苦手単語も取得
session_weak = []
if "engine" in st.session_state and st.session_state.engine is not None:
    engine = st.session_state.engine
    weak_df = engine.get_weak_words(top_n=50)
    if not weak_df.empty:
        for _, row in weak_df.iterrows():
            session_weak.append({
                "word": row["word"],
                "meaning_ja": row["meaning_ja"],
                "miss_count": int(row["miss_count"]),
                "hint": row.get("hint", ""),
            })

# 表示する単語リストを決定（セッション中 > 保存済み）
display_words = session_weak if session_weak else weak_words

if not display_words:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;'
        'border-radius:12px;padding:40px;text-align:center;">'
        '<div style="font-size:3rem;margin-bottom:16px;">🎉</div>'
        '<div style="font-size:1.1rem;color:#ffe066;margin-bottom:8px;">苦手単語はまだありません！</div>'
        '<div style="font-size:.9rem;color:#888;">クエストに挑戦すると、間違えた単語がここに記録されます。</div>'
        '</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.page_link("pages/01_quest.py", label="⚔️ クエストに挑戦する", icon="🗡️")
else:
    # 統計表示
    total_weak = len(display_words)
    total_misses = sum(w.get("miss_count", 1) for w in display_words)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '<div style="background:#1a1a3a;border-radius:10px;padding:16px;text-align:center;">'
            '<div style="font-size:.8rem;color:#888;">苦手単語数</div>'
            '<div style="font-size:2rem;color:#ff8080;font-weight:700;">' + str(total_weak) + '</div>'
            '</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(
            '<div style="background:#1a1a3a;border-radius:10px;padding:16px;text-align:center;">'
            '<div style="font-size:.8rem;color:#888;">累計ミス数</div>'
            '<div style="font-size:2rem;color:#ffaa44;font-weight:700;">' + str(total_misses) + '</div>'
            '</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # フィルター
    sort_option = st.selectbox("並び順", ["ミス回数が多い順", "ミス回数が少ない順", "単語のアルファベット順"])

    if sort_option == "ミス回数が多い順":
        display_words = sorted(display_words, key=lambda x: x.get("miss_count", 1), reverse=True)
    elif sort_option == "ミス回数が少ない順":
        display_words = sorted(display_words, key=lambda x: x.get("miss_count", 1))
    else:
        display_words = sorted(display_words, key=lambda x: x.get("word", ""))

    st.markdown("<br>", unsafe_allow_html=True)

    # 単語カード表示
    for w in display_words:
        miss = w.get("miss_count", 1)
        word = w.get("word", "")
        meaning = w.get("meaning_ja", "")
        hint = w.get("hint", "")
        example_en = w.get("example_en", "")
        example_ja = w.get("example_ja", "")

        # ミス回数に応じてカードの色を変える
        card_class = "word-card-danger" if miss >= 3 else "word-card"
        miss_color = "#ff8080" if miss >= 3 else "#ffaa44"

        hint_html = '<div style="font-size:.8rem;color:#aaaa88;margin-top:6px;">💡 ' + hint + '</div>' if hint else ""
        example_html = (
            '<div style="font-size:.85rem;color:#aaaacc;font-style:italic;margin-top:8px;">'
            '📖 ' + example_en + '<br>' + example_ja + '</div>'
        ) if example_en else ""

        st.markdown(
            '<div class="' + card_class + '">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
            '<span style="font-size:1.4rem;font-weight:700;color:#ffe066;">' + word + '</span>'
            '<span style="background:#2a0a0a;color:' + miss_color + ';border-radius:6px;padding:3px 10px;font-size:.85rem;">×' + str(miss) + ' ミス</span>'
            '</div>'
            '<div style="font-size:1rem;color:#e0e0e0;margin-bottom:4px;">' + meaning + '</div>'
            + example_html + hint_html +
            '</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.page_link("pages/01_quest.py", label="⚔️ クエストで復習する", icon="🗡️")
