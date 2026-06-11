"""
migrate_to_supabase.py ― 既存ローカルセーブをSupabaseへ移行する一回限りのスクリプト

data/saves/ 配下の users.json / user_*.json / rankings.json を読み込み、
Supabaseの users / players / history / rankings テーブルへ投入する。

使い方:
  1. supabase_schema.sql をSupabaseのSQL Editorで実行してテーブルを作る
  2. .env に SUPABASE_URL / SUPABASE_KEY を設定する
  3. python migrate_to_supabase.py
"""

from __future__ import annotations
import json
from pathlib import Path

from core.supabase_client import get_client

SAVE_DIR = Path("data/saves")


def _safe_name(username: str) -> str:
    return "".join(c for c in username if c.isalnum() or c in "-_")


def main():
    client = get_client()

    users_file = SAVE_DIR / "users.json"
    if not users_file.exists():
        print("移行するローカルセーブが見つかりません: " + str(users_file))
        return

    with open(users_file, encoding="utf-8") as f:
        accounts = json.load(f).get("accounts", {})

    rankings: dict = {}
    rankings_file = SAVE_DIR / "rankings.json"
    if rankings_file.exists():
        with open(rankings_file, encoding="utf-8") as f:
            rankings = json.load(f)

    migrated = 0
    for username, info in accounts.items():
        # 既に登録済みならスキップ
        exists = (
            client.table("users")
            .select("id")
            .eq("username_lower", username.lower())
            .limit(1)
            .execute()
        )
        if exists.data:
            print("スキップ（登録済み）: " + username)
            continue

        res = client.table("users").insert({
            "username": username,
            "password_hash": info.get("password_hash", ""),
            "created_at": info.get("created_at") or None,
        }).execute()
        user_id = res.data[0]["id"]

        save_file = SAVE_DIR / ("user_" + _safe_name(username) + ".json")
        save_data: dict = {}
        if save_file.exists():
            with open(save_file, encoding="utf-8") as f:
                save_data = json.load(f)

        client.table("players").insert({
            "user_id": user_id,
            "data": save_data.get("player", {}),
            "weak_words": save_data.get("weak_words", []),
        }).execute()

        history_rows = [
            {
                "user_id": user_id,
                "played_on": h.get("date") or "1970-01-01",
                "played_at": h.get("timestamp") or "1970-01-01T00:00:00",
                "grade": h.get("grade", ""),
                "total": h.get("total", 0),
                "correct": h.get("correct", 0),
                "accuracy": float(h.get("accuracy", 0.0)),
                "exp_gained": h.get("exp_gained", 0),
                "damage_taken": h.get("damage_taken", 0),
            }
            for h in save_data.get("history", [])
        ]
        if history_rows:
            client.table("history").insert(history_rows).execute()

        rank = rankings.get("users", {}).get(username)
        if rank:
            client.table("rankings").upsert({
                "user_id": user_id,
                "username": username,
                "name": rank.get("name", username),
                "character": rank.get("character", ""),
                "level": rank.get("level", 1),
                "total_exp": rank.get("total_exp", 0),
                "grade_target": rank.get("grade_target", "grade_5"),
                "weekly_correct": rank.get("weekly_correct", 0),
                "weekly_total": rank.get("weekly_total", 0),
                "max_streak": rank.get("max_streak", 0),
                "best_streak": rank.get("best_streak", 0),
                "boss_defeats": rank.get("boss_defeats", 0),
                "active_title": rank.get("active_title"),
                "titles": rank.get("titles", []),
                "week_start": rankings.get("week_start") or "1970-01-01",
            }).execute()

        migrated += 1
        print("移行完了: " + username + " (履歴" + str(len(history_rows)) + "件)")

    print("\n✅ " + str(migrated) + "人のユーザーを移行しました")


if __name__ == "__main__":
    main()
