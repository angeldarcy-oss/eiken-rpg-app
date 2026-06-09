import sys
import streamlit as st
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.save_manager import load_player, save_player
from core.player import PlayerManager
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html
from core.equipment import ITEMS, QUEST_REWARDS, LOGIN_BONUS_REWARDS, LOGIN_BONUS_THRESHOLDS
from core.daily_quest import (
    QUEST_DEFS, get_or_reset_daily_quests, get_login_streak,
    get_claimable_login_bonuses, claim_login_bonus, claim_quest_reward,
    equip_item, unequip_slot,
)

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
.quest-claimed{border-color:#3a3a6a !important;opacity:0.6;}
.item-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:2px solid #3a3a6a;border-radius:10px;padding:12px 10px;text-align:center;}
.item-card-equipped{border-color:#ffe066 !important;background:linear-gradient(135deg,#2a2000,#3a3000) !important;}
</style>""", unsafe_allow_html=True)


def init_session():
    if "player" not in st.session_state or st.session_state.player is None:
        st.session_state.player = load_player(st.session_state.get("username", ""))
    for k, v in [("total_correct", 0), ("total_questions", 0), ("streak", 0)]:
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ログイン連続日数の更新（ページアクセス時）
login_streak_updated = st.session_state.get("_login_streak_updated", False)
if not login_streak_updated:
    get_login_streak(st.session_state.player)
    st.session_state["_login_streak_updated"] = True


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

p = st.session_state.player
username = st.session_state.get("username", "")

st.markdown(
    '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">📅 デイリークエスト</div>'
    '<div style="font-size:.9rem;color:#888;margin-bottom:20px;">毎日リセット！クリアして装備をゲットしよう</div>',
    unsafe_allow_html=True)

# ─── ログインボーナス ───────────────────────────────────────
st.markdown(
    '<div style="font-size:1.1rem;font-weight:700;color:#ffe066;margin-bottom:12px;">🔥 連続ログインボーナス</div>',
    unsafe_allow_html=True)

ls = p.get("login_streak", {})
streak_days = ls.get("streak_days", 0)
claimed_ms = set(ls.get("claimed_milestones", []))

# ログインボーナスステップ表示
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
                item_id = claim_login_bonus(p, days)
                if item_id:
                    save_player(p, username)
                    st.success(f"{ITEMS[item_id]['name']} をゲット！")
                    st.rerun()

st.markdown(
    f'<div style="font-size:.85rem;color:#aaaacc;margin-bottom:20px;">'
    f'現在の連続ログイン日数：<b style="color:#ffe066;">{streak_days}日</b>'
    f'</div>', unsafe_allow_html=True)

st.markdown("---")

# ─── デイリークエスト ───────────────────────────────────────
st.markdown(
    '<div style="font-size:1.1rem;font-weight:700;color:#ffe066;margin-bottom:12px;">⚔️ 今日のクエスト</div>',
    unsafe_allow_html=True)

quests = get_or_reset_daily_quests(p)

for i, (qdef, q) in enumerate(zip(QUEST_DEFS, quests)):
    reward_item_id = QUEST_REWARDS.get(q["id"], "")
    reward_item = ITEMS.get(reward_item_id, {})
    progress_pct = min(100, round(q["progress"] / q["target"] * 100)) if q["target"] > 0 else 0
    card_class = "quest-claimed" if q["claimed"] else ("quest-done" if q["completed"] else "quest-card")

    status_text = "✓ 受取済" if q["claimed"] else ("🎁 受取可能！" if q["completed"] else f'{q["progress"]} / {q["target"]}')
    status_color = "#888" if q["claimed"] else ("#88ff88" if q["completed"] else "#aaaacc")

    st.markdown(
        f'<div class="{card_class}">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        f'<div style="font-size:1rem;font-weight:700;color:#fff;">{qdef["icon"]} {qdef["title"]}</div>'
        f'<div style="font-size:.85rem;color:{status_color};">{status_text}</div>'
        f'</div>'
        f'<div style="background:#0a0a1a;border-radius:6px;height:8px;width:100%;margin-bottom:8px;overflow:hidden;">'
        f'<div style="background:linear-gradient(90deg,#ffe066,#ff9900);height:100%;width:{progress_pct}%;border-radius:6px;"></div>'
        f'</div>'
        f'<div style="font-size:.78rem;color:#888;">報酬：{reward_item.get("icon","")}{reward_item.get("name","")}</div>'
        f'</div>', unsafe_allow_html=True)

    if q["completed"] and not q["claimed"]:
        if st.button(f"🎁 報酬を受け取る", key=f"claim_quest_{i}", use_container_width=True, type="primary"):
            item_id = claim_quest_reward(p, q["id"])
            if item_id:
                save_player(p, username)
                st.success(f"{ITEMS[item_id]['name']} をゲット！インベントリから装備できます。")
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
    # スロット別に整理
    slot_names = {"hat": "🎩 帽子", "weapon": "⚔️ 武器", "armor": "🛡️ 防具", "cloak": "🧥 マント"}
    slot_items = {"hat": [], "weapon": [], "armor": [], "cloak": []}
    for item_id in inventory:
        item = ITEMS.get(item_id)
        if item:
            slot_items[item["type"]].append(item_id)

    for slot, slot_label in slot_names.items():
        items_in_slot = slot_items[slot]
        equipped_id = equip.get(slot)
        st.markdown(f'<div style="font-size:.9rem;font-weight:700;color:#aaaacc;margin:12px 0 6px;">{slot_label}</div>', unsafe_allow_html=True)

        if not items_in_slot:
            st.markdown('<div style="font-size:.8rem;color:#555;margin-bottom:8px;">なし</div>', unsafe_allow_html=True)
            continue

        cols = st.columns(min(len(items_in_slot), 4))
        for col, item_id in zip(cols, items_in_slot):
            item = ITEMS[item_id]
            is_equipped = (equipped_id == item_id)
            border = "#ffe066" if is_equipped else "#3a3a6a"
            bg = "linear-gradient(135deg,#2a2000,#3a3000)" if is_equipped else "linear-gradient(135deg,#1e1e3a,#2a2a4a)"
            tier_stars = "★" * item["tier"] + "☆" * (3 - item["tier"])
            with col:
                st.markdown(
                    f'<div style="background:{bg};border:2px solid {border};border-radius:10px;'
                    f'padding:10px 6px;text-align:center;margin-bottom:4px;">'
                    f'<div style="font-size:1.6rem;">{item["icon"]}</div>'
                    f'<div style="font-size:.65rem;color:#ffe066;margin-top:4px;">{item["name"]}</div>'
                    f'<div style="font-size:.6rem;color:#aa8800;">{tier_stars}</div>'
                    f'</div>', unsafe_allow_html=True)
                if is_equipped:
                    if st.button("外す", key=f"unequip_{slot}_{item_id}", use_container_width=True):
                        unequip_slot(p, slot)
                        save_player(p, username)
                        st.rerun()
                else:
                    if st.button("装備", key=f"equip_{item_id}", use_container_width=True, type="primary"):
                        equip_item(p, item_id)
                        save_player(p, username)
                        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── 現在の装備まとめ表示 ──────────────────────────────────
st.markdown(
    '<div style="font-size:.9rem;font-weight:700;color:#ffe066;margin-bottom:8px;">装備中のアイテム</div>',
    unsafe_allow_html=True)

equip_display = []
for slot, slot_label in [("hat", "帽子"), ("weapon", "武器"), ("armor", "防具"), ("cloak", "マント")]:
    item_id = equip.get(slot)
    if item_id and item_id in ITEMS:
        item = ITEMS[item_id]
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
