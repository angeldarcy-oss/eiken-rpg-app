import sys
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.mobile_css import MOBILE_CSS
from core.equipment_bonus import sidebar_bonus_html
from core.nav import render_nav
from core.save_manager import load_player, load_history
from core.player import PlayerManager
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html


st.markdown("""<style>
html,body,[class*="css"]{font-family:'Noto Sans JP',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460);}
[data-testid="stSidebar"] *{color:#e0e0e0 !important;}
.hp-bar-outer{background:#2a0a0a;border-radius:8px;height:18px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a1a1a;}
.hp-bar-inner{background:linear-gradient(90deg,#e05252,#ff8080);height:100%;border-radius:8px;}
.exp-bar-outer{background:#1a1500;border-radius:8px;height:14px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a4a00;}
.exp-bar-inner{background:linear-gradient(90deg,#c8a000,#ffe066);height:100%;border-radius:8px;}
.stat-label{font-size:11px;color:#aaaacc !important;}
.metric-card{background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid #3a3a6a;
border-radius:12px;padding:14px 10px;text-align:center;}
.metric-value{font-size:1.5rem;font-weight:700;color:#ffe066;}
.metric-label{font-size:.72rem;color:#aaaacc;margin-top:2px;}
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

p = st.session_state.player
lang = p.get("language", "ja")
_ja = (lang == "ja")
username = st.session_state.get("username", "")

st.markdown(
    '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">📈 '
    + ("学習記録" if _ja else "學習紀錄") + '</div>'
    '<div style="font-size:.9rem;color:#888;margin-bottom:20px;">'
    + ("がんばりが目に見える！毎日の記録" if _ja else "看得見的努力！每日紀錄") + '</div>',
    unsafe_allow_html=True)

history = load_history(username)

if not history:
    st.info(("まだ記録がありません。クエストを最後までクリアすると記録されます！" if _ja
             else "還沒有紀錄。完成任務後就會留下紀錄！"))
    st.page_link("pages/01_quest.py", label=t("start_quest", lang), icon="⚔️")
    st.stop()

df = pd.DataFrame(history)
df["date"] = pd.to_datetime(df["date"]).dt.date

# ─── 累計サマリー ────────────────────────────────────────────
total_q = int(df["total"].sum())
total_c = int(df["correct"].sum())
overall_acc = round(total_c / total_q * 100) if total_q > 0 else 0
total_exp = int(df["exp_gained"].sum())
study_days = df["date"].nunique()
streak_days = p.get("login_streak", {}).get("streak_days", 0)

_labels = (["といた問題", "正答率", "学習した日", "総獲得EXP"] if _ja
           else ["答題數", "正確率", "學習天數", "總獲得EXP"])
_values = [str(total_q), str(overall_acc) + "%", str(study_days), str(total_exp)]
cols = st.columns(4)
for col, label, value in zip(cols, _labels, _values):
    with col:
        st.markdown(
            '<div class="metric-card"><div class="metric-value">' + value + '</div>'
            '<div class="metric-label">' + label + '</div></div>',
            unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── 日別グラフ（直近14日、データのない日は0で埋める） ──────
daily = df.groupby("date").agg(
    total=("total", "sum"), correct=("correct", "sum"), exp=("exp_gained", "sum")
)
last14 = [date.today() - timedelta(days=i) for i in range(13, -1, -1)]
daily = daily.reindex(last14, fill_value=0)
daily.index = [d.strftime("%m/%d") for d in daily.index]

st.markdown('<div style="font-size:1.05rem;font-weight:700;color:#ffe066;">📊 '
            + ("毎日の問題数（14日間）" if _ja else "每日答題數（14天）") + '</div>',
            unsafe_allow_html=True)
st.bar_chart(daily[["total", "correct"]].rename(
    columns={"total": ("問題数" if _ja else "題數"), "correct": ("正解" if _ja else "答對")}),
    color=["#4a4a8a", "#ffe066"], height=220)

st.markdown('<div style="font-size:1.05rem;font-weight:700;color:#ffe066;">⚡ '
            + ("毎日の獲得EXP（14日間）" if _ja else "每日獲得EXP（14天）") + '</div>',
            unsafe_allow_html=True)
st.bar_chart(daily[["exp"]].rename(columns={"exp": "EXP"}), color=["#ffaa00"], height=200)

# ─── 正答率の推移（記録のある日のみ） ───────────────────────
acc_daily = df.groupby("date").agg(total=("total", "sum"), correct=("correct", "sum"))
acc_daily = acc_daily[acc_daily["total"] > 0].tail(30)
if len(acc_daily) >= 2:
    acc_daily[("正答率%" if _ja else "正確率%")] = (acc_daily["correct"] / acc_daily["total"] * 100).round(1)
    acc_daily.index = [d.strftime("%m/%d") for d in acc_daily.index]
    st.markdown('<div style="font-size:1.05rem;font-weight:700;color:#ffe066;">🎯 '
                + ("正答率のへんか" if _ja else "正確率變化") + '</div>',
                unsafe_allow_html=True)
    st.line_chart(acc_daily[[("正答率%" if _ja else "正確率%")]], color=["#88ff88"], height=200)

# ─── 最近のクエスト一覧 ─────────────────────────────────────
st.markdown('<div style="font-size:1.05rem;font-weight:700;color:#ffe066;margin-top:8px;">📜 '
            + ("さいきんのクエスト" if _ja else "最近的任務") + '</div>',
            unsafe_allow_html=True)
recent = df.head(10)
for _, r in recent.iterrows():
    acc = round(float(r["accuracy"]))
    acc_color = "#88ff88" if acc >= 75 else ("#ffe066" if acc >= 50 else "#ff8080")
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid #3a3a6a;'
        'border-radius:10px;padding:8px 14px;margin-bottom:6px;display:flex;'
        'justify-content:space-between;align-items:center;font-size:.85rem;">'
        '<span style="color:#aaaacc;">' + str(r["date"]) + ' ' + grade_label(str(r["grade"]), lang) + '</span>'
        '<span style="color:#ccccee;">' + str(r["correct"]) + '/' + str(r["total"]) + '問 '
        '<b style="color:' + acc_color + ';">' + str(acc) + '%</b>'
        ' <span style="color:#ffaa00;">+' + str(r["exp_gained"]) + 'EXP</span></span>'
        '</div>', unsafe_allow_html=True)
