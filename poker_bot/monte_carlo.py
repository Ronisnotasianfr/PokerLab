"""
monte_carlo.py — Win-rate simulation engine using Monte Carlo sampling.

Given hole cards and any known board cards, estimates win probability
by simulating random opponent hands and remaining community cards.
"""

import random
from poker_bot.cards import get_deck
from poker_bot.evaluator import rank_hand


def win_rate(hole_cards, board_cards=None, n_opponents=1, trials=10000):
    """Estimate win probability via Monte Carlo simulation.

    Works for any street: preflop (0 board), flop (3), turn (4), river (5).

    Args:
        hole_cards: list of 2 treys card ints (our hand)
        board_cards: list of 0-5 treys card ints (known community cards)
        n_opponents: number of opponents to simulate (default 1 for heads-up)
        trials: number of simulation runs (more = slower but more accurate)

    Returns:
        float: estimated win probability between 0.0 and 1.0
    """
    if board_cards is None:
        board_cards = []

    known = list(hole_cards) + list(board_cards)
    remaining_deck = get_deck(exclude=known)
    cards_to_deal = 5 - len(board_cards)  # remaining community cards
    wins = 0
    ties = 0

    for _ in range(trials):
        # Shuffle and deal from the remaining deck
        sampled = random.sample(remaining_deck, cards_to_deal + 2 * n_opponents)

        # Complete the board
        sim_board = list(board_cards) + sampled[:cards_to_deal]

        # Evaluate our hand
        our_rank = rank_hand(list(hole_cards), sim_board)

        # Evaluate each opponent's hand
        best_opp_rank = 7463  # worse than worst possible
        idx = cards_to_deal
        for _ in range(n_opponents):
            opp_hole = [sampled[idx], sampled[idx + 1]]
            opp_rank = rank_hand(opp_hole, sim_board)
            if opp_rank < best_opp_rank:
                best_opp_rank = opp_rank
            idx += 2

        # Compare (lower rank = better hand in treys)
        if our_rank < best_opp_rank:
            wins += 1
        elif our_rank == best_opp_rank:
            ties += 1

    # Count ties as half a win
    return (wins + ties * 0.5) / trials
