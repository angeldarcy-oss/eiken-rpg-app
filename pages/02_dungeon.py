"""pages/02_dungeon.py — ダンジョン画面"""
import sys
import time
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.mobile_css import MOBILE_CSS
from core.equipment_bonus import sidebar_bonus_html
from core.nav import render_nav

from core.save_manager import load_player, save_player, update_ranking
from core.player import PlayerManager, streak_multiplier
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html, CHARACTERS
from core.quiz_engine import QuizEngine
from core.monsters import get_monster_for_grade, calc_player_damage
from core.equipment import ITEMS as _EQUIP_ITEMS
from core.titles import evaluate_titles, _TITLE_MAP as _TITLES_MAP
from core.dungeon_manager import (
    DUNGEONS, get_dungeon, get_player_dungeon_progress,
    record_clear, update_dungeon_ranking, get_dungeon_ranking,
)


def _get_audio_b64(word: str):
    try:
        from gtts import gTTS
        import io, base64
        tts = gTTS(text=word, lang="en", slow=True)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()
    except Exception:
        return None




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
.mon-hp-outer{background:#1a0a0a;border-radius:5px;height:10px;overflow:hidden;margin-top:4px;}
.mon-hp-inner{height:100%;border-radius:5px;}
.progress-bar-outer{background:#1a1a2e;border-radius:8px;height:14px;overflow:hidden;border:1px solid #3a3a6a;}
.progress-bar-inner{background:linear-gradient(90deg,#4488ff,#88ccff);height:100%;border-radius:8px;transition:width .5s ease;}
@keyframes boss-pulse{0%,100%{filter:drop-shadow(0 0 4px #ff0044)}50%{filter:drop-shadow(0 0 14px #ff0044)}}
</style>""", unsafe_allow_html=True)
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

_GRADE_MAP = {
    "grade_5": "5級", "grade_4": "4級", "grade_3": "3級",
    "grade_pre2": "準2級", "grade_2": "2級",
}


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
            '<div style="font-size:.8rem;color:#aaaacc;">'
            + t("level", lang) + ' ' + str(p["level"]) + ' | ' + grade_label(p["grade_target"], lang) + '</div>'
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
        clears = sum(1 for d in DUNGEONS if get_player_dungeon_progress(p, d["id"])["clears"] > 0)
        st.markdown(
            '<div style="font-size:.82rem;color:#ccccee;">'
            '🏚️ クリア済み <b style="color:#ffe066;">' + str(clears) + '</b> / 5 ダンジョン'
            '</div>', unsafe_allow_html=True)
        st.markdown("---")
        render_nav(lang)


render_sidebar()


# ─── ダンジョン初期化 ──────────────────────────────────────────────
def init_dungeon(dungeon_id: str):
    dungeon = get_dungeon(dungeon_id)
    if dungeon is None:
        return
    engine = QuizEngine(grade=dungeon["grade"], data_dir="data/words", language="ja")
    st.session_state.dungeon_active = True
    st.session_state.dungeon_id = dungeon_id
    st.session_state.dungeon_engine = engine
    st.session_state.dungeon_correct = 0
    st.session_state.dungeon_total = 0
    st.session_state.dungeon_start_time = time.time()
    st.session_state.dungeon_boss_active = False
    st.session_state.dungeon_cleared = False
    st.session_state.dungeon_question = None
    st.session_state.dungeon_answered = False
    st.session_state.dungeon_last_result = None
    st.session_state.dungeon_damage_this_turn = 0
    st.session_state.dungeon_last_gain = None
    st.session_state.dungeon_rewards = None
    st.session_state.dungeon_show_result = False
    _spawn_monster(dungeon_id, force_boss=False)


def _spawn_monster(dungeon_id: str, force_boss: bool = False):
    dungeon = get_dungeon(dungeon_id)
    if dungeon is None:
        return
    if force_boss:
        boss = dict(dungeon["boss_def"])
        boss["is_boss"] = True
        st.session_state.dungeon_monster = boss
        st.session_state.dungeon_monster_hp = boss["hp"]
        st.session_state.dungeon_boss_active = True
    else:
        m = dict(get_monster_for_grade(dungeon["grade"]))
        m["is_boss"] = False
        m["hp"] = calc_player_damage(1)  # 1問正解で倒せるHP
        st.session_state.dungeon_monster = m
        st.session_state.dungeon_monster_hp = m["hp"]


def _load_question():
    engine = st.session_state.get("dungeon_engine")
    if engine is None:
        return
    q = engine.get_next_question()
    if q is None:
        dungeon_id = st.session_state.get("dungeon_id", "cave")
        dungeon = get_dungeon(dungeon_id)
        if dungeon:
            st.session_state.dungeon_engine = QuizEngine(
                grade=dungeon["grade"], data_dir="data/words", language="ja")
            q = st.session_state.dungeon_engine.get_next_question()
    st.session_state.dungeon_question = q
    st.session_state.dungeon_answered = False
    st.session_state.dungeon_last_result = None
    st.session_state.dungeon_damage_this_turn = 0


def _exit_dungeon():
    for k in ["dungeon_active", "dungeon_id", "dungeon_engine", "dungeon_correct",
              "dungeon_total", "dungeon_start_time", "dungeon_boss_active", "dungeon_cleared",
              "dungeon_question", "dungeon_answered", "dungeon_last_result",
              "dungeon_damage_this_turn", "dungeon_monster", "dungeon_monster_hp",
              "dungeon_rewards", "dungeon_last_gain", "dungeon_show_result",
              "dungeon_clear_time", "dungeon_clear_accuracy", "dungeon_new_titles"]:
        st.session_state.pop(k, None)


# ─── 正解・不正解処理 ──────────────────────────────────────────────
def _on_correct(result, question=None):
    gain = pm.gain_exp(base_exp=result.exp_gained, streak=p.get("streak", 0))
    pm.increment_streak()
    st.session_state.dungeon_last_gain = gain

    _diff = getattr(question, "difficulty", 1) if question else 1
    _dmg = calc_player_damage(_diff)
    st.session_state.dungeon_damage_this_turn = _dmg
    st.session_state.dungeon_monster_hp = max(0, st.session_state.dungeon_monster_hp - _dmg)

    st.session_state.dungeon_correct += 1
    p["weekly_correct"] = p.get("weekly_correct", 0) + 1
    p["weekly_total"] = p.get("weekly_total", 0) + 1
    p["total_correct_ever"] = p.get("total_correct_ever", 0) + 1
    p["total_questions_ever"] = p.get("total_questions_ever", 0) + 1

    dungeon = get_dungeon(st.session_state.get("dungeon_id", "cave"))
    if dungeon and st.session_state.dungeon_correct >= dungeon["required_correct"]:
        # ダンジョンクリア：報酬を一度だけ計算
        st.session_state.dungeon_cleared = True
        st.session_state.dungeon_monster_hp = 0  # ボスを力場KO
        time_sec = time.time() - st.session_state.get("dungeon_start_time", time.time())
        total = st.session_state.get("dungeon_total", 1)
        correct = st.session_state.dungeon_correct
        accuracy = round(correct / max(total, 1) * 100, 1)
        rewards = record_clear(p, st.session_state.dungeon_id, time_sec, accuracy)
        new_titles = evaluate_titles(p)
        save_player(p, username)
        update_ranking(p, username)
        update_dungeon_ranking(username, p["name"], st.session_state.dungeon_id,
                               time_sec, accuracy, p.get("character", ""))
        st.session_state.dungeon_rewards = rewards
        st.session_state.dungeon_clear_time = time_sec
        st.session_state.dungeon_clear_accuracy = accuracy
        st.session_state.dungeon_new_titles = new_titles


def _on_wrong(result):
    pm.take_damage(result.hp_damage)
    pm.reset_streak()
    p["weekly_total"] = p.get("weekly_total", 0) + 1
    p["total_questions_ever"] = p.get("total_questions_ever", 0) + 1
    st.session_state.dungeon_damage_this_turn = 0


def _next_step():
    if st.session_state.get("dungeon_cleared"):
        return
    correct = st.session_state.get("dungeon_correct", 0)
    dungeon_id = st.session_state.get("dungeon_id", "cave")
    dungeon = get_dungeon(dungeon_id)
    if dungeon is None:
        return
    required = dungeon["required_correct"]
    is_boss = st.session_state.get("dungeon_boss_active", False)
    # ボスは一度登場したら入れ替えない
    if not is_boss:
        _spawn_monster(dungeon_id, force_boss=(correct >= required - 1))
    _load_question()


# ─── マップ画面 ────────────────────────────────────────────────────
def render_map():
    st.markdown(
        '<div style="font-size:2rem;font-weight:700;color:#ffe066;margin-bottom:4px;">🏚️ ダンジョン</div>'
        '<div style="font-size:.9rem;color:#888;margin-bottom:18px;">挑戦するダンジョンを選ぼう！</div>',
        unsafe_allow_html=True)

    for dungeon in DUNGEONS:
        prog = get_player_dungeon_progress(p, dungeon["id"])
        is_cleared = prog["clears"] > 0
        theme = dungeon["theme_color"]
        _t = int(prog["best_time"]) if prog["best_time"] is not None else None
        best_time_str = (f'{_t // 60}分{_t % 60}秒' if _t is not None else "---")
        best_acc_str = (f'{prog["best_accuracy"]}%' if prog["best_accuracy"] is not None else "---")
        cleared_badge = (
            '<span style="background:#1a4a1a;border:1px solid #44cc44;color:#44ff88;'
            'border-radius:8px;padding:2px 8px;font-size:.7rem;font-weight:700;">✅ クリア済み</span>'
            if is_cleared else
            '<span style="background:#1a1a1a;border:1px solid #444;color:#888;'
            'border-radius:8px;padding:2px 8px;font-size:.7rem;">🔒 未クリア</span>'
        )
        st.markdown(
            '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);'
            'border:2px solid ' + theme + '55;border-radius:14px;overflow:hidden;margin-bottom:12px;">'
            '<div style="width:100%;height:110px;overflow:hidden;">' + dungeon["map_svg"] + '</div>'
            '<div style="padding:12px 16px;">'
            '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">'
            '<div><span style="font-size:1.2rem;font-weight:700;color:#ffe066;">'
            + dungeon["emoji"] + ' ' + dungeon["name"] + '</span>'
            '<span style="font-size:.72rem;color:#888;margin-left:10px;">'
            + _GRADE_MAP.get(dungeon["grade"], dungeon["grade"]) + ' | ' + dungeon["diff_label"] + '</span>'
            '</div>' + cleared_badge + '</div>'
            '<div style="font-size:.78rem;color:#aaaacc;margin-bottom:8px;">'
            '🏆 クリア: <b style="color:#ffe066;">' + str(prog["clears"]) + '</b> 回　'
            '⏱ ベスト: <b style="color:#88ccff;">' + best_time_str + '</b>　'
            '📊 最高正答率: <b style="color:#88ff88;">' + best_acc_str + '</b>'
            '</div>'
            '</div></div>', unsafe_allow_html=True)

        btn_type = "primary" if not is_cleared else "secondary"
        if st.button('⚔️ ' + dungeon["name"] + 'に挑戦！', key='enter_' + dungeon["id"],
                     use_container_width=True, type=btn_type):
            init_dungeon(dungeon["id"])
            st.rerun()


# ─── バトル画面 ────────────────────────────────────────────────────
def render_battle():
    dungeon_id = st.session_state.get("dungeon_id", "cave")
    dungeon = get_dungeon(dungeon_id)
    if dungeon is None:
        _exit_dungeon()
        st.rerun()
        return

    correct = st.session_state.get("dungeon_correct", 0)
    required = dungeon["required_correct"]
    is_boss = st.session_state.get("dungeon_boss_active", False)
    monster = st.session_state.get("dungeon_monster", {})
    monster_hp = st.session_state.get("dungeon_monster_hp", 0)
    monster_hp_max = max(monster.get("hp", 1), 1)
    damage = st.session_state.get("dungeon_damage_this_turn", 0)

    # ── ヘッダー ──
    theme = dungeon["theme_color"]
    boss_badge = ('<span style="background:#5a0022;border:1px solid #ff0044;color:#ff4466;'
                  'border-radius:6px;padding:2px 8px;font-size:.75rem;">👑 BOSS BATTLE！</span>'
                  if is_boss else "")
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);'
        'border:2px solid ' + theme + ';border-radius:14px;padding:12px 18px;margin-bottom:12px;">'
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        '<div style="font-size:1rem;font-weight:700;color:#ffe066;">'
        + dungeon["emoji"] + ' ' + dungeon["name"] + '</div>'
        + boss_badge + '</div>'
        '<div style="font-size:.78rem;color:#aaaacc;margin-bottom:5px;">正解: '
        + str(correct) + ' / ' + str(required) + '</div>'
        '<div class="progress-bar-outer"><div class="progress-bar-inner" style="width:'
        + str(round(correct / required * 100, 1)) + '%;'
        + ('background:linear-gradient(90deg,#ff4444,#ff8888);' if is_boss else '') + '"></div>'
        '</div></div>', unsafe_allow_html=True)

    # ── モンスター ──
    hp_pct = round(max(0, monster_hp / monster_hp_max * 100), 1)
    hp_col = "#44ff88" if hp_pct > 50 else ("#ffcc00" if hp_pct > 25 else "#ff2222")
    damage_html = ('<div style="position:absolute;top:-10px;right:-10px;font-size:1.2rem;'
                   'font-weight:900;color:#ffe066;text-shadow:0 0 8px #ffcc00;">-' + str(damage) + '</div>'
                   if damage > 0 else "")
    svg_size = 110 if is_boss else 82
    boss_style = 'style="animation:boss-pulse 1.8s ease-in-out infinite;"' if is_boss else ""
    st.markdown(
        '<div style="text-align:center;margin-bottom:8px;">'
        '<div style="position:relative;display:inline-block;width:' + str(svg_size) + 'px;" ' + boss_style + '>'
        '<div style="width:' + str(svg_size) + 'px;height:' + str(svg_size) + 'px;'
        'display:flex;align-items:center;justify-content:center;">'
        '<div style="width:100%;height:100%;">' + monster.get("svg", "") + '</div>'
        '</div>' + damage_html + '</div>'
        '<div style="font-size:.9rem;font-weight:700;color:'
        + ('#ff4466' if is_boss else '#e8d8ff') + ';margin-top:4px;">'
        + monster.get("emoji", "") + ' ' + monster.get("name", "モンスター") + '</div>'
        '<div style="max-width:' + str(svg_size + 20) + 'px;margin:4px auto 0;">'
        '<div class="mon-hp-outer"><div class="mon-hp-inner" style="background:' + hp_col
        + ';width:' + str(hp_pct) + '%;"></div></div>'
        '<div style="font-size:.7rem;color:#888;margin-top:1px;">HP ' + str(max(0, monster_hp))
        + ' / ' + str(monster_hp_max) + '</div>'
        '</div></div>', unsafe_allow_html=True)

    # ── 問題ロード ──
    if st.session_state.get("dungeon_question") is None:
        _load_question()
        st.rerun()

    q = st.session_state.dungeon_question
    if q is None:
        st.error("問題を読み込めませんでした")
        return

    streak = p.get("streak", 0)
    mult = streak_multiplier(streak)
    bonus_span = (' <span style="background:#2a1a00;color:#ffe066;border:1px solid #5a3a00;'
                  'border-radius:6px;padding:1px 6px;font-size:.7rem;">🔥 ×' + str(mult) + '</span>'
                  if mult > 1.0 else "")
    st.markdown(
        '<div class="quiz-card">'
        '<div style="font-size:.85rem;color:#aaaacc;text-align:center;margin-bottom:16px;">'
        + '⭐' * q.difficulty + bonus_span + '</div>'
        '<div style="font-size:2.8rem;font-weight:700;text-align:center;color:#ffe066;margin-bottom:6px;">'
        + q.word + '</div></div>', unsafe_allow_html=True)

    audio_b64 = _get_audio_b64(q.word)
    if audio_b64:
        components.html(
            '<style>'
            'html,body{margin:0;padding:0;background:transparent;text-align:center;overflow:hidden;}'
            '.sl{display:inline-flex;align-items:center;justify-content:center;'
            'color:#7788bb;cursor:pointer;font-size:.95rem;'
            "font-family:'Noto Sans JP',Arial,sans-serif;user-select:none;"
            'min-height:44px;padding:6px 20px;border-radius:22px;'
            'touch-action:manipulation;-webkit-tap-highlight-color:transparent;'
            'background:rgba(119,136,187,0.1);border:1px solid rgba(119,136,187,0.25);'
            'transition:background .15s;}'
            '.sl:hover,.sl:active{color:#aabbee;background:rgba(170,187,238,0.18);}'
            '</style>'
            '<script>'
            'try{var f=window.frameElement;'
            'f.style.background="transparent";'
            'f.setAttribute("allowtransparency","true");}catch(e){}'
            '</script>'
            '<audio id="da" src="data:audio/mp3;base64,' + audio_b64 + '"></audio>'
            "<span class='sl' onclick=\"document.getElementById('da').play()\">"
            '🔊 ' + q.word +
            '</span>',
            height=52, scrolling=False
        )

    # ── 選択肢ボタン ──
    if not st.session_state.dungeon_answered:
        cols = st.columns(2)
        labels = ["Ａ", "Ｂ", "Ｃ", "Ｄ"]
        for i, choice in enumerate(q.choices):
            with cols[i % 2]:
                if st.button(labels[i] + '　' + choice, key='dc_' + str(i), use_container_width=True):
                    engine = st.session_state.dungeon_engine
                    result = engine.judge(q, selected_answer=choice)
                    st.session_state.dungeon_last_result = result
                    st.session_state.dungeon_answered = True
                    st.session_state.dungeon_total += 1
                    if result.is_correct:
                        _on_correct(result, q)
                    else:
                        _on_wrong(result)
                    # 途中でページを閉じてもEXPが消えないよう毎回保存する
                    save_player(st.session_state.player, st.session_state.get("username", ""))
                    st.rerun()

    # ── 結果表示 ──
    if st.session_state.dungeon_answered and st.session_state.dungeon_last_result:
        result = st.session_state.dungeon_last_result
        if result.is_correct:
            gain = st.session_state.get("dungeon_last_gain")
            exp_str = str(gain.exp_gained_final) if gain else str(result.exp_gained)
            bonus_html = (' <span style="color:#ffe066;">(×' + str(gain.streak_multiplier) + ')</span>'
                          if gain and gain.streak_multiplier > 1.0 else "")
            st.markdown(
                '<div style="background:linear-gradient(135deg,#0a2a0a,#1a4a1a);border:1px solid #2a7a2a;'
                'border-radius:12px;padding:14px 18px;margin:10px 0;">'
                '<div style="font-size:1rem;font-weight:700;color:#88ff88;margin-bottom:4px;">'
                '✅ 正解！ +' + exp_str + ' EXP' + bonus_html + '</div>'
                '<div style="color:#cceebb;font-size:.88rem;"><b style="color:#fff;">'
                + q.word + '</b> = ' + q.meaning_ja + '</div>'
                '</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="background:linear-gradient(135deg,#2a0a0a,#4a1a1a);border:1px solid #7a2a2a;'
                'border-radius:12px;padding:14px 18px;margin:10px 0;">'
                '<div style="font-size:1rem;font-weight:700;color:#ff8080;margin-bottom:4px;">'
                '❌ 不正解… -' + str(result.hp_damage) + ' HP</div>'
                '<div style="color:#ffcccc;font-size:.88rem;">正解: <b style="color:#ffe066;">'
                + q.correct_answer + '</b></div>'
                '</div>', unsafe_allow_html=True)

        if st.session_state.get("dungeon_cleared"):
            # クリア画面へのボタン（副作用なし）
            st.balloons()
            if st.button("🎉 クリア！結果を見る", use_container_width=True, type="primary"):
                st.session_state.dungeon_show_result = True
                st.rerun()
        else:
            btn_label = ('⚔️ ボスに挑む！次へ' if is_boss else
                         '⚔️ 次の問題へ (' + str(correct) + '/' + str(required) + ')')
            if st.button(btn_label, use_container_width=True, type="primary"):
                _next_step()
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 ダンジョンを諦める", use_container_width=True):
        _exit_dungeon()
        st.rerun()


# ─── クリア画面 ────────────────────────────────────────────────────
def render_clear():
    dungeon_id = st.session_state.get("dungeon_id", "cave")
    dungeon = get_dungeon(dungeon_id)
    if dungeon is None:
        _exit_dungeon()
        st.rerun()
        return

    time_sec = st.session_state.get("dungeon_clear_time", 0)
    accuracy = st.session_state.get("dungeon_clear_accuracy", 100.0)
    rewards = st.session_state.get("dungeon_rewards") or {}
    new_titles = st.session_state.get("dungeon_new_titles") or []
    is_first = rewards.get("first_clear", False)
    items = rewards.get("items") or []
    mins, secs = int(time_sec) // 60, int(time_sec) % 60
    time_str = (f'{mins}分{secs}秒' if mins > 0 else f'{secs}秒')

    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a1000,#3a2800,#1a1000);'
        'border:3px solid #ffcc00;border-radius:16px;padding:24px;text-align:center;margin-bottom:16px;">'
        '<div style="font-size:2.2rem;font-weight:900;color:#ffcc00;'
        'text-shadow:0 0 20px #ffaa00;">🏆 ダンジョンクリア！</div>'
        '<div style="font-size:1.2rem;color:#ffe066;margin-top:6px;">'
        + dungeon["emoji"] + ' ' + dungeon["name"] + '</div>'
        + ('<div style="background:#0a2a00;border:1px solid #44ff44;border-radius:8px;'
           'padding:4px 12px;display:inline-block;margin-top:8px;font-size:.82rem;color:#44ff88;">'
           '🌟 初クリアボーナス！</div>'
           if is_first else '') +
        '</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '<div style="background:#1a1a3a;border-radius:12px;padding:16px;text-align:center;">'
            '<div style="font-size:.8rem;color:#888;">⏱ クリアタイム</div>'
            '<div style="font-size:1.8rem;font-weight:700;color:#88ccff;">' + time_str + '</div>'
            '</div>', unsafe_allow_html=True)
    with col2:
        acc_col = "#88ff88" if accuracy >= 80 else ("#ffe066" if accuracy >= 60 else "#ff8080")
        st.markdown(
            '<div style="background:#1a1a3a;border-radius:12px;padding:16px;text-align:center;">'
            '<div style="font-size:.8rem;color:#888;">📊 正答率</div>'
            '<div style="font-size:1.8rem;font-weight:700;color:' + acc_col + ';">'
            + str(accuracy) + '%</div>'
            '</div>', unsafe_allow_html=True)

    if items:
        st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin:14px 0 6px;">🎁 獲得アイテム</div>', unsafe_allow_html=True)
        for item_id in items:
            item_def = _EQUIP_ITEMS.get(item_id, {})
            item_name = item_def.get("name", item_id)
            item_icon = item_def.get("icon", "📦")
            is_rare = item_def.get("rare", False)
            border_col = "#ffcc00" if is_rare else "#3a3a6a"
            glow = "box-shadow:0 0 12px #ffaa0066;" if is_rare else ""
            st.markdown(
                '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);border:2px solid '
                + border_col + ';border-radius:10px;padding:10px 16px;margin-bottom:6px;'
                'display:flex;align-items:center;gap:10px;' + glow + '">'
                '<div style="font-size:1.6rem;">' + item_icon + '</div>'
                '<div><div style="font-size:.95rem;font-weight:700;color:'
                + ('#ffcc00' if is_rare else '#ffe066') + ';">' + item_name + '</div>'
                '<div style="font-size:.72rem;color:#888;">インベントリに追加されました</div>'
                '</div></div>', unsafe_allow_html=True)

    for tid in new_titles:
        tdef = _TITLES_MAP.get(tid, {})
        st.markdown(
            '<div style="background:linear-gradient(135deg,#1a1200,#3a2800);'
            'border:2px solid #ffcc00;border-radius:12px;padding:10px 16px;margin-bottom:8px;">'
            '<div style="font-size:.9rem;font-weight:900;color:#ffcc00;">🏅 称号解除！</div>'
            '<div style="font-size:1rem;color:#ffe066;">'
            + tdef.get("icon", "") + ' ' + tdef.get("name", "") + '</div>'
            '</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗺️ マップへ戻る", use_container_width=True, type="primary"):
            _exit_dungeon()
            st.rerun()
    with col_b:
        if st.button("🔄 もう一度！", use_container_width=True):
            _did = dungeon_id
            _exit_dungeon()
            init_dungeon(_did)
            st.rerun()


# ─── ランキング画面 ────────────────────────────────────────────────
def render_ranking():
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#ffe066;margin-bottom:8px;">🏆 ランキング（クリアタイム順）</div>', unsafe_allow_html=True)
    tabs = st.tabs([d["emoji"] + " " + d["name"] for d in DUNGEONS])
    MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
    for i, dungeon in enumerate(DUNGEONS):
        with tabs[i]:
            entries = get_dungeon_ranking(dungeon["id"])
            if not entries:
                st.info("まだクリア記録がありません。最初のクリアを目指そう！")
                continue
            for j, entry in enumerate(entries[:20]):
                rank = j + 1
                medal = MEDALS.get(rank, str(rank))
                is_me = entry.get("username") == username
                char_id = entry.get("character", "")
                char_html = (
                    '<div style="width:34px;height:43px;flex-shrink:0;">'
                    + CHARACTERS[char_id]["svg"] + '</div>'
                    if char_id in CHARACTERS else '<div style="font-size:1.4rem;">⚔️</div>'
                )
                _t = int(entry.get("time", 0))
                time_str = f'{_t // 60}分{_t % 60}秒' if _t >= 60 else f'{_t}秒'
                me_badge = (' <span style="background:#ffe066;color:#1a1a2e;font-size:.6rem;'
                            'padding:1px 5px;border-radius:8px;font-weight:700;">YOU</span>'
                            if is_me else "")
                extra = "border-color:#ffe066;background:linear-gradient(135deg,#2a2000,#3a3010);" if is_me else ""
                st.markdown(
                    '<div style="background:linear-gradient(135deg,#1a1a2e,#222244);border:1px solid #3a3a6a;'
                    + extra +
                    'border-radius:10px;padding:8px 12px;margin-bottom:5px;display:flex;align-items:center;gap:10px;">'
                    '<div style="font-size:1.3rem;min-width:32px;text-align:center;">' + medal + '</div>'
                    + char_html +
                    '<div style="flex:1;min-width:0;">'
                    '<div style="font-size:.9rem;font-weight:700;color:#ffe066;">'
                    + entry.get("name", "?") + me_badge + '</div>'
                    '<div style="font-size:.7rem;color:#888;">' + entry.get("date", "") + '</div>'
                    '</div>'
                    '<div style="text-align:right;flex-shrink:0;">'
                    '<div style="font-size:1rem;font-weight:700;color:#88ccff;">' + time_str + '</div>'
                    '<div style="font-size:.68rem;color:#888;">' + str(entry.get("accuracy", 0)) + '% 正答</div>'
                    '</div></div>', unsafe_allow_html=True)


# ─── メインルーティング ────────────────────────────────────────────
is_active = st.session_state.get("dungeon_active", False)
is_cleared = st.session_state.get("dungeon_cleared", False)
show_result = st.session_state.get("dungeon_show_result", False)

if is_active and is_cleared and show_result:
    render_clear()
elif is_active:
    render_battle()
else:
    tab_map, tab_ranking = st.tabs(["🗺️ ダンジョンマップ", "🏆 ランキング"])
    with tab_map:
        render_map()
    with tab_ranking:
        render_ranking()
