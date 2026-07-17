from treys import Card, Deck

FULL_DECK = Deck().cards[:]
RANK_CHARS = "23456789TJQKA"
SUIT_CHARS = "shdc"


def to_treys(card_str):
    return Card.new(card_str)


def to_treys_list(card_strs):
    return [Card.new(c) for c in card_strs]


def from_treys(card_int):
    return Card.int_to_str(card_int)


def from_treys_list(card_ints):
    return [Card.int_to_str(c) for c in card_ints]


def get_deck(exclude=None):
    if exclude is None:
        return list(FULL_DECK)
    exclude_set = set(exclude)
    return [c for c in FULL_DECK if c not in exclude_set]


def pretty_print(card_ints):
    return Card.print_pretty_cards(card_ints)
