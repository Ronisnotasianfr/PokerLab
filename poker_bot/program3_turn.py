from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate
from poker_bot.thresholds import action_from_win_rate


def rate_turn(hole_cards, board_cards, n_opponents=1, trials=10000):
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
