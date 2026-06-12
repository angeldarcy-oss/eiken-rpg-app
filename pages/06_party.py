"""pages/06_party.py — パーティー画面"""
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

from core.save_manager import load_player, save_player
from core.player import PlayerManager
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html, CHARACTERS
from core.monsters import BOSS_MONSTERS, get_weekly_boss
from core.equipment import ITEMS as _EQUIP_ITEMS
from core.party_manager import (
    create_party, join_party, leave_party, get_party,
    start_battle, send_message, claim_rewards,
    get_member_player, get_all_parties,
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
.party-code-box{background:linear-gradient(135deg,#1a1a2e,#2a2a4e);border:2px solid #4466ff;border-radius:14px;padding:18px;text-align:center;margin:12px 0;}
.member-card{background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid #3a3a6a;border-radius:12px;padding:12px 16px;margin-bottom:8px;display:flex;align-items:center;gap:14px;}
.member-card-leader{border-color:#ffcc00;background:linear-gradient(135deg,#1e1a00,#2e2800);}
.party-boss-bar{background:linear-gradient(135deg,#2a0011,#44001a);border:2px solid #ff0044;border-radius:12px;padding:14px 18px;margin:10px 0;}
.chat-box{background:#0a0a1a;border:1px solid #2a2a4a;border-radius:10px;padding:12px;margin:8px 0;max-height:200px;overflow-y:auto;}
.chat-msg{font-size:.85rem;color:#ccccee;margin-bottom:6px;line-height:1.5;}
.log-box{background:#0a0a1a;border:1px solid #2a2a4a;border-radius:10px;padding:12px;margin:8px 0;max-height:160px;overflow-y:auto;}
.log-entry{font-size:.8rem;color:#aaaacc;margin-bottom:4px;}
@keyframes party-pulse{0%,100%{box-shadow:0 0 8px #4466ff44}50%{box-shadow:0 0 20px #4466ffaa}}
</style>""", unsafe_allow_html=True)
st.markdown(MOBILE_CSS, unsafe_allow_html=True)


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


# ─── サイドバー ────────────────────────────────────────────────────
def render_sidebar():
    hp_pct = pm.hp_percent() * 100
    exp_pct = pm.exp_percent() * 100
    char_id = p.get("character", "")
    equip = p.get("equipment")
    with st.sidebar:
        from core.titles import title_badge_html as _tbh
        from core.pets import pet_sidebar_html as _psh
        st.markdown(
            '<div style="text-align:center;padding:12px 0 6px;">'
            + sidebar_avatar_html(char_id, equip) +
            '<div style="font-size:1.2rem;font-weight:700;color:#ffe066;margin-top:6px;">' + p["name"] + '</div>'
            '<div style="font-size:.8rem;color:#aaaacc;">' + t("level", lang) + ' ' + str(p["level"]) + ' | ' + grade_label(p["grade_target"], lang) + '</div>'
            + _tbh(p, style="sidebar") + _psh(p) +
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


# ─── メンバーカード HTML ───────────────────────────────────────────
def _member_card(uname: str, mdata: dict, is_leader: bool) -> str:
    mp = get_member_player(uname)
    char_id = mp.get("character", "") if mp else ""
    char_svg = ""
    if char_id and char_id in CHARACTERS:
        char_svg = '<div style="width:44px;height:55px;flex-shrink:0;">' + CHARACTERS[char_id]["svg"] + '</div>'
    else:
        char_svg = '<div style="font-size:2rem;flex-shrink:0;">⚔️</div>'

    name_str = mdata.get("name", uname)
    dmg = mdata.get("damage_dealt", 0)
    leader_badge = ' <span style="background:#ffcc00;color:#1a1a00;font-size:.6rem;padding:1px 6px;border-radius:8px;font-weight:700;">LEADER</span>' if is_leader else ""

    hp_html = ""
    if mp:
        _hp = mp.get("hp", 0)
        _hpmax = mp.get("hp_max", 100)
        _hppct = round(max(0, _hp / _hpmax * 100), 1) if _hpmax else 0
        _hpcol = "#44ff88" if _hppct > 50 else ("#ffcc00" if _hppct > 25 else "#ff4444")
        _lv = mp.get("level", 1)
        hp_html = (
            '<div style="font-size:.72rem;color:#888;margin-bottom:2px;">Lv' + str(_lv) + ' | HP ' + str(_hp) + '/' + str(_hpmax) + '</div>'
            '<div style="background:#1a0a0a;border-radius:4px;height:6px;overflow:hidden;width:120px;">'
            '<div style="background:' + _hpcol + ';width:' + str(_hppct) + '%;height:100%;"></div>'
            '</div>'
        )

    card_cls = "member-card-leader" if is_leader else ""
    return (
        '<div class="member-card ' + card_cls + '">'
        + char_svg +
        '<div style="flex:1;min-width:0;">'
        '<div style="font-size:.95rem;font-weight:700;color:#ffe066;">' + name_str + leader_badge + '</div>'
        + hp_html +
        '</div>'
        '<div style="text-align:right;flex-shrink:0;">'
        '<div style="font-size:1rem;font-weight:700;color:#ff6644;">' + str(dmg) + '</div>'
        '<div style="font-size:.68rem;color:#888;">ダメージ</div>'
        '</div>'
        '</div>'
    )


# ─── パーティーなし画面 ────────────────────────────────────────────
def render_no_party():
    st.markdown(
        '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">⚔️ パーティー</div>'
        '<div style="font-size:.9rem;color:#888;margin-bottom:20px;">仲間と一緒にボスに挑戦しよう！</div>',
        unsafe_allow_html=True)

    tab_create, tab_join, tab_ranking = st.tabs(["🆕 作成", "📨 参加", "🏆 ランキング"])

    with tab_create:
        st.markdown('<div style="font-size:.9rem;color:#ccccee;margin:12px 0 8px;">パーティーを作成して、コードを仲間にシェアしよう！</div>', unsafe_allow_html=True)
        if st.button("⚔️ パーティーを作成する", use_container_width=True, type="primary"):
            party = create_party(username, p["name"])
            p["party_code"] = party["code"]
            save_player(p, username)
            st.rerun()

    with tab_join:
        st.markdown('<div style="font-size:.9rem;color:#ccccee;margin:12px 0 8px;">仲間から受け取ったパーティーコードを入力して参加しよう！</div>', unsafe_allow_html=True)
        code_input = st.text_input("パーティーコード（6文字）", max_chars=6, placeholder="例: AB1234")
        if st.button("📨 パーティーに参加する", use_container_width=True, type="primary"):
            if not code_input or len(code_input.strip()) != 6:
                st.error("6文字のパーティーコードを入力してください")
            else:
                party, err = join_party(code_input.strip().upper(), username, p["name"])
                if err:
                    st.error(err)
                elif party:
                    p["party_code"] = party["code"]
                    save_player(p, username)
                    st.rerun()

    with tab_ranking:
        _render_party_ranking()


def _render_party_ranking():
    st.markdown('<div style="font-size:.85rem;color:#888;margin-bottom:12px;">パーティーのボス撃破ランキング</div>', unsafe_allow_html=True)
    all_parties = get_all_parties()
    if not all_parties:
        st.info("まだパーティーデータがありません。パーティーを作ってボスに挑戦しよう！")
        return
    finished = [p2 for p2 in all_parties if p2.get("boss_defeats", 0) > 0 or p2.get("status") == "completed"]
    if not finished:
        st.info("まだボスを撃破したパーティーがいません。最初のパーティーになろう！")
        return
    sorted_p = sorted(all_parties, key=lambda x: x.get("boss_defeats", 0), reverse=True)
    MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
    for i, pt in enumerate(sorted_p[:10]):
        rank = i + 1
        medal = MEDALS.get(rank, str(rank))
        members_str = "、".join(m["name"] for m in pt.get("members", {}).values())
        defeats = pt.get("boss_defeats", 0)
        total_dmg = sum(m.get("damage_dealt", 0) for m in pt.get("members", {}).values())
        status_badge = ""
        if pt.get("status") == "battling":
            status_badge = ' <span style="background:#ff4400;color:#fff;font-size:.6rem;padding:1px 6px;border-radius:8px;">バトル中</span>'
        elif pt.get("status") == "completed":
            status_badge = ' <span style="background:#448800;color:#fff;font-size:.6rem;padding:1px 6px;border-radius:8px;">勝利</span>'
        st.markdown(
            '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid #3a3a6a;'
            'border-radius:10px;padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:10px;">'
            '<div style="font-size:1.4rem;min-width:36px;text-align:center;">' + medal + '</div>'
            '<div style="flex:1;min-width:0;">'
            '<div style="font-size:.85rem;color:#ffe066;font-weight:700;">コード: ' + pt["code"] + status_badge + '</div>'
            '<div style="font-size:.72rem;color:#aaaacc;margin-top:2px;">メンバー: ' + members_str + '</div>'
            '</div>'
            '<div style="text-align:right;flex-shrink:0;">'
            '<div style="font-size:1rem;font-weight:700;color:#ff6644;">' + str(defeats) + ' 体</div>'
            '<div style="font-size:.68rem;color:#888;">累計撃破</div>'
            '</div>'
            '</div>', unsafe_allow_html=True)


# ─── ロビー画面 ────────────────────────────────────────────────────
@st.fragment(run_every="5s")
def _lobby_members_fragment(code: str):
    """ロビーのメンバーリスト。5秒ごとに再取得し、開始されたら全体を再描画する。"""
    pt = get_party(code)
    if pt is None or pt.get("status") != "waiting":
        st.rerun(scope="app")
        return
    n = len(pt.get("members", {}))
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin:12px 0 6px;">👥 メンバー（'
                + str(n) + ' / 4 人）</div>', unsafe_allow_html=True)
    members_html = ""
    for uname, mdata in pt.get("members", {}).items():
        members_html += _member_card(uname, mdata, is_leader=(pt.get("leader") == uname))
    st.markdown(members_html, unsafe_allow_html=True)


def render_lobby(party: dict):
    code = party["code"]
    is_leader = (party.get("leader") == username)
    n_members = len(party.get("members", {}))

    st.markdown(
        '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">⚔️ パーティーロビー</div>'
        '<div style="font-size:.9rem;color:#888;margin-bottom:12px;">仲間を待って、準備が整ったらバトルを開始しよう！</div>',
        unsafe_allow_html=True)

    # パーティーコード表示
    st.markdown(
        '<div class="party-code-box" style="animation:party-pulse 2s ease-in-out infinite;">'
        '<div style="font-size:.8rem;color:#8888cc;margin-bottom:6px;">パーティーコード（仲間にシェアしてね）</div>'
        '<div style="font-size:2.8rem;font-weight:900;color:#4488ff;letter-spacing:.15em;font-family:monospace;">'
        + code + '</div>'
        '<div style="font-size:.75rem;color:#6666aa;margin-top:6px;">' + str(n_members) + ' / 4 人参加中</div>'
        '</div>', unsafe_allow_html=True)
    st.code(code, language=None)

    # 週替わりボス情報
    boss = get_weekly_boss()
    st.markdown(
        '<div style="background:linear-gradient(135deg,#220011,#3a0022);border:1px solid #880033;'
        'border-radius:12px;padding:12px 16px;margin:10px 0;display:flex;align-items:center;gap:14px;">'
        '<div style="width:60px;height:60px;flex-shrink:0;">' + boss.get("svg", "") + '</div>'
        '<div>'
        '<div style="font-size:.72rem;color:#cc4466;margin-bottom:2px;">今週の挑戦ボス</div>'
        '<div style="font-size:1.2rem;font-weight:700;color:#ff6688;">'
        + boss.get("emoji", "👑") + ' ' + boss.get("name", "BOSS") + '</div>'
        '<div style="font-size:.8rem;color:#aa4455;">HP ' + str(int(boss["hp"] * (1 + 0.5 * (n_members - 1)))) + ' <span style="color:#666;">（' + str(n_members) + '人スケール）</span></div>'
        '</div>'
        '</div>', unsafe_allow_html=True)

    # メンバーリスト（5秒ごとに自動更新。バトルが始まったら全体を再描画）
    _lobby_members_fragment(code)

    # リーダーのバトル開始ボタン
    if is_leader:
        st.markdown('<div style="font-size:.82rem;color:#888;margin:8px 0;">リーダーのみバトルを開始できます。全員が参加したら開始しましょう！</div>', unsafe_allow_html=True)
        if st.button("⚔️ バトル開始！", use_container_width=True, type="primary"):
            _, err = start_battle(code, boss)
            if err:
                st.error(err)
            else:
                st.rerun()
    else:
        st.info("リーダーがバトルを開始するのを待っています…（自動で更新されます）")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 パーティーを抜ける", use_container_width=True):
        leave_party(code, username)
        p["party_code"] = ""
        save_player(p, username)
        st.rerun()


# ─── バトル画面 ────────────────────────────────────────────────────
@st.fragment(run_every="5s")
def _battle_status_fragment(code: str):
    """ボスHP・メンバー貢献度・バトルログ。5秒ごとに再取得して部分更新する。"""
    party = get_party(code)
    if party is None or party.get("status") != "battling":
        st.rerun(scope="app")  # 勝利・解散などの状態変化は全体を再描画
        return

    boss_info = party.get("boss", {})
    boss_def = BOSS_MONSTERS.get(boss_info.get("id", ""), {})
    boss_svg = boss_def.get("svg", "")
    boss_hp = party.get("boss_hp", 0)
    boss_hp_max = party.get("boss_hp_max", 1)
    boss_pct = round(max(0, boss_hp / boss_hp_max * 100), 1) if boss_hp_max else 0
    boss_col = "#44ff88" if boss_pct > 50 else ("#ffcc00" if boss_pct > 25 else "#ff2222")
    my_damage = party.get("members", {}).get(username, {}).get("damage_dealt", 0)

    # ボスHPバー
    st.markdown(
        '<div class="party-boss-bar">'
        '<div style="display:flex;align-items:center;gap:14px;margin-bottom:8px;">'
        '<div style="width:70px;height:70px;flex-shrink:0;">' + boss_svg + '</div>'
        '<div style="flex:1;">'
        '<div style="font-size:1.1rem;font-weight:700;color:#ff4466;">'
        + boss_info.get("emoji", "👑") + ' ' + boss_info.get("name", "BOSS") + '</div>'
        '<div style="font-size:.8rem;color:#cc3355;margin-bottom:6px;">HP ' + str(boss_hp) + ' / ' + str(boss_hp_max) + '</div>'
        '<div style="background:#1a0008;border-radius:6px;height:18px;overflow:hidden;border:1px solid #550022;">'
        '<div style="background:linear-gradient(90deg,' + boss_col + ',' + boss_col + '88);'
        'width:' + str(boss_pct) + '%;height:100%;border-radius:6px;transition:width .6s ease;"></div>'
        '</div>'
        '</div>'
        '</div>'
        '<div style="font-size:.75rem;color:#886677;text-align:right;">あなたの貢献: <b style="color:#ff8877;">' + str(my_damage) + ' ダメージ</b></div>'
        '</div>', unsafe_allow_html=True)

    # メンバー貢献度
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin:14px 0 6px;">👥 メンバー貢献度</div>', unsafe_allow_html=True)
    members_sorted = sorted(party.get("members", {}).items(), key=lambda x: x[1].get("damage_dealt", 0), reverse=True)
    members_html = ""
    for uname, mdata in members_sorted:
        members_html += _member_card(uname, mdata, is_leader=(party.get("leader") == uname))
    st.markdown(members_html, unsafe_allow_html=True)

    # バトルログ
    st.markdown('<div style="font-size:.95rem;font-weight:700;color:#ffe066;margin:12px 0 4px;">📋 バトルログ</div>', unsafe_allow_html=True)
    log = party.get("battle_log", [])
    if log:
        log_entries = "".join(
            '<div class="log-entry">⚔️ <b style="color:#ffaa88;">' + e.get("name", "?") + '</b> が '
            '<b style="color:#ff6644;">' + str(e.get("damage", 0)) + '</b> ダメージ！'
            ' (残HP: ' + str(e.get("hp_left", 0)) + ')'
            '<span style="color:#555;font-size:.72rem;"> ' + e.get("ts", "")[-8:] + '</span></div>'
            for e in reversed(log[-15:])
        )
        st.markdown('<div class="log-box">' + log_entries + '</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#555;font-size:.82rem;">まだ誰も攻撃していません</div>', unsafe_allow_html=True)


def render_battle(party: dict):
    code = party["code"]

    st.markdown(
        '<div style="font-size:1.8rem;font-weight:700;color:#ff4466;margin-bottom:4px;">⚔️ パーティーバトル中！</div>'
        '<div style="font-size:.85rem;color:#888;margin-bottom:10px;">クエストで正解すると、みんなのダメージがボスに入る！'
        '（ボスHPは自動で更新されます）</div>',
        unsafe_allow_html=True)

    # ボスHP・貢献度・ログ（5秒ごとに自動更新）
    _battle_status_fragment(code)

    # クエストページへの誘導
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a1500,#2a2500);border:1px solid #554400;'
        'border-radius:10px;padding:10px 16px;text-align:center;margin:8px 0;">'
        '<div style="font-size:.9rem;color:#ffe066;">🗡️ クエスト画面で問題を解いてボスを攻撃しよう！</div>'
        '<div style="font-size:.75rem;color:#888;margin-top:2px;">正解するたびにパーティーボスにもダメージが入ります</div>'
        '</div>', unsafe_allow_html=True)

    if st.button("🗡️ クエストへ", use_container_width=True, type="primary"):
        st.switch_page("pages/01_quest.py")

    # パーティーチャット
    _render_chat(party)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 パーティーを抜ける", use_container_width=True):
        leave_party(code, username)
        p["party_code"] = ""
        save_player(p, username)
        st.rerun()


# ─── 勝利画面 ──────────────────────────────────────────────────────
def render_victory(party: dict):
    code = party["code"]
    boss_info = party.get("boss", {})
    already_claimed = username in party.get("rewards_claimed", [])

    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a1000,#3a2800,#1a1000);'
        'border:3px solid #ffcc00;border-radius:16px;padding:24px;text-align:center;margin-bottom:16px;">'
        '<div style="font-size:2.4rem;font-weight:900;color:#ffcc00;'
        'text-shadow:0 0 20px #ffaa00,0 0 40px #ff8800;">🎉 VICTORY！</div>'
        '<div style="font-size:1.1rem;color:#ffe066;margin-top:8px;">'
        + boss_info.get("emoji", "👑") + ' ' + boss_info.get("name", "BOSS") + ' を撃破した！</div>'
        '<div style="font-size:.85rem;color:#cc9900;margin-top:6px;">パーティー全員での勝利おめでとう！</div>'
        '</div>', unsafe_allow_html=True)

    # 報酬受け取り
    if not already_claimed:
        st.markdown('<div style="font-size:.9rem;color:#ccccee;margin-bottom:8px;">⬇️ 報酬を受け取ろう！</div>', unsafe_allow_html=True)
        if st.button("🎁 報酬を受け取る", use_container_width=True, type="primary"):
            rewards = claim_rewards(code, username)
            if rewards:
                item_id = rewards[0]
                item_def = _EQUIP_ITEMS.get(item_id, {})
                item_name = item_def.get("name", item_id)
                p.setdefault("inventory", [])
                if item_id not in p["inventory"]:
                    p["inventory"].append(item_id)
                save_player(p, username)
                st.success("🎁 " + item_name + " を獲得した！インベントリに追加されました。")
                st.rerun()
    else:
        st.markdown(
            '<div style="background:#0a1a0a;border:1px solid #2a5a2a;border-radius:10px;'
            'padding:10px 16px;text-align:center;margin-bottom:12px;">'
            '<div style="color:#44cc44;font-size:.9rem;">✅ 報酬受け取り済み</div>'
            '</div>', unsafe_allow_html=True)

    # 貢献度ランキング
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin:12px 0 6px;">🏆 貢献度ランキング</div>', unsafe_allow_html=True)
    members_sorted = sorted(party.get("members", {}).items(), key=lambda x: x[1].get("damage_dealt", 0), reverse=True)
    members_html = ""
    for uname, mdata in members_sorted:
        members_html += _member_card(uname, mdata, is_leader=(party.get("leader") == uname))
    st.markdown(members_html, unsafe_allow_html=True)

    # チャット
    _render_chat(party)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 パーティーを解散・退出する", use_container_width=True):
        leave_party(code, username)
        p["party_code"] = ""
        save_player(p, username)
        st.rerun()


# ─── チャット共通 ──────────────────────────────────────────────────
def _render_chat(party: dict):
    code = party["code"]
    st.markdown('<div style="font-size:.95rem;font-weight:700;color:#ffe066;margin:12px 0 4px;">💬 パーティーチャット</div>', unsafe_allow_html=True)
    msgs = party.get("messages", [])
    if msgs:
        chat_entries = "".join(
            '<div class="chat-msg"><b style="color:#88aaff;">' + m.get("name", "?") + '</b>'
            '<span style="color:#555;font-size:.72rem;"> ' + m.get("ts", "")[-8:] + '</span>'
            '<br>' + m.get("text", "") + '</div>'
            for m in reversed(msgs[-15:])
        )
        st.markdown('<div class="chat-box">' + chat_entries + '</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#555;font-size:.82rem;margin-bottom:6px;">まだメッセージがありません</div>', unsafe_allow_html=True)

    with st.form("chat_form_" + code, clear_on_submit=True):
        msg_col, btn_col = st.columns([5, 1])
        with msg_col:
            chat_text = st.text_input("メッセージ", label_visibility="collapsed", placeholder="一言メッセージを送ろう！", max_chars=80)
        with btn_col:
            submitted = st.form_submit_button("送信")
        if submitted and chat_text.strip():
            send_message(code, username, p["name"], chat_text.strip())
            st.rerun()


# ─── メインルーティング ────────────────────────────────────────────
party_code = p.get("party_code", "")

if not party_code:
    render_no_party()
else:
    party = get_party(party_code)
    if party is None:
        p["party_code"] = ""
        save_player(p, username)
        st.info("パーティーが見つかりません（解散されたか、コードが無効です）")
        render_no_party()
    else:
        status = party.get("status", "waiting")
        if status == "waiting":
            render_lobby(party)
        elif status == "battling":
            render_battle(party)
        elif status in ("completed",):
            render_victory(party)
        else:
            render_lobby(party)
