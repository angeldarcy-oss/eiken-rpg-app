"""
core/player.py  ―  プレイヤーステータス管理エンジン

役割:
  - レベル・EXP・HPの本格計算式
  - レベルアップ処理（連鎖レベルアップにも対応）
  - ステータス辞書を受け取り、更新した辞書を返す（Streamlitのセッションと相性◎）
  - レベルに応じたステータス成長（HP上限アップ）
"""

from __future__ import annotations
from typing import Optional, List, Dict
from dataclasses import dataclass, field


# ─────────────────────────────────────────
# 定数・計算式
# ─────────────────────────────────────────

# レベルNに上がるために必要な累計EXP
#   公式: BASE_EXP * (level ^ EXP_EXPONENT)
#   例: Lv2=100, Lv3=230, Lv4=397, Lv5=604 ...
BASE_EXP: int   = 100    # Lv2に必要なEXP
EXP_EXPONENT: float = 1.6  # 指数（大きいほど後半が急になる）

# レベルアップごとにHP上限が増える量
HP_GROWTH_PER_LEVEL: int = 10   # Lv2→ 110, Lv3→ 120 ...
HP_BASE: int = 100              # Lv1のHP上限

# 連続正解ボーナス（streak数 → EXP倍率）
STREAK_BONUS_TABLE: Dict[int, float] = {
    3:  1.2,   # 3連続 → EXP×1.2
    5:  1.5,   # 5連続 → EXP×1.5
    10: 2.0,   # 10連続 → EXP×2.0
}


# ─────────────────────────────────────────
# データクラス
# ─────────────────────────────────────────

@dataclass
class LevelUpEvent:
    """レベルアップが起きたときの情報"""
    old_level: int
    new_level: int
    hp_recovered: int       # 回復量（= hp_max_new）
    hp_max_old: int
    hp_max_new: int


@dataclass
class GainExpResult:
    """gain_exp() の戻り値"""
    exp_gained_raw: int         # 元のEXP
    exp_gained_final: int       # ボーナス込みの実際のEXP
    streak_multiplier: float    # 適用された倍率（ボーナスなし=1.0）
    level_up_events: List[LevelUpEvent] = field(default_factory=list)
    leveled_up: bool = False


# ─────────────────────────────────────────
# 計算ユーティリティ（純粋関数）
# ─────────────────────────────────────────

def exp_to_next_level(level: int) -> int:
    """
    現在レベルから次のレベルに上がるために必要なEXPを返す。

    Args:
        level: 現在のレベル（1始まり）

    Returns:
        必要EXP（整数）

    Examples:
        exp_to_next_level(1) → 100
        exp_to_next_level(2) → 230
        exp_to_next_level(5) → 604
    """
    return int(BASE_EXP * ((level + 1) ** EXP_EXPONENT))


def max_hp_at_level(level: int) -> int:
    """
    レベルに応じたHP上限を返す。

    Args:
        level: レベル（1始まり）

    Returns:
        HP上限

    Examples:
        max_hp_at_level(1) → 100
        max_hp_at_level(5) → 140
    """
    return HP_BASE + HP_GROWTH_PER_LEVEL * (level - 1)


def streak_multiplier(streak: int) -> float:
    """
    連続正解数に応じたEXP倍率を返す。
    最も高い閾値を優先する。

    Args:
        streak: 連続正解数

    Returns:
        EXP倍率（float）

    Examples:
        streak_multiplier(2)  → 1.0
        streak_multiplier(3)  → 1.2
        streak_multiplier(10) → 2.0
    """
    multiplier = 1.0
    for threshold in sorted(STREAK_BONUS_TABLE.keys()):
        if streak >= threshold:
            multiplier = STREAK_BONUS_TABLE[threshold]
    return multiplier


# ─────────────────────────────────────────
# PlayerManager クラス
# ─────────────────────────────────────────

class PlayerManager:
    """
    プレイヤーステータス辞書を操作するクラス。

    Streamlit の session_state.player（dict）を直接受け取り、
    in-place で更新する設計。

    使い方:
        pm = PlayerManager(st.session_state.player)
        result = pm.gain_exp(20, streak=5)
        pm.take_damage(10)
    """

    def __init__(self, player: dict):
        """
        Args:
            player: session_state.player の辞書。以下のキーが必須:
                level, exp, exp_to_next, hp, hp_max, streak (任意)
        """
        self.p = player
        # 旧フォーマットの辞書を自動補完（後方互換）
        self.p.setdefault("streak", 0)
        self.p.setdefault("total_exp_earned", 0)
        self.p.setdefault("total_damage_taken", 0)

    # ──────────────────────────────────────
    # EXP・レベルアップ
    # ──────────────────────────────────────

    def gain_exp(self, base_exp: int, streak: int = 0) -> GainExpResult:
        """
        EXPを加算し、必要に応じてレベルアップ処理を行う。
        連続正解ボーナスも自動適用。

        Args:
            base_exp: 基本獲得EXP
            streak:   現在の連続正解数（ボーナス計算に使う）

        Returns:
            GainExpResult（何が起きたかの詳細）
        """
        multiplier = streak_multiplier(streak)
        final_exp = max(1, int(base_exp * multiplier))

        self.p["exp"] += final_exp
        self.p["total_exp_earned"] = self.p.get("total_exp_earned", 0) + final_exp

        # レベルアップ（連鎖対応）
        level_up_events: List[LevelUpEvent] = []
        while self.p["exp"] >= self.p["exp_to_next"]:
            event = self._do_level_up()
            level_up_events.append(event)

        return GainExpResult(
            exp_gained_raw=base_exp,
            exp_gained_final=final_exp,
            streak_multiplier=multiplier,
            level_up_events=level_up_events,
            leveled_up=len(level_up_events) > 0,
        )

    def _do_level_up(self) -> LevelUpEvent:
        """レベルアップを1回実行し、LevelUpEventを返す内部メソッド。"""
        old_level = self.p["level"]
        old_hp_max = self.p["hp_max"]

        # EXPを繰り越す
        self.p["exp"] -= self.p["exp_to_next"]
        self.p["level"] += 1

        # 新しいHP上限と次レベルに必要なEXPを計算
        new_hp_max = max_hp_at_level(self.p["level"])
        self.p["hp_max"] = new_hp_max
        self.p["hp"] = new_hp_max          # レベルアップ時はHP全回復
        self.p["exp_to_next"] = exp_to_next_level(self.p["level"])

        return LevelUpEvent(
            old_level=old_level,
            new_level=self.p["level"],
            hp_recovered=new_hp_max,
            hp_max_old=old_hp_max,
            hp_max_new=new_hp_max,
        )

    # ──────────────────────────────────────
    # HP管理
    # ──────────────────────────────────────

    def take_damage(self, damage: int) -> dict:
        """
        HPにダメージを与える。0以下にはならない。

        Args:
            damage: ダメージ量（正の整数）

        Returns:
            {"hp_before": int, "hp_after": int, "is_ko": bool}
        """
        hp_before = self.p["hp"]
        self.p["hp"] = max(0, self.p["hp"] - damage)
        self.p["total_damage_taken"] = self.p.get("total_damage_taken", 0) + damage

        return {
            "hp_before": hp_before,
            "hp_after": self.p["hp"],
            "is_ko": self.p["hp"] == 0,
        }

    def heal(self, amount: int) -> dict:
        """
        HPを回復する。hp_maxを超えない。

        Args:
            amount: 回復量

        Returns:
            {"hp_before": int, "hp_after": int, "healed": int}
        """
        hp_before = self.p["hp"]
        self.p["hp"] = min(self.p["hp_max"], self.p["hp"] + amount)
        return {
            "hp_before": hp_before,
            "hp_after": self.p["hp"],
            "healed": self.p["hp"] - hp_before,
        }

    def full_heal(self) -> None:
        """HPをhp_maxまで全回復する。"""
        self.p["hp"] = self.p["hp_max"]

    # ──────────────────────────────────────
    # 連続正解
    # ──────────────────────────────────────

    def increment_streak(self) -> int:
        """連続正解数を1増やして返す。"""
        self.p["streak"] = self.p.get("streak", 0) + 1
        return self.p["streak"]

    def reset_streak(self) -> None:
        """連続正解数をリセットする。"""
        self.p["streak"] = 0

    # ──────────────────────────────────────
    # ステータス参照
    # ──────────────────────────────────────

    @property
    def level(self) -> int:
        return self.p["level"]

    @property
    def hp(self) -> int:
        return self.p["hp"]

    @property
    def hp_max(self) -> int:
        return self.p["hp_max"]

    @property
    def exp(self) -> int:
        return self.p["exp"]

    @property
    def exp_to_next(self) -> int:
        return self.p["exp_to_next"]

    @property
    def streak(self) -> int:
        return self.p.get("streak", 0)

    def hp_percent(self) -> float:
        """HP残量を0.0〜1.0で返す。"""
        return self.p["hp"] / self.p["hp_max"] if self.p["hp_max"] > 0 else 0.0

    def exp_percent(self) -> float:
        """EXP進捗を0.0〜1.0で返す。"""
        return min(1.0, self.p["exp"] / self.p["exp_to_next"])

    def summary(self) -> dict:
        """現在のステータスを辞書で返す（ログ・表示用）。"""
        return {
            "level": self.level,
            "hp": f"{self.hp}/{self.hp_max}",
            "exp": f"{self.exp}/{self.exp_to_next}",
            "streak": self.streak,
            "hp_pct": f"{self.hp_percent()*100:.1f}%",
            "exp_pct": f"{self.exp_percent()*100:.1f}%",
        }


# ─────────────────────────────────────────
# プレイヤーデータの初期値を生成するファクトリ
# ─────────────────────────────────────────

def new_player(name: str = "勇者", grade_target: str = "grade_4") -> dict:
    """
    新規プレイヤーの初期ステータス辞書を返す。
    save_manager.py や app.py から呼ぶ。

    Args:
        name:         プレイヤー名
        grade_target: 挑戦中の英検の級

    Returns:
        session_state.player として使える辞書
    """
    return {
        "name": name,
        "level": 1,
        "hp": HP_BASE,
        "hp_max": HP_BASE,
        "exp": 0,
        "exp_to_next": exp_to_next_level(1),
        "grade_target": grade_target,
        "streak": 0,
        "total_exp_earned": 0,
        "total_damage_taken": 0,
    }


# ─────────────────────────────────────────
# 動作確認（直接実行したとき）
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  player.py 動作確認テスト")
    print("=" * 55)

    # 新規プレイヤー作成
    player = new_player(name="テスト勇者", grade_target="grade_4")
    pm = PlayerManager(player)
    print(f"\n初期ステータス: {pm.summary()}")

    # ── EXP獲得テスト ──
    print("\n--- EXP獲得テスト ---")
    for i in range(1, 12):
        # 3問目から連続正解ボーナス発動
        streak = i
        pm.increment_streak()
        result = pm.gain_exp(base_exp=15, streak=streak)

        bonus_str = f" (×{result.streak_multiplier}ボーナス!)" if result.streak_multiplier > 1.0 else ""
        print(f"  第{i:2d}問 正解 +{result.exp_gained_final}EXP{bonus_str}", end="")

        if result.leveled_up:
            for ev in result.level_up_events:
                print(f"  ✨ Lv{ev.old_level}→{ev.new_level}！HP上限{ev.hp_max_old}→{ev.hp_max_new}")
        else:
            print()

    print(f"\n  ステータス: {pm.summary()}")

    # ── ダメージテスト ──
    print("\n--- ダメージテスト ---")
    for _ in range(3):
        dmg = pm.take_damage(10)
        pm.reset_streak()
        print(f"  不正解 HP: {dmg['hp_before']} → {dmg['hp_after']}", end="")
        if dmg["is_ko"]:
            print("  💀 KO！")
        else:
            print()

    # ── 回復テスト ──
    print("\n--- 回復テスト ---")
    heal = pm.heal(30)
    print(f"  30回復: HP {heal['hp_before']} → {heal['hp_after']} (実回復量: {heal['healed']})")

    # ── レベルアップ時の計算式確認 ──
    print("\n--- レベルアップ必要EXP一覧 ---")
    for lv in range(1, 11):
        print(f"  Lv{lv:2d} → Lv{lv+1:2d}: {exp_to_next_level(lv):5d} EXP  "
              f"(HP上限: {max_hp_at_level(lv)} → {max_hp_at_level(lv+1)})")

    print("\n✅ テスト完了")