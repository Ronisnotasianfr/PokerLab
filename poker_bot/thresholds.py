"""
thresholds.py — Maps win-rate floats to betting actions.

Actions (from the assignment):
  - Fold
  - Check
  - Raise 1/2 pot
  - Raise pot
  - Raise 1.5x pot
  - Raise 2x pot

Threshold rationale:
  < 30%   → Fold: Statistically behind most opponent ranges. Throwing money
            away to continue.
  30-45%  → Check: Marginal hand. Worth seeing more cards for free but not
            worth investing chips.
  45-60%  → Raise 1/2 pot: Decent hand. Small bet extracts value from worse
            hands and defines the pot without overcommitting.
  60-75%  → Raise pot: Strong hand. Standard value bet that charges draws
            the wrong price to continue.
  75-90%  → Raise 1.5x pot: Very strong. Maximizes value extraction while
            still getting calls from second-best hands.
  > 90%   → Raise 2x pot: Near-nuts. Overbet for maximum value since we're
            rarely losing at showdown.
"""

# Action constants
FOLD = "Fold"
CHECK = "Check"
RAISE_HALF = "Raise 1/2 pot"
RAISE_POT = "Raise pot"
RAISE_1_5X = "Raise 1.5x pot"
RAISE_2X = "Raise 2x pot"

# Ordered list of all actions (weakest to strongest)
ALL_ACTIONS = [FOLD, CHECK, RAISE_HALF, RAISE_POT, RAISE_1_5X, RAISE_2X]

# Default thresholds: (min_win_rate, action)
DEFAULT_THRESHOLDS = [
    (0.90, RAISE_2X),
    (0.75, RAISE_1_5X),
    (0.60, RAISE_POT),
    (0.45, RAISE_HALF),
    (0.30, CHECK),
    (0.00, FOLD),
]


def action_from_win_rate(wr, thresholds=None):
    """Map a win-rate to a betting action.

    Args:
        wr: float win probability (0.0 to 1.0)
        thresholds: optional custom threshold list; defaults to DEFAULT_THRESHOLDS

    Returns:
        str: one of the 6 allowed actions
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    for cutoff, action in thresholds:
        if wr >= cutoff:
            return action
    return FOLD


def action_index(action):
    """Return the index of an action in ALL_ACTIONS (0=Fold, 5=Raise 2x)."""
    return ALL_ACTIONS.index(action)


def shift_action(action, steps):
    """Shift an action up or down by a number of steps.

    Used for opponent-model adjustments and noise injection.

    Args:
        action: current action string
        steps: positive = more aggressive, negative = more conservative

    Returns:
        str: adjusted action, clamped to valid range
    """
    idx = action_index(action)
    new_idx = max(0, min(len(ALL_ACTIONS) - 1, idx + steps))
    return ALL_ACTIONS[new_idx]
