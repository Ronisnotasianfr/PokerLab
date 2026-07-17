from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate
from poker_bot.thresholds import action_from_win_rate


def rate_preflop(hole_cards, n_opponents=1, trials=10000):
    hole = to_treys_list(hole_cards)
    wr = win_rate(hole, board_cards=[], n_opponents=n_opponents, trials=trials)
    action = action_from_win_rate(wr)
    return action


if __name__ == "__main__":
    cards = ["As", "Kh"]
    action = rate_preflop(cards)
    print(f"Hole cards: {cards}")
    print(f"Action: {action}")
