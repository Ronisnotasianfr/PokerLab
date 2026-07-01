"""
program3_turn.py — Program 3: Turn hand rating.

Input:  2 hole cards + 4 board cards
Output: one of Fold / Check / Raise 1/2 pot / Raise pot / Raise 1.5x pot / Raise 2x pot
"""

from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate
from poker_bot.thresholds import action_from_win_rate


def rate_turn(hole_cards, board_cards, n_opponents=1, trials=10000):
    """Rate a hand on the turn and return a betting action.

    Args:
        hole_cards: list of 2 card strings, e.g. ["As", "Kh"]
        board_cards: list of 4 card strings (flop + turn)
        n_opponents: number of opponents at the table (default 1)
        trials: Monte Carlo simulation trials

    Returns:
        str: recommended action
    """
    if len(board_cards) != 4:
        raise ValueError(f"Turn requires exactly 4 board cards, got {len(board_cards)}")

    hole = to_treys_list(hole_cards)
    board = to_treys_list(board_cards)
    wr = win_rate(hole, board_cards=board, n_opponents=n_opponents, trials=trials)
    action = action_from_win_rate(wr)
    return action


if __name__ == "__main__":
    hole = ["As", "Kh"]
    board = ["Ac", "7d", "2s", "Ks"]
    action = rate_turn(hole, board)
    print(f"Hole: {hole}  Turn board: {board}")
    print(f"Action: {action}")
