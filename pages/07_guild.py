"""pages/07_guild.py — ギルド画面"""
import sys
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from core.mobile_css import MOBILE_CSS
from core.equipment_bonus import sidebar_bonus_html
from core.nav import render_nav

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.save_manager import load_player, save_player, update_ranking
from core.player import PlayerManager, streak_multiplier
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html, CHARACTERS
from core.quiz_engine import QuizEngine
from core.monsters import calc_player_damage
from core.equipment import ITEMS as _EQUIP_ITEMS
from core.titles import title_badge_html as _tbh
from core.pets import pet_sidebar_html as _psh
from core.guild_manager import (
    get_guild, create_guild, join_guild, leave_guild,
    sync_member_stats, post_bulletin,
    set_weekly_goal, claim_weekly_reward, WEEKLY_GOAL_OPTIONS,
    start_guild_boss, guild_boss_deal_damage, claim_guild_boss_reward,
    get_guild_rankings, set_member_role,
    GUILD_BOSS_DROPS,
)


st.markdown("""<style>
html,body,[class*="css"]{font-family:'Noto Sans JP',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460);}
[data-testid="stSidebar"] *{color:#e0e0e0 !important;}
.hp-bar-outer{background:#2a0a0a;border-radius:8px;height:18px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a1a1a;}
.hp-bar-inner{background:linear-gradient(90deg,#e05252,#ff8080);height:100%;border-radius:8px;}
.exp-bar-outer{background:#1a1500;border-radius:8px;height:14px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a4a00;}
.exp-bar-inner{background:linear-gradient(90deg,#c8a000,#ffe066);height:100%;border-radius:8px;}
.stat-label{font-size:11px;color:#aaaacc !important;}
.quiz-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;border-radius:16px;padding:24px 28px;margin-bottom:4px;}
.guild-card{background:linear-gradient(135deg,#1a1a2e,#222244);border:2px solid #4a3a8a;border-radius:14px;padding:18px 22px;margin-bottom:10px;}
.progress-bar-outer{background:#1a1a2e;border-radius:8px;height:14px;overflow:hidden;border:1px solid #3a3a6a;}
.progress-bar-inner{background:linear-gradient(90deg,#cc44ff,#ff88ff);height:100%;border-radius:8px;transition:width .4s ease;}
.boss-hp-outer{background:#1a0a0a;border-radius:6px;height:16px;overflow:hidden;border:1px solid #550022;}
.boss-hp-inner{background:linear-gradient(90deg,#ff2255,#ff88aa);height:100%;border-radius:6px;transition:width .5s ease;}
@keyframes boss-pulse{0%,100%{filter:drop-shadow(0 0 4px #cc44ff)}50%{filter:drop-shadow(0 0 16px #cc44ff)}}
@keyframes victory-glow{0%{box-shadow:0 0 0 #ffcc00;opacity:0}30%{box-shadow:0 0 28px #ffcc00;opacity:1;transform:scale(1.02)}100%{box-shadow:0 0 10px #ff880044;opacity:1;transform:scale(1)}}
.victory-banner{animation:victory-glow .8s ease-out;}
</style>""", unsafe_allow_html=True)
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

_ROLE_LABEL = {"master": "👑 ギルドマスター", "officer": "⚔️ オフィサー", "member": "🧑 メンバー"}
_ROLE_COLOR = {"master": "#ffcc00", "officer": "#88ccff", "member": "#aaaacc"}


# ── 初期化 ─────────────────────────────────────────────────
def init_session():
    if "player" not in st.session_state or st.session_state.player is None:
        st.session_state.player = load_player(st.session_state.get("username", ""))


init_session()
username = st.session_state.get("username", "")

if not username:
    st.warning("先にホーム画面でログインしてください")
    st.stop()

p = st.session_state.player
lang = p.get("language", "ja")
pm = PlayerManager(p)


# ── サイドバー ─────────────────────────────────────────────
def render_sidebar():
    hp_pct = pm.hp_percent() * 100
    exp_pct = pm.exp_percent() * 100
    char_id = p.get("character", "")
    equip = p.get("equipment")
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:12px 0 6px;">'
            + sidebar_avatar_html(char_id, equip) +
            '<div style="font-size:1.2rem;font-weight:700;color:#ffe066;margin-top:6px;">' + p["name"] + '</div>'
            '<div style="font-size:.8rem;color:#aaaacc;">'
            + t("level", lang) + ' ' + str(p["level"]) + ' | ' + grade_label(p["grade_target"], lang) +
            '</div>' + _tbh(p, style="sidebar") + _psh(p) +
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
        guild_code = p.get("guild_code", "")
        if guild_code:
            guild = get_guild(guild_code)
            if guild:
                boss = guild.get("guild_boss", {})
                boss_hp = boss.get("hp", 0)
                boss_max = boss.get("hp_max", 1)
                boss_pct = round(max(0, boss_hp / boss_max * 100), 1) if boss_max else 0
                if boss.get("active"):
                    st.markdown(
                        '<div style="background:linear-gradient(135deg,#1a002a,#2a0044);border:1px solid #cc44ff;'
                        'border-radius:8px;padding:6px 10px;margin-bottom:8px;">'
                        '<div style="font-size:.62rem;color:#cc88ff;margin-bottom:2px;">🏰 ギルドボス出現中</div>'
                        '<div style="font-size:.8rem;color:#ff88ff;font-weight:700;margin-bottom:4px;">'
                        + boss.get("boss_emoji", "") + ' ' + boss.get("boss_name", "") + '</div>'
                        '<div style="background:#2a0033;border-radius:4px;height:7px;overflow:hidden;">'
                        '<div style="background:linear-gradient(90deg,#cc44ff,#ff88ff);width:' + str(boss_pct) + '%;height:100%;"></div>'
                        '</div>'
                        '<div style="font-size:.6rem;color:#bb88ff;margin-top:2px;">HP '
                        + str(boss_hp) + ' / ' + str(boss_max) + '</div>'
                        '</div>', unsafe_allow_html=True)
                st.markdown(
                    '<div style="font-size:.82rem;color:#ccccee;">🏰 ギルド: <b style="color:#cc88ff;">'
                    + guild.get("icon", "🏰") + ' ' + guild.get("name", "") + '</b></div>',
                    unsafe_allow_html=True)
        st.markdown("---")
        render_nav(lang)


render_sidebar()


# ── ギルドバトル用クイズエンジン取得 ─────────────────────────
def _get_battle_engine() -> QuizEngine:
    engine = st.session_state.get("guild_battle_engine")
    if engine is None or engine.grade != p.get("grade_target", "grade_5"):
        engine = QuizEngine(
            grade=p.get("grade_target", "grade_5"),
            data_dir="data/words",
            language="ja",
        )
        st.session_state.guild_battle_engine = engine
    return engine


# ── ギルド未加入UI ──────────────────────────────────────────
def render_no_guild():
    st.markdown(
        '<div style="font-size:2rem;font-weight:700;color:#cc88ff;margin-bottom:4px;">🏰 ギルド</div>'
        '<div style="font-size:.9rem;color:#888;margin-bottom:20px;">'
        'ギルドを作成するか、コードで既存のギルドに参加しよう！</div>',
        unsafe_allow_html=True)

    tab_create, tab_join = st.tabs(["🏗️ ギルドを作成", "🚪 ギルドに参加"])

    with tab_create:
        st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:12px;">新しいギルドを作成</div>', unsafe_allow_html=True)
        icon = st.text_input("ギルドアイコン（絵文字1文字）", value="🏰", max_chars=2)
        guild_name = st.text_input("ギルド名（最大20文字）", max_chars=20, placeholder="例: 英語の騎士団")
        description = st.text_input("紹介文（最大60文字）", max_chars=60, placeholder="例: 一緒に英検を目指そう！")
        if st.button("🏰 ギルドを作成！", use_container_width=True, type="primary"):
            if not guild_name.strip():
                st.error("ギルド名を入力してください")
            else:
                guild = create_guild(
                    username=username,
                    player_name=p["name"],
                    guild_name=guild_name,
                    description=description,
                    icon=icon or "🏰",
                    character=p.get("character", ""),
                )
                p["guild_code"] = guild["code"]
                save_player(p, username)
                st.success(f"ギルド「{guild['name']}」を作成しました！\nコード: **{guild['code']}**")
                st.rerun()

    with tab_join:
        st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:12px;">ギルドに参加</div>', unsafe_allow_html=True)
        join_code = st.text_input("ギルドコード（6文字）", max_chars=6, placeholder="例: ABC123").upper().strip()
        if st.button("🚪 参加する", use_container_width=True, type="primary"):
            if len(join_code) != 6:
                st.error("6文字のコードを入力してください")
            else:
                guild, err = join_guild(join_code, username, p["name"], p.get("character", ""))
                if err:
                    st.error(err)
                elif guild:
                    p["guild_code"] = guild["code"]
                    save_player(p, username)
                    st.success(f"ギルド「{guild['name']}」に参加しました！")
                    st.rerun()


# ── ギルドホームタブ ────────────────────────────────────────
def render_guild_home(guild: dict):
    icon = guild.get("icon", "🏰")
    stats = guild.get("stats", {})
    weekly = guild.get("weekly", {})
    members = guild.get("members", {})
    my_role = members.get(username, {}).get("role", "member")

    # ── ギルドヘッダー ──
    n_members = len(members)
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a0a2a,#2a1a4a);border:2px solid #8844cc;'
        'border-radius:16px;padding:20px 24px;margin-bottom:14px;">'
        '<div style="display:flex;align-items:center;gap:14px;">'
        '<div style="font-size:3rem;">' + icon + '</div>'
        '<div><div style="font-size:1.5rem;font-weight:900;color:#cc88ff;">' + guild["name"] + '</div>'
        '<div style="font-size:.82rem;color:#aaaacc;margin-top:2px;">' + guild.get("description", "") + '</div>'
        '<div style="font-size:.72rem;color:#8866aa;margin-top:4px;">'
        '👥 ' + str(n_members) + '/20人 ｜ コード: <b style="color:#cc88ff;letter-spacing:.1em;">'
        + guild["code"] + '</b></div></div></div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:14px;">'
        '<div style="background:#1a1a2e;border-radius:10px;padding:10px;text-align:center;">'
        '<div style="font-size:.72rem;color:#888;">✨ 総EXP</div>'
        '<div style="font-size:1.3rem;font-weight:700;color:#ffe066;">'
        + f'{stats.get("total_exp", 0):,}' + '</div></div>'
        '<div style="background:#1a1a2e;border-radius:10px;padding:10px;text-align:center;">'
        '<div style="font-size:.72rem;color:#888;">👑 ボス撃破</div>'
        '<div style="font-size:1.3rem;font-weight:700;color:#ff8888;">'
        + str(stats.get("boss_defeats", 0)) + '</div></div>'
        '<div style="background:#1a1a2e;border-radius:10px;padding:10px;text-align:center;">'
        '<div style="font-size:.72rem;color:#888;">🏚️ ダンジョン</div>'
        '<div style="font-size:1.3rem;font-weight:700;color:#88ccff;">'
        + str(stats.get("dungeon_clears", 0)) + '</div></div>'
        '</div></div>', unsafe_allow_html=True)

    # ── 週間目標 ──
    goal_type = weekly.get("goal_type", "correct")
    goal_target = weekly.get("goal_target", 1000)
    goal_current = weekly.get(goal_type, 0)
    goal_pct = min(100, round(goal_current / max(goal_target, 1) * 100, 1))
    goal_label_map = {"correct": "合計正解数", "dungeon": "ダンジョンクリア数", "boss": "ボス撃破数"}
    goal_completed = weekly.get("goal_completed", False)
    already_claimed = username in weekly.get("reward_claimed", [])

    bar_color = "#44ff88" if goal_completed else "#cc44ff"
    completed_badge = (
        '<span style="background:#0a2a0a;border:1px solid #44ff44;color:#44ff88;'
        'border-radius:6px;padding:2px 8px;font-size:.7rem;font-weight:700;">✅ 達成！</span>'
        if goal_completed else ""
    )
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a0a2a,#2a1040);border:1px solid #6633aa;'
        'border-radius:12px;padding:14px 18px;margin-bottom:12px;">'
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        '<div style="font-size:.9rem;font-weight:700;color:#cc88ff;">🎯 週間目標: '
        + goal_label_map.get(goal_type, goal_type) + ' ' + str(goal_target) + '</div>'
        + completed_badge + '</div>'
        '<div class="progress-bar-outer"><div class="progress-bar-inner" style="width:' + str(goal_pct)
        + '%;background:linear-gradient(90deg,' + bar_color + ',' + bar_color + '88);"></div></div>'
        '<div style="font-size:.75rem;color:#888;margin-top:4px;">'
        + str(goal_current) + ' / ' + str(goal_target) + ' (' + str(goal_pct) + '%)</div>'
        '</div>', unsafe_allow_html=True)

    if goal_completed and not already_claimed:
        if st.button("🎁 週間目標報酬を受け取る！ (+500 EXP)", use_container_width=True, type="primary"):
            exp_reward = claim_weekly_reward(guild["code"], username)
            if exp_reward > 0:
                gain = pm.gain_exp(base_exp=exp_reward, streak=p.get("streak", 0))
                save_player(p, username)
                update_ranking(p, username)
                st.success(f"🎉 報酬 +{gain.exp_gained_final} EXP を受け取りました！")
                st.rerun()
    elif goal_completed and already_claimed:
        st.info("✅ 今週の報酬はすでに受け取り済みです", icon="✅")

    # マスター/オフィサーは目標設定可能
    if my_role in ("master", "officer"):
        with st.expander("⚙️ 週間目標を変更"):
            opt_labels = [o["label"] for o in WEEKLY_GOAL_OPTIONS]
            sel_type_label = st.selectbox("目標タイプ", opt_labels)
            sel_opt = next(o for o in WEEKLY_GOAL_OPTIONS if o["label"] == sel_type_label)
            sel_target = st.selectbox("目標値", sel_opt["targets"],
                                       format_func=lambda x: f"{x:,}")
            if st.button("目標を設定", use_container_width=True):
                if set_weekly_goal(guild["code"], username, sel_opt["type"], sel_target):
                    st.success("週間目標を更新しました！")
                    st.rerun()

    st.markdown("---")

    # ── メンバーリスト ──
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:8px;">👥 メンバー一覧</div>', unsafe_allow_html=True)
    sorted_members = sorted(members.items(), key=lambda kv: (
        {"master": 0, "officer": 1, "member": 2}.get(kv[1].get("role", "member"), 2),
        -kv[1].get("total_exp", 0)
    ))
    for uname, mdata in sorted_members:
        role = mdata.get("role", "member")
        char_id = mdata.get("character", "")
        is_me = uname == username
        char_html = (
            '<div style="width:30px;height:38px;flex-shrink:0;">' + CHARACTERS[char_id]["svg"] + '</div>'
            if char_id in CHARACTERS else '<div style="font-size:1.4rem;">🧑</div>'
        )
        me_badge = (' <span style="background:#ffe066;color:#1a1a2e;font-size:.6rem;padding:1px 5px;border-radius:6px;font-weight:700;">YOU</span>'
                    if is_me else "")
        role_col = _ROLE_COLOR.get(role, "#aaaacc")
        extra_border = "border-color:#ffe066;" if is_me else ""
        st.markdown(
            '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid #3a3a6a;'
            + extra_border +
            'border-radius:10px;padding:8px 12px;margin-bottom:5px;display:flex;align-items:center;gap:10px;">'
            + char_html +
            '<div style="flex:1;min-width:0;">'
            '<div style="font-size:.9rem;font-weight:700;color:#ffe066;">'
            + mdata.get("name", uname) + me_badge + '</div>'
            '<div style="font-size:.7rem;color:' + role_col + ';">' + _ROLE_LABEL.get(role, role) + '</div>'
            '</div>'
            '<div style="text-align:right;font-size:.72rem;color:#888;">'
            'Lv.' + str(mdata.get("level", 1)) + '<br>'
            '週 ' + str(mdata.get("weekly_correct", 0)) + '問<br>'
            '総 ' + f'{mdata.get("total_correct", 0):,}' + '問'
            '</div></div>', unsafe_allow_html=True)

    # マスターによる役職管理
    if my_role == "master":
        with st.expander("⚙️ 役職管理"):
            other_members = [(u, d) for u, d in sorted_members if u != username]
            if other_members:
                target_name_map = {d["name"]: u for u, d in other_members}
                target_display = st.selectbox("対象メンバー", list(target_name_map.keys()))
                target_uname = target_name_map[target_display]
                cur_role = members[target_uname].get("role", "member")
                new_role = st.selectbox("新しい役職", ["member", "officer", "master"],
                                         format_func=lambda r: _ROLE_LABEL.get(r, r),
                                         index=["member", "officer", "master"].index(cur_role))
                if st.button("役職を変更", use_container_width=True):
                    ok, err = set_member_role(guild["code"], username, target_uname, new_role)
                    if ok:
                        if new_role == "master":
                            p["guild_code"] = guild["code"]
                        st.success("役職を変更しました！")
                        st.rerun()
                    else:
                        st.error(err)
            else:
                st.info("他のメンバーがいません")

    st.markdown("---")

    # ── ギルド掲示板 ──
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:8px;">📋 ギルド掲示板</div>', unsafe_allow_html=True)
    bulletin = guild.get("bulletin", [])
    if not bulletin:
        st.markdown('<div style="font-size:.85rem;color:#666;text-align:center;padding:10px;">まだ投稿がありません</div>', unsafe_allow_html=True)
    for msg in reversed(bulletin[-15:]):
        ts = msg.get("ts", "")[:16].replace("T", " ")
        is_me_msg = msg.get("username") == username
        bg = "background:#1a2a0a;border-color:#336633;" if is_me_msg else "background:#1a1a2e;border-color:#3a3a6a;"
        st.markdown(
            '<div style="' + bg + 'border:1px solid;border-radius:10px;padding:8px 14px;margin-bottom:5px;">'
            '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:3px;">'
            '<span style="font-size:.82rem;font-weight:700;color:#cc88ff;">' + msg.get("name", "?") + '</span>'
            '<span style="font-size:.65rem;color:#555;">' + ts + '</span></div>'
            '<div style="font-size:.88rem;color:#e0e0e0;">' + msg["text"] + '</div>'
            '</div>', unsafe_allow_html=True)

    with st.form("bulletin_form", clear_on_submit=True):
        msg_text = st.text_input("一言メッセージ（最大100文字）", max_chars=100, placeholder="みんなへのメッセージ...")
        if st.form_submit_button("📬 投稿", use_container_width=True):
            if post_bulletin(guild["code"], username, p["name"], msg_text):
                st.rerun()

    st.markdown("---")
    if st.button("🚪 ギルドを脱退する", use_container_width=True):
        st.session_state["_guild_leave_confirm"] = True

    if st.session_state.get("_guild_leave_confirm"):
        st.warning("本当にギルドを脱退しますか？（ギルドマスターの場合は他メンバーに引き継がれます）")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ 脱退する", use_container_width=True, type="primary"):
                leave_guild(guild["code"], username)
                p["guild_code"] = ""
                save_player(p, username)
                st.session_state.pop("_guild_leave_confirm", None)
                st.rerun()
        with col_b:
            if st.button("キャンセル", use_container_width=True):
                st.session_state.pop("_guild_leave_confirm", None)
                st.rerun()


# ── ギルドバトルタブ ────────────────────────────────────────
def render_guild_battle(guild: dict):
    members = guild.get("members", {})
    my_role = members.get(username, {}).get("role", "member")
    boss = guild.get("guild_boss", {})

    st.markdown(
        '<div style="font-size:1.8rem;font-weight:900;color:#cc88ff;margin-bottom:4px;">⚔️ ギルドバトル</div>'
        '<div style="font-size:.85rem;color:#888;margin-bottom:16px;">'
        'ギルドメンバー全員で協力してボスを倒そう！正解するたびにダメージ！</div>',
        unsafe_allow_html=True)

    # ── ボス撃破済み表示 ──
    if boss.get("defeated") and not boss.get("active"):
        from core.save_manager import save_player as _sp, update_ranking as _ur
        if username not in boss.get("rewards_claimed", []):
            st.markdown(
                '<div class="victory-banner" style="background:linear-gradient(135deg,#1a1000,#3a2800);'
                'border:3px solid #ffcc00;border-radius:16px;padding:20px;text-align:center;margin-bottom:14px;">'
                '<div style="font-size:2rem;font-weight:900;color:#ffcc00;">🏆 ギルドボス撃破！</div>'
                '<div style="color:#ffe066;margin-top:6px;">'
                + boss.get("boss_emoji", "") + ' ' + boss.get("boss_name", "") + '</div>'
                '</div>', unsafe_allow_html=True)
            if st.button("🎁 報酬を受け取る！", use_container_width=True, type="primary"):
                drops = claim_guild_boss_reward(guild["code"], username)
                for item_id in drops:
                    item_def = _EQUIP_ITEMS.get(item_id, {})
                    inv = p.setdefault("inventory", [])
                    if item_id not in inv:
                        inv.append(item_id)
                _sp(p, username)
                _ur(p, username)
                if drops:
                    item_name = _EQUIP_ITEMS.get(drops[0], {}).get("name", drops[0])
                    item_icon = _EQUIP_ITEMS.get(drops[0], {}).get("icon", "📦")
                    st.success(f"🎉 {item_icon} 「{item_name}」をゲット！")
                    st.balloons()
                st.rerun()
        else:
            st.success("✅ このギルドボスの報酬はすでに受け取り済みです")
            st.markdown('<div style="font-size:.85rem;color:#888;text-align:center;margin:10px 0;">次のボスはギルドマスター/オフィサーが召喚できます</div>', unsafe_allow_html=True)

    # ── ボス出現中 ──
    if boss.get("active"):
        boss_hp = boss.get("hp", 0)
        boss_max = boss.get("hp_max", 1)
        boss_pct = round(max(0, boss_hp / boss_max * 100), 1)
        hp_col = "#44ff88" if boss_pct > 50 else ("#ffcc00" if boss_pct > 25 else "#ff2222")

        st.markdown(
            '<div style="background:linear-gradient(135deg,#1a0030,#2a0050);border:2px solid #cc44ff;'
            'border-radius:14px;padding:16px 20px;margin-bottom:12px;">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
            '<div style="font-size:1.1rem;font-weight:700;color:#ff88ff;animation:boss-pulse 1.8s ease-in-out infinite;">'
            + boss.get("boss_emoji", "") + ' ' + boss.get("boss_name", "") + '</div>'
            '<div style="font-size:.82rem;color:#cc44ff;">HP ' + str(boss_hp) + ' / ' + str(boss_max) + '</div>'
            '</div>'
            '<div class="boss-hp-outer"><div class="boss-hp-inner" style="background:linear-gradient(90deg,'
            + hp_col + ',' + hp_col + '88);width:' + str(boss_pct) + '%;"></div></div>'
            '</div>', unsafe_allow_html=True)

        # ボスSVG表示
        svg_html = boss.get("boss_svg", "")
        if svg_html:
            st.markdown(
                '<div style="text-align:center;margin:8px 0 12px;">'
                '<div style="display:inline-block;width:110px;height:110px;'
                'animation:boss-pulse 1.8s ease-in-out infinite;">'
                + svg_html + '</div></div>', unsafe_allow_html=True)

        # バトルログ（直近5件）
        battle_log = boss.get("battle_log", [])[-5:]
        if battle_log:
            log_html = '<div style="font-size:.72rem;color:#888;margin-bottom:10px;">'
            for entry in reversed(battle_log):
                log_html += (
                    '<div>⚔️ <b style="color:#cc88ff;">' + entry.get("name", "?") + '</b> → '
                    '<span style="color:#ff8888;">-' + str(entry.get("damage", 0)) + '</span>'
                    ' (残HP: ' + str(entry.get("hp_left", 0)) + ')</div>'
                )
            log_html += '</div>'
            st.markdown(log_html, unsafe_allow_html=True)

        # クイズバトルUI
        battle_mode = st.session_state.get("guild_battle_mode")

        if battle_mode is None:
            if st.button("⚔️ ボスを攻撃！", use_container_width=True, type="primary"):
                engine = _get_battle_engine()
                q = engine.get_next_question()
                if q is None:
                    engine.reset_session()
                    q = engine.get_next_question()
                st.session_state.guild_battle_mode = "question"
                st.session_state.guild_battle_q = q
                st.rerun()

        elif battle_mode == "question":
            q = st.session_state.get("guild_battle_q")
            if q is None:
                st.session_state.guild_battle_mode = None
                st.rerun()
                return
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
                    if st.button(labels[i] + "　" + choice, key="gb_" + str(i), use_container_width=True):
                        engine = _get_battle_engine()
                        result = engine.judge(q, selected_answer=choice)
                        st.session_state.guild_battle_result = result
                        st.session_state.guild_battle_mode = "result"
                        if result.is_correct:
                            dmg = calc_player_damage(q.difficulty) * 2
                            guild_updated = guild_boss_deal_damage(
                                guild["code"], username, p["name"], dmg)
                            st.session_state.guild_battle_dmg = dmg
                            if guild_updated:
                                st.session_state.guild_battle_guild = guild_updated
                        else:
                            st.session_state.guild_battle_dmg = 0
                        st.rerun()

        elif battle_mode == "result":
            result = st.session_state.get("guild_battle_result")
            q = st.session_state.get("guild_battle_q")
            dmg = st.session_state.get("guild_battle_dmg", 0)

            if result and result.is_correct:
                st.markdown(
                    '<div style="background:linear-gradient(135deg,#0a1a30,#102040);border:1px solid #2255aa;'
                    'border-radius:12px;padding:14px 18px;margin:10px 0;">'
                    '<div style="font-size:1rem;font-weight:700;color:#6699ff;margin-bottom:4px;">'
                    '⚔️ ヒット！ <span style="color:#ff8888;">-' + str(dmg) + ' ダメージ！</span></div>'
                    '<div style="color:#cceebb;font-size:.88rem;"><b style="color:#fff;">'
                    + (q.word if q else "") + '</b> = ' + (q.meaning_ja if q else "") + '</div>'
                    '</div>', unsafe_allow_html=True)
            elif result:
                st.markdown(
                    '<div style="background:linear-gradient(135deg,#2a0a0a,#4a1a1a);border:1px solid #7a2a2a;'
                    'border-radius:12px;padding:14px 18px;margin:10px 0;">'
                    '<div style="font-size:1rem;font-weight:700;color:#ff8080;margin-bottom:4px;">'
                    '❌ ミス！ダメージなし</div>'
                    '<div style="color:#ffcccc;font-size:.88rem;">正解: <b style="color:#ffe066;">'
                    + (q.correct_answer if q else "") + '</b></div>'
                    '</div>', unsafe_allow_html=True)

            # ボスが倒れた場合
            updated_guild = st.session_state.get("guild_battle_guild", guild)
            if updated_guild.get("guild_boss", {}).get("hp", 1) <= 0:
                st.balloons()
                st.markdown(
                    '<div style="background:linear-gradient(135deg,#1a1000,#3a2800);border:2px solid #ffcc00;'
                    'border-radius:12px;padding:14px 18px;text-align:center;margin:10px 0;">'
                    '<div style="font-size:1.5rem;font-weight:900;color:#ffcc00;">🏆 ボスを倒した！</div>'
                    '</div>', unsafe_allow_html=True)
                st.session_state.guild_battle_mode = None
                if st.button("🎉 報酬を確認する", use_container_width=True, type="primary"):
                    st.rerun()
            else:
                if st.button("⚔️ 次の攻撃へ", use_container_width=True, type="primary"):
                    engine = _get_battle_engine()
                    q2 = engine.get_next_question()
                    if q2 is None:
                        engine.reset_session()
                        q2 = engine.get_next_question()
                    st.session_state.guild_battle_mode = "question"
                    st.session_state.guild_battle_q = q2
                    st.rerun()

    # ── ボス未出現（召喚フォーム）──
    elif not boss.get("defeated"):
        st.markdown(
            '<div style="text-align:center;padding:30px;background:linear-gradient(135deg,#1a1a2e,#222244);'
            'border:1px solid #3a3a6a;border-radius:14px;margin-bottom:16px;">'
            '<div style="font-size:3rem;margin-bottom:10px;">🐉</div>'
            '<div style="font-size:1.1rem;color:#aaaacc;">ギルドボスがまだ出現していません</div>'
            '<div style="font-size:.82rem;color:#666;margin-top:6px;">'
            'ギルドマスター・オフィサーがボスを召喚できます</div>'
            '</div>', unsafe_allow_html=True)

        if my_role in ("master", "officer"):
            if st.button("🐉 ギルドボスを召喚！", use_container_width=True, type="primary"):
                ok, err = start_guild_boss(guild["code"], username)
                if ok:
                    st.session_state.guild_battle_mode = None
                    st.rerun()
                else:
                    st.error(err)

    # ── 過去のバトルログ ──
    log = boss.get("battle_log", [])
    if log and not boss.get("active"):
        with st.expander("📜 直近バトルログ"):
            for entry in reversed(log[-20:]):
                ts = entry.get("ts", "")[:16].replace("T", " ")
                st.markdown(
                    f'<div style="font-size:.75rem;color:#888;">'
                    f'[{ts}] <b style="color:#cc88ff;">{entry.get("name","?")}</b> → '
                    f'<span style="color:#ff8888;">-{entry.get("damage",0)}</span> '
                    f'(残HP: {entry.get("hp_left",0)})</div>',
                    unsafe_allow_html=True)


# ── ギルドランキングタブ ─────────────────────────────────────
def render_guild_ranking():
    st.markdown(
        '<div style="font-size:1.8rem;font-weight:900;color:#cc88ff;margin-bottom:4px;">🏆 ギルドランキング</div>'
        '<div style="font-size:.85rem;color:#888;margin-bottom:16px;">全ギルドの実力を比べよう！</div>',
        unsafe_allow_html=True)

    rankings = get_guild_rankings()
    my_guild_code = p.get("guild_code", "")
    MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

    tab_exp, tab_boss, tab_weekly = st.tabs(["✨ 総EXP順", "👑 ボス撃破順", "🔥 今週の正解数"])

    def _guild_row(i: int, g: dict, value_str: str, value_color: str):
        rank = i + 1
        medal = MEDALS.get(rank, str(rank))
        is_mine = g.get("code") == my_guild_code
        n = len(g.get("members", {}))
        extra = "border-color:#cc88ff;background:linear-gradient(135deg,#1a0a2a,#2a1a4a);" if is_mine else ""
        me_badge = (' <span style="background:#cc88ff;color:#1a1a2e;font-size:.6rem;padding:1px 5px;border-radius:6px;font-weight:700;">MY GUILD</span>'
                    if is_mine else "")
        st.markdown(
            '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid #3a3a6a;'
            + extra +
            'border-radius:10px;padding:9px 14px;margin-bottom:5px;display:flex;align-items:center;gap:10px;">'
            '<div style="font-size:1.3rem;min-width:32px;text-align:center;">' + medal + '</div>'
            '<div style="font-size:1.8rem;min-width:32px;text-align:center;">' + g.get("icon", "🏰") + '</div>'
            '<div style="flex:1;min-width:0;">'
            '<div style="font-size:.9rem;font-weight:700;color:#cc88ff;">' + g.get("name", "?") + me_badge + '</div>'
            '<div style="font-size:.7rem;color:#888;">👥 ' + str(n) + '人</div>'
            '</div>'
            '<div style="font-size:1rem;font-weight:700;color:' + value_color + ';text-align:right;">'
            + value_str + '</div>'
            '</div>', unsafe_allow_html=True)

    with tab_exp:
        guilds = rankings["by_exp"]
        if not guilds:
            st.info("まだギルドがありません")
        else:
            for i, g in enumerate(guilds):
                v = g.get("stats", {}).get("total_exp", 0)
                _guild_row(i, g, f'{v:,} EXP', "#ffe066")

    with tab_boss:
        guilds = rankings["by_boss"]
        if not guilds:
            st.info("まだギルドがありません")
        else:
            for i, g in enumerate(guilds):
                v = g.get("stats", {}).get("boss_defeats", 0)
                _guild_row(i, g, f'{v} 撃破', "#ff8888")

    with tab_weekly:
        guilds = rankings["by_weekly"]
        if not guilds:
            st.info("まだギルドがありません")
        else:
            week_start = rankings.get("week_start", "")
            st.markdown(f'<div style="font-size:.75rem;color:#666;margin-bottom:8px;">集計期間: {week_start} ～</div>', unsafe_allow_html=True)
            for i, g in enumerate(guilds):
                cur_week = rankings.get("week_start", "")
                w = g.get("weekly", {})
                v = w.get("correct", 0) if w.get("week_start") == cur_week else 0
                _guild_row(i, g, f'{v:,} 問', "#88ccff")


# ── メインルーティング ─────────────────────────────────────
guild_code = p.get("guild_code", "")

if not guild_code:
    render_no_guild()
else:
    guild = get_guild(guild_code)
    if guild is None:
        st.error("ギルドデータが見つかりません。ギルドコードをリセットします。")
        p["guild_code"] = ""
        save_player(p, username)
        st.rerun()
    else:
        # メンバーステータスを同期
        sync_member_stats(guild_code, username, p)
        guild = get_guild(guild_code)  # 同期後に再読み込み

        st.markdown(
            '<div style="font-size:2rem;font-weight:700;color:#cc88ff;margin-bottom:2px;">'
            '🏰 ギルド</div>'
            '<div style="font-size:.85rem;color:#888;margin-bottom:12px;">'
            + guild.get("icon", "🏰") + ' <b style="color:#cc88ff;">' + guild.get("name", "") + '</b>'
            '</div>', unsafe_allow_html=True)

        tab_home, tab_battle, tab_ranking = st.tabs(["🏠 ホーム", "⚔️ ギルドバトル", "🏆 ランキング"])

        with tab_home:
            render_guild_home(guild)
        with tab_battle:
            # バトル後にギルドデータを再読み込み
            guild_for_battle = st.session_state.get("guild_battle_guild") or guild
            render_guild_battle(guild_for_battle)
        with tab_ranking:
            render_guild_ranking()
