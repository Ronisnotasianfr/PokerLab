"""
program4_river.py — Program 4: River hand rating.

Input:  2 hole cards + 5 board cards (full board known)
Output: one of Fold / Check / Raise 1/2 pot / Raise pot / Raise 1.5x pot / Raise 2x pot

Note: On the river the exact win-rate is computable but we still use Monte Carlo
for code consistency. With 5 board cards, Monte Carlo only simulates opponent
hole cards (no board uncertainty), so it converges quickly and is accurate.
"""

from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate
from poker_bot.thresholds import action_from_win_rate


def rate_river(hole_cards, board_cards, n_opponents=1, trials=10000):
    """Rate a hand on the river and return a betting action.

    Args:
        hole_cards: list of 2 card strings, e.g. ["As", "Kh"]
        board_cards: list of 5 card strings (full board)
        n_opponents: number of opponents at the table (default 1)
        trials: Monte Carlo simulation trials

    Returns:
        str: recommended action
    """
    if len(board_cards) != 5:
        raise ValueError(f"River requires exactly 5 board cards, got {len(board_cards)}")

    hole = to_treys_list(hole_cards)
    board = to_treys_list(board_cards)
    wr = win_rate(hole, board_cards=board, n_opponents=n_opponents, trials=trials)
    action = action_from_win_rate(wr)
    return action


if __name__ == "__main__":
    hole = ["As", "Kh"]
    board = ["Ac", "7d", "2s", "Ks", "3h"]
    action = rate_river(hole, board)
    print(f"Hole: {hole}  River board: {board}")
    print(f"Action: {action}")
