import sys
from pathlib import Path
_root = Path(__file__).parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
from core.save_manager import save_player, delete_save, update_ranking
from core.player import PlayerManager, streak_multiplier, STREAK_BONUS_TABLE
from core.i18n import t, grade_label
from core.characters import get_character, sidebar_avatar_html
from core.nav import render_nav
from core.equipment_bonus import sidebar_bonus_html
from core.mobile_css import MOBILE_CSS


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
        _bhtml = sidebar_bonus_html(p)
        if _bhtml:
            st.markdown(_bhtml, unsafe_allow_html=True)
        st.markdown("---")
        render_nav(lang)


def render():
    p = st.session_state.player
    lang = p.get("language", "ja")
    c = get_character(p.get("character", ""))

    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

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


render_sidebar()
render()
