from __future__ import annotations
from typing import Dict
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_GRADE_PERSONA = {
    "grade_5": {"label":"5級","age":"小学生","style":"ひらがなをたくさん使って、やさしいことばで","length":"3〜4文"},
    "grade_4": {"label":"4級","age":"中学1年生","style":"やさしいことばで、漢字には読み仮名をつけながら","length":"3〜4文"},
    "grade_3": {"label":"3級","age":"中学生","style":"中学生に分かりやすいことばで","length":"4〜5文"},
    "grade_pre2": {"label":"準2級","age":"高校生","style":"語源や関連語にも触れながら","length":"4〜5文"},
    "grade_2": {"label":"2級","age":"大学生","style":"語源・類義語・反義語も交えて","length":"5〜6文"},
}

_explanation_cache: Dict[str, str] = {}


def get_explanation(word, meaning_ja, wrong_answer, example_en, example_ja, grade, word_id="", hint=""):
    cache_key = (word_id or word) + "::" + grade
    if cache_key in _explanation_cache:
        return _explanation_cache[cache_key]

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _fallback(word, meaning_ja, wrong_answer)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        persona = _GRADE_PERSONA.get(grade, _GRADE_PERSONA["grade_4"])
        hint_section = "ヒント: " + hint if hint else ""
        prompt = (
            "あなたはやさしい家庭教師のハナ先生です。\n"
            "英検" + persona["label"] + "を勉強している" + persona["age"] + "の生徒が間違えました。\n"
            + persona["style"] + "、" + persona["length"] + "で解説してください。\n\n"
            "単語: " + word + "\n"
            "正しい意味: " + meaning_ja + "\n"
            "生徒の誤答: " + wrong_answer + "\n"
            "例文: " + example_en + "\n"
            "例文訳: " + example_ja + "\n"
            + hint_section + "\n\n"
            "1. 間違えた気持ちに共感\n"
            "2. 正しい意味を説明\n"
            "3. 例文でイメージ\n"
            "4. 覚え方で締める\n"
            "マークダウン不要"
        )
        response = model.generate_content(prompt)
        explanation = response.text.strip()
        _explanation_cache[cache_key] = explanation
        return explanation
    except Exception as e:
        return _fallback(word, meaning_ja, wrong_answer, error=str(e))


def _fallback(word, meaning_ja, wrong_answer, error=""):
    lines = [
        "「" + wrong_answer + "」と迷ってしまったんだね。",
        "「" + word + "」の正しい意味は「" + meaning_ja + "」だよ。",
        "例文を何度か声に出して読んでみると、きっと覚えられるよ！",
    ]
    if error:
        lines.append("（AI解説は現在利用できません。しばらくしてからお試しください。）")
    return "\n".join(lines)


def clear_cache():
    _explanation_cache.clear()


def cache_size():
    return len(_explanation_cache)
