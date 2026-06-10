import sys
import streamlit as st
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.mobile_css import MOBILE_CSS
from core.equipment_bonus import sidebar_bonus_html
from core.nav import render_nav

from core.save_manager import load_player, save_player, load_rankings, update_ranking
from core.player import PlayerManager
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html, CHARACTERS
from core.titles import title_badge_html, _TITLE_MAP as _TITLES_MAP



st.markdown("""<style>
html,body,[class*="css"]{font-family:'Noto Sans JP',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460);}
[data-testid="stSidebar"] *{color:#e0e0e0 !important;}
.hp-bar-outer{background:#2a0a0a;border-radius:8px;height:18px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a1a1a;}
.hp-bar-inner{background:linear-gradient(90deg,#e05252,#ff8080);height:100%;border-radius:8px;}
.exp-bar-outer{background:#1a1500;border-radius:8px;height:14px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a4a00;}
.exp-bar-inner{background:linear-gradient(90deg,#c8a000,#ffe066);height:100%;border-radius:8px;}
.stat-label{font-size:11px;color:#aaaacc !important;}
.rank-row{border-radius:10px;padding:10px 14px;margin-bottom:8px;display:flex;align-items:center;gap:12px;}
.rank-row-me{background:linear-gradient(135deg,#2a2000,#3a3010);border:2px solid #ffe066;}
.rank-row-other{background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid #3a3a6a;}
.rank-row-top3{background:linear-gradient(135deg,#1e1800,#2e2a00);border:1px solid #aa8800;}
</style>""", unsafe_allow_html=True)
st.markdown(MOBILE_CSS, unsafe_allow_html=True)


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

# ─── 自分のデータをランキングに反映 ───
username = st.session_state.get("username", "")
update_ranking(st.session_state.player, username)

p = st.session_state.player
lang = p.get("language", "ja")

st.markdown(
    '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">🏆 ランキング</div>'
    '<div style="font-size:.9rem;color:#888;margin-bottom:20px;">全プレイヤーとスコアを競おう！</div>',
    unsafe_allow_html=True)

data = load_rankings()
users = data.get("users", {})

if not users:
    st.info("まだランキングデータがありません。クエストをプレイしてランクインしよう！")
    st.stop()

tab_weekly, tab_alltime, tab_streak, tab_boss = st.tabs(["📅 週間ランキング", "🌟 総合ランキング", "🔥 ベストストリーク", "👑 ボス撃破"])

RANK_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
GRADE_LABELS = {
    "grade_5": "5級", "grade_4": "4級", "grade_3": "3級",
    "grade_pre2": "準2級", "grade_2": "2級",
}


def _char_svg_small(char_id: str) -> str:
    if char_id and char_id in CHARACTERS:
        return '<div style="width:36px;height:45px;flex-shrink:0;">' + CHARACTERS[char_id]["svg"] + '</div>'
    return '<div style="font-size:1.8rem;flex-shrink:0;">⚔️</div>'


def render_ranking(entries: list, sort_key: str, stat_label: str, stat_fmt):
    sorted_entries = sorted(entries, key=lambda x: x[sort_key], reverse=True)
    my_rank = next((i + 1 for i, e in enumerate(sorted_entries) if e["username"] == username), None)

    if my_rank:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#1a1a2e,#2a2a4a);border:1px solid #3a3a6a;'
            f'border-radius:10px;padding:10px 16px;margin-bottom:16px;font-size:.9rem;color:#ffe066;">'
            f'あなたの順位：<b style="font-size:1.3rem;">{my_rank}位</b> / {len(sorted_entries)}人中'
            f'</div>', unsafe_allow_html=True)

    for i, entry in enumerate(sorted_entries[:20]):
        rank = i + 1
        is_me = entry["username"] == username
        is_top3 = rank <= 3
        row_class = "rank-row-me" if is_me else ("rank-row-top3" if is_top3 else "rank-row-other")
        medal = RANK_MEDALS.get(rank, str(rank))
        stat_val = stat_fmt(entry)
        grade = GRADE_LABELS.get(entry.get("grade_target", ""), "")
        name_color = "#ffe066" if is_me else "#ffffff"
        me_badge = ' <span style="background:#ffe066;color:#1a1a2e;font-size:.65rem;padding:1px 6px;border-radius:10px;font-weight:700;">YOU</span>' if is_me else ""

        _title_html = ""
        _tid = entry.get("active_title") or (entry.get("titles") or [None])[0]
        if _tid and _tid in _TITLES_MAP:
            _td = _TITLES_MAP[_tid]
            _title_html = (
                ' <span style="background:linear-gradient(135deg,#2a1800,#3a2800);'
                'border:1px solid #886600;border-radius:8px;padding:1px 6px;'
                'font-size:.6rem;color:#ffcc44;white-space:nowrap;">'
                + _td["icon"] + " " + _td["name"] + "</span>"
            )
        st.markdown(
            f'<div class="rank-row {row_class}">'
            f'<div style="font-size:1.4rem;min-width:36px;text-align:center;">{medal}</div>'
            + _char_svg_small(entry.get("character", "")) +
            f'<div style="flex:1;min-width:0;">'
            f'<div style="font-size:.95rem;font-weight:700;color:{name_color};">{entry["name"]}{me_badge}{_title_html}</div>'
            f'<div style="font-size:.72rem;color:#aaaacc;">Lv{entry["level"]} | 英検{grade}</div>'
            f'</div>'
            f'<div style="text-align:right;flex-shrink:0;">'
            f'<div style="font-size:1.05rem;font-weight:700;color:#ffe066;">{stat_val}</div>'
            f'<div style="font-size:.7rem;color:#888;">{stat_label}</div>'
            f'</div>'
            f'</div>', unsafe_allow_html=True)

    if len(sorted_entries) > 20:
        st.markdown(f'<div style="color:#666;font-size:.82rem;text-align:center;margin-top:8px;">他 {len(sorted_entries)-20} 人</div>', unsafe_allow_html=True)


all_entries = [{"username": uname, **udata} for uname, udata in users.items()]

with tab_weekly:
    st.markdown('<div style="font-size:.85rem;color:#888;margin-bottom:12px;">今週（月曜日リセット）の正解数ランキング</div>', unsafe_allow_html=True)
    weekly_entries = [e for e in all_entries if e.get("weekly_total", 0) > 0]
    if not weekly_entries:
        st.info("今週のデータがまだありません。クエストで最初の回答をしよう！")
    else:
        def weekly_fmt(e):
            wc = e.get("weekly_correct", 0)
            wt = e.get("weekly_total", 0)
            acc = round(wc / wt * 100) if wt > 0 else 0
            return f"{wc}問正解 ({acc}%)"
        render_ranking(weekly_entries, "weekly_correct", "今週の正解", weekly_fmt)

with tab_alltime:
    st.markdown('<div style="font-size:.85rem;color:#888;margin-bottom:12px;">累計獲得EXP総合ランキング</div>', unsafe_allow_html=True)
    def alltime_fmt(e):
        return f"{e.get('total_exp', 0):,} EXP"
    render_ranking(all_entries, "total_exp", "累計EXP", alltime_fmt)

with tab_streak:
    st.markdown('<div style="font-size:.85rem;color:#888;margin-bottom:12px;">連続正解の最高記録ランキング</div>', unsafe_allow_html=True)
    streak_entries = [e for e in all_entries if e.get("best_streak", e.get("max_streak", 0)) > 0]
    if not streak_entries:
        st.info("まだ連続正解記録がありません。クエストで連続正解に挑戦しよう！")
    else:
        # best_streak を正規化（旧データは max_streak で補完）
        for e in streak_entries:
            if "best_streak" not in e:
                e["best_streak"] = e.get("max_streak", 0)
        def streak_fmt(e):
            bs = e.get("best_streak", e.get("max_streak", 0))
            return f"{bs} 問連続"
        render_ranking(streak_entries, "best_streak", "最高連続正解", streak_fmt)

with tab_boss:
    st.markdown('<div style="font-size:.85rem;color:#888;margin-bottom:12px;">週替わりボスの累計撃破数ランキング</div>', unsafe_allow_html=True)
    boss_entries = [e for e in all_entries if e.get("boss_defeats", 0) > 0]
    if not boss_entries:
        st.info("まだボス撃破記録がありません。クエストで5体倒してボスに挑戦しよう！")
    else:
        def boss_fmt(e):
            bd = e.get("boss_defeats", 0)
            return f"{bd} 体"
        render_ranking(boss_entries, "boss_defeats", "撃破数", boss_fmt)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<div style="font-size:.8rem;color:#555;text-align:center;">'
    'ランキングはセーブ時に自動更新されます'
    '</div>', unsafe_allow_html=True)
