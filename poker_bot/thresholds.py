FOLD = "Fold"
CHECK = "Check"
RAISE_HALF = "Raise 1/2 pot"
RAISE_POT = "Raise pot"
RAISE_1_5X = "Raise 1.5x pot"
RAISE_2X = "Raise 2x pot"

ALL_ACTIONS = [FOLD, CHECK, RAISE_HALF, RAISE_POT, RAISE_1_5X, RAISE_2X]

DEFAULT_THRESHOLDS = [
    (0.90, RAISE_2X),
    (0.75, RAISE_1_5X),
    (0.60, RAISE_POT),
    (0.45, RAISE_HALF),
    (0.30, CHECK),
    (0.00, FOLD),
]


def action_from_win_rate(wr, thresholds=None):
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    for cutoff, action in thresholds:
        if wr >= cutoff:
            return action
    return FOLD


def action_index(action):
    return ALL_ACTIONS.index(action)


def shift_action(action, steps):
    idx = action_index(action)
    new_idx = max(0, min(len(ALL_ACTIONS) - 1, idx + steps))
    return ALL_ACTIONS[new_idx]
