import random
from poker_bot.cards import get_deck
from poker_bot.evaluator import rank_hand


def win_rate(hole_cards, board_cards=None, n_opponents=1, trials=10000):
    if board_cards is None:
        board_cards = []

    known = list(hole_cards) + list(board_cards)
    remaining_deck = get_deck(exclude=known)
    cards_to_deal = 5 - len(board_cards)
    wins = 0
    ties = 0

    for _ in range(trials):
        sampled = random.sample(remaining_deck, cards_to_deal + 2 * n_opponents)

        sim_board = list(board_cards) + sampled[:cards_to_deal]

        our_rank = rank_hand(list(hole_cards), sim_board)

        best_opp_rank = 7463
        idx = cards_to_deal
        for _ in range(n_opponents):
            opp_hole = [sampled[idx], sampled[idx + 1]]
            opp_rank = rank_hand(opp_hole, sim_board)
            if opp_rank < best_opp_rank:
                best_opp_rank = opp_rank
            idx += 2

        if our_rank < best_opp_rank:
            wins += 1
        elif our_rank == best_opp_rank:
            ties += 1

    return (wins + ties * 0.5) / trials
