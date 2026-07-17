import unittest
from poker_bot.cards import to_treys_list
from poker_bot.evaluator import rank_hand, class_string


class TestEvaluator(unittest.TestCase):

    def test_royal_flush_beats_quads(self):
        hole_rf = to_treys_list(["As", "Ks"])
        board_rf = to_treys_list(["Qs", "Js", "Ts", "2d", "3c"])
        rank_rf = rank_hand(hole_rf, board_rf)

        hole_q = to_treys_list(["Ac", "Ad"])
        board_q = to_treys_list(["2d", "2h", "2s", "2c", "3h"])
        rank_q = rank_hand(hole_q, board_q)

        self.assertLess(rank_rf, rank_q)

    def test_full_house_beats_flush(self):
        hole_fh = to_treys_list(["As", "Ah"])
        board_fh = to_treys_list(["Ad", "Kh", "Kc", "2d", "7s"])
        rank_fh = rank_hand(hole_fh, board_fh)

        hole_fl = to_treys_list(["2h", "4h"])
        board_fl = to_treys_list(["6h", "8h", "Th", "3d", "5s"])
        rank_fl = rank_hand(hole_fl, board_fl)

        self.assertLess(rank_fh, rank_fl)

    def test_pair_beats_high_card(self):
        hole_pair = to_treys_list(["As", "Ah"])
        board_pair = to_treys_list(["2d", "7c", "Ks", "4h", "9c"])
        rank_pair = rank_hand(hole_pair, board_pair)

        hole_hc = to_treys_list(["2s", "4d"])
        board_hc = to_treys_list(["7h", "9c", "Jd", "Ks", "3h"])
        rank_hc = rank_hand(hole_hc, board_hc)

        self.assertLess(rank_pair, rank_hc)

    def test_class_string_returns_string(self):
        hole = to_treys_list(["As", "Ah"])
        board = to_treys_list(["Ad", "Ac", "Kh", "Qs", "Jd"])
        rank = rank_hand(hole, board)
        cs = class_string(rank)
        self.assertIsInstance(cs, str)
        self.assertGreater(len(cs), 0)


if __name__ == "__main__":
    unittest.main()
