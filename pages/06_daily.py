import sys
import struct as _struct
import math as _math
import base64 as _base64
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from core.mobile_css import MOBILE_CSS

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import json
from core.save_manager import load_player, save_player, get_user_save_path
from core.player import PlayerManager
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html
from core.equipment import ITEMS, QUEST_REWARDS, LOGIN_BONUS_REWARDS, LOGIN_BONUS_THRESHOLDS
from core.daily_quest import (
    QUEST_DEFS, get_or_reset_daily_quests, get_login_streak,
    get_claimable_login_bonuses, claim_login_bonus, claim_quest_reward,
    equip_item, unequip_slot,
)
from core.equipment_bonus import get_all_bonuses, sidebar_bonus_html
from datetime import date as _date

# ── 効果音生成（stdlib のみ） ────────────────────────────────
def _make_wav_b64(notes_durs, sr: int = 8000, vol: float = 0.22) -> str:
    samples = []
    for freq, dur in notes_durs:
        n = int(sr * dur)
        fade = max(1, n // 5)
        for i in range(n):
            s = vol * _math.sin(2 * _math.pi * freq * i / sr)
            if i >= n - fade:
                s *= (n - i) / fade
            samples.append(max(-32767, min(32767, int(s * 32767))))
    raw = _struct.pack('<' + 'h' * len(samples), *samples)
    hdr = (b'RIFF' + _struct.pack('<I', 36 + len(raw)) + b'WAVE'
           + b'fmt ' + _struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16)
           + b'data' + _struct.pack('<I', len(raw)))
    return _base64.b64encode(hdr + raw).decode()


# クエスト達成音：C-E-G-Cの華やかなファンファーレ
_QUEST_WAV = _make_wav_b64([
    (523.25, 0.09), (659.25, 0.09), (783.99, 0.09),
    (1046.50, 0.16), (1318.51, 0.40),
], vol=0.30)

# 全クエスト完了音：より壮大な勝利ファンファーレ
_MEGA_WAV = _make_wav_b64([
    (392.00, 0.07), (523.25, 0.07), (659.25, 0.07),
    (783.99, 0.07), (1046.50, 0.10), (1318.51, 0.10),
    (1567.98, 0.12), (2093.00, 0.15), (1567.98, 0.08),
    (2093.00, 0.55),
], vol=0.33)


def _sound_script(b64: str) -> str:
    return (
        '<script>(function(){'
        'var a=new Audio("data:audio/wav;base64,' + b64 + '");'
        'a.volume=0.85;var p=a.play();if(p)p.catch(function(){});'
        '})();</script>'
    )


def _confetti_component(mega: bool):
    """紙吹雪＋浮かぶ絵文字＋達成音を iframe で再生する"""
    count = 240 if mega else 120
    dur = 240 if mega else 150
    height = 260 if mega else 200
    stars_count = 14 if mega else 7
    # Python 変数として定義し f-string で JS に埋め込む
    emoji_js = '["\\u2728","\\u2b50","\\ud83c\\udf1f","\\ud83d\\udcab","\\ud83c\\udf8a","\\ud83c\\udf89"]' if mega else '["\\u2728","\\u2b50","\\ud83d\\udcab"]'
    b64 = _MEGA_WAV if mega else _QUEST_WAV
    sound_js = _sound_script(b64)

    js = (
        "(function(){"
        "var cvs=document.getElementById('cc');"
        "var W=window.innerWidth||800,H=" + str(height) + ";"
        "cvs.width=W;cvs.height=H;"
        "var ctx=cvs.getContext('2d');"
        "var cols=['#ffe066','#ff6b6b','#4ecdc4','#45b7d1','#aa66ff','#ff9944','#44ffaa','#ff66aa','#66ffdd'];"
        "var ps=[];"
        "for(var i=0;i<" + str(count) + ";i++){"
        "var c=(Math.random()>0.55);"
        "ps.push({"
        "x:Math.random()*W,y:-30-Math.random()*150,"
        "w:c?0:(5+Math.random()*11),h:c?0:(3+Math.random()*6),"
        "r:c?(3+Math.random()*6):0,"
        "col:cols[Math.floor(Math.random()*cols.length)],"
        "vx:(Math.random()-0.5)*5,vy:2.5+Math.random()*5,"
        "rot:Math.random()*360,rv:(Math.random()-0.5)*10,"
        "alpha:1,circle:c"
        "});}"
        "var f=0,D=" + str(dur) + ";"
        "(function draw(){"
        "ctx.clearRect(0,0,W,H);"
        "var fading=(f>D*0.58);"
        "ps.forEach(function(p){"
        "if(fading)p.alpha-=1.8/(D*0.42);"
        "var a=Math.max(0,p.alpha);"
        "ctx.save();ctx.globalAlpha=a;ctx.fillStyle=p.col;"
        "if(p.circle){ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();}"
        "else{ctx.translate(p.x+p.w/2,p.y+p.h/2);ctx.rotate(p.rot*Math.PI/180);"
        "ctx.fillRect(-p.w/2,-p.h/2,p.w,p.h);}"
        "ctx.restore();"
        "p.x+=p.vx;p.y+=p.vy;p.rot+=p.rv;"
        "});"
        "f++;if(f<D)requestAnimationFrame(draw);"
        "else ctx.clearRect(0,0,W,H);"
        "})();"
        "var emojis=" + emoji_js + ";"
        "var sd=document.getElementById('sd');"
        "for(var s=0;s<" + str(stars_count) + ";s++){"
        "var sp=document.createElement('span');"
        "sp.textContent=emojis[Math.floor(Math.random()*emojis.length)];"
        "var delay=(Math.random()*0.7).toFixed(2);"
        "var spd=(1.2+Math.random()*1.6).toFixed(2);"
        "sp.style.cssText='position:absolute;left:'+(4+Math.random()*88)+'%;'"
        "+'font-size:'+(1.1+Math.random()*1.3).toFixed(1)+'rem;'"
        "+'animation:starrise '+spd+'s ease-out '+delay+'s forwards;opacity:0;';"
        "sd.appendChild(sp);}"
        "})();"
    )

    html = (
        "<style>"
        "body{margin:0;padding:0;overflow:hidden;background:transparent;}"
        "#cc{position:absolute;top:0;left:0;width:100%;height:100%;}"
        "#sd{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;}"
        "@keyframes starrise{"
        "0%{transform:translateY(60px) scale(0.4);opacity:0;}"
        "25%{opacity:1;}"
        "100%{transform:translateY(-30px) scale(1.8);opacity:0;}}"
        "</style>"
        "<canvas id='cc'></canvas>"
        "<div id='sd'></div>"
        + sound_js
        + "<script>" + js + "</script>"
    )
    components.html(html, height=height, scrolling=False)


# ────────────────────────────────────────────────────────────
st.set_page_config(page_title="デイリー | 英検Quest", page_icon="📅", layout="centered", initial_sidebar_state="expanded")

st.markdown("""<style>
html,body,[class*="css"]{font-family:'Noto Sans JP',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460);}
[data-testid="stSidebar"] *{color:#e0e0e0 !important;}
.hp-bar-outer{background:#2a0a0a;border-radius:8px;height:18px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a1a1a;}
.hp-bar-inner{background:linear-gradient(90deg,#e05252,#ff8080);height:100%;border-radius:8px;}
.exp-bar-outer{background:#1a1500;border-radius:8px;height:14px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a4a00;}
.exp-bar-inner{background:linear-gradient(90deg,#c8a000,#ffe066);height:100%;border-radius:8px;}
.stat-label{font-size:11px;color:#aaaacc !important;}
.quest-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;border-radius:12px;padding:16px 20px;margin-bottom:10px;}
.quest-done{border-color:#2a7a2a !important;background:linear-gradient(135deg,#0a2a0a,#1a3a1a) !important;}
.quest-done-new{
  border-color:#44ff88 !important;
  background:linear-gradient(135deg,#082a10,#0f3a1a) !important;
  animation:qglow 0.75s ease-in-out 6;
}
@keyframes qglow{
  0%,100%{box-shadow:none;}
  50%{box-shadow:0 0 18px rgba(68,255,136,0.85),0 0 36px rgba(68,255,136,0.35);}
}
.quest-claimed{border-color:#3a3a6a !important;opacity:0.55;}
.check-bounce{display:inline-block;animation:cbounce 0.5s cubic-bezier(.36,1.56,.64,1) both;}
@keyframes cbounce{0%{transform:scale(0);}100%{transform:scale(1);}}
.sparkle-spin{display:inline-block;animation:sspin 1.8s linear infinite;}
@keyframes sspin{to{transform:rotate(360deg);}}
.all-complete-banner{
  background:linear-gradient(135deg,#0a2a08,#1a4a14);
  border:2px solid #44ff88;border-radius:14px;
  padding:22px 20px;text-align:center;margin-bottom:18px;
  animation:allglow 1.2s ease-in-out infinite;
}
@keyframes allglow{
  0%,100%{box-shadow:0 0 8px rgba(68,255,136,0.4);}
  50%{box-shadow:0 0 28px rgba(68,255,136,0.9),0 0 55px rgba(68,255,136,0.35);}
}
</style>""", unsafe_allow_html=True)
st.markdown(MOBILE_CSS, unsafe_allow_html=True)


def init_session():
    if "player" not in st.session_state or st.session_state.player is None:
        st.session_state.player = load_player(st.session_state.get("username", ""))
    for k, v in [("total_correct", 0), ("total_questions", 0), ("streak", 0)]:
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

if not st.session_state.get("_login_streak_updated", False):
    _p_ref = st.session_state.player
    _prev_login = _p_ref.get("login_streak", {}).get("last_login", "")
    get_login_streak(_p_ref)
    _today_str = _date.today().isoformat()
    _is_new_login = (_prev_login != _today_str)
    st.session_state["_login_streak_updated"] = True
    if _is_new_login:
        _bonuses = get_all_bonuses(_p_ref)
        _login_bonus_applied = False
        # ネコペット: 毎日ログインEXP+50
        _cat_exp = _bonuses.get("cat_login_exp", 0)
        if _cat_exp > 0:
            PlayerManager(_p_ref).gain_exp(_cat_exp, streak=0)
            st.session_state["_cat_login_exp_gained"] = _cat_exp
            _login_bonus_applied = True
        # ユニコーンペット: 1日1回HP全回復（自動）
        if _bonuses.get("unicorn_daily_hp") and _p_ref.get("unicorn_heal_used") != _today_str:
            _p_ref["hp"] = _p_ref.get("hp_max", 100)
            _p_ref["unicorn_heal_used"] = _today_str
            st.session_state["_unicorn_healed_today"] = True
            _login_bonus_applied = True
        if _login_bonus_applied:
            _uname = st.session_state.get("username", "")
            if _uname:
                save_player(_p_ref, _uname)


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

render_sidebar()

p = st.session_state.player
username = st.session_state.get("username", "")

# ─── 苦手単語数を取得してクエスト目標を調整 ────────────────
_weak_count: int | None = None
if username:
    _sp = get_user_save_path(username)
    if _sp.exists():
        try:
            with open(_sp, encoding="utf-8") as _f:
                _weak_count = len(json.load(_f).get("weak_words", []))
        except Exception:
            pass

# ─── 新規クリア検出 ─────────────────────────────────────────
quests = get_or_reset_daily_quests(p, weak_count=_weak_count)
prev_seen = set(st.session_state.get("_daily_seen_completed", []))
current_completed_ids = {q["id"] for q in quests if q["completed"]}
newly_completed_ids = current_completed_ids - prev_seen
st.session_state["_daily_seen_completed"] = list(current_completed_ids)

all_complete = (len(current_completed_ids) == len(QUEST_DEFS))
all_just_complete = all_complete and len(newly_completed_ids) > 0

# ─── ページタイトル ──────────────────────────────────────────
st.markdown(
    '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">📅 デイリークエスト</div>'
    '<div style="font-size:.9rem;color:#888;margin-bottom:20px;">毎日リセット！クリアして装備をゲットしよう</div>',
    unsafe_allow_html=True)

# ─── 演出 ───────────────────────────────────────────────────
if all_just_complete:
    st.balloons()
    _confetti_component(mega=True)
    st.markdown(
        '<div class="all-complete-banner">'
        '<div style="font-size:2rem;margin-bottom:8px;">🎊 全クエストコンプリート！ 🎊</div>'
        '<div style="font-size:1rem;color:#88ff88;font-weight:700;">すべてのデイリークエストをクリアした！</div>'
        '<div style="font-size:.85rem;color:#aaffaa;margin-top:6px;">今日も英単語の達人に一歩近づいた！</div>'
        '</div>', unsafe_allow_html=True)
elif newly_completed_ids:
    _confetti_component(mega=False)

# ペットログインボーナス通知（ネコEXP / ユニコーンHP回復）
_cat_exp_gained = st.session_state.pop("_cat_login_exp_gained", 0)
if _cat_exp_gained:
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#1a1a00,#2a2a00);'
        f'border:1px solid #aaaa44;border-radius:10px;padding:10px 16px;'
        f'margin-bottom:8px;text-align:center;">'
        f'<span style="color:#ffee88;">🐱 ネコペット: ログインEXP +{_cat_exp_gained} 獲得！</span>'
        f'</div>', unsafe_allow_html=True)
_unicorn_healed = st.session_state.pop("_unicorn_healed_today", False)
if _unicorn_healed:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a001a,#2a002a);'
        'border:1px solid #cc88ff;border-radius:10px;padding:10px 16px;'
        'margin-bottom:8px;text-align:center;">'
        '<span style="color:#eeccff;">🦄 ユニコーンペット: HP全回復！（本日1回のみ）</span>'
        '</div>', unsafe_allow_html=True)

# ─── ログインボーナス ───────────────────────────────────────
st.markdown(
    '<div style="font-size:1.1rem;font-weight:700;color:#ffe066;margin-bottom:12px;">🔥 連続ログインボーナス</div>',
    unsafe_allow_html=True)

ls = p.get("login_streak", {})
streak_days = ls.get("streak_days", 0)
claimed_ms = set(ls.get("claimed_milestones", []))

login_cols = st.columns(len(LOGIN_BONUS_THRESHOLDS))
for col, days in zip(login_cols, LOGIN_BONUS_THRESHOLDS):
    item_id = LOGIN_BONUS_REWARDS[days]
    item = ITEMS[item_id]
    is_reached = streak_days >= days
    is_claimed = days in claimed_ms
    border = "#ffe066" if (is_reached and not is_claimed) else ("#2a7a2a" if is_claimed else "#3a3a6a")
    bg = "linear-gradient(135deg,#2a2000,#3a3000)" if (is_reached and not is_claimed) else (
        "linear-gradient(135deg,#0a2a0a,#1a3a1a)" if is_claimed else "linear-gradient(135deg,#1a1a2e,#2a2a4a)"
    )
    check = "✓ " if is_claimed else ""
    with col:
        st.markdown(
            f'<div style="background:{bg};border:2px solid {border};border-radius:10px;'
            f'padding:10px 6px;text-align:center;margin-bottom:6px;">'
            f'<div style="font-size:1.4rem;">{item["icon"]}</div>'
            f'<div style="font-size:.65rem;color:#ffe066;margin-top:4px;">{check}{days}日</div>'
            f'<div style="font-size:.6rem;color:#888;">{item["name"]}</div>'
            f'</div>', unsafe_allow_html=True)
        if is_reached and not is_claimed:
            if st.button("受取", key=f"login_bonus_{days}", use_container_width=True, type="primary"):
                rewarded = claim_login_bonus(p, days)
                if rewarded:
                    save_player(p, username)
                    st.session_state["_daily_just_claimed"] = ITEMS[rewarded]["name"]
                    st.rerun()

# 報酬受取後のミニ演出（rerun 後に1回だけ表示）
just_claimed = st.session_state.get("_daily_just_claimed")
if just_claimed:
    del st.session_state["_daily_just_claimed"]
    _jc_exp = st.session_state.pop("_daily_claim_exp", 50)
    _jc_bonus_pct = st.session_state.pop("_daily_claim_exp_bonus_pct", 0)
    _jc_exp_text = f" ＋ {_jc_exp} EXP"
    if _jc_bonus_pct > 0:
        _jc_exp_text += f" (📿+{_jc_bonus_pct}%)"
    components.html(
        _sound_script(_QUEST_WAV)
        + '<div style="font-size:1.05rem;color:#ffe066;text-align:center;'
        'font-family:sans-serif;padding:6px;background:#1a1a2e;border-radius:8px;">'
        + '✨ ' + just_claimed + ' をゲット！' + _jc_exp_text + ' ✨'
        + '</div>',
        height=48, scrolling=False)

st.markdown(
    f'<div style="font-size:.85rem;color:#aaaacc;margin-bottom:20px;">'
    f'現在の連続ログイン日数：<b style="color:#ffe066;">{streak_days}日</b>'
    f'</div>', unsafe_allow_html=True)

st.markdown("---")

# ─── デイリークエスト ───────────────────────────────────────
st.markdown(
    '<div style="font-size:1.1rem;font-weight:700;color:#ffe066;margin-bottom:12px;">⚔️ 今日のクエスト</div>',
    unsafe_allow_html=True)

for i, (qdef, q) in enumerate(zip(QUEST_DEFS, quests)):
    reward_item_id = QUEST_REWARDS.get(q["id"], "")
    reward_item = ITEMS.get(reward_item_id, {})
    progress_pct = min(100, round(q["progress"] / q["target"] * 100)) if q["target"] > 0 else 0
    is_newly_done = q["id"] in newly_completed_ids

    # 苦手単語クエストはターゲット数を動的にタイトルへ反映
    if q["id"] == "weak3":
        quest_title = f'苦手単語を{q["target"]}問正解する'
    else:
        quest_title = qdef["title"]

    if q["claimed"]:
        card_class = "quest-claimed"
        status_text = '<span class="check-bounce">✅</span> 受取済'
        status_color = "#888"
        bar_color = "linear-gradient(90deg,#446644,#335533)"
    elif q["completed"]:
        card_class = "quest-done-new" if is_newly_done else "quest-done"
        status_text = '🎁 受取可能！ <span class="sparkle-spin">✨</span>' if is_newly_done else "🎁 受取可能！"
        status_color = "#44ff88" if is_newly_done else "#88ff88"
        bar_color = "linear-gradient(90deg,#44ff88,#00cc66)"
    else:
        card_class = "quest-card"
        status_text = f'{q["progress"]} / {q["target"]}'
        status_color = "#aaaacc"
        bar_color = "linear-gradient(90deg,#ffe066,#ff9900)"

    st.markdown(
        f'<div class="{card_class}">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        f'<div style="font-size:1rem;font-weight:700;color:#fff;">{qdef["icon"]} {quest_title}</div>'
        f'<div style="font-size:.85rem;color:{status_color};">{status_text}</div>'
        f'</div>'
        f'<div style="background:#0a0a1a;border-radius:6px;height:8px;width:100%;margin-bottom:8px;overflow:hidden;">'
        f'<div style="background:{bar_color};height:100%;width:{progress_pct}%;border-radius:6px;"></div>'
        f'</div>'
        f'<div style="font-size:.78rem;color:#888;">報酬：{reward_item.get("icon","")}{reward_item.get("name","")}</div>'
        f'</div>', unsafe_allow_html=True)

    if q["completed"] and not q["claimed"]:
        if st.button("🎁 報酬を受け取る", key=f"claim_quest_{i}", use_container_width=True, type="primary"):
            rewarded = claim_quest_reward(p, q["id"])
            if rewarded:
                # ネックレスボーナス: デイリー報酬EXPボーナス
                _dq_bonuses = get_all_bonuses(p)
                _daily_exp_bonus_pct = _dq_bonuses.get("daily_exp_bonus_pct", 0)
                _base_claim_exp = 50
                _claim_exp = max(_base_claim_exp, int(_base_claim_exp * (1 + _daily_exp_bonus_pct / 100)))
                PlayerManager(p).gain_exp(_claim_exp, streak=0)
                st.session_state["_daily_claim_exp"] = _claim_exp
                st.session_state["_daily_claim_exp_bonus_pct"] = _daily_exp_bonus_pct
                save_player(p, username)
                st.session_state["_daily_just_claimed"] = ITEMS[rewarded]["name"]
                st.rerun()

st.markdown("---")

# ─── インベントリ・装備管理 ────────────────────────────────
st.markdown(
    '<div style="font-size:1.1rem;font-weight:700;color:#ffe066;margin-bottom:4px;">🎒 インベントリ & 装備</div>'
    '<div style="font-size:.82rem;color:#888;margin-bottom:12px;">アイテムをクリックして装備・解除できます</div>',
    unsafe_allow_html=True)

inventory = p.get("inventory", [])
equip = p.get("equipment", {})

if not inventory:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;'
        'border-radius:12px;padding:28px;text-align:center;color:#888;">'
        'まだアイテムがありません。<br>デイリークエストやログインボーナスで装備をゲットしよう！'
        '</div>', unsafe_allow_html=True)
else:
    slot_names = {"hat": "🎩 帽子", "weapon": "⚔️ 武器", "armor": "🛡️ 防具", "cloak": "🧥 マント"}
    slot_items: dict = {"hat": [], "weapon": [], "armor": [], "cloak": []}
    for iid in inventory:
        item = ITEMS.get(iid)
        if item:
            slot_items[item["type"]].append(iid)

    for slot, slot_label in slot_names.items():
        items_in_slot = slot_items[slot]
        equipped_id = equip.get(slot)
        st.markdown(f'<div style="font-size:.9rem;font-weight:700;color:#aaaacc;margin:12px 0 6px;">{slot_label}</div>', unsafe_allow_html=True)
        if not items_in_slot:
            st.markdown('<div style="font-size:.8rem;color:#555;margin-bottom:8px;">なし</div>', unsafe_allow_html=True)
            continue
        cols = st.columns(min(len(items_in_slot), 4))
        for col, iid in zip(cols, items_in_slot):
            item = ITEMS[iid]
            is_equipped = (equipped_id == iid)
            border = "#ffe066" if is_equipped else "#3a3a6a"
            bg = "linear-gradient(135deg,#2a2000,#3a3000)" if is_equipped else "linear-gradient(135deg,#1e1e3a,#2a2a4a)"
            tier_stars = "★" * item["tier"] + "☆" * (3 - item["tier"])
            with col:
                from core.equipment_bonus import get_bonus_description as _gbd
                _bonus_desc = _gbd(iid)
                _bonus_line = f'<div style="font-size:.58rem;color:#88ccaa;margin-top:2px;">{_bonus_desc}</div>' if _bonus_desc else ""
                st.markdown(
                    f'<div style="background:{bg};border:2px solid {border};border-radius:10px;'
                    f'padding:10px 6px;text-align:center;margin-bottom:4px;">'
                    f'<div style="font-size:1.6rem;">{item["icon"]}</div>'
                    f'<div style="font-size:.65rem;color:#ffe066;margin-top:4px;">{item["name"]}</div>'
                    f'<div style="font-size:.6rem;color:#aa8800;">{tier_stars}</div>'
                    + _bonus_line +
                    f'</div>', unsafe_allow_html=True)
                if is_equipped:
                    if st.button("外す", key=f"unequip_{slot}_{iid}", use_container_width=True):
                        unequip_slot(p, slot)
                        save_player(p, username)
                        st.rerun()
                else:
                    if st.button("装備", key=f"equip_{iid}", use_container_width=True, type="primary"):
                        equip_item(p, iid)
                        save_player(p, username)
                        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── 現在の装備まとめ ──────────────────────────────────────
st.markdown('<div style="font-size:.9rem;font-weight:700;color:#ffe066;margin-bottom:8px;">装備中のアイテム</div>', unsafe_allow_html=True)
equip_display = []
for slot, slot_label in [("hat", "帽子"), ("weapon", "武器"), ("armor", "防具"), ("cloak", "マント")]:
    iid = equip.get(slot)
    if iid and iid in ITEMS:
        item = ITEMS[iid]
        equip_display.append(f'{item["icon"]} {slot_label}：{item["name"]}')
    else:
        equip_display.append(f'〈{slot_label}〉なし')

st.markdown(
    '<div style="background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;'
    'border-radius:10px;padding:14px 18px;">'
    + "".join(f'<div style="font-size:.88rem;color:#ccccee;line-height:2;">{line}</div>' for line in equip_display)
    + '</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.page_link("pages/01_quest.py", label="🗡️ クエストへ", icon="🗡️")
