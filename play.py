"""
play.py — Interactive CLI for the poker bot.

Run this script and it will walk you through a full hand,
asking for cards and game info at each street, then telling
you exactly what action to take.

Usage:
    python play.py
"""

from poker_bot.cards import to_treys_list
from poker_bot.monte_carlo import win_rate
from poker_bot.thresholds import action_from_win_rate
from poker_bot.bot import PokerBot

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

SUITS = {"s", "h", "d", "c"}
RANKS = {"2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"}

ACTION_DESCRIPTIONS = {
    "Fold":          "🚫  FOLD  — throw your hand away",
    "Check":         "✅  CHECK / CALL  — match the bet or check for free",
    "Raise 1/2 pot": "📈  RAISE ½ POT  — raise by half the pot",
    "Raise pot":     "📈  RAISE POT  — raise by the full pot",
    "Raise 1.5x pot":"📈  RAISE 1.5× POT  — raise 1.5× the pot",
    "Raise 2x pot":  "📈  RAISE 2× POT  — raise 2× the pot",
    "All-in":        "💥  ALL-IN  — shove everything",
}

DIVIDER = "─" * 50


def header(text):
    print(f"\n{DIVIDER}")
    print(f"  {text}")
    print(DIVIDER)


def parse_card(s):
    """Validate and normalise a card string like 'as' → 'As'."""
    s = s.strip()
    if len(s) < 2:
        return None
    rank = s[:-1].upper()
    suit = s[-1].lower()
    if rank not in RANKS or suit not in SUITS:
        return None
    return rank + suit


def input_cards(prompt, count):
    """Keep asking until we get exactly `count` valid unique cards."""
    while True:
        raw = input(f"  {prompt}: ").strip()
        parts = raw.split()
        if len(parts) != count:
            print(f"  ⚠  Please enter exactly {count} card(s) separated by spaces.")
            continue
        cards = [parse_card(p) for p in parts]
        if any(c is None for c in cards):
            print("  ⚠  Invalid card. Use format like: As Kh Td 2c 9s")
            continue
        if len(set(cards)) != count:
            print("  ⚠  Duplicate cards detected. Try again.")
            continue
        return cards


def input_int(prompt, default=None):
    """Ask for an integer; return default if blank."""
    while True:
        raw = input(f"  {prompt}: ").strip()
        if raw == "" and default is not None:
            return default
        try:
            return int(raw)
        except ValueError:
            print(f"  ⚠  Please enter a whole number.")


def input_yes(prompt):
    """Ask a yes/no question; return True for yes."""
    while True:
        raw = input(f"  {prompt} (y/n): ").strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  ⚠  Please type y or n.")


def show_recommendation(wr, action, pot, stack):
    print(f"\n  Win probability : {wr*100:.1f}%")
    print(f"  Pot size        : {pot} chips")
    print(f"  Your stack      : {stack} chips")
    print(f"\n  ► Recommended action:")
    print(f"    {ACTION_DESCRIPTIONS.get(action, action)}")
    if action in ("Raise 1/2 pot", "Raise pot", "Raise 1.5x pot", "Raise 2x pot"):
        multiplier = {"Raise 1/2 pot": 0.5, "Raise pot": 1.0,
                      "Raise 1.5x pot": 1.5, "Raise 2x pot": 2.0}[action]
        amount = int(pot * multiplier)
        actual = min(amount, stack)
        print(f"    Raise amount    : {actual} chips")


# ─────────────────────────────────────────────
# Main hand loop
# ─────────────────────────────────────────────

def play_hand(bot, session_stats):
    header("NEW HAND")

    # Stack and opponent
    stack = input_int("Your chip stack (press Enter for 1000)", default=1000)
    n_opp = input_int("Number of active opponents (press Enter for 1)", default=1)
    opponent_id = input("  Opponent name/ID (press Enter for 'villain'): ").strip() or "villain"

    board_cards = []

    # ── PREFLOP ──────────────────────────────
    header("PREFLOP")
    hole_cards = input_cards("Your 2 hole cards (e.g. As Kh)", 2)
    pot  = input_int("Current pot size (press Enter for 0)", default=0)
    to_call = input_int("Chips you need to call (press Enter for 0)", default=0)
    facing_allin = input_yes("Are you facing an all-in?")

    game_state = {
        "hole_cards": hole_cards, "board_cards": board_cards,
        "pot": pot, "stack": stack, "to_call": to_call,
        "opponent_id": opponent_id, "facing_all_in": facing_allin,
        "n_opponents": n_opp,
    }
    hole = to_treys_list(hole_cards)
    wr = win_rate(hole, board_cards=[], n_opponents=n_opp, trials=10000)
    action = bot.decide(game_state)
    show_recommendation(wr, action, pot, stack)

    # Record opponent action if we saw one
    if input_yes("\n  Did you see the opponent act before your turn?"):
        opp_act = input("  What did they do? (fold/call/raise/check): ").strip().lower()
        bot.record_opponent_action(opponent_id, opp_act, context="preflop")

    # ── FLOP ─────────────────────────────────
    if not input_yes("\n  Did you see a flop?"):
        print("\n  Hand over. Starting a new hand.\n")
        return

    header("FLOP")
    flop = input_cards("3 flop cards (e.g. Ac 7d 2s)", 3)
    board_cards = flop
    pot  = input_int("Current pot size", default=pot)
    to_call = input_int("Chips to call (0 if checking)", default=0)
    facing_allin = input_yes("Facing an all-in?")

    game_state.update({"board_cards": board_cards, "pot": pot,
                        "to_call": to_call, "facing_all_in": facing_allin})
    board = to_treys_list(board_cards)
    wr = win_rate(hole, board_cards=board, n_opponents=n_opp, trials=10000)
    action = bot.decide(game_state)
    show_recommendation(wr, action, pot, stack)

    if input_yes("\n  Did you see the opponent act?"):
        opp_act = input("  What did they do? (fold/call/raise/check): ").strip().lower()
        bot.record_opponent_action(opponent_id, opp_act,
            context="facing_raise" if to_call > 0 else "general")

    # ── TURN ─────────────────────────────────
    if not input_yes("\n  Did you see a turn card?"):
        print("\n  Hand over.\n")
        return

    header("TURN")
    turn = input_cards("Turn card (e.g. Ks)", 1)
    board_cards = flop + turn
    pot  = input_int("Current pot size", default=pot)
    to_call = input_int("Chips to call (0 if checking)", default=0)
    facing_allin = input_yes("Facing an all-in?")

    game_state.update({"board_cards": board_cards, "pot": pot,
                        "to_call": to_call, "facing_all_in": facing_allin})
    board = to_treys_list(board_cards)
    wr = win_rate(hole, board_cards=board, n_opponents=n_opp, trials=10000)
    action = bot.decide(game_state)
    show_recommendation(wr, action, pot, stack)

    if input_yes("\n  Did you see the opponent act?"):
        opp_act = input("  What did they do? (fold/call/raise/check): ").strip().lower()
        bot.record_opponent_action(opponent_id, opp_act,
            context="facing_raise" if to_call > 0 else "general")

    # ── RIVER ────────────────────────────────
    if not input_yes("\n  Did you see a river card?"):
        print("\n  Hand over.\n")
        return

    header("RIVER")
    river = input_cards("River card (e.g. 3h)", 1)
    board_cards = flop + turn + river
    pot  = input_int("Current pot size", default=pot)
    to_call = input_int("Chips to call (0 if checking)", default=0)
    facing_allin = input_yes("Facing an all-in?")

    game_state.update({"board_cards": board_cards, "pot": pot,
                        "to_call": to_call, "facing_all_in": facing_allin})
    board = to_treys_list(board_cards)
    wr = win_rate(hole, board_cards=board, n_opponents=n_opp, trials=10000)
    action = bot.decide(game_state)
    show_recommendation(wr, action, pot, stack)

    if input_yes("\n  Did you see the opponent act?"):
        opp_act = input("  What did they do? (fold/call/raise/check): ").strip().lower()
        bot.record_opponent_action(opponent_id, opp_act,
            context="facing_raise" if to_call > 0 else "general")

    print(f"\n  Hand complete. Opponent model updated for '{opponent_id}'.")
    session_stats["hands"] += 1


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def main():
    print("\n" + "═" * 50)
    print("   POKER BOT — Interactive Advisor")
    print("   Enter your cards and game info.")
    print("   The bot tells you what to do.")
    print("═" * 50)
    print("\n  Card format examples:")
    print("    As = Ace of Spades    Kh = King of Hearts")
    print("    Td = Ten of Diamonds  2c = 2 of Clubs")
    print("  Ranks: 2 3 4 5 6 7 8 9 T J Q K A")
    print("  Suits: s h d c")

    bot = PokerBot()
    session_stats = {"hands": 0}

    while True:
        try:
            play_hand(bot, session_stats)
            print(f"\n  Session hands played: {session_stats['hands']}")
            if not input_yes("  Play another hand?"):
                print("\n  Good luck at the tables. 🃏\n")
                break
        except KeyboardInterrupt:
            print("\n\n  Exiting. Good luck! 🃏\n")
            break


if __name__ == "__main__":
    main()
