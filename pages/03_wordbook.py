import sys
import streamlit as st
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.save_manager import load_player, save_player, get_user_save_path
from core.player import PlayerManager
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html

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


def init_session():
    if "player" not in st.session_state or st.session_state.player is None:
        st.session_state.player = load_player(st.session_state.get("username", ""))
    for k, v in [("total_correct", 0), ("total_questions", 0), ("streak", 0)]:
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


def render_sidebar():
    p = st.session_state.player
    lang = p.get("language", "ja")
    pm = PlayerManager(p)
    hp_pct = pm.hp_percent() * 100
    exp_pct = pm.exp_percent() * 100
    char_id = p.get("character", "")
    equip = p.get("equipment")
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:12px 0 6px;">'
            + sidebar_avatar_html(char_id, equip) +
            '<div style="font-size:1.2rem;font-weight:700;color:#ffe066;margin-top:6px;">' + p["name"] + '</div>'
            '<div style="font-size:.8rem;color:#aaaacc;">' + t("level", lang) + ' ' + str(p["level"]) + ' | ' + grade_label(p["grade_target"], lang) + '</div>'
            '</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="stat-label">' + t("hp", lang) + ' ' + str(p["hp"]) + ' / ' + str(p["hp_max"]) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="hp-bar-outer"><div class="hp-bar-inner" style="width:' + str(round(hp_pct, 1)) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">' + t("exp", lang) + ' ' + str(p["exp"]) + ' / ' + str(p["exp_to_next"]) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="exp-bar-outer"><div class="exp-bar-inner" style="width:' + str(round(exp_pct, 1)) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown("---")

render_sidebar()


# ─────────────────────────────────────────
# メイン画面
# ─────────────────────────────────────────
p = st.session_state.player
lang = p.get("language", "ja")

st.markdown(
    '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">' + t("wordbook_title", lang) + '</div>'
    '<div style="font-size:.9rem;color:#888;margin-bottom:24px;">' + t("wordbook_subtitle", lang) + '</div>',
    unsafe_allow_html=True)

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

session_weak = []
if "engine" in st.session_state and st.session_state.engine is not None:
    engine = st.session_state.engine
    weak_df = engine.get_weak_words(top_n=50)
    if not weak_df.empty:
        for _, row in weak_df.iterrows():
            session_weak.append({
                "word": row["word"],
                "meaning_ja": row["meaning_ja"],
                "meaning_zh": "" if str(row.get("meaning_zh", "")) == "nan" else str(row.get("meaning_zh", "")),
                "miss_count": int(row["miss_count"]),
                "hint": row.get("hint", ""),
                "example_en": str(row.get("example_en", "")),
                "example_ja": str(row.get("example_ja", "")),
            })

display_words = session_weak if session_weak else weak_words

if not display_words:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;'
        'border-radius:12px;padding:40px;text-align:center;">'
        '<div style="font-size:3rem;margin-bottom:16px;">🎉</div>'
        '<div style="font-size:1.1rem;color:#ffe066;margin-bottom:8px;">' + t("no_weak", lang) + '</div>'
        '<div style="font-size:.9rem;color:#888;">' + t("no_weak_sub", lang) + '</div>'
        '</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.page_link("pages/01_quest.py", label=t("start_quest_link", lang), icon="🗡️")
else:
    total_weak = len(display_words)
    total_misses = sum(w.get("miss_count", 1) for w in display_words)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '<div style="background:#1a1a3a;border-radius:10px;padding:16px;text-align:center;">'
            '<div style="font-size:.8rem;color:#888;">' + t("weak_count", lang) + '</div>'
            '<div style="font-size:2rem;color:#ff8080;font-weight:700;">' + str(total_weak) + '</div>'
            '</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(
            '<div style="background:#1a1a3a;border-radius:10px;padding:16px;text-align:center;">'
            '<div style="font-size:.8rem;color:#888;">' + t("miss_count", lang) + '</div>'
            '<div style="font-size:2rem;color:#ffaa44;font-weight:700;">' + str(total_misses) + '</div>'
            '</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    sort_options = [t("sort_most", lang), t("sort_least", lang), t("sort_alpha", lang)]
    sort_option = st.selectbox(t("sort_label", lang), sort_options)

    if sort_option == sort_options[0]:
        display_words = sorted(display_words, key=lambda x: x.get("miss_count", 1), reverse=True)
    elif sort_option == sort_options[1]:
        display_words = sorted(display_words, key=lambda x: x.get("miss_count", 1))
    else:
        display_words = sorted(display_words, key=lambda x: x.get("word", ""))

    st.markdown("<br>", unsafe_allow_html=True)

    for w in display_words:
        miss = w.get("miss_count", 1)
        word = w.get("word", "")
        meaning_zh = w.get("meaning_zh", "")
        meaning_ja = w.get("meaning_ja", "")
        meaning = meaning_zh if (lang == "zh" and meaning_zh) else meaning_ja
        hint = w.get("hint", "")
        example_en = w.get("example_en", "")
        example_ja = w.get("example_ja", "")

        card_class = "word-card-danger" if miss >= 3 else "word-card"
        miss_color = "#ff8080" if miss >= 3 else "#ffaa44"
        miss_label = t("miss_label", lang).format(n=miss)

        hint_html = '<div style="font-size:.8rem;color:#aaaa88;margin-top:6px;">💡 ' + hint + '</div>' if hint else ""
        example_html = (
            '<div style="font-size:.85rem;color:#aaaacc;font-style:italic;margin-top:8px;">'
            '📖 ' + example_en + '<br>' + example_ja + '</div>'
        ) if example_en else ""

        st.markdown(
            '<div class="' + card_class + '">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
            '<span style="font-size:1.4rem;font-weight:700;color:#ffe066;">' + word + '</span>'
            '<span style="background:#2a0a0a;color:' + miss_color + ';border-radius:6px;padding:3px 10px;font-size:.85rem;">' + miss_label + '</span>'
            '</div>'
            '<div style="font-size:1rem;color:#e0e0e0;margin-bottom:4px;">' + meaning + '</div>'
            + example_html + hint_html +
            '</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.page_link("pages/01_quest.py", label=t("review_link", lang), icon="🗡️")
