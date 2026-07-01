"""
cards.py — Format conversion between human-readable card strings and treys integer format.

Card format: Rank + Suit
  Ranks: 2,3,4,5,6,7,8,9,T,J,Q,K,A
  Suits: s(spades), h(hearts), d(diamonds), c(clubs)
  Examples: "As" = Ace of spades, "Td" = Ten of diamonds
"""

from treys import Card, Deck


# Full 52-card deck as treys integers (generated once at import time)
FULL_DECK = Deck().cards[:]

# String representations for the full deck
RANK_CHARS = "23456789TJQKA"
SUIT_CHARS = "shdc"


def to_treys(card_str):
    """Convert a human-readable card string to a treys integer.

    Args:
        card_str: e.g. "As", "Td", "2c"

    Returns:
        treys integer representation of the card
    """
    return Card.new(card_str)


def to_treys_list(card_strs):
    """Convert a list of card strings to treys integers.

    Args:
        card_strs: list of strings like ["As", "Kh"]

    Returns:
        list of treys integers
    """
    return [Card.new(c) for c in card_strs]


def from_treys(card_int):
    """Convert a treys integer back to a human-readable string.

    Args:
        card_int: treys integer

    Returns:
        string like "As", "Td"
    """
    return Card.int_to_str(card_int)


def from_treys_list(card_ints):
    """Convert a list of treys integers to human-readable strings."""
    return [Card.int_to_str(c) for c in card_ints]


def get_deck(exclude=None):
    """Return the full deck minus any excluded cards.

    Args:
        exclude: list of treys integers to remove from the deck

    Returns:
        list of treys integers representing the remaining deck
    """
    if exclude is None:
        return list(FULL_DECK)
    exclude_set = set(exclude)
    return [c for c in FULL_DECK if c not in exclude_set]


def pretty_print(card_ints):
    """Pretty-print a list of treys card integers."""
    return Card.print_pretty_cards(card_ints)
