import random

from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate
from poker_bot.thresholds import action_from_win_rate, ALL_ACTIONS, FOLD, CHECK, RAISE_2X


class AlwaysRaiseBot:
    def decide(self, game_state):
        return RAISE_2X


class AlwaysCallBot:
    def decide(self, game_state):
        return CHECK


class TightFoldBot:
    THRESHOLD = 0.80

    def decide(self, game_state):
        hole = to_treys_list(game_state["hole_cards"])
        board = to_treys_list(game_state.get("board_cards", []))
        n_opp = game_state.get("n_opponents", 1)
        wr = win_rate(hole, board_cards=board, n_opponents=n_opp, trials=4000)
        if wr >= self.THRESHOLD:
            return RAISE_2X
        return FOLD


class RandomBot:
    def decide(self, game_state):
        return random.choice(ALL_ACTIONS)


class StaticWinRateBot:
    def decide(self, game_state):
        hole = to_treys_list(game_state["hole_cards"])
        board = to_treys_list(game_state.get("board_cards", []))
        n_opp = game_state.get("n_opponents", 1)
        wr = win_rate(hole, board_cards=board, n_opponents=n_opp, trials=4000)
        return action_from_win_rate(wr)
