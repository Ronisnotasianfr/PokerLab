import random

from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate
from poker_bot.thresholds import (
    action_from_win_rate,
    shift_action,
    FOLD,
    CHECK,
    RAISE_HALF,
    RAISE_POT,
    RAISE_1_5X,
    RAISE_2X,
)
from poker_bot.opponent_model import OpponentModelRegistry

NOISE_RATE = 0.12
MC_TRIALS = 8000


class PokerBot:
    def __init__(self):
        self.opponent_registry = OpponentModelRegistry()

    def decide(self, game_state):
        hole_cards = game_state["hole_cards"]
        board_cards = game_state.get("board_cards", [])
        pot = game_state.get("pot", 0)
        stack = game_state.get("stack", 1000)
        to_call = game_state.get("to_call", 0)
        opponent_id = game_state.get("opponent_id", "unknown")
        facing_all_in = game_state.get("facing_all_in", False)
        n_opponents = game_state.get("n_opponents", 1)

        hole = to_treys_list(hole_cards)
        board = to_treys_list(board_cards) if board_cards else []
        wr = win_rate(hole, board_cards=board, n_opponents=n_opponents, trials=MC_TRIALS)

        action = action_from_win_rate(wr)

        opp_model = self.opponent_registry.get(opponent_id)
        adj = opp_model.action_adjustment()
        if adj != 0:
            action = shift_action(action, adj)

        if random.random() < NOISE_RATE:
            action = shift_action(action, random.choice([-1, 1]))

        action = self._apply_edge_cases(action, wr, pot, stack, to_call, facing_all_in)

        return action

    def record_opponent_action(self, opponent_id, action, context="general"):
        model = self.opponent_registry.get(opponent_id)
        if context == "preflop":
            model.record_preflop_action(action)
        elif context == "facing_raise":
            model.record_response_to_raise(folded=(action == "fold"))
        else:
            model.record_action(action)

    def new_match(self):
        self.opponent_registry.reset()

    def _apply_edge_cases(self, action, wr, pot, stack, to_call, facing_all_in):
        if facing_all_in:
            return CHECK if wr >= 0.45 else FOLD

        if action in (RAISE_HALF, RAISE_POT, RAISE_1_5X, RAISE_2X):
            raise_amount = self._raise_amount(action, pot)
            if raise_amount > stack:
                if wr >= 0.45:
                    return "All-in"
                else:
                    return FOLD if to_call > 0 else CHECK

        if to_call > 0 and action == CHECK:
            pot_odds = to_call / (pot + to_call)
            if wr > pot_odds + 0.05:
                return CHECK
            return FOLD

        if to_call == 0 and action == FOLD:
            return CHECK

        return action

    def _raise_amount(self, action, pot):
        multipliers = {
            RAISE_HALF: 0.5,
            RAISE_POT: 1.0,
            RAISE_1_5X: 1.5,
            RAISE_2X: 2.0,
        }
        return int(pot * multipliers.get(action, 1.0))
