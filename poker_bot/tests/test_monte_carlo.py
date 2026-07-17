import unittest
from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate

TRIALS = 5000


class TestMonteCarlo(unittest.TestCase):

    def test_pocket_aces_preflop(self):
        hole = to_treys_list(["As", "Ah"])
        wr = win_rate(hole, board_cards=[], n_opponents=1, trials=TRIALS)
        self.assertGreater(wr, 0.78)
        self.assertLess(wr, 0.95)

    def test_72_offsuit_preflop(self):
        hole = to_treys_list(["7s", "2d"])
        wr = win_rate(hole, board_cards=[], n_opponents=1, trials=TRIALS)
        self.assertLess(wr, 0.42)
        self.assertGreater(wr, 0.28)

    def test_win_rate_in_bounds(self):
        hole = to_treys_list(["Tc", "9h"])
        board = to_treys_list(["8s", "7d", "Jc"])
        wr = win_rate(hole, board_cards=board, n_opponents=1, trials=TRIALS)
        self.assertGreaterEqual(wr, 0.0)
        self.assertLessEqual(wr, 1.0)

    def test_flop_strong_hand(self):
        hole = to_treys_list(["As", "Ah"])
        board = to_treys_list(["Ad", "2c", "7h"])
        wr = win_rate(hole, board_cards=board, n_opponents=1, trials=TRIALS)
        self.assertGreater(wr, 0.85)

    def test_multiway_reduces_win_rate(self):
        hole = to_treys_list(["As", "Kh"])
        wr_hu = win_rate(hole, board_cards=[], n_opponents=1, trials=TRIALS)
        wr_3way = win_rate(hole, board_cards=[], n_opponents=2, trials=TRIALS)
        self.assertGreater(wr_hu, wr_3way)


if __name__ == "__main__":
    unittest.main()
