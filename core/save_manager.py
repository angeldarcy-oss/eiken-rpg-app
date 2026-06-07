"""
core/save_manager.py  ―  セーブデータ管理（JSON永続化）

役割:
  - プレイヤーデータを data/saves/player_data.json に保存・読み込み
  - 学習履歴（日別ログ）の追記
  - セーブファイルが壊れていても新規データで起動できる安全設計
"""

from __future__ import annotations
from typing import Optional, List, Dict
import json
import os
from datetime import date, datetime
from pathlib import Path

from core.player import new_player, exp_to_next_level


# ─────────────────────────────────────────
# パス定数
# ─────────────────────────────────────────

SAVE_DIR  = Path("data/saves")
SAVE_FILE = SAVE_DIR / "player_data.json"


# ─────────────────────────────────────────
# セーブ・ロード
# ─────────────────────────────────────────

def load_player() -> dict:
    """
    player_data.json を読み込んでプレイヤー辞書を返す。
    ファイルが存在しない・壊れている場合は新規データを返す。

    Returns:
        session_state.player として使える辞書
    """
    if not SAVE_FILE.exists():
        return new_player()

    try:
        with open(SAVE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        player = data.get("player", {})
        return _validate_and_fill(player)

    except (json.JSONDecodeError, KeyError, TypeError):
        # ファイルが壊れていたら新規作成
        return new_player()


def save_player(player: dict) -> bool:
    """
    プレイヤー辞書を player_data.json に保存する。

    Args:
        player: session_state.player の辞書

    Returns:
        True: 保存成功 / False: 失敗
    """
    try:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)

        # 既存データを読み込んで player キーだけ上書き（他のキーを保持）
        existing: dict = {}
        if SAVE_FILE.exists():
            try:
                with open(SAVE_FILE, encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass

        existing["player"] = player
        existing["last_saved"] = datetime.now().isoformat(timespec="seconds")

        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(f"[SaveManager] 保存失敗: {e}")
        return False


# ─────────────────────────────────────────
# 学習履歴の追記
# ─────────────────────────────────────────

def append_history(session_stats: dict) -> bool:
    """
    1クエスト分の学習記録を player_data.json の history 配列に追記する。

    Args:
        session_stats: QuizEngine.get_session_stats() の戻り値に
                       grade_target を加えた辞書

        例:
        {
            "total": 15,
            "correct": 12,
            "accuracy": 80.0,
            "total_exp": 195,
            "total_damage": 30,
            "grade_target": "grade_4",
        }

    Returns:
        True: 成功 / False: 失敗
    """
    try:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)

        existing: dict = {}
        if SAVE_FILE.exists():
            try:
                with open(SAVE_FILE, encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass

        history: list = existing.get("history", [])

        record = {
            "date": date.today().isoformat(),          # 例: "2025-06-05"
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "grade": session_stats.get("grade_target", ""),
            "total":    session_stats.get("total", 0),
            "correct":  session_stats.get("correct", 0),
            "accuracy": session_stats.get("accuracy", 0.0),
            "exp_gained": session_stats.get("total_exp", 0),
            "damage_taken": session_stats.get("total_damage", 0),
        }
        history.append(record)

        # 直近180件だけ保持（古いデータを自動削除）
        existing["history"] = history[-180:]
        existing["last_saved"] = datetime.now().isoformat(timespec="seconds")

        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(f"[SaveManager] 履歴保存失敗: {e}")
        return False


def load_history() -> List[dict]:
    """
    学習履歴を新しい順のリストで返す。

    Returns:
        list of dict（各要素は append_history で保存したrecord形式）
        ファイルが存在しない場合は空リスト
    """
    if not SAVE_FILE.exists():
        return []
    try:
        with open(SAVE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        history = data.get("history", [])
        return list(reversed(history))   # 新しい順
    except Exception:
        return []


# ─────────────────────────────────────────
# セーブデータ削除（リセット用）
# ─────────────────────────────────────────

def delete_save() -> bool:
    """
    セーブファイルを削除して完全リセットする。

    Returns:
        True: 削除成功または元々存在しない / False: 失敗
    """
    try:
        if SAVE_FILE.exists():
            SAVE_FILE.unlink()
        return True
    except Exception as e:
        print(f"[SaveManager] 削除失敗: {e}")
        return False


def save_exists() -> bool:
    """セーブファイルが存在するかどうかを返す。"""
    return SAVE_FILE.exists()


# ─────────────────────────────────────────
# 内部ユーティリティ
# ─────────────────────────────────────────

def _validate_and_fill(player: dict) -> dict:
    """
    読み込んだプレイヤー辞書に必要なキーが揃っているか確認し、
    不足分をデフォルト値で補う（バージョンアップ時の後方互換）。
    """
    defaults = new_player()
    for key, default_val in defaults.items():
        if key not in player:
            player[key] = default_val

    # exp_to_next が古い固定値のままならリセット
    expected = exp_to_next_level(player["level"])
    if player.get("exp_to_next", 0) != expected:
        player["exp_to_next"] = expected

    return player


# ─────────────────────────────────────────
# 動作確認（直接実行したとき）
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  save_manager.py 動作確認テスト")
    print("=" * 55)

    # ── 保存テスト ──
    test_player = new_player(name="テスト勇者", grade_target="grade_4")
    test_player["level"] = 3
    test_player["exp"] = 45
    test_player["hp"] = 80

    print(f"\n[保存] {test_player['name']} Lv{test_player['level']}")
    ok = save_player(test_player)
    print(f"  → {'✅ 成功' if ok else '❌ 失敗'}")

    # ── 読み込みテスト ──
    loaded = load_player()
    print(f"\n[読込] {loaded['name']} Lv{loaded['level']} "
          f"HP:{loaded['hp']}/{loaded['hp_max']} "
          f"EXP:{loaded['exp']}/{loaded['exp_to_next']}")

    # ── 履歴追記テスト ──
    stats = {
        "total": 15, "correct": 12, "accuracy": 80.0,
        "total_exp": 195, "total_damage": 30,
        "grade_target": "grade_4",
    }
    ok2 = append_history(stats)
    print(f"\n[履歴追記] → {'✅ 成功' if ok2 else '❌ 失敗'}")

    # ── 履歴読み込みテスト ──
    history = load_history()
    print(f"[履歴件数] {len(history)} 件")
    if history:
        print(f"  最新: {history[0]}")

    # ── JSONファイルの中身を表示 ──
    print(f"\n[保存先] {SAVE_FILE.resolve()}")
    with open(SAVE_FILE, encoding="utf-8") as f:
        print(f.read())

    print("✅ テスト完了")