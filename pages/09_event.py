"""pages/09_event.py — 季節イベント画面"""
import sys
import streamlit as st
from pathlib import Path
from datetime import date

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.save_manager import load_player, save_player, update_ranking
from core.player import PlayerManager
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html, CHARACTERS
from core.mobile_css import MOBILE_CSS
from core.equipment_bonus import sidebar_bonus_html
from core.nav import render_nav
from core.quiz_engine import QuizEngine
from core.monsters import calc_player_damage
from core.equipment import ITEMS as _EQUIP_ITEMS
from core.titles import title_badge_html as _tbh, evaluate_titles
from core.pets import pet_sidebar_html as _psh
from core.seasonal_events import (
    SEASONS, get_current_season, days_remaining, get_season_year,
    get_event_ranking, get_player_rank, add_boss_attempt_score,
    record_boss_attempt, can_challenge_boss_today,
    get_quest_progress, is_quest_complete, is_quest_claimed, claim_quest,
)


# ── ログインチェック ────────────────────────────────────────────
if "player" not in st.session_state or st.session_state.player is None:
    st.session_state.player = load_player(st.session_state.get("username", ""))

username = st.session_state.get("username", "")
if not username:
    st.warning("先にホーム画面でログインしてください")
    st.stop()

p = st.session_state.player
lang = p.get("language", "ja")
pm = PlayerManager(p)

# 現在の季節
current_season = get_current_season()


# ── 動的テーマCSS ──────────────────────────────────────────────
def _theme_css(theme: dict | None) -> str:
    if not theme:
        return ""
    bg = theme.get("bg", "#1a1a2e")
    border = theme.get("border", "#4a4a8a")
    primary = theme.get("primary", "#cc88ff")
    glow = theme.get("glow", "none")
    return f"""
    .event-banner {{
        background: {bg};
        border: 2px solid {border};
        border-radius: 18px;
        padding: 22px 28px;
        margin-bottom: 14px;
        box-shadow: {glow};
    }}
    .event-quest-card {{
        background: {bg};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }}
    .event-primary {{ color: {primary}; }}
    """


if current_season:
    theme = current_season.get("theme", {})
    st.markdown(f"<style>{_theme_css(theme)}</style>", unsafe_allow_html=True)

st.markdown("""<style>
html,body,[class*="css"]{font-family:'Noto Sans JP',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460);}
[data-testid="stSidebar"] *{color:#e0e0e0 !important;}
.hp-bar-outer{background:#2a0a0a;border-radius:8px;height:18px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a1a1a;}
.hp-bar-inner{background:linear-gradient(90deg,#e05252,#ff8080);height:100%;border-radius:8px;}
.exp-bar-outer{background:#1a1500;border-radius:8px;height:14px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a4a00;}
.exp-bar-inner{background:linear-gradient(90deg,#c8a000,#ffe066);height:100%;border-radius:8px;}
.stat-label{font-size:11px;color:#aaaacc !important;}
.prog-bar-outer{background:#1a1a2e;border-radius:8px;height:12px;overflow:hidden;border:1px solid #3a3a6a;}
.quiz-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;border-radius:16px;padding:24px 28px;margin-bottom:4px;}
@keyframes event-pulse{0%,100%{opacity:1}50%{opacity:.7}}
@keyframes boss-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes countdown-glow{0%,100%{filter:drop-shadow(0 0 4px #ff4400)}50%{filter:drop-shadow(0 0 12px #ff8800)}}
</style>""", unsafe_allow_html=True)
st.markdown(MOBILE_CSS, unsafe_allow_html=True)


# ── サイドバー ─────────────────────────────────────────────────
def render_sidebar():
    hp_pct = pm.hp_percent() * 100
    exp_pct = pm.exp_percent() * 100
    char_id = p.get("character", "")
    equip = p.get("equipment")
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:12px 0 6px;">'
            + sidebar_avatar_html(char_id, equip) +
            '<div style="font-size:1.2rem;font-weight:700;color:#ffe066;margin-top:6px;">'
            + p["name"] + '</div>'
            '<div style="font-size:.8rem;color:#aaaacc;">'
            + t("level", lang) + ' ' + str(p["level"]) + ' | ' + grade_label(p["grade_target"], lang)
            + '</div>' + _tbh(p, style="sidebar") + _psh(p) + '</div>',
            unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(
            '<div class="stat-label">' + t("hp", lang) + ' ' + str(p["hp"]) + ' / ' + str(p["hp_max"]) + '</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div class="hp-bar-outer"><div class="hp-bar-inner" style="width:'
            + str(round(hp_pct, 1)) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="stat-label">' + t("exp", lang) + ' ' + str(p["exp"]) + ' / ' + str(p["exp_to_next"]) + '</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div class="exp-bar-outer"><div class="exp-bar-inner" style="width:'
            + str(round(exp_pct, 1)) + '%"></div></div>', unsafe_allow_html=True)
        _bhtml = sidebar_bonus_html(p)
        if _bhtml:
            st.markdown(_bhtml, unsafe_allow_html=True)
        st.markdown("---")
        if current_season:
            theme = current_season.get("theme", {})
            remaining = days_remaining(current_season)
            border = theme.get("border", "#4a4a8a")
            primary = theme.get("primary", "#cc88ff")
            urgent_color = "#ff4400" if remaining <= 7 else primary
            st.markdown(
                '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid '
                + border + ';border-radius:8px;padding:8px 10px;">'
                '<div style="font-size:.62rem;color:#888;margin-bottom:2px;">🎪 開催中イベント</div>'
                '<div style="font-size:.85rem;font-weight:700;color:' + primary + ';">'
                + current_season["icon"] + ' ' + current_season["name"] + '</div>'
                '<div style="font-size:.72rem;color:' + urgent_color + ';margin-top:3px;">'
                '⏳ 残り <b>' + str(remaining) + '</b> 日'
                + (' ⚠️' if remaining <= 7 else '') + '</div>'
                '</div>', unsafe_allow_html=True)
        st.markdown("---")
        render_nav(lang)


render_sidebar()


# ── クイズエンジン取得 ─────────────────────────────────────────
def _get_event_engine() -> QuizEngine:
    engine = st.session_state.get("event_quiz_engine")
    if engine is None or engine.grade != p.get("grade_target", "grade_5"):
        engine = QuizEngine(
            grade=p.get("grade_target", "grade_5"),
            data_dir="data/words",
            language="ja",
        )
        st.session_state.event_quiz_engine = engine
    return engine


# ── ページヘッダー ─────────────────────────────────────────────
st.markdown(
    '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:2px;">🎪 季節イベント</div>'
    '<div style="font-size:.85rem;color:#888;margin-bottom:12px;">'
    '季節ごとの限定クエスト・ボス・装備をゲットしよう！</div>',
    unsafe_allow_html=True)

# ── タブ ──────────────────────────────────────────────────────
tab_current, tab_quests, tab_boss, tab_ranking, tab_archive = st.tabs(
    ["🎪 現在のイベント", "📋 イベントクエスト", "⚔️ イベントボス", "🏆 ランキング", "📚 アーカイブ"])


# ─── Tab1: 現在のイベント ──────────────────────────────────────
with tab_current:
    if current_season is None:
        st.markdown(
            '<div style="text-align:center;padding:40px 20px;background:linear-gradient(135deg,#1a1a2e,#222244);'
            'border:1px solid #3a3a6a;border-radius:14px;">'
            '<div style="font-size:3rem;margin-bottom:12px;">😴</div>'
            '<div style="font-size:1.2rem;color:#888;">現在開催中のイベントはありません</div>'
            '<div style="font-size:.82rem;color:#555;margin-top:6px;">次のイベントをお楽しみに！</div>'
            '</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(
            '<div style="font-size:.9rem;color:#888;margin-bottom:8px;">次のイベント予定</div>',
            unsafe_allow_html=True)
        today = date.today()
        for s in SEASONS:
            months_str = "・".join([f"{m}月" for m in s["months"]])
            theme = s.get("theme", {})
            border = theme.get("border", "#4a4a8a")
            primary = theme.get("primary", "#cc88ff")
            is_next = any(
                (today.month < m) or (today.month == 12 and m == 1)
                for m in s["months"]
            )
            st.markdown(
                '<div style="background:#1a1a2e;border:1px solid ' + border + ';'
                'border-radius:10px;padding:8px 14px;margin-bottom:6px;">'
                '<span style="font-size:1.2rem;">' + s["icon"] + '</span>'
                ' <b style="color:' + primary + ';">' + s["name"] + '</b>'
                ' <span style="font-size:.72rem;color:#666;">（' + months_str + '）</span>'
                '</div>', unsafe_allow_html=True)
    else:
        s = current_season
        theme = s.get("theme", {})
        banner_bg = theme.get("banner_bg", "#1a1a2e")
        border = theme.get("border", "#4a4a8a")
        primary = theme.get("primary", "#cc88ff")
        secondary = theme.get("secondary", "#aa88ff")
        glow = theme.get("glow", "none")
        remaining = days_remaining(s)
        urgent = remaining <= 7

        # イベントバナー
        st.markdown(
            '<div style="background:' + banner_bg + ';border:2px solid ' + border + ';'
            'border-radius:18px;padding:22px 28px;margin-bottom:14px;box-shadow:' + glow + ';">'
            '<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">'
            '<div style="font-size:3.5rem;animation:boss-float 3s ease-in-out infinite;">'
            + s["icon"] + '</div>'
            '<div>'
            '<div style="font-size:1.6rem;font-weight:900;color:' + primary + ';">'
            + s["name"] + '</div>'
            '<div style="font-size:.88rem;color:' + secondary + ';margin-top:4px;">'
            + s["description"] + '</div>'
            '</div></div>'
            '</div>', unsafe_allow_html=True)

        # カウントダウン
        countdown_color = "#ff4400" if urgent else primary
        st.markdown(
            '<div style="background:linear-gradient(135deg,#1a0a0a,#2a1010);border:1px solid '
            + ("#ff4400" if urgent else border) + ';'
            'border-radius:12px;padding:14px 18px;margin-bottom:14px;">'
            '<div style="font-size:.82rem;color:#888;margin-bottom:6px;">⏳ イベント終了まで</div>'
            '<div style="font-size:2.5rem;font-weight:900;color:' + countdown_color + ';'
            + ('animation:countdown-glow 1.5s ease-in-out infinite;' if urgent else '') + '">'
            + str(remaining) + ' <span style="font-size:1rem;font-weight:400;">日</span></div>'
            + ('<div style="font-size:.78rem;color:#ff4400;margin-top:4px;">⚠️ もうすぐ終了！急いで報酬をゲットしよう！</div>'
               if urgent else '')
            + '</div>', unsafe_allow_html=True)

        # 今週のボス情報プレビュー
        boss = s.get("boss", {})
        can_fight = can_challenge_boss_today(p)
        year = get_season_year(s)
        rank = get_player_rank(s["id"], year, username)

        st.markdown(
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">',
            unsafe_allow_html=True)
        col_boss, col_rank = st.columns(2)
        with col_boss:
            boss_status = "✅ 今日の挑戦済み" if not can_fight else "🆕 挑戦可能！"
            boss_color = "#888" if not can_fight else primary
            st.markdown(
                '<div style="background:#1a1a2e;border:1px solid ' + border + ';'
                'border-radius:10px;padding:10px;text-align:center;">'
                '<div style="font-size:1.6rem;">' + boss.get("emoji", "👾") + '</div>'
                '<div style="font-size:.82rem;font-weight:700;color:' + primary + ';">'
                + boss.get("name", "") + '</div>'
                '<div style="font-size:.7rem;color:' + boss_color + ';margin-top:2px;">'
                + boss_status + '</div>'
                '</div>', unsafe_allow_html=True)
        with col_rank:
            rank_str = str(rank) + "位" if rank else "未参加"
            rank_color = "#ffcc00" if rank and rank <= 3 else primary
            st.markdown(
                '<div style="background:#1a1a2e;border:1px solid ' + border + ';'
                'border-radius:10px;padding:10px;text-align:center;">'
                '<div style="font-size:1.6rem;">🏆</div>'
                '<div style="font-size:.82rem;font-weight:700;color:' + rank_color + ';">'
                + rank_str + '</div>'
                '<div style="font-size:.7rem;color:#888;margin-top:2px;">イベントランキング</div>'
                '</div>', unsafe_allow_html=True)

        # 季節限定アイテムプレビュー
        st.markdown(
            '<div style="font-size:.9rem;font-weight:700;color:#ffe066;margin:12px 0 8px;">'
            '🎁 今季の限定報酬</div>', unsafe_allow_html=True)
        all_items = []
        for q in s.get("quests", []):
            if q.get("reward_item"):
                all_items.append(q["reward_item"])
        items_html = ""
        for item_id in all_items:
            item = _EQUIP_ITEMS.get(item_id, {})
            in_inv = item_id in p.get("inventory", [])
            obtained = "✅ " if in_inv else ""
            color = "#44ff88" if in_inv else primary
            items_html += (
                '<div style="background:#1a1a2e;border:1px solid ' + (
                    "#44ff44" if in_inv else border) + ';'
                'border-radius:8px;padding:6px 10px;display:inline-flex;'
                'align-items:center;gap:6px;margin:3px;">'
                '<span style="font-size:1.2rem;">' + item.get("icon", "📦") + '</span>'
                '<span style="font-size:.78rem;color:' + color + ';">'
                + obtained + item.get("name", item_id) + '</span>'
                '</div>'
            )
        st.markdown(
            '<div style="margin-bottom:10px;">' + items_html + '</div>',
            unsafe_allow_html=True)


# ─── Tab2: イベントクエスト ────────────────────────────────────
with tab_quests:
    if current_season is None:
        st.info("現在イベント開催中ではありません")
    else:
        s = current_season
        theme = s.get("theme", {})
        border = theme.get("border", "#4a4a8a")
        primary = theme.get("primary", "#cc88ff")
        year = get_season_year(s)

        st.markdown(
            '<div style="font-size:1.3rem;font-weight:700;color:#ffe066;margin-bottom:4px;">'
            + s["icon"] + ' イベントクエスト</div>'
            '<div style="font-size:.82rem;color:#888;margin-bottom:14px;">'
            '全クエスト達成で季節称号をゲット！</div>',
            unsafe_allow_html=True)

        for quest in s.get("quests", []):
            cur, target = get_quest_progress(quest, p)
            pct = min(100, round(cur / max(target, 1) * 100, 1))
            completed = is_quest_complete(quest, p)
            claimed = is_quest_claimed(s["id"], year, quest["id"], p)

            reward_item_id = quest.get("reward_item")
            reward_item = _EQUIP_ITEMS.get(reward_item_id, {}) if reward_item_id else None

            bar_color = ("#44ff88" if claimed else
                         ("#88ffaa" if completed else primary))
            card_border = "#44ff44" if claimed else ("#88ff44" if completed else border)
            status_badge = (
                '<span style="background:#0a2a0a;border:1px solid #44ff44;color:#44ff88;'
                'border-radius:6px;padding:1px 7px;font-size:.7rem;font-weight:700;">✅ 受取済み</span>'
                if claimed else (
                    '<span style="background:#1a2a0a;border:1px solid #88ff44;color:#aaffaa;'
                    'border-radius:6px;padding:1px 7px;font-size:.7rem;font-weight:700;">🎉 達成！受取可能</span>'
                    if completed else ""
                )
            )

            reward_html = ""
            if reward_item:
                reward_html += (
                    '<span style="font-size:.8rem;color:' + ("#44ff88" if claimed else "#ffe066") + ';">'
                    + reward_item.get("icon", "📦") + ' ' + reward_item.get("name", "") + ' </span>'
                )
            reward_html += (
                '<span style="font-size:.8rem;color:#ffe066;">✨ ' + str(quest["reward_exp"]) + ' EXP</span>'
            )
            if quest.get("reward_title"):
                from core.titles import _TITLE_MAP
                tdef = _TITLE_MAP.get(quest["reward_title"], {})
                if tdef:
                    reward_html += (
                        ' <span style="font-size:.78rem;color:#ffaa44;">'
                        + tdef.get("icon", "") + ' ' + tdef.get("name", "") + '</span>'
                    )

            st.markdown(
                '<div style="background:linear-gradient(135deg,#1a1a2e,#222240);border:1px solid '
                + card_border + ';border-radius:12px;padding:14px 18px;margin-bottom:10px;">'
                '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
                '<div style="font-size:.95rem;font-weight:700;color:#ffe066;">'
                + quest.get("icon", "") + ' ' + quest["name"] + '</div>'
                + status_badge + '</div>'
                '<div style="font-size:.82rem;color:#aaaacc;margin-bottom:8px;">'
                + quest["desc"] + '</div>'
                '<div style="background:#1a1a2e;border-radius:6px;height:10px;overflow:hidden;margin-bottom:4px;">'
                '<div style="background:' + bar_color + ';width:' + str(pct) + '%;height:100%;border-radius:6px;transition:width .4s ease;"></div>'
                '</div>'
                '<div style="font-size:.7rem;color:#888;margin-bottom:8px;">'
                + str(cur) + ' / ' + str(target) + ' (' + str(pct) + '%)</div>'
                '<div style="font-size:.78rem;">報酬: ' + reward_html + '</div>'
                '</div>', unsafe_allow_html=True)

            if completed and not claimed:
                if st.button(
                    "🎁 報酬を受け取る！",
                    key=f"claim_{quest['id']}",
                    use_container_width=True,
                    type="primary",
                ):
                    reward = claim_quest(
                        s["id"], year, quest, p,
                        username, p["name"], p.get("character", ""),
                    )
                    if reward:
                        gain = pm.gain_exp(base_exp=reward["exp"], streak=p.get("streak", 0))
                        newly = evaluate_titles(p)
                        save_player(p, username)
                        update_ranking(p, username)
                        msgs = [f"✨ +{gain.exp_gained_final} EXP"]
                        if reward.get("item"):
                            item_def = _EQUIP_ITEMS.get(reward["item"], {})
                            msgs.append(f'{item_def.get("icon","📦")} 「{item_def.get("name", reward["item"])}」をゲット！')
                        if reward.get("title") or newly:
                            from core.titles import _TITLE_MAP
                            tids = ([reward["title"]] if reward.get("title") else []) + newly
                            for tid in set(tids):
                                td = _TITLE_MAP.get(tid, {})
                                if td:
                                    msgs.append(f'🏅 称号「{td["icon"]} {td["name"]}」を獲得！')
                        st.success(" / ".join(msgs))
                        st.balloons()
                        st.rerun()


# ─── Tab3: イベントボス ────────────────────────────────────────
with tab_boss:
    if current_season is None:
        st.info("現在イベント開催中ではありません")
    else:
        s = current_season
        theme = s.get("theme", {})
        border = theme.get("border", "#4a4a8a")
        primary = theme.get("primary", "#cc88ff")
        banner_bg = theme.get("banner_bg", "#1a1a2e")
        glow = theme.get("glow", "none")
        boss = s.get("boss", {})
        year = get_season_year(s)
        can_fight = can_challenge_boss_today(p)

        st.markdown(
            '<div style="font-size:1.3rem;font-weight:700;color:#ffe066;margin-bottom:4px;">⚔️ イベントボス挑戦</div>'
            '<div style="font-size:.82rem;color:#888;margin-bottom:14px;">'
            '1日1回チャレンジ！5問クイズで攻撃してスコアを稼ごう</div>',
            unsafe_allow_html=True)

        # ボス紹介パネル
        st.markdown(
            '<div style="background:' + banner_bg + ';border:2px solid ' + border + ';'
            'border-radius:16px;padding:16px 20px;margin-bottom:14px;box-shadow:' + glow + ';">'
            '<div style="display:flex;align-items:center;gap:14px;">'
            '<div style="width:90px;height:90px;flex-shrink:0;'
            'animation:boss-float 3s ease-in-out infinite;">'
            + boss.get("svg", "") + '</div>'
            '<div>'
            '<div style="font-size:1.4rem;font-weight:800;color:' + primary + ';">'
            + boss.get("emoji", "") + ' ' + boss.get("name", "") + '</div>'
            '<div style="font-size:.82rem;color:#aaaacc;margin-top:4px;">'
            + boss.get("desc", "") + '</div>'
            '<div style="font-size:.75rem;color:#888;margin-top:8px;">'
            '🎯 1問正解 = <b style="color:' + primary + ';">+' + str(boss.get("score_per_correct", 20)) + 'スコア</b>'
            ' | 全問正解ボーナス: <b style="color:#ffcc00;">+' + str(boss.get("bonus_score", 50)) + '</b>'
            '</div></div></div></div>', unsafe_allow_html=True)

        # バトル状態機
        mode = st.session_state.get("event_boss_mode")
        q_count = st.session_state.get("event_boss_q_count", 0)
        correct_count = st.session_state.get("event_boss_correct", 0)
        TOTAL_Q = 5  # 1回の挑戦で出る問題数

        if not can_fight and mode is None:
            st.markdown(
                '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid #3a3a6a;'
                'border-radius:12px;padding:16px;text-align:center;">'
                '<div style="font-size:1.5rem;margin-bottom:6px;">😴</div>'
                '<div style="font-size:.95rem;color:#888;">今日のボス挑戦は完了しました</div>'
                '<div style="font-size:.78rem;color:#555;margin-top:4px;">明日またチャレンジしよう！</div>'
                '</div>', unsafe_allow_html=True)

        elif mode is None:
            st.markdown(
                '<div style="background:linear-gradient(135deg,#1a0a0a,#2a1010);border:1px solid '
                + border + ';border-radius:12px;padding:14px;text-align:center;margin-bottom:12px;">'
                '<div style="font-size:.88rem;color:#aaaacc;">5問連続クイズでボスを攻撃！</div>'
                '<div style="font-size:.75rem;color:#888;margin-top:4px;">'
                '正解するたびにスコアゲット。全問正解でボーナス！</div>'
                '</div>', unsafe_allow_html=True)
            if st.button(
                boss.get("emoji", "👾") + " ボスに挑戦！（1日1回）",
                use_container_width=True,
                type="primary",
            ):
                engine = _get_event_engine()
                engine.reset_session()
                q = engine.get_next_question()
                st.session_state.event_boss_mode = "fighting"
                st.session_state.event_boss_q = q
                st.session_state.event_boss_q_count = 1
                st.session_state.event_boss_correct = 0
                record_boss_attempt(p)
                save_player(p, username)
                st.rerun()

        elif mode == "fighting":
            q = st.session_state.get("event_boss_q")
            if q is None:
                st.session_state.event_boss_mode = None
                st.rerun()
            else:
                # 進捗バー
                pct = round((q_count - 1) / TOTAL_Q * 100)
                st.markdown(
                    '<div style="margin-bottom:12px;">'
                    '<div style="font-size:.75rem;color:#888;margin-bottom:4px;">'
                    '問題 ' + str(q_count) + ' / ' + str(TOTAL_Q) + ' | 正解: ' + str(correct_count) + '</div>'
                    '<div style="background:#1a1a2e;border-radius:6px;height:8px;overflow:hidden;">'
                    '<div style="background:' + primary + ';width:' + str(pct) + '%;height:100%;border-radius:6px;"></div>'
                    '</div></div>', unsafe_allow_html=True)

                st.markdown(
                    '<div class="quiz-card">'
                    '<div style="font-size:.82rem;color:#aaaacc;text-align:center;margin-bottom:14px;">'
                    + '⭐' * q.difficulty +
                    '</div>'
                    '<div style="font-size:2.4rem;font-weight:700;text-align:center;color:#ffe066;margin-bottom:4px;">'
                    + q.word + '</div></div>', unsafe_allow_html=True)

                cols = st.columns(2)
                labels = ["Ａ", "Ｂ", "Ｃ", "Ｄ"]
                for i, choice in enumerate(q.choices):
                    with cols[i % 2]:
                        if st.button(labels[i] + "　" + choice, key="eb_" + str(i), use_container_width=True):
                            engine = _get_event_engine()
                            result = engine.judge(q, selected_answer=choice)
                            if result.is_correct:
                                st.session_state.event_boss_correct = correct_count + 1
                            # 次の問題 or 終了
                            if q_count >= TOTAL_Q:
                                st.session_state.event_boss_mode = "result"
                                st.session_state.event_boss_last_q = q
                                st.session_state.event_boss_last_result = result
                            else:
                                q_next = engine.get_next_question()
                                if q_next is None:
                                    engine.reset_session()
                                    q_next = engine.get_next_question()
                                st.session_state.event_boss_q = q_next
                                st.session_state.event_boss_q_count = q_count + 1
                            st.rerun()

        elif mode == "result":
            final_correct = st.session_state.get("event_boss_correct", 0)
            bonus = boss.get("bonus_score", 50) if final_correct == TOTAL_Q else 0
            score = boss.get("score_per_correct", 20) * final_correct + bonus
            is_perfect = final_correct == TOTAL_Q
            last_q = st.session_state.get("event_boss_last_q")
            last_result = st.session_state.get("event_boss_last_result")

            # スコア保存
            saved_score = st.session_state.get("event_boss_score_saved", False)
            if not saved_score:
                add_boss_attempt_score(
                    s["id"], year, username, p["name"],
                    p.get("character", ""), p["level"],
                    final_correct, TOTAL_Q,
                )
                st.session_state.event_boss_score_saved = True

            if is_perfect:
                st.balloons()
                st.markdown(
                    '<div style="background:linear-gradient(135deg,#1a1000,#3a2800);border:3px solid #ffcc00;'
                    'border-radius:16px;padding:20px;text-align:center;margin-bottom:14px;">'
                    '<div style="font-size:2.5rem;font-weight:900;color:#ffcc00;">🏆 パーフェクト！</div>'
                    '<div style="font-size:1rem;color:#ffe066;margin-top:6px;">全問正解！ボーナスゲット！</div>'
                    '</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);border:2px solid '
                    + border + ';border-radius:16px;padding:18px;text-align:center;margin-bottom:14px;">'
                    '<div style="font-size:1.6rem;font-weight:700;color:' + primary + ';">⚔️ バトル終了！</div>'
                    '</div>', unsafe_allow_html=True)

            # スコア内訳
            st.markdown(
                '<div style="background:#1a1a2e;border:1px solid ' + border + ';'
                'border-radius:12px;padding:14px 18px;margin-bottom:12px;">'
                '<div style="font-size:.9rem;font-weight:700;color:#ffe066;margin-bottom:8px;">📊 結果</div>'
                '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">'
                '<div style="text-align:center;"><div style="font-size:.7rem;color:#888;">正解数</div>'
                '<div style="font-size:1.4rem;font-weight:700;color:' + primary + ';">'
                + str(final_correct) + '/' + str(TOTAL_Q) + '</div></div>'
                '<div style="text-align:center;"><div style="font-size:.7rem;color:#888;">ボーナス</div>'
                '<div style="font-size:1.4rem;font-weight:700;color:#ffcc00;">+' + str(bonus) + '</div></div>'
                '<div style="text-align:center;"><div style="font-size:.7rem;color:#888;">獲得スコア</div>'
                '<div style="font-size:1.4rem;font-weight:700;color:#88ff88;">+' + str(score) + '</div></div>'
                '</div></div>', unsafe_allow_html=True)

            # 最後の問題の答え表示
            if last_q and last_result and not last_result.is_correct:
                st.markdown(
                    '<div style="background:#2a0a0a;border:1px solid #7a2a2a;border-radius:10px;'
                    'padding:10px 14px;margin-bottom:10px;">'
                    '<div style="font-size:.78rem;color:#ff8080;">最後の問題の正解:</div>'
                    '<div style="color:#ffe066;font-size:.9rem;">'
                    + last_q.word + ' = <b>' + last_q.correct_answer + '</b></div>'
                    '</div>', unsafe_allow_html=True)

            if st.button("✅ 結果を確認", use_container_width=True, type="primary"):
                st.session_state.event_boss_mode = None
                st.session_state.event_boss_q_count = 0
                st.session_state.event_boss_correct = 0
                st.session_state.event_boss_score_saved = False
                st.rerun()


# ─── Tab4: イベントランキング ──────────────────────────────────
with tab_ranking:
    if current_season is None:
        st.info("現在イベント開催中ではありません")
    else:
        s = current_season
        theme = s.get("theme", {})
        border = theme.get("border", "#4a4a8a")
        primary = theme.get("primary", "#cc88ff")
        year = get_season_year(s)
        ranking = get_event_ranking(s["id"], year)
        my_rank = get_player_rank(s["id"], year, username)

        st.markdown(
            '<div style="font-size:1.3rem;font-weight:700;color:#ffe066;margin-bottom:4px;">🏆 イベントランキング</div>'
            '<div style="font-size:.82rem;color:#888;margin-bottom:14px;">'
            + s["icon"] + ' ' + s["name"] + ' | イベントスコア順</div>',
            unsafe_allow_html=True)

        if my_rank:
            rank_color = "#ffcc00" if my_rank <= 3 else primary
            st.markdown(
                '<div style="background:linear-gradient(135deg,#1a0a2a,#2a1a4a);border:2px solid '
                + border + ';border-radius:10px;padding:10px 16px;margin-bottom:12px;">'
                '<div style="font-size:.78rem;color:#888;">あなたの順位</div>'
                '<div style="font-size:1.8rem;font-weight:900;color:' + rank_color + ';">'
                + str(my_rank) + ' <span style="font-size:.9rem;font-weight:400;">位</span></div>'
                '</div>', unsafe_allow_html=True)

        MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
        if not ranking:
            st.markdown(
                '<div style="text-align:center;padding:30px;color:#555;">まだ参加者がいません。最初の挑戦者になろう！</div>',
                unsafe_allow_html=True)
        for i, entry in enumerate(ranking):
            rank = i + 1
            medal = MEDALS.get(rank, str(rank))
            is_me = entry.get("username") == username
            char_id = entry.get("character", "")
            char_html = (
                '<div style="width:28px;height:34px;flex-shrink:0;">'
                + CHARACTERS[char_id]["svg"] + '</div>'
                if char_id in CHARACTERS else '<div style="font-size:1.3rem;">🧑</div>'
            )
            extra = "border-color:" + border + ";background:linear-gradient(135deg,#1a0a2a,#2a1040);" if is_me else ""
            me_badge = (
                ' <span style="background:' + border + ';color:#fff;font-size:.6rem;'
                'padding:1px 5px;border-radius:6px;font-weight:700;">YOU</span>'
                if is_me else ""
            )
            score_color = "#ffcc00" if rank <= 3 else "#88ff88"
            st.markdown(
                '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid #3a3a6a;'
                + extra +
                'border-radius:10px;padding:8px 12px;margin-bottom:5px;display:flex;align-items:center;gap:10px;">'
                '<div style="font-size:1.2rem;min-width:28px;text-align:center;">' + medal + '</div>'
                + char_html +
                '<div style="flex:1;min-width:0;">'
                '<div style="font-size:.9rem;font-weight:700;color:#ffe066;">'
                + entry.get("name", "?") + me_badge + '</div>'
                '<div style="font-size:.7rem;color:#888;">'
                'Lv.' + str(entry.get("level", 1)) + ' | '
                'クエスト ' + str(entry.get("quests_completed", 0)) + '件 | '
                'ボス ' + str(entry.get("boss_attempts", 0)) + '回'
                '</div></div>'
                '<div style="font-size:1.1rem;font-weight:700;color:' + score_color + ';text-align:right;">'
                + f'{entry.get("score", 0):,}' + '<div style="font-size:.65rem;color:#888;">スコア</div>'
                '</div></div>', unsafe_allow_html=True)


# ─── Tab5: アーカイブ ─────────────────────────────────────────
with tab_archive:
    st.markdown(
        '<div style="font-size:1.3rem;font-weight:700;color:#ffe066;margin-bottom:4px;">📚 イベントアーカイブ</div>'
        '<div style="font-size:.82rem;color:#888;margin-bottom:14px;">'
        '過去・未来のイベント情報</div>',
        unsafe_allow_html=True)

    today_month = date.today().month
    for s in SEASONS:
        theme = s.get("theme", {})
        border = theme.get("border", "#4a4a8a")
        primary = theme.get("primary", "#cc88ff")
        banner_bg = theme.get("banner_bg", "#1a1a2e")
        months_str = "・".join([f"{m}月" for m in s["months"]])
        is_current = today_month in s["months"]
        current_badge = (
            ' <span style="background:' + primary + ';color:#fff;font-size:.65rem;'
            'padding:1px 6px;border-radius:6px;font-weight:700;">開催中</span>'
            if is_current else ""
        )

        # そのシーズンのクエスト報酬アイテム一覧
        items_in_season = []
        for q in s.get("quests", []):
            if q.get("reward_item"):
                item_id = q["reward_item"]
                item_def = _EQUIP_ITEMS.get(item_id, {})
                in_inv = item_id in p.get("inventory", [])
                items_in_season.append((item_def.get("icon", "📦"), item_def.get("name", item_id), in_inv))

        items_html = ""
        for icon, name, obtained in items_in_season:
            col = "#44ff88" if obtained else "#888"
            check = "✅ " if obtained else ""
            items_html += f'<span style="color:{col};font-size:.78rem;margin-right:8px;">{icon} {check}{name}</span>'

        with st.expander(s["icon"] + " " + s["name"] + current_badge + f"（{months_str}）", expanded=is_current):
            st.markdown(
                '<div style="font-size:.88rem;color:#aaaacc;margin-bottom:8px;">'
                + s["description"] + '</div>', unsafe_allow_html=True)

            # ボス情報
            boss = s.get("boss", {})
            st.markdown(
                '<div style="background:#1a1a2e;border:1px solid ' + border + ';'
                'border-radius:8px;padding:8px 12px;margin-bottom:8px;">'
                '<div style="font-size:.72rem;color:#888;margin-bottom:3px;">⚔️ イベントボス</div>'
                '<div style="font-size:.9rem;color:' + primary + ';font-weight:700;">'
                + boss.get("emoji", "") + ' ' + boss.get("name", "") + '</div>'
                '<div style="font-size:.75rem;color:#888;">' + boss.get("desc", "") + '</div>'
                '</div>', unsafe_allow_html=True)

            # クエスト一覧
            st.markdown('<div style="font-size:.75rem;color:#888;margin-bottom:4px;">📋 クエスト</div>', unsafe_allow_html=True)
            for q in s.get("quests", []):
                qr_item = q.get("reward_item")
                reward_str = f'EXP×{q["reward_exp"]}'
                if qr_item:
                    qi = _EQUIP_ITEMS.get(qr_item, {})
                    reward_str += f' + {qi.get("icon","📦")} {qi.get("name", qr_item)}'
                st.markdown(
                    f'<div style="font-size:.8rem;color:#ccccee;margin-bottom:3px;">'
                    f'{q.get("icon","")} <b>{q["name"]}</b> — {q["desc"]}'
                    f'<span style="color:#ffe066;margin-left:6px;">({reward_str})</span></div>',
                    unsafe_allow_html=True)

            # 入手済みアイテム表示
            if items_html:
                st.markdown(
                    '<div style="margin-top:8px;font-size:.72rem;color:#888;margin-bottom:3px;">🎁 限定装備</div>'
                    + items_html, unsafe_allow_html=True)

            st.markdown(
                '<div style="font-size:.7rem;color:#555;margin-top:6px;">'
                + s.get("archive_note", "") + '</div>', unsafe_allow_html=True)
