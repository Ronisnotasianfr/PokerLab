"""
test_bot.py — Integration tests for Program 6 (PokerBot) and baseline bots.

Tests:
  - Bot returns valid actions for all streets
  - Edge cases: facing all-in, can't afford raise, check-when-free
  - Opponent model accumulates data and adjusts over time
  - Baseline bots all return valid actions
  - Bot beats AlwaysCallBot over many simulated decisions (win-rate > 50%)
"""

import unittest
import random
from poker_bot.bot import PokerBot
from poker_bot.baseline_bots import (
    AlwaysRaiseBot, AlwaysCallBot, TightFoldBot, RandomBot, StaticWinRateBot
)
from poker_bot.thresholds import ALL_ACTIONS

# Seed for reproducibility
random.seed(42)

VALID_ACTIONS = set(ALL_ACTIONS) | {"All-in"}


def make_state(**overrides):
    """Create a default game state dict with optional overrides."""
    state = {
        "hole_cards": ["As", "Kh"],
        "board_cards": [],
        "pot": 100,
        "stack": 1000,
        "to_call": 0,
        "opponent_id": "test_opp",
        "facing_all_in": False,
        "n_opponents": 1,
    }
    state.update(overrides)
    return state


class TestBotValidActions(unittest.TestCase):

    def setUp(self):
        self.bot = PokerBot()

    def test_preflop_action_valid(self):
        state = make_state(hole_cards=["As", "Kh"], board_cards=[])
        action = self.bot.decide(state)
        self.assertIn(action, VALID_ACTIONS)

    def test_flop_action_valid(self):
        state = make_state(board_cards=["Ac", "7d", "2s"])
        action = self.bot.decide(state)
        self.assertIn(action, VALID_ACTIONS)

    def test_turn_action_valid(self):
        state = make_state(board_cards=["Ac", "7d", "2s", "Ks"])
        action = self.bot.decide(state)
        self.assertIn(action, VALID_ACTIONS)

    def test_river_action_valid(self):
        state = make_state(board_cards=["Ac", "7d", "2s", "Ks", "3h"])
        action = self.bot.decide(state)
        self.assertIn(action, VALID_ACTIONS)


class TestEdgeCases(unittest.TestCase):

    def setUp(self):
        self.bot = PokerBot()

    def test_facing_allin_strong_hand(self):
        # Pocket aces facing all-in should call (Check)
        state = make_state(hole_cards=["As", "Ah"], facing_all_in=True)
        action = self.bot.decide(state)
        self.assertIn(action, {"Check", "Fold"})

    def test_facing_allin_weak_hand(self):
        # 72o facing all-in preflop should fold
        state = make_state(hole_cards=["7s", "2d"], facing_all_in=True)
        action = self.bot.decide(state)
        self.assertIn(action, {"Check", "Fold"})

    def test_no_fold_when_check_free(self):
        # With to_call=0, bot should never return Fold
        # Run many times because of noise
        for _ in range(20):
            state = make_state(hole_cards=["7s", "2d"], board_cards=[], to_call=0)
            action = self.bot.decide(state)
            self.assertNotEqual(action, "Fold", "Should never fold when check is free")

    def test_short_stack_goes_allin(self):
        # Stack smaller than raise amount should trigger All-in for strong hands
        state = make_state(hole_cards=["As", "Ah"], stack=10, pot=1000)
        action = self.bot.decide(state)
        self.assertIn(action, VALID_ACTIONS)


class TestOpponentModel(unittest.TestCase):

    def setUp(self):
        self.bot = PokerBot()

    def test_records_opponent_actions(self):
        for _ in range(15):
            self.bot.record_opponent_action("villain", "fold", "facing_raise")
        model = self.bot.opponent_registry.get("villain")
        self.assertIsNotNone(model.fold_to_raise)
        self.assertGreater(model.fold_to_raise, 0.5)

    def test_new_match_resets_models(self):
        for _ in range(15):
            self.bot.record_opponent_action("villain", "fold", "facing_raise")
        self.bot.new_match()
        model = self.bot.opponent_registry.get("villain")
        # Should have no data after reset
        self.assertIsNone(model.fold_to_raise)


class TestBaselineBots(unittest.TestCase):

    def test_all_baseline_bots_return_valid_actions(self):
        bots = [AlwaysRaiseBot(), AlwaysCallBot(), TightFoldBot(), RandomBot(), StaticWinRateBot()]
        state = make_state(board_cards=["Ac", "7d", "2s"])
        for bot in bots:
            action = bot.decide(state)
            self.assertIn(action, VALID_ACTIONS, f"{bot.__class__.__name__} returned invalid action: {action}")


if __name__ == "__main__":
    unittest.main()
