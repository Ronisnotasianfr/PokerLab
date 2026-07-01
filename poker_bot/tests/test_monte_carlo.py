"""
test_monte_carlo.py — Validate Monte Carlo win-rate estimates.

Spot checks:
  - Pocket aces preflop heads-up: expect ~80-90% win rate
  - 7-2 offsuit preflop heads-up: expect ~30-40% win rate
  - Made flush vs random board: significantly above 50%
  - Win rate is always in [0, 1]
"""

import unittest
from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate

TRIALS = 5000  # lower for fast tests; increase for accuracy


class TestMonteCarlo(unittest.TestCase):

    def test_pocket_aces_preflop(self):
        hole = to_treys_list(["As", "Ah"])
        wr = win_rate(hole, board_cards=[], n_opponents=1, trials=TRIALS)
        self.assertGreater(wr, 0.78, f"Pocket aces should have >78% win rate, got {wr:.2%}")
        self.assertLess(wr, 0.95, f"Pocket aces win rate unrealistically high: {wr:.2%}")

    def test_72_offsuit_preflop(self):
        hole = to_treys_list(["7s", "2d"])
        wr = win_rate(hole, board_cards=[], n_opponents=1, trials=TRIALS)
        self.assertLess(wr, 0.42, f"7-2 offsuit should have <42% win rate, got {wr:.2%}")
        self.assertGreater(wr, 0.28, f"7-2 offsuit win rate unrealistically low: {wr:.2%}")

    def test_win_rate_in_bounds(self):
        hole = to_treys_list(["Tc", "9h"])
        board = to_treys_list(["8s", "7d", "Jc"])
        wr = win_rate(hole, board_cards=board, n_opponents=1, trials=TRIALS)
        self.assertGreaterEqual(wr, 0.0)
        self.assertLessEqual(wr, 1.0)

    def test_flop_strong_hand(self):
        # Top set (three aces) on flop should be very strong
        hole = to_treys_list(["As", "Ah"])
        board = to_treys_list(["Ad", "2c", "7h"])
        wr = win_rate(hole, board_cards=board, n_opponents=1, trials=TRIALS)
        self.assertGreater(wr, 0.85, f"Top set should be >85% on flop, got {wr:.2%}")

    def test_multiway_reduces_win_rate(self):
        # More opponents = lower win rate for the same hand
        hole = to_treys_list(["As", "Kh"])
        wr_hu = win_rate(hole, board_cards=[], n_opponents=1, trials=TRIALS)
        wr_3way = win_rate(hole, board_cards=[], n_opponents=2, trials=TRIALS)
        self.assertGreater(wr_hu, wr_3way, "Win rate should decrease with more opponents")


if __name__ == "__main__":
    unittest.main()
