"""
bot.py — Program 6: Full stateful Texas Hold'em playing bot.

Decision pipeline each action:
  1. Monte Carlo win-rate (cards.py + monte_carlo.py)
  2. Baseline action (thresholds.py)
  3. Opponent model adjustment (opponent_model.py)
  4. Noise / unpredictability injection (~12% random one-tier deviation)
  5. Edge-case guards (stack size, all-in, etc.)
  6. Return final action string

GameState dict expected by decide():
  {
    "hole_cards":    ["As", "Kh"],          # our hole cards
    "board_cards":   ["Ac", "7d", "2s"],    # community cards seen so far
    "pot":           150,                   # current pot size
    "stack":         1000,                  # our remaining chips
    "to_call":       50,                    # chips needed to call (0 = can check)
    "opponent_id":   "player_2",            # ID of current main opponent
    "facing_all_in": False,                 # True if opponent pushed all-in
    "n_opponents":   1,                     # active opponents remaining
  }
"""

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

# Probability of injecting a one-tier noise deviation (up or down randomly)
NOISE_RATE = 0.12
# Number of Monte Carlo trials per decision
MC_TRIALS = 8000


class PokerBot:
    """Stateful poker bot for Program 6."""

    def __init__(self):
        self.opponent_registry = OpponentModelRegistry()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def decide(self, game_state):
        """Decide what action to take given the current game state.

        Args:
            game_state: dict described in module docstring

        Returns:
            str: action string (one of the 6 allowed actions)
        """
        hole_cards = game_state["hole_cards"]
        board_cards = game_state.get("board_cards", [])
        pot = game_state.get("pot", 0)
        stack = game_state.get("stack", 1000)
        to_call = game_state.get("to_call", 0)
        opponent_id = game_state.get("opponent_id", "unknown")
        facing_all_in = game_state.get("facing_all_in", False)
        n_opponents = game_state.get("n_opponents", 1)

        # 1. Compute win rate
        hole = to_treys_list(hole_cards)
        board = to_treys_list(board_cards) if board_cards else []
        wr = win_rate(hole, board_cards=board, n_opponents=n_opponents, trials=MC_TRIALS)

        # 2. Baseline action from win-rate thresholds
        action = action_from_win_rate(wr)

        # 3. Opponent model adjustment
        opp_model = self.opponent_registry.get(opponent_id)
        adj = opp_model.action_adjustment()
        if adj != 0:
            action = shift_action(action, adj)

        # 4. Inject noise (~12% of the time, shift ±1 tier)
        if random.random() < NOISE_RATE:
            action = shift_action(action, random.choice([-1, 1]))

        # 5. Edge-case guards
        action = self._apply_edge_cases(action, wr, pot, stack, to_call, facing_all_in)

        return action

    def record_opponent_action(self, opponent_id, action, context="general"):
        """Update opponent model with an observed action.

        Args:
            opponent_id: string player identifier
            action: 'fold', 'call', 'raise', or 'check'
            context: 'preflop', 'facing_raise', or 'general'
        """
        model = self.opponent_registry.get(opponent_id)
        if context == "preflop":
            model.record_preflop_action(action)
        elif context == "facing_raise":
            model.record_response_to_raise(folded=(action == "fold"))
        else:
            model.record_action(action)

    def new_match(self):
        """Reset opponent models for a fresh match."""
        self.opponent_registry.reset()

    # ------------------------------------------------------------------ #
    # Edge-case handling
    # ------------------------------------------------------------------ #

    def _apply_edge_cases(self, action, wr, pot, stack, to_call, facing_all_in):
        """Apply safety guards to the chosen action.

        Guards applied:
          - If facing all-in: call with wr > 0.45, fold otherwise
          - If raise cost exceeds stack: go all-in (return 'All-in')
          - If must pay to_call to check: upgrade Check → Raise 1/2 pot if strong
            enough, else Fold
          - Minimum sanity: never Fold when we can Check for free
        """
        # Facing an all-in push — only calling or folding makes sense
        if facing_all_in:
            return CHECK if wr >= 0.45 else FOLD  # "Check" here means call

        # Can't afford a sized raise → go all-in
        if action in (RAISE_HALF, RAISE_POT, RAISE_1_5X, RAISE_2X):
            raise_amount = self._raise_amount(action, pot)
            if raise_amount > stack:
                if wr >= 0.45:
                    return "All-in"
                else:
                    return FOLD if to_call > 0 else CHECK

        # There's a bet to call — Check means free; if action is Check/Fold
        # but there's a to_call, we must decide to call or fold
        if to_call > 0 and action == CHECK:
            # Willing to call only if pot odds justify it
            pot_odds = to_call / (pot + to_call)
            if wr > pot_odds + 0.05:  # small margin above break-even
                return CHECK  # "Check" interpreted as call by game engine
            return FOLD

        # Never fold when checking is free
        if to_call == 0 and action == FOLD:
            return CHECK

        return action

    def _raise_amount(self, action, pot):
        """Return chip cost of a raise action given current pot."""
        multipliers = {
            RAISE_HALF: 0.5,
            RAISE_POT: 1.0,
            RAISE_1_5X: 1.5,
            RAISE_2X: 2.0,
        }
        return int(pot * multipliers.get(action, 1.0))
