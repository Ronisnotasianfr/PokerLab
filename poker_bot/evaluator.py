from treys import Evaluator

_evaluator = Evaluator()


def rank_hand(hole_cards, board_cards):
    return _evaluator.evaluate(board_cards, hole_cards)


def rank_class(rank):
    return _evaluator.get_rank_class(rank)


def class_string(rank):
    return _evaluator.class_to_string(rank_class(rank))


def compare_hands(hole1, hole2, board):
    r1 = rank_hand(hole1, board)
    r2 = rank_hand(hole2, board)
    if r1 < r2:
        return 1
    elif r1 > r2:
        return -1
    return 0
