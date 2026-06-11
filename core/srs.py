"""
core/srs.py ― 間隔反復（SRS / Leitner方式）

単語ごとに「箱」(box 1〜5) と次回復習日 (due) を player["srs"] に記録する。
  - 正解するたびに box が1つ上がり、次の復習日が遠くなる
      box1: 当日 / box2: 翌日 / box3: 3日後 / box4: 7日後 / box5: 14日後
  - 不正解すると box1 に戻り、すぐに復習対象になる
  - box5 に到達した単語は「マスター済み」とみなす（14日周期で軽く復習）

player dict は回答ごとにSupabaseへ保存されるため、追加の永続化は不要。
"""

from __future__ import annotations
from datetime import date, timedelta

BOX_INTERVALS = {1: 0, 2: 1, 3: 3, 4: 7, 5: 14}
MAX_BOX = 5


def record_result(player: dict, word: str, is_correct: bool) -> int:
    """回答結果をSRSに記録し、新しいbox番号を返す。"""
    srs = player.setdefault("srs", {})
    entry = srs.get(word, {})
    if is_correct:
        box = min(MAX_BOX, entry.get("box", 0) + 1)
    else:
        box = 1
    due = (date.today() + timedelta(days=BOX_INTERVALS[box])).isoformat()
    srs[word] = {"box": box, "due": due}
    return box


def due_words(player: dict) -> list[str]:
    """今日復習すべき単語のリストを返す（期限が今日以前のもの）。"""
    today = date.today().isoformat()
    srs = player.get("srs", {})
    return [w for w, e in srs.items() if str(e.get("due", "")) <= today]


def mastered_count(player: dict) -> int:
    """マスター済み（box5到達）の単語数を返す。"""
    return sum(1 for e in player.get("srs", {}).values() if e.get("box", 0) >= MAX_BOX)


def tracked_count(player: dict) -> int:
    """SRSに記録されている単語数を返す。"""
    return len(player.get("srs", {}))
