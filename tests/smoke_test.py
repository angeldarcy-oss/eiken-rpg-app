# -*- coding: utf-8 -*-
"""
CI用スモークテスト

Supabaseの接続情報なしで実行できる（DB呼び出しはすべてグレースフルに失敗する設計）。
  1. 全Pythonファイルのコンパイルチェック
  2. 単語CSVの整合性チェック（列・重複・難易度）
  3. 純粋ロジックの単体テスト（SRS / player / daily_quest / quiz_engine）
  4. AppTestによる全ページのスモークテスト
"""
import csv
import collections
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

FAILED = []


def check(name, fn):
    try:
        fn()
        print("OK  " + name)
    except Exception as e:
        FAILED.append(name + ": " + repr(e)[:200])
        print("NG  " + name + " — " + repr(e)[:200])


# ── 1. コンパイル ───────────────────────────────────────────
def compile_all():
    targets = list((ROOT / "core").glob("*.py")) + list((ROOT / "pages").glob("*.py"))
    targets += [ROOT / "app.py", ROOT / "home.py"]
    for f in targets:
        py_compile.compile(str(f), doraise=True)

check("全ファイルコンパイル", compile_all)


# ── 2. 単語CSV ──────────────────────────────────────────────
def validate_csvs():
    expected_cols = ["word_id", "word", "meaning_ja", "meaning_zh", "part_of_speech",
                     "example_en", "example_ja", "example_zh", "hint", "hint_zh", "difficulty"]
    for path in sorted((ROOT / "data" / "words").glob("*.csv")):
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert rows, path.name + " が空"
        assert list(rows[0].keys()) == expected_cols, path.name + " の列が想定と違う"
        for r in rows:
            assert None not in r.values() and None not in r, path.name + " に列数不正の行: " + r["word_id"]
            assert r["word"] and r["meaning_ja"] and r["example_en"], path.name + " に必須欄が空の行: " + r["word_id"]
            assert r["difficulty"].isdigit(), path.name + " のdifficultyが数値でない: " + r["word_id"]
        for key in ("word", "word_id"):
            dups = [w for w, c in collections.Counter(r[key].lower() for r in rows).items() if c > 1]
            assert not dups, path.name + " に重複 " + key + ": " + str(dups[:5])

check("単語CSV整合性", validate_csvs)


# ── 3. 純粋ロジック ─────────────────────────────────────────
def test_player_logic():
    from core.player import new_player, PlayerManager, exp_to_next_level
    p = new_player("t")
    pm = PlayerManager(p)
    r = pm.gain_exp(exp_to_next_level(1), streak=0)
    assert r.leveled_up and p["level"] == 2 and p["hp"] == p["hp_max"]
    d = pm.take_damage(9999)
    assert d["is_ko"] and p["hp"] == 0

check("playerロジック", test_player_logic)


def test_srs_logic():
    from datetime import date, timedelta
    from core.player import new_player
    from core.srs import record_result, due_words, mastered_count
    p = new_player("t")
    record_result(p, "apple", False)
    assert p["srs"]["apple"]["box"] == 1 and "apple" in due_words(p)
    for _ in range(5):
        record_result(p, "apple", True)
    assert p["srs"]["apple"]["box"] == 5 and mastered_count(p) == 1
    assert p["srs"]["apple"]["due"] == (date.today() + timedelta(days=14)).isoformat()
    record_result(p, "apple", False)
    assert p["srs"]["apple"]["box"] == 1

check("SRSロジック", test_srs_logic)


def test_daily_quest_logic():
    from core.player import new_player
    from core.daily_quest import (get_login_streak, claim_daily_login_exp,
                                  daily_login_exp_amount, get_or_reset_daily_quests)
    p = new_player("t")
    ls = get_login_streak(p)
    assert ls["streak_days"] == 1
    assert claim_daily_login_exp(p) == daily_login_exp_amount(1)
    assert claim_daily_login_exp(p) == 0  # 同日2回目は付与しない
    quests = get_or_reset_daily_quests(p)
    assert len(quests) >= 4 and all(not q["completed"] for q in quests)

check("デイリークエストロジック", test_daily_quest_logic)


def test_quiz_engine():
    from core.quiz_engine import QuizEngine
    for grade in ("grade_5", "grade_4", "grade_3", "grade_pre2", "grade_2"):
        e = QuizEngine(grade=grade, data_dir=str(ROOT / "data" / "words"), language="ja")
        for _ in range(20):
            q = e.get_next_question()
            assert q is not None and len(q.choices) == 4 and q.correct_answer in q.choices
    # SRS優先出題
    e = QuizEngine(grade="grade_4", data_dir=str(ROOT / "data" / "words"), language="ja")
    q = e.get_next_question(preferred_words=["begin"], preferred_prob=1.0)
    assert q.word == "begin"

check("QuizEngine出題", test_quiz_engine)


def test_password_hashing():
    from core.save_manager import _hash_password_bcrypt, _check_password, _hash_password
    h = _hash_password_bcrypt("pw123")
    assert h.startswith("$2") and _check_password("pw123", h) and not _check_password("x", h)
    legacy = _hash_password("pw123")
    assert _check_password("pw123", legacy) and not _check_password("x", legacy)

check("パスワードハッシュ", test_password_hashing)


# ── 4. 全ページAppTestスモーク ──────────────────────────────
def smoke_all_pages():
    from streamlit.testing.v1 import AppTest
    from core.player import new_player

    pages = ["pages/01_quest.py", "pages/02_dungeon.py", "pages/03_daily.py",
             "pages/04_wordbook.py", "pages/05_ranking.py", "pages/11_progress.py",
             "pages/06_party.py", "pages/07_guild.py", "pages/08_shop.py",
             "pages/09_event.py", "pages/10_settings.py"]

    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120)
    p = new_player("ci_tester")
    p["character"] = "knight"
    at.session_state["logged_in"] = True
    at.session_state["username"] = "ci_tester"
    at.session_state["player"] = p
    at.session_state["streak"] = 0
    at.session_state["total_questions"] = 0
    at.session_state["total_correct"] = 0
    at.run()
    assert not at.exception, "home: " + str(at.exception[0].value)
    for page in pages:
        at.switch_page(page)
        at.run()
        assert not at.exception, page + ": " + str(at.exception[0].value)
        print("    page OK: " + page)

check("全ページスモークテスト", smoke_all_pages)


print()
if FAILED:
    print("❌ 失敗 " + str(len(FAILED)) + "件:")
    for f in FAILED:
        print("  - " + f)
    sys.exit(1)
print("✅ 全チェック合格")
