"""
core/quiz_engine.py
英検RPGアプリ - クイズエンジン

役割:
  - CSVから単語を読み込む
  - 4択問題を生成する
  - 正誤判定を行う
  - 苦手単語を管理する
"""

from __future__ import annotations
from typing import Optional, List, Dict
import pandas as pd
import random
from pathlib import Path
from dataclasses import dataclass, field


# ─────────────────────────────────────────
# データクラス定義
# ─────────────────────────────────────────

@dataclass
class Question:
    """1問分のクイズデータを表すクラス"""
    word_id: str          # 例: "g4_001"
    grade: str            # 例: "grade_4"
    word: str             # 例: "important"
    part_of_speech: str   # 例: "adj"
    meaning_ja: str       # 例: "重要な"
    example_en: str       # 例: "This is an important decision."
    example_ja: str       # 例: "これは重要な決断です。"
    hint: str             # 例: "importと同じ語源"
    tags: List[str]       # 例: ["business", "adjective"]
    difficulty: int       # 例: 2
    choices: List[str]    # 例: ["重要な", "簡単な", "小さな", "古い"]（シャッフル済み）
    correct_answer: str   # 例: "重要な"


@dataclass
class QuizResult:
    """1問の結果データ"""
    question: Question
    selected_answer: str
    is_correct: bool
    # 正解時のEXP（difficultyで変動）
    exp_gained: int = 0
    # 不正解時のHPダメージ
    hp_damage: int = 0


# ─────────────────────────────────────────
# QuizEngine クラス本体
# ─────────────────────────────────────────

class QuizEngine:
    """
    クイズの出題・判定・履歴管理を担当するクラス。

    使い方:
        engine = QuizEngine(grade="grade_4")
        question = engine.get_next_question()
        result = engine.judge(question, selected_answer="重要な")
    """

    # 難易度ごとの獲得EXP
    EXP_TABLE = {1: 10, 2: 15, 3: 20, 4: 30, 5: 50}

    # 不正解時のHPダメージ（固定）
    HP_DAMAGE = 10

    def __init__(self, grade: str, data_dir: str = "data/words", language: str = "ja"):
        """
        Args:
            grade: 出題する英検の級。例: "grade_5", "grade_4", "grade_3"
            data_dir: 単語CSVが置いてあるディレクトリのパス
            language: 表示言語。"ja"（日本語）または "zh"（繁體中文）
        """
        self.grade = grade
        self.data_dir = Path(data_dir)
        self.language = language

        # 単語データをDataFrameとして読み込む
        self.df = self._load_csv()

        # まだ出題していない単語IDのリスト（セッション中の出題管理）
        self.remaining_ids: List[str] = list(self.df["word_id"])
        random.shuffle(self.remaining_ids)

        # セッション中の履歴
        self.history: List[QuizResult] = []

    # ──────────────────────────────────────
    # パブリックメソッド（外から呼ぶ関数）
    # ──────────────────────────────────────

    def get_next_question(self, prioritize_weak: bool = False) -> Optional["Question"]:
        """
        次の問題を1問返す。

        Args:
            prioritize_weak: Trueにすると苦手単語を優先して出題する

        Returns:
            Question オブジェクト。出題できる単語がなければ None を返す。
        """
        if not self.remaining_ids:
            return None  # 全問出題済み

        # 苦手単語優先モード
        if prioritize_weak:
            word_id = self._pick_weak_word() or self.remaining_ids.pop(0)
        else:
            word_id = self.remaining_ids.pop(0)

        # DataFrameから対象行を取得
        row = self.df[self.df["word_id"] == word_id].iloc[0]

        return self._build_question(row)

    def judge(self, question: Question, selected_answer: str) -> QuizResult:
        """
        回答を受け取り、正誤判定してQuizResultを返す。

        Args:
            question: get_next_question() で得たQuestionオブジェクト
            selected_answer: ユーザーが選んだ選択肢の文字列

        Returns:
            QuizResult オブジェクト
        """
        is_correct = (selected_answer == question.correct_answer)

        exp_gained = self.EXP_TABLE.get(question.difficulty, 10) if is_correct else 0
        hp_damage = 0 if is_correct else self.HP_DAMAGE

        result = QuizResult(
            question=question,
            selected_answer=selected_answer,
            is_correct=is_correct,
            exp_gained=exp_gained,
            hp_damage=hp_damage,
        )

        self.history.append(result)
        return result

    def get_weak_words(self, top_n: int = 10) -> pd.DataFrame:
        """
        セッション中に間違えた単語を間違えた回数順で返す。

        Args:
            top_n: 上位何件取得するか

        Returns:
            DataFrame（word, meaning_ja, miss_count 列を含む）
        """
        if not self.history:
            return pd.DataFrame()

        # 不正解だった問題を集計
        mistakes: Dict[str, int] = {}
        for result in self.history:
            if not result.is_correct:
                wid = result.question.word_id
                mistakes[wid] = mistakes.get(wid, 0) + 1

        if not mistakes:
            return pd.DataFrame()

        # DataFrameに変換して返す
        miss_df = pd.DataFrame(
            [{"word_id": k, "miss_count": v} for k, v in mistakes.items()]
        )
        cols = ["word_id", "word", "meaning_ja", "hint", "example_en", "example_ja"]
        if "meaning_zh" in self.df.columns:
            cols.append("meaning_zh")
        if "hint_zh" in self.df.columns:
            cols.append("hint_zh")
        merged = miss_df.merge(self.df[cols], on="word_id")
        return merged.sort_values("miss_count", ascending=False).head(top_n)

    def get_session_stats(self) -> dict:
        """
        現在のセッション統計を辞書で返す。

        Returns:
            {
              "total": 出題数,
              "correct": 正解数,
              "accuracy": 正答率（%）,
              "total_exp": 合計獲得EXP,
              "total_damage": 合計受けたHPダメージ
            }
        """
        total = len(self.history)
        if total == 0:
            return {"total": 0, "correct": 0, "accuracy": 0.0,
                    "total_exp": 0, "total_damage": 0}

        correct = sum(1 for r in self.history if r.is_correct)
        total_exp = sum(r.exp_gained for r in self.history)
        total_damage = sum(r.hp_damage for r in self.history)

        return {
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total * 100, 1),
            "total_exp": total_exp,
            "total_damage": total_damage,
        }

    def reset_session(self):
        """出題履歴をリセットして最初からやり直す。"""
        self.remaining_ids = list(self.df["word_id"])
        random.shuffle(self.remaining_ids)
        self.history = []

    def questions_left(self) -> int:
        """残り出題数を返す。"""
        return len(self.remaining_ids)

    # ──────────────────────────────────────
    # プライベートメソッド（内部処理）
    # ──────────────────────────────────────

    def _load_csv(self) -> pd.DataFrame:
        """CSVを読み込んでDataFrameを返す。ファイルが存在しない場合はエラー。"""
        csv_path = self.data_dir / f"{self.grade}.csv"

        if not csv_path.exists():
            raise FileNotFoundError(
                f"単語データが見つかりません: {csv_path}\n"
                f"data/words/ フォルダに {self.grade}.csv を置いてください。"
            )

        df = pd.read_csv(csv_path, dtype=str)  # 全列を文字列で読む

        # difficulty だけ数値に変換（なければデフォルト1）
        df["difficulty"] = pd.to_numeric(df.get("difficulty", 1), errors="coerce").fillna(1).astype(int)

        return df

    def _build_question(self, row: pd.Series) -> Question:
        """DataFrameの1行からQuestionオブジェクトを組み立てる。"""

        # 言語選択：meaning_zh が存在して空でなければ中国語を使用、なければ日本語にフォールバック
        if self.language == "zh" and "meaning_zh" in self.df.columns:
            zh_val = str(row.get("meaning_zh", "")).strip()
            correct = zh_val if (zh_val and zh_val != "nan") else str(row["meaning_ja"])
        else:
            correct = str(row["meaning_ja"])

        # ── 選択肢を組み立てる ──
        # 常に meaning_ja / meaning_zh プールから選ぶ（英語が混入しないよう wrong_choice列は使わない）
        wrong_choices = self._fill_wrong_choices(correct, [])

        # 正解を混ぜてシャッフル
        choices = wrong_choices[:3] + [correct]
        random.shuffle(choices)

        # タグをリストに変換
        raw_tags = str(row.get("tags", "")).strip()
        tags = raw_tags.split("|") if raw_tags and raw_tags != "nan" else []

        # ヒント（言語に応じて hint_zh / hint を選択）
        if self.language == "zh" and "hint_zh" in self.df.columns:
            zh_hint = str(row.get("hint_zh", "")).strip()
            hint = zh_hint if (zh_hint and zh_hint != "nan") else str(row.get("hint", "")).strip()
        else:
            hint = str(row.get("hint", "")).strip()
        hint = "" if hint == "nan" else hint

        # 例文（中国語があれば使用。なければ zh モードでは空文字にして日本語を表示しない）
        if self.language == "zh" and "example_zh" in self.df.columns:
            zh_ex = str(row.get("example_zh", "")).strip()
            example_ja_or_zh = zh_ex if (zh_ex and zh_ex != "nan") else ""
        else:
            example_ja_or_zh = str(row.get("example_ja", ""))

        return Question(
            word_id=str(row["word_id"]),
            grade=str(row.get("grade", "")),
            word=str(row["word"]),
            part_of_speech=str(row["part_of_speech"]),
            meaning_ja=correct,
            example_en=str(row.get("example_en", "")),
            example_ja=example_ja_or_zh,
            hint=hint,
            tags=tags,
            difficulty=int(row["difficulty"]),
            choices=choices,
            correct_answer=correct,
        )

    def _fill_wrong_choices(self, correct: str, existing: List[str]) -> List[str]:
        """
        ひっかけ選択肢が足りないとき、他の単語の意味から補う。
        中国語モードでは meaning_zh 列を使用（なければ meaning_ja にフォールバック）。
        """
        if self.language == "zh" and "meaning_zh" in self.df.columns:
            raw = self.df["meaning_zh"].dropna().tolist()
            all_meanings = [m for m in raw if str(m).strip() and str(m) != "nan"]
            if len(all_meanings) < 4:
                all_meanings = self.df["meaning_ja"].dropna().tolist()
        else:
            raw_ja = self.df["meaning_ja"].dropna().tolist()
            # ASCIIのみの値（英語が混入したデータ）を除外する
            all_meanings = [m for m in raw_ja if m and m != "nan" and not str(m).encode("ascii", errors="ignore").decode() == str(m)]
            if len(all_meanings) < 4:
                all_meanings = raw_ja
        pool = [m for m in all_meanings if m != correct and m not in existing]
        random.shuffle(pool)

        result = existing[:]
        for m in pool:
            if len(result) >= 3:
                break
            result.append(m)

        return result

    def _pick_weak_word(self) -> Optional[str]:
        """
        セッション履歴の中で一番間違えた単語のIDを返す。
        まだ間違えた単語がなければ None を返す。
        """
        mistakes: Dict[str, int] = {}
        for result in self.history:
            if not result.is_correct:
                wid = result.question.word_id
                # remaining_ids にあるもの（まだ出題可能なもの）だけカウント
                if wid in self.remaining_ids:
                    mistakes[wid] = mistakes.get(wid, 0) + 1

        if not mistakes:
            return None

        # 最も間違えた単語を返す
        worst_id = max(mistakes, key=lambda k: mistakes[k])
        self.remaining_ids.remove(worst_id)
        return worst_id


# ─────────────────────────────────────────
# 動作確認用スクリプト（直接実行したとき）
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  QuizEngine 動作確認テスト")
    print("=" * 50)

    # ── エンジンを初期化 ──
    engine = QuizEngine(grade="grade_4", data_dir="data/words")
    print(f"\n✅ grade_4.csv を読み込みました（{len(engine.df)}単語）")
    print(f"   残り問題数: {engine.questions_left()} 問\n")

    # ── 3問だけ出題してみる ──
    for i in range(3):
        question = engine.get_next_question()
        if question is None:
            print("出題できる単語がありません。")
            break

        print(f"─── 第{i+1}問 ───────────────────────────")
        print(f"  単語      : {question.word} ({question.part_of_speech})")
        print(f"  選択肢    : {question.choices}")
        print(f"  正解      : {question.correct_answer}")
        print(f"  例文(EN)  : {question.example_en}")
        print(f"  例文(JA)  : {question.example_ja}")
        if question.hint:
            print(f"  ヒント    : {question.hint}")
        print(f"  難易度    : {question.difficulty} / タグ: {question.tags}")

        # テスト用：最初の選択肢を選ぶ（正解とは限らない）
        selected = question.choices[0]
        result = engine.judge(question, selected_answer=selected)

        if result.is_correct:
            print(f"  → ✅ 正解！ 獲得EXP: +{result.exp_gained}")
        else:
            print(f"  → ❌ 不正解。HP: -{result.hp_damage}  正解は「{question.correct_answer}」")
        print()

    # ── セッション統計 ──
    stats = engine.get_session_stats()
    print("─── セッション統計 ─────────────────────")
    print(f"  出題数    : {stats['total']} 問")
    print(f"  正解数    : {stats['correct']} 問")
    print(f"  正答率    : {stats['accuracy']} %")
    print(f"  獲得EXP   : {stats['total_exp']}")
    print(f"  受けたダメージ: {stats['total_damage']} HP")

    # ── 苦手単語 ──
    weak = engine.get_weak_words()
    if not weak.empty:
        print("\n─── 苦手単語 ───────────────────────────")
        print(weak[["word", "meaning_ja", "miss_count"]].to_string(index=False))

    print("\n✅ テスト完了")