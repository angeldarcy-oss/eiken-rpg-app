"""
英検単語CSV自動生成スクリプト（Groq版）
使い方: python3 generate_words.py
"""
import os
import json
import time
import csv
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GRADES = {
    "grade_5":    {"label": "5級",  "target": 500,  "level": "小学生レベル、基本的な日常単語"},
    "grade_4":    {"label": "4級",  "target": 700,  "level": "中学1-2年レベル、基本単語"},
    "grade_3":    {"label": "3級",  "target": 1300, "level": "中学卒業レベル"},
    "grade_pre2": {"label": "準2級","target": 2000, "level": "高校中級レベル"},
    "grade_2":    {"label": "2級",  "target": 2500, "level": "高校卒業レベル"},
}

FIELDNAMES = ["word_id","word","meaning_ja","part_of_speech","example_en","example_ja","hint","difficulty"]

def generate_batch(grade_info, existing_words, batch_size=50):
    existing_list = list(existing_words)[-100:]
    existing_str = ", ".join(existing_list) if existing_list else "なし"
    prompt = f"""英検{grade_info['label']}レベル（{grade_info['level']}）の英単語を{batch_size}個生成してください。

除外する単語: {existing_str}

以下のJSON配列のみを返してください。説明文は不要です：
[
  {{
    "word": "英単語",
    "meaning_ja": "日本語の意味",
    "part_of_speech": "n",
    "example_en": "短い英語例文",
    "example_ja": "例文の日本語訳",
    "hint": "覚え方ヒント（任意、空でも可）",
    "difficulty": 1
  }}
]

part_of_speechはn/v/adj/adv/prepのいずれか。difficultyは1か2か3。
JSONのみ返してください。"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000,
        )
        text = response.choices[0].message.content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"  エラー: {e}")
        return []

def generate_grade_csv(grade_key, grade_info, output_dir):
    output_path = Path(output_dir) / f"{grade_key}.csv"
    existing_words = set()
    rows = []

    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                clean_row = {k: row.get(k, "") for k in FIELDNAMES}
                rows.append(clean_row)
                existing_words.add(row["word"])
        print(f"  既存: {len(rows)}単語")

    target = grade_info["target"]
    consecutive_failures = 0

    while len(rows) < target:
        print(f"  {len(rows)}/{target}単語 生成中...")
        batch = generate_batch(grade_info, existing_words)

        if not batch:
            consecutive_failures += 1
            if consecutive_failures >= 3:
                print("  3回連続失敗。終了します。")
                break
            print(f"  生成失敗({consecutive_failures}回目)。10秒待機...")
            time.sleep(10)
            continue

        consecutive_failures = 0
        added = 0
        for item in batch:
            word = str(item.get("word", "")).strip()
            if not word or word in existing_words:
                continue
            rows.append({
                "word_id": f"{grade_key}_{len(rows)+1:04d}",
                "word": word,
                "meaning_ja": str(item.get("meaning_ja", "")),
                "part_of_speech": str(item.get("part_of_speech", "n")),
                "example_en": str(item.get("example_en", "")),
                "example_ja": str(item.get("example_ja", "")),
                "hint": str(item.get("hint", "")),
                "difficulty": int(item.get("difficulty", 1)),
            })
            existing_words.add(word)
            added += 1

        print(f"  → {added}単語追加 (合計: {len(rows)})")

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)

        if added == 0:
            print("  新規単語なし。終了します。")
            break

        time.sleep(2)

    print(f"  完了: {len(rows)}単語")
    return len(rows)

def main():
    output_dir = "data/words"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print("英検単語生成スクリプト（Groq版）")
    print("=" * 40)
    for key, info in GRADES.items():
        csv_path = Path(output_dir) / f"{key}.csv"
        current = 0
        if csv_path.exists():
            with open(csv_path) as f:
                current = sum(1 for _ in f) - 1
        print(f"  {info['label']}: 現在{current}語 → 目標{info['target']}語")

    print("\n生成開始（Ctrl+Cで中断可能）")
    print("=" * 40)

    for grade_key, grade_info in GRADES.items():
        csv_path = Path(output_dir) / f"{grade_key}.csv"
        current = 0
        if csv_path.exists():
            with open(csv_path) as f:
                current = sum(1 for _ in f) - 1
        if current >= grade_info["target"]:
            print(f"\n英検{grade_info['label']}はすでに完了（{current}語）")
            continue
        print(f"\n【英検{grade_info['label']}】生成開始...")
        count = generate_grade_csv(grade_key, grade_info, output_dir)
        print(f"英検{grade_info['label']}完了: {count}語")
        time.sleep(3)

    print("\n全級完了！")
    print("次のコマンドでGitHubにプッシュ:")
    print("  git add data/words/")
    print("  git commit -m '単語データ増量'")
    print("  git push")

if __name__ == "__main__":
    main()
