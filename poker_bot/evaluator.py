"""
evaluator.py — Thin wrapper around treys.Evaluator for clean hand ranking.

treys ranks: 1 (Royal Flush) to 7462 (worst hand). Lower = better.
"""

from treys import Evaluator

_evaluator = Evaluator()


def rank_hand(hole_cards, board_cards):
    """Evaluate the strength of a poker hand.

    Args:
        hole_cards: list of 2 treys card integers (player's hole cards)
        board_cards: list of 3-5 treys card integers (community cards)

    Returns:
        int: hand rank (1 = best, 7462 = worst)
    """
    return _evaluator.evaluate(board_cards, hole_cards)


def rank_class(rank):
    """Get the hand class (e.g. 'Full House') from a rank integer.

    Args:
        rank: integer rank from rank_hand()

    Returns:
        int: class integer (1=Straight Flush through 9=High Card)
    """
    return _evaluator.get_rank_class(rank)


def class_string(rank):
    """Get a human-readable string for a hand rank.

    Args:
        rank: integer rank from rank_hand()

    Returns:
        str: e.g. "Full House", "Two Pair"
    """
    return _evaluator.class_to_string(rank_class(rank))


def compare_hands(hole1, hole2, board):
    """Compare two hands on a given board.

    Returns:
        1 if hand1 wins, -1 if hand2 wins, 0 if tie
    """
    r1 = rank_hand(hole1, board)
    r2 = rank_hand(hole2, board)
    if r1 < r2:
        return 1
    elif r1 > r2:
        return -1
    return 0
