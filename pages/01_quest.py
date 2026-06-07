import sys
import streamlit as st
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.quiz_engine import QuizEngine, Question, QuizResult
from core.ai_tutor import get_explanation
from core.player import PlayerManager, streak_multiplier
from core.save_manager import load_player, save_player, append_history

st.set_page_config(page_title="クエスト", page_icon="🗡️", layout="centered", initial_sidebar_state="expanded")

st.markdown("""<style>
html,body,[class*="css"]{font-family:'Noto Sans JP',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460);}
[data-testid="stSidebar"] *{color:#e0e0e0 !important;}
.hp-bar-outer{background:#2a0a0a;border-radius:8px;height:18px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a1a1a;}
.hp-bar-inner{background:linear-gradient(90deg,#e05252,#ff8080);height:100%;border-radius:8px;}
.exp-bar-outer{background:#1a1500;border-radius:8px;height:14px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a4a00;}
.exp-bar-inner{background:linear-gradient(90deg,#c8a000,#ffe066);height:100%;border-radius:8px;}
.stat-label{font-size:11px;color:#aaaacc !important;}
.quiz-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;border-radius:16px;padding:28px 32px;margin-bottom:24px;}
.word-display{font-size:3rem;font-weight:700;text-align:center;color:#ffe066;margin-bottom:6px;}
.pos-badge{display:inline-block;background:#0f3460;color:#88aaff;font-size:.75rem;padding:2px 10px;border-radius:20px;border:1px solid #2244aa;margin-bottom:20px;}
.progress-label{font-size:.82rem;color:#888;margin-bottom:4px;}
</style>""", unsafe_allow_html=True)


def _get_audio_b64(word):
    try:
        from gtts import gTTS
        import io, base64
        tts = gTTS(text=word, lang="en", slow=True)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        return b64
    except Exception:
        return None


def _grade_label(k):
    return {"grade_5":"5級","grade_4":"4級","grade_3":"3級","grade_pre2":"準2級","grade_2":"2級"}.get(k,k)


def init_session():
    if "player" not in st.session_state:
        username = st.session_state.get("username", "")
        st.session_state.player = load_player(username)
    defaults = [("total_correct",0),("total_questions",0),("streak",0),
                ("engine",None),("current_question",None),("answered",False),
                ("last_result",None),("quest_finished",False),("session_correct",0),
                ("session_total",0),("ai_explanation",None),("last_gain_result",None)]
    for k,v in defaults:
        if k not in st.session_state:
            st.session_state[k] = v
    if st.session_state.engine is None:
        grade = st.session_state.player["grade_target"]
        st.session_state.engine = QuizEngine(grade=grade, data_dir="data/words")

init_session()


def render_sidebar():
    p = st.session_state.player
    pm = PlayerManager(p)
    hp_pct = pm.hp_percent() * 100
    exp_pct = pm.exp_percent() * 100
    streak = st.session_state.streak
    total = st.session_state.total_questions
    correct = st.session_state.total_correct
    accuracy = str(round(correct/total*100)) + "%" if total > 0 else "---"
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:16px 0 8px;">'
            '<div style="font-size:3rem;">⚔️</div>'
            '<div style="font-size:1.3rem;font-weight:700;color:#ffe066;margin-top:8px;">' + p["name"] + '</div>'
            '<div style="font-size:.85rem;color:#aaaacc;">Lv. ' + str(p["level"]) + ' | 英検' + _grade_label(p["grade_target"]) + '</div>'
            '</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="stat-label">HP ' + str(p["hp"]) + ' / ' + str(p["hp_max"]) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="hp-bar-outer"><div class="hp-bar-inner" style="width:' + str(round(hp_pct,1)) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">EXP ' + str(p["exp"]) + ' / ' + str(p["exp_to_next"]) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="exp-bar-outer"><div class="exp-bar-inner" style="width:' + str(round(exp_pct,1)) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(
            '<div style="font-size:.82rem;line-height:2.1;color:#ccccee;">'
            '🔥 連続正解 <b style="color:#ffe066;">' + str(streak) + '</b> 問<br>'
            '📊 正答率 <b style="color:#ffe066;">' + accuracy + '</b><br>'
            '📝 累計 <b style="color:#ffe066;">' + str(total) + '</b> 問'
            '</div>', unsafe_allow_html=True)
        st.markdown("---")
        if p["hp"] <= 0:
            st.error("HPが0！正解するとHP回復します")
        if st.button("💾 セーブ", use_container_width=True):
            save_player(st.session_state.player, st.session_state.get("username", ""))
            st.success("セーブしました！")
        with st.expander("開発者メニュー"):
            if st.button("全リセット", use_container_width=True):
                from core.save_manager import delete_save
                delete_save(st.session_state.get("username", ""))
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

render_sidebar()


def apply_correct(result):
    pm = PlayerManager(st.session_state.player)
    streak = pm.increment_streak()
    st.session_state.streak = streak
    gain = pm.gain_exp(base_exp=result.exp_gained, streak=streak)
    st.session_state.last_gain_result = gain
    st.session_state.total_correct += 1
    st.session_state.session_correct += 1


def apply_wrong(result):
    pm = PlayerManager(st.session_state.player)
    pm.take_damage(result.hp_damage)
    pm.reset_streak()
    st.session_state.streak = 0
    st.session_state.last_gain_result = None


def load_next_question():
    engine = st.session_state.engine
    q = engine.get_next_question()
    if q is None:
        st.session_state.quest_finished = True
    else:
        st.session_state.current_question = q
        st.session_state.answered = False
        st.session_state.last_result = None
        st.session_state.ai_explanation = None
        st.session_state.last_gain_result = None


if st.session_state.quest_finished:
    engine = st.session_state.engine
    stats = engine.get_session_stats()
    username = st.session_state.get("username", "")
    save_player(st.session_state.player, username)
    append_history({**stats, "grade_target": st.session_state.player["grade_target"]}, username)
    accuracy = stats["accuracy"]
    if accuracy >= 90: rank, color = "S ランク 🏆", "#ffe066"
    elif accuracy >= 75: rank, color = "A ランク ⭐", "#88ff88"
    elif accuracy >= 60: rank, color = "B ランク 👍", "#88ccff"
    else: rank, color = "C ランク 📖", "#ffaa88"
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a1a2e,#2a1a3e);border:1px solid #5a3a8a;border-radius:16px;padding:28px;text-align:center;">'
        '<div style="font-size:2rem;color:#ffe066;margin-bottom:16px;">🎉 クエスト完了！</div>'
        '<div style="font-size:1.8rem;font-weight:700;color:' + color + ';margin-bottom:20px;">' + rank + '</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">'
        '<div style="background:#1a1a3a;border-radius:10px;padding:14px;"><div style="font-size:.8rem;color:#888;">出題数</div><div style="font-size:1.8rem;color:#fff;font-weight:700;">' + str(stats["total"]) + '</div></div>'
        '<div style="background:#1a1a3a;border-radius:10px;padding:14px;"><div style="font-size:.8rem;color:#888;">正解数</div><div style="font-size:1.8rem;color:#88ff88;font-weight:700;">' + str(stats["correct"]) + '</div></div>'
        '<div style="background:#1a1a3a;border-radius:10px;padding:14px;"><div style="font-size:.8rem;color:#888;">正答率</div><div style="font-size:1.8rem;color:#ffe066;font-weight:700;">' + str(stats["accuracy"]) + '%</div></div>'
        '<div style="background:#1a1a3a;border-radius:10px;padding:14px;"><div style="font-size:.8rem;color:#888;">獲得EXP</div><div style="font-size:1.8rem;color:#ffcc44;font-weight:700;">+' + str(stats["total_exp"]) + '</div></div>'
        '</div></div>', unsafe_allow_html=True)
    if st.button("🔄 もう一度", use_container_width=True):
        grade = st.session_state.player["grade_target"]
        st.session_state.engine = QuizEngine(grade=grade, data_dir="data/words")
        for key in ["quest_finished","current_question","answered","last_result",
                    "session_correct","session_total","ai_explanation","last_gain_result"]:
            st.session_state[key] = False if key in ("quest_finished","answered") else (0 if key in ("session_correct","session_total") else None)
        st.rerun()
    st.stop()


if st.session_state.current_question is None:
    load_next_question()
    st.rerun()

q = st.session_state.current_question
engine = st.session_state.engine
total_words = len(engine.df)
answered_count = total_words - engine.questions_left()

st.markdown('<div class="progress-label">進捗 ' + str(answered_count) + ' / ' + str(total_words) + ' 問</div>', unsafe_allow_html=True)
st.progress(answered_count / total_words)

pos_map = {"n":"名詞","v":"動詞","adj":"形容詞","adv":"副詞","prep":"前置詞"}
pos_ja = pos_map.get(q.part_of_speech, q.part_of_speech)
diff_stars = "⭐" * q.difficulty
streak = st.session_state.streak
mult = streak_multiplier(streak)
bonus = '<span style="background:#2a1a00;color:#ffe066;border:1px solid #5a3a00;border-radius:6px;padding:2px 8px;font-size:.75rem;margin-left:8px;">🔥 EXP x' + str(mult) + '</span>' if mult > 1.0 else ""

audio_b64 = _get_audio_b64(q.word)
if audio_b64:
    audio_html = (
        '<audio id="quiz-audio" src="data:audio/mp3;base64,' + audio_b64 + '"></audio>'
        '<span onclick="document.getElementById(&quot;quiz-audio&quot;).play()" '
        'style="cursor:pointer;font-size:1.5rem;margin-left:10px;" title="発音を聞く">🔊</span>'
    )
else:
    audio_html = ""


st.markdown(
    '<div class="quiz-card">'
    '<div style="font-size:.9rem;color:#aaaacc;text-align:center;margin-bottom:20px;">次の英単語の意味を選んでください ' + diff_stars + bonus + '</div>'
    '<div class="word-display">' + q.word + '</div>'
    '<div style="text-align:center;"><span class="pos-badge">' + pos_ja + '</span></div>'
    '</div>', unsafe_allow_html=True)
if st.button('🔊 発音を聞く', key='speak_'+q.word):
    if audio_b64:
        import base64
        st.audio(base64.b64decode(audio_b64), format='audio/mp3')

if not st.session_state.answered:
    cols = st.columns(2)
    labels = ["Ａ","Ｂ","Ｃ","Ｄ"]
    for i, choice in enumerate(q.choices):
        with cols[i % 2]:
            if st.button(labels[i] + "　" + choice, key="choice_" + str(i), use_container_width=True):
                result = engine.judge(q, selected_answer=choice)
                st.session_state.last_result = result
                st.session_state.answered = True
                st.session_state.total_questions += 1
                st.session_state.session_total += 1
                if result.is_correct:
                    apply_correct(result)
                else:
                    apply_wrong(result)
                st.rerun()

if st.session_state.answered and st.session_state.last_result:
    result = st.session_state.last_result
    gain = st.session_state.last_gain_result

    if result.is_correct:
        levelup_html = ""
        if gain and gain.leveled_up:
            for ev in gain.level_up_events:
                levelup_html += (
                    '<div style="background:#1a2a0a;border:1px solid #5aaa2a;border-radius:10px;'
                    'padding:10px;margin-bottom:12px;text-align:center;">'
                    '✨ <b style="color:#aaff44;">Lv.' + str(ev.new_level) + ' になりました！</b><br>'
                    '<span style="font-size:.85rem;color:#88cc88;">HP上限 ' + str(ev.hp_max_old) + ' → ' + str(ev.hp_max_new) + ' 💚 全回復！</span>'
                    '</div>'
                )
        bonus_html = ""
        if gain and gain.streak_multiplier > 1.0:
            bonus_html = ' <span style="color:#ffe066;">(x' + str(gain.streak_multiplier) + ' ボーナス！)</span>'
        exp_show = str(gain.exp_gained_final) if gain else str(result.exp_gained)
        hint_html = '<div style="font-size:.82rem;color:#aaaa88;margin-top:6px;">💡 ' + q.hint + '</div>' if q.hint else ""
        st.markdown(
            '<div style="background:linear-gradient(135deg,#0a2a0a,#1a4a1a);border:1px solid #2a7a2a;border-radius:12px;padding:20px 24px;margin:16px 0;">'
            + levelup_html +
            '<div style="font-size:1.1rem;font-weight:700;color:#88ff88;margin-bottom:10px;">✅ 正解！ +' + exp_show + ' EXP' + bonus_html + '</div>'
            '<div style="color:#cceebb;font-size:.92rem;margin-bottom:8px;"><b style="color:#fff;">' + q.word + '</b> = ' + q.meaning_ja + '</div>'
            '<div style="font-size:.88rem;color:#aaccaa;font-style:italic;margin-top:8px;">📖 ' + q.example_en + '<br>' + q.example_ja + '</div>'
            + hint_html +
            '</div>', unsafe_allow_html=True)
        
    else:
        hint_html = '<div style="font-size:.82rem;color:#aaaa88;margin-top:6px;">💡 ' + q.hint + '</div>' if q.hint else ""
        st.markdown(
            '<div style="background:linear-gradient(135deg,#2a0a0a,#4a1a1a);border:1px solid #7a2a2a;border-radius:12px;padding:20px 24px;margin:16px 0;">'
            '<div style="font-size:1.1rem;font-weight:700;color:#ff8080;margin-bottom:10px;">❌ 不正解 HP -' + str(result.hp_damage) + '</div>'
            '<div style="color:#ffcccc;font-size:.92rem;margin-bottom:8px;">正解は <b style="color:#ffe066;font-size:1.1rem;">' + q.correct_answer + '</b> でした</div>'
            '<div style="color:#ddbbbb;font-size:.88rem;margin-bottom:8px;">あなたの答え：<span style="color:#ff8080;">' + result.selected_answer + '</span></div>'
            '<div style="font-size:.88rem;color:#ccaaaa;font-style:italic;margin-top:8px;">📖 ' + q.example_en + '<br>' + q.example_ja + '</div>'
            + hint_html +
            '</div>', unsafe_allow_html=True)
        

        if st.session_state.ai_explanation is None:
            if st.button("🤖 ハナ先生に解説してもらう", use_container_width=True):
                with st.spinner("解説を考えています…"):
                    explanation = get_explanation(
                        word=q.word, meaning_ja=q.correct_answer,
                        wrong_answer=result.selected_answer,
                        example_en=q.example_en, example_ja=q.example_ja,
                        grade=st.session_state.player["grade_target"],
                        word_id=q.word_id, hint=q.hint)
                    st.session_state.ai_explanation = explanation
                    st.rerun()

        if st.session_state.ai_explanation:
            st.markdown(
                '<div style="background:linear-gradient(135deg,#1a1030,#2a1a40);border:1px solid #6a3aaa;border-radius:12px;padding:18px 22px;margin-top:8px;">'
                '<div style="font-size:.8rem;color:#aa88dd;margin-bottom:10px;">🤖 ハナ先生の解説</div>'
                '<div style="font-size:.92rem;color:#e8d8ff;line-height:1.9;">' + st.session_state.ai_explanation.replace("\n","<br>") + '</div>'
                '</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    remaining = engine.questions_left()
    btn_label = "次の問題へ ➡️ （残り " + str(remaining) + " 問）" if remaining > 0 else "🏁 結果を見る"
    if st.button(btn_label, use_container_width=True, type="primary"):
        load_next_question()
        st.rerun()
