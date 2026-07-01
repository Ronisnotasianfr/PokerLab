"""
baseline_bots.py — Simple reference bots for testing Program 6.

Each bot implements a decide(game_state) -> str interface identical to PokerBot,
making it easy to run simulated matchups.

Bots:
  - AlwaysRaiseBot   — always raises 2x pot
  - AlwaysCallBot    — always calls (returns Check)
  - TightFoldBot     — folds unless it has a very strong hand (wr > 0.80)
  - RandomBot        — picks a random action every time
  - StaticWinRateBot — basic win-rate bot with no opponent modeling or noise
"""

import random

from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate
from poker_bot.thresholds import action_from_win_rate, ALL_ACTIONS, FOLD, CHECK, RAISE_2X


class AlwaysRaiseBot:
    """Always raises 2x pot. Maximally aggressive."""

    def decide(self, game_state):
        return RAISE_2X


class AlwaysCallBot:
    """Always calls (never folds, never raises). Passive calling station."""

    def decide(self, game_state):
        return CHECK  # interpreted as call by game engine


class TightFoldBot:
    """Only raises when win rate is very high; folds otherwise."""

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
    """Picks a uniformly random action each decision."""

    def decide(self, game_state):
        return random.choice(ALL_ACTIONS)


class StaticWinRateBot:
    """Vanilla Monte Carlo win-rate bot — no opponent modeling, no noise.

    Represents a typical classmate submission.
    """

    def decide(self, game_state):
        hole = to_treys_list(game_state["hole_cards"])
        board = to_treys_list(game_state.get("board_cards", []))
        n_opp = game_state.get("n_opponents", 1)
        wr = win_rate(hole, board_cards=board, n_opponents=n_opp, trials=4000)
        return action_from_win_rate(wr)
