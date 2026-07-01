"""
program1_preflop.py — Program 1: Preflop hand rating.

Input:  2 hole cards (strings like "As", "Kh")
Output: one of Fold / Check / Raise 1/2 pot / Raise pot / Raise 1.5x pot / Raise 2x pot

Uses Monte Carlo simulation (10,000 trials, heads-up) to estimate win rate,
then maps that to a betting action via the standard threshold table.
"""

from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate
from poker_bot.thresholds import action_from_win_rate


def rate_preflop(hole_cards, n_opponents=1, trials=10000):
    """Rate a preflop hand and return a betting action.

    Args:
        hole_cards: list of 2 card strings, e.g. ["As", "Kh"]
        n_opponents: number of opponents at the table (default 1)
        trials: Monte Carlo simulation trials

    Returns:
        str: recommended action
    """
    hole = to_treys_list(hole_cards)
    wr = win_rate(hole, board_cards=[], n_opponents=n_opponents, trials=trials)
    action = action_from_win_rate(wr)
    return action


if __name__ == "__main__":
    # Example usage
    cards = ["As", "Kh"]
    action = rate_preflop(cards)
    print(f"Hole cards: {cards}")
    print(f"Action: {action}")
