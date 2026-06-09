import sys
import streamlit as st
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit.components.v1 as components
from core.quiz_engine import QuizEngine, Question, QuizResult
from core.ai_tutor import get_explanation
from core.player import PlayerManager, streak_multiplier
from core.save_manager import load_player, save_player, append_history, update_ranking
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html
from core.daily_quest import get_or_reset_daily_quests, update_quest_progress

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
.quiz-card{background:linear-gradient(135deg,#1e1e3a,#2a2a4a);border:1px solid #3a3a6a;border-radius:16px;padding:28px 32px;margin-bottom:4px;}
.word-display{font-size:3rem;font-weight:700;text-align:center;color:#ffe066;margin-bottom:6px;}
.pos-badge{display:inline-block;background:#0f3460;color:#88aaff;font-size:.75rem;padding:2px 10px;border-radius:20px;border:1px solid #2244aa;margin-bottom:20px;}
.progress-label{font-size:.82rem;color:#888;margin-bottom:4px;}
</style>""", unsafe_allow_html=True)


# ── 効果音：Python で WAV を生成して base64 化（外部ライブラリ不要）─────────
import struct as _struct
import math as _math
import base64 as _base64


def _make_wav_b64(notes_durs, sr: int = 8000, vol: float = 0.22) -> str:
    """sine 波の WAV を Python stdlib だけで生成して base64 文字列を返す。"""
    samples = []
    for freq, dur in notes_durs:
        n = int(sr * dur)
        fade = max(1, n // 5)
        for i in range(n):
            s = vol * _math.sin(2 * _math.pi * freq * i / sr)
            if i >= n - fade:          # フェードアウト
                s *= (n - i) / fade
            samples.append(max(-32767, min(32767, int(s * 32767))))
    raw = _struct.pack('<' + 'h' * len(samples), *samples)
    hdr = (b'RIFF' + _struct.pack('<I', 36 + len(raw)) + b'WAVE'
           + b'fmt ' + _struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16)
           + b'data' + _struct.pack('<I', len(raw)))
    return _base64.b64encode(hdr + raw).decode()


# モジュール読み込み時に一度だけ計算してキャッシュ
_CORRECT_WAV = _make_wav_b64(
    [(523.25, 0.10), (659.25, 0.10), (783.99, 0.10), (1046.50, 0.28)])
_WRONG_WAV = _make_wav_b64(
    [(392.00, 0.22), (311.13, 0.32)], vol=0.18)


def _play_sound(sound_type: str):
    """WAV データを data URI として iframe 内で再生する。"""
    b64 = _CORRECT_WAV if sound_type == "correct" else _WRONG_WAV
    # Web Audio API（AudioContext）は iframe + Streamlit rerun 後に
    # suspended になる問題があるため、new Audio() を使う。
    # height=1 で iframe を確実にレンダリングさせる。
    components.html(
        '<script>'
        '(function(){'
        'var a=new Audio("data:audio/wav;base64,' + b64 + '");'
        'a.volume=0.65;'
        'var p=a.play();'
        'if(p!==undefined){p.catch(function(){});}'
        '})();'
        '</script>',
        height=1, scrolling=False)


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


def init_session():
    if "player" not in st.session_state or st.session_state.player is None:
        username = st.session_state.get("username", "")
        st.session_state.player = load_player(username)
    defaults = [("total_correct", 0), ("total_questions", 0), ("streak", 0),
                ("engine", None), ("current_question", None), ("answered", False),
                ("last_result", None), ("quest_finished", False), ("session_correct", 0),
                ("session_total", 0), ("ai_explanation", None), ("last_gain_result", None),
                ("play_sound", None)]
    for k, v in defaults:
        if k not in st.session_state:
            st.session_state[k] = v
    player_lang = st.session_state.player.get("language", "ja")
    engine = st.session_state.engine
    if engine is None or engine.language != player_lang or engine.grade != st.session_state.player["grade_target"]:
        grade = st.session_state.player["grade_target"]
        st.session_state.engine = QuizEngine(grade=grade, data_dir="data/words", language=player_lang)
        st.session_state.current_question = None
        st.session_state.answered = False
        st.session_state.last_result = None
        st.session_state.quest_finished = False
        st.session_state.session_correct = 0
        st.session_state.session_total = 0
        st.session_state.ai_explanation = None
        st.session_state.last_gain_result = None

init_session()


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
        st.markdown(
            '<div style="font-size:.82rem;line-height:2.1;color:#ccccee;">'
            '🔥 ' + t("streak", lang) + ' <b style="color:#ffe066;">' + str(streak) + '</b> ' + t("questions", lang) + '<br>'
            '📊 ' + t("accuracy", lang) + ' <b style="color:#ffe066;">' + accuracy + '</b><br>'
            '📝 ' + t("total_q", lang) + ' <b style="color:#ffe066;">' + str(total) + '</b> ' + t("questions", lang) +
            '</div>', unsafe_allow_html=True)
        st.markdown("---")

render_sidebar()


def apply_correct(result, question=None):
    p = st.session_state.player
    pm = PlayerManager(p)
    was_zero = (pm.hp == 0)
    streak = pm.increment_streak()
    st.session_state.streak = streak
    gain = pm.gain_exp(base_exp=result.exp_gained, streak=streak)
    st.session_state.last_gain_result = gain
    st.session_state.total_correct += 1
    st.session_state.session_correct += 1
    if was_zero and not gain.leveled_up:
        pm.heal(10)

    # 週間統計
    p["weekly_correct"] = p.get("weekly_correct", 0) + 1
    p["weekly_total"] = p.get("weekly_total", 0) + 1
    if streak > p.get("max_streak", 0):
        p["max_streak"] = streak

    # デイリークエスト進捗（苦手単語数を渡してターゲットを自動調整）
    engine = st.session_state.get("engine")
    _wc: int | None = None
    is_weak_word = False
    if engine is not None:
        try:
            wdf = engine.get_weak_words(top_n=50)
            _wc = 0 if wdf.empty else len(wdf)
        except Exception:
            pass
        if question is not None:
            word_row = engine.df[engine.df["word"] == question.word]
            if not word_row.empty and int(word_row.iloc[0].get("miss_count", 0)) > 0:
                is_weak_word = True
    get_or_reset_daily_quests(p, weak_count=_wc)
    update_quest_progress(p, "correct10")
    if streak >= 5:
        update_quest_progress(p, "streak5")
    if question is not None:
        if question.difficulty >= 3:
            update_quest_progress(p, "hard5")
        if is_weak_word:
            update_quest_progress(p, "weak3")


def apply_wrong(result):
    p = st.session_state.player
    pm = PlayerManager(p)
    pm.take_damage(result.hp_damage)
    pm.reset_streak()
    st.session_state.streak = 0
    st.session_state.last_gain_result = None
    p["weekly_total"] = p.get("weekly_total", 0) + 1


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


lang = st.session_state.player.get("language", "ja")

if st.session_state.quest_finished:
    engine = st.session_state.engine
    stats = engine.get_session_stats()
    username = st.session_state.get("username", "")
    save_player(st.session_state.player, username)
    append_history({**stats, "grade_target": st.session_state.player["grade_target"]}, username)
    weak_df = engine.get_weak_words(top_n=50)
    if not weak_df.empty:
        from core.save_manager import save_weak_words
        weak_list = []
        for _, row in weak_df.iterrows():
            weak_list.append({
                "word": row["word"],
                "meaning_ja": row["meaning_ja"],
                "meaning_zh": "" if str(row.get("meaning_zh", "")) == "nan" else str(row.get("meaning_zh", "")),
                "miss_count": int(row["miss_count"]),
                "hint": "" if str(row.get("hint", "")) == "nan" else str(row.get("hint", "")),
                "example_en": "" if str(row.get("example_en", "")) == "nan" else str(row.get("example_en", "")),
                "example_ja": "" if str(row.get("example_ja", "")) == "nan" else str(row.get("example_ja", "")),
            })
        save_weak_words(weak_list, username)

    update_ranking(st.session_state.player, username)

    accuracy = stats["accuracy"]
    if accuracy >= 90:
        rank, color = t("rank_s", lang), "#ffe066"
    elif accuracy >= 75:
        rank, color = t("rank_a", lang), "#88ff88"
    elif accuracy >= 60:
        rank, color = t("rank_b", lang), "#88ccff"
    else:
        rank, color = t("rank_c", lang), "#ffaa88"

    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a1a2e,#2a1a3e);border:1px solid #5a3a8a;border-radius:16px;padding:28px;text-align:center;">'
        '<div style="font-size:2rem;color:#ffe066;margin-bottom:16px;">' + t("quest_done", lang) + '</div>'
        '<div style="font-size:1.8rem;font-weight:700;color:' + color + ';margin-bottom:20px;">' + rank + '</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">'
        '<div style="background:#1a1a3a;border-radius:10px;padding:14px;"><div style="font-size:.8rem;color:#888;">' + t("stat_total", lang) + '</div><div style="font-size:1.8rem;color:#fff;font-weight:700;">' + str(stats["total"]) + '</div></div>'
        '<div style="background:#1a1a3a;border-radius:10px;padding:14px;"><div style="font-size:.8rem;color:#888;">' + t("stat_correct", lang) + '</div><div style="font-size:1.8rem;color:#88ff88;font-weight:700;">' + str(stats["correct"]) + '</div></div>'
        '<div style="background:#1a1a3a;border-radius:10px;padding:14px;"><div style="font-size:.8rem;color:#888;">' + t("stat_accuracy", lang) + '</div><div style="font-size:1.8rem;color:#ffe066;font-weight:700;">' + str(stats["accuracy"]) + '%</div></div>'
        '<div style="background:#1a1a3a;border-radius:10px;padding:14px;"><div style="font-size:.8rem;color:#888;">' + t("stat_exp", lang) + '</div><div style="font-size:1.8rem;color:#ffcc44;font-weight:700;">+' + str(stats["total_exp"]) + '</div></div>'
        '</div></div>', unsafe_allow_html=True)
    if st.button(t("retry_btn", lang), use_container_width=True):
        grade = st.session_state.player["grade_target"]
        lang_now = st.session_state.player.get("language", "ja")
        st.session_state.engine = QuizEngine(grade=grade, data_dir="data/words", language=lang_now)
        for key in ["quest_finished", "current_question", "answered", "last_result",
                    "session_correct", "session_total", "ai_explanation", "last_gain_result"]:
            st.session_state[key] = False if key in ("quest_finished", "answered") else (0 if key in ("session_correct", "session_total") else None)
        st.rerun()
    st.stop()


if st.session_state.current_question is None:
    load_next_question()
    st.rerun()

q = st.session_state.current_question
engine = st.session_state.engine
total_words = len(engine.df)
answered_count = total_words - engine.questions_left()

st.markdown('<div class="progress-label">' + t("progress_label", lang) + ' ' + str(answered_count) + ' / ' + str(total_words) + ' ' + t("questions", lang) + '</div>', unsafe_allow_html=True)
st.progress(answered_count / total_words)

pos_map = {"n": "名詞" if lang == "ja" else "名詞",
           "v": "動詞" if lang == "ja" else "動詞",
           "adj": "形容詞" if lang == "ja" else "形容詞",
           "adv": "副詞" if lang == "ja" else "副詞",
           "prep": "前置詞" if lang == "ja" else "介詞"}
pos_ja = pos_map.get(q.part_of_speech, q.part_of_speech)
diff_stars = "⭐" * q.difficulty
streak = st.session_state.streak
mult = streak_multiplier(streak)
bonus = ('<span style="background:#2a1a00;color:#ffe066;border:1px solid #5a3a00;border-radius:6px;'
         'padding:2px 8px;font-size:.75rem;margin-left:8px;">🔥 EXP x' + str(mult) + '</span>'
         if mult > 1.0 else "")

# クイズカード（単語・品詞バッジ）
st.markdown(
    '<div class="quiz-card">'
    '<div style="font-size:.9rem;color:#aaaacc;text-align:center;margin-bottom:20px;">' + t("quest_instruction", lang) + ' ' + diff_stars + bonus + '</div>'
    '<div class="word-display">' + q.word + '</div>'
    '<div style="text-align:center;"><span class="pos-badge">' + pos_ja + '</span></div>'
    '</div>', unsafe_allow_html=True)

# 発音ボタン：st.markdown は React レンダラー経由で onclick を除去するため
# components.html（実 iframe）内に audio 要素とクリック要素を同居させる
audio_b64 = _get_audio_b64(q.word)
if audio_b64:
    components.html(
        '<style>'
        'html,body{margin:0;padding:2px 0 6px;background:transparent;'
        'text-align:center;overflow:hidden;}'
        '.sl{color:#7788bb;cursor:pointer;font-size:.9rem;'
        "font-family:'Noto Sans JP',Arial,sans-serif;user-select:none;}"
        '.sl:hover{color:#aabbee;}'
        '</style>'
        '<script>'
        'try{var f=window.frameElement;'
        'f.style.background="transparent";'
        'f.setAttribute("allowtransparency","true");}catch(e){}'
        '</script>'
        '<audio id="sa" src="data:audio/mp3;base64,' + audio_b64 + '"></audio>'
        "<span class='sl' onclick=\"document.getElementById('sa').play()\">"
        '🔊 ' + q.word +
        '</span>',
        height=34, scrolling=False
    )

if not st.session_state.answered:
    cols = st.columns(2)
    labels = ["Ａ", "Ｂ", "Ｃ", "Ｄ"]
    for i, choice in enumerate(q.choices):
        with cols[i % 2]:
            if st.button(labels[i] + "　" + choice, key="choice_" + str(i), use_container_width=True):
                result = engine.judge(q, selected_answer=choice)
                st.session_state.last_result = result
                st.session_state.answered = True
                st.session_state.total_questions += 1
                st.session_state.session_total += 1
                if result.is_correct:
                    apply_correct(result, question=q)
                    st.session_state.play_sound = "correct"
                else:
                    apply_wrong(result)
                    st.session_state.play_sound = "wrong"
                st.rerun()

if st.session_state.answered and st.session_state.last_result:
    result = st.session_state.last_result
    gain = st.session_state.last_gain_result

    # 回答直後のみ効果音を再生（フラグをクリアして重複再生を防ぐ）
    if st.session_state.get("play_sound"):
        _play_sound(st.session_state.play_sound)
        st.session_state.play_sound = None

    if result.is_correct:
        levelup_html = ""
        if gain and gain.leveled_up:
            for ev in gain.level_up_events:
                levelup_html += (
                    '<div style="background:#1a2a0a;border:1px solid #5aaa2a;border-radius:10px;'
                    'padding:10px;margin-bottom:12px;text-align:center;">'
                    + t("levelup_msg", lang).format(new=ev.new_level) + '<br>'
                    '<span style="font-size:.85rem;color:#88cc88;">'
                    + t("levelup_hp", lang).format(old=ev.hp_max_old, new=ev.hp_max_new) +
                    '</span>'
                    '</div>'
                )
        bonus_html = ""
        if gain and gain.streak_multiplier > 1.0:
            bonus_html = ' <span style="color:#ffe066;">(x' + str(gain.streak_multiplier) + ' ' + t("bonus_label", lang) + ')</span>'
        exp_show = str(gain.exp_gained_final) if gain else str(result.exp_gained)
        hint_html = '<div style="font-size:.82rem;color:#aaaa88;margin-top:6px;">💡 ' + q.hint + '</div>' if q.hint else ""
        ex2 = ('<br>' + q.example_ja) if q.example_ja else ''
        st.markdown(
            '<div style="background:linear-gradient(135deg,#0a2a0a,#1a4a1a);border:1px solid #2a7a2a;border-radius:12px;padding:20px 24px;margin:16px 0;">'
            + levelup_html +
            '<div style="font-size:1.1rem;font-weight:700;color:#88ff88;margin-bottom:10px;">'
            + t("correct_msg", lang).format(exp=exp_show, bonus=bonus_html) + '</div>'
            '<div style="color:#cceebb;font-size:.92rem;margin-bottom:8px;"><b style="color:#fff;">' + q.word + '</b> = ' + q.meaning_ja + '</div>'
            '<div style="font-size:.88rem;color:#aaccaa;font-style:italic;margin-top:8px;">📖 ' + q.example_en + ex2 + '</div>'
            + hint_html +
            '</div>', unsafe_allow_html=True)

    else:
        hint_html = '<div style="font-size:.82rem;color:#aaaa88;margin-top:6px;">💡 ' + q.hint + '</div>' if q.hint else ""
        ex2 = ('<br>' + q.example_ja) if q.example_ja else ''
        st.markdown(
            '<div style="background:linear-gradient(135deg,#2a0a0a,#4a1a1a);border:1px solid #7a2a2a;border-radius:12px;padding:20px 24px;margin:16px 0;">'
            '<div style="font-size:1.1rem;font-weight:700;color:#ff8080;margin-bottom:10px;">'
            + t("wrong_msg", lang).format(hp=result.hp_damage) + '</div>'
            '<div style="color:#ffcccc;font-size:.92rem;margin-bottom:8px;">' + t("wrong_answer_was", lang) + ' <b style="color:#ffe066;font-size:1.1rem;">' + q.correct_answer + '</b></div>'
            '<div style="color:#ddbbbb;font-size:.88rem;margin-bottom:8px;">' + t("your_answer", lang) + '<span style="color:#ff8080;">' + result.selected_answer + '</span></div>'
            '<div style="font-size:.88rem;color:#ccaaaa;font-style:italic;margin-top:8px;">📖 ' + q.example_en + ex2 + '</div>'
            + hint_html +
            '</div>', unsafe_allow_html=True)

        if st.session_state.ai_explanation is None:
            if st.button(t("ai_explain_btn", lang), use_container_width=True):
                with st.spinner("解説を考えています…" if lang == "ja" else "正在思考解說…"):
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
                '<div style="font-size:.8rem;color:#aa88dd;margin-bottom:10px;">' + t("ai_teacher_label", lang) + '</div>'
                '<div style="font-size:.92rem;color:#e8d8ff;line-height:1.9;">' + st.session_state.ai_explanation.replace("\n", "<br>") + '</div>'
                '</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    remaining = engine.questions_left()
    btn_label = t("next_btn", lang).format(n=remaining) if remaining > 0 else t("result_btn", lang)
    if st.button(btn_label, use_container_width=True, type="primary"):
        load_next_question()
        st.rerun()
