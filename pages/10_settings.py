import sys
import streamlit as st
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.mobile_css import MOBILE_CSS
from core.equipment_bonus import sidebar_bonus_html
from core.nav import render_nav

from core.save_manager import load_player, save_player, delete_save
from core.player import PlayerManager, new_player
from core.i18n import t, grade_label, LANG_OPTIONS
from core.characters import CHARACTERS, CHARACTER_ORDER, get_character, sidebar_avatar_html

_page_lang = (st.session_state.get("player") or {}).get("language", "ja")
st.set_page_config(page_title=(t("pt_settings", _page_lang) + " | 英検Quest"), page_icon="⚙️", layout="centered", initial_sidebar_state="expanded")

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
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

_CHAR_CARD_CSS = """<style>
.char-mini-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:2px solid #3a3a6a;border-radius:12px;padding:12px 8px;text-align:center;margin-bottom:4px;}
.char-mini-selected{border-color:#ffe066 !important;background:linear-gradient(135deg,#2a2000,#3a3000) !important;}
</style>"""
st.markdown(_CHAR_CARD_CSS, unsafe_allow_html=True)

GRADE_OPTIONS = {
    "grade_5": "英検5級",
    "grade_4": "英検4級",
    "grade_3": "英検3級",
    "grade_pre2": "英検準2級",
    "grade_2": "英検2級",
}


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
        _bhtml = sidebar_bonus_html(p)
        if _bhtml:
            st.markdown(_bhtml, unsafe_allow_html=True)
        st.markdown("---")
        render_nav(lang)

render_sidebar()


# ─────────────────────────────────────────
# メイン画面
# ─────────────────────────────────────────
p = st.session_state.player
lang = p.get("language", "ja")

st.markdown(
    '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">' + t("settings_title", lang) + '</div>'
    '<div style="font-size:.9rem;color:#888;margin-bottom:24px;">' + t("settings_subtitle", lang) + '</div>',
    unsafe_allow_html=True)

# ── 現在のステータス表示 ──
st.markdown(
    '<div class="setting-card">'
    '<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:16px;">' + t("player_info_title", lang) + '</div>'
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">'
    '<div style="background:#1a1a3a;border-radius:8px;padding:12px;">'
    '<div style="font-size:.75rem;color:#888;">' + t("info_name", lang) + '</div>'
    '<div style="font-size:1.1rem;color:#fff;font-weight:700;">' + p["name"] + '</div>'
    '</div>'
    '<div style="background:#1a1a3a;border-radius:8px;padding:12px;">'
    '<div style="font-size:.75rem;color:#888;">' + t("info_level", lang) + '</div>'
    '<div style="font-size:1.1rem;color:#ffe066;font-weight:700;">' + t("level", lang) + ' ' + str(p["level"]) + '</div>'
    '</div>'
    '<div style="background:#1a1a3a;border-radius:8px;padding:12px;">'
    '<div style="font-size:.75rem;color:#888;">' + t("info_grade", lang) + '</div>'
    '<div style="font-size:1.1rem;color:#88aaff;font-weight:700;">' + grade_label(p["grade_target"], lang) + '</div>'
    '</div>'
    '<div style="background:#1a1a3a;border-radius:8px;padding:12px;">'
    '<div style="font-size:.75rem;color:#888;">' + t("info_total_exp", lang) + '</div>'
    '<div style="font-size:1.1rem;color:#ffcc44;font-weight:700;">' + str(p.get("total_exp_earned", 0)) + '</div>'
    '</div>'
    '</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 名前変更 ──
st.markdown('<div class="setting-card">', unsafe_allow_html=True)
st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:12px;">' + t("change_name_title", lang) + '</div>', unsafe_allow_html=True)

new_name = st.text_input(t("new_name_label", lang), value=p["name"], max_chars=10, placeholder=t("new_name_ph", lang))

if st.button(t("save_name_btn", lang), use_container_width=True):
    if new_name.strip():
        st.session_state.player["name"] = new_name.strip()
        save_player(st.session_state.player, st.session_state.get("username", ""))
        st.success(t("name_saved_msg", lang).format(name=new_name.strip()))
        st.rerun()
    else:
        st.error(t("name_empty_err", lang))

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 挑戦級変更 ──
st.markdown('<div class="setting-card">', unsafe_allow_html=True)
st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:4px;">' + t("change_grade_title", lang) + '</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.85rem;color:#888;margin-bottom:12px;">' + t("change_grade_note", lang) + '</div>', unsafe_allow_html=True)

grade_keys = list(GRADE_OPTIONS.keys())
grade_labels_ja = list(GRADE_OPTIONS.values())
current_index = grade_keys.index(p["grade_target"]) if p["grade_target"] in grade_keys else 1

selected_grade_label = st.selectbox(t("grade_select_label", lang), grade_labels_ja, index=current_index)
selected_grade_key = grade_keys[grade_labels_ja.index(selected_grade_label)]

if st.button(t("save_grade_btn", lang), use_container_width=True):
    st.session_state.player["grade_target"] = selected_grade_key
    if "engine" in st.session_state:
        del st.session_state["engine"]
    if "current_question" in st.session_state:
        del st.session_state["current_question"]
    save_player(st.session_state.player, st.session_state.get("username", ""))
    st.success(t("grade_saved_msg", lang).format(grade=selected_grade_label))
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 言語設定 ──
st.markdown('<div class="setting-card">', unsafe_allow_html=True)
st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:12px;">' + t("lang_setting_title", lang) + '</div>', unsafe_allow_html=True)

lang_labels = list(LANG_OPTIONS.keys())
lang_codes = list(LANG_OPTIONS.values())
current_lang_index = lang_codes.index(lang) if lang in lang_codes else 0

selected_lang_label = st.selectbox(t("lang_select_label", lang), lang_labels, index=current_lang_index)
selected_lang_code = LANG_OPTIONS[selected_lang_label]

if st.button(("💾 言語を保存" if lang == "ja" else "💾 儲存語言"), use_container_width=True):
    st.session_state.player["language"] = selected_lang_code
    save_player(st.session_state.player, st.session_state.get("username", ""))
    # 言語が変わったのでエンジンを破棄（次回クエスト時に新しい言語で再生成される）
    for key in ["engine", "current_question", "quest_finished", "answered", "last_result",
                "session_correct", "session_total", "ai_explanation", "last_gain_result"]:
        if key in st.session_state:
            del st.session_state[key]
    st.success(t("lang_saved_msg", selected_lang_code))
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── キャラクター変更 ──
st.markdown('<div class="setting-card">', unsafe_allow_html=True)
st.markdown(
    '<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:4px;">キャラクター変更</div>'
    '<div style="font-size:.85rem;color:#888;margin-bottom:16px;">冒険を共にするキャラクターを選び直せます</div>',
    unsafe_allow_html=True)

current_char = p.get("character", "")
char_cols_per_row = 2
char_rows = [CHARACTER_ORDER[i:i+char_cols_per_row] for i in range(0, len(CHARACTER_ORDER), char_cols_per_row)]

for char_row in char_rows:
    ccols = st.columns(char_cols_per_row)
    for ccol, char_id in zip(ccols, char_row):
        c = CHARACTERS[char_id]
        is_selected = (char_id == current_char)
        border_color = "#ffe066" if is_selected else "#3a3a6a"
        bg = "linear-gradient(135deg,#2a2000,#3a3000)" if is_selected else "linear-gradient(135deg,#1e1e3a,#2a2a4a)"
        with ccol:
            st.markdown(
                f'<div style="background:{bg};border:2px solid {border_color};border-radius:12px;'
                f'padding:10px 8px;text-align:center;margin-bottom:4px;">'
                f'<div style="width:60px;height:75px;margin:0 auto;">{c["svg"]}</div>'
                f'<div style="font-size:.95rem;font-weight:700;color:#ffe066;margin-top:6px;">{c["name"]}</div>'
                f'<div style="font-size:.7rem;color:#aa88ff;">{c["title"]}</div>'
                f'</div>',
                unsafe_allow_html=True)
            btn_label = "✓ 選択中" if is_selected else "変更する"
            btn_type = "primary" if not is_selected else "secondary"
            if st.button(btn_label, key=f"settings_char_{char_id}", use_container_width=True, type=btn_type):
                st.session_state.player["character"] = char_id
                save_player(st.session_state.player, st.session_state.get("username", ""))
                st.success(f"{c['name']}（{c['title']}）に変更しました！")
                st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 危険ゾーン ──
st.markdown('<div style="background:linear-gradient(135deg,#2a0a0a,#3a1010);border:1px solid #7a2a2a;border-radius:12px;padding:24px;margin-bottom:16px;">', unsafe_allow_html=True)
st.markdown('<div style="font-size:1rem;font-weight:700;color:#ff8080;margin-bottom:4px;">' + t("danger_title", lang) + '</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.85rem;color:#cc8888;margin-bottom:16px;">' + t("danger_note", lang) + '</div>', unsafe_allow_html=True)

confirm = st.checkbox(t("reset_confirm_label", lang))
if confirm:
    if st.button(t("reset_btn", lang), use_container_width=True):
        delete_save(st.session_state.get("username", ""))
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success(t("reset_done_msg", lang))
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
