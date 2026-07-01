# Texas Hold'em Poker Bot

A Python-based poker bot built for the William Gasarch research project at UMD. Programs 1–4 rate hands at each street; Program 6 is a full stateful tournament bot.

## Project Structure

```
poker_bot/
├── cards.py              # treys card format conversion
├── evaluator.py          # hand ranking wrapper
├── monte_carlo.py        # win-rate simulation engine
├── thresholds.py         # win-rate → action mapping
├── program1_preflop.py   # Program 1
├── program2_flop.py      # Program 2
├── program3_turn.py      # Program 3
├── program4_river.py     # Program 4
├── opponent_model.py     # per-opponent stat tracking
├── bot.py                # Program 6 — full bot
├── baseline_bots.py      # reference bots for testing
└── tests/
    ├── test_evaluator.py
    ├── test_monte_carlo.py
    └── test_bot.py
```

## Setup

```bash
pip install treys
```

## Quick Start

### Programs 1–4 (hand raters)

```python
from poker_bot.program1_preflop import rate_preflop
from poker_bot.program2_flop import rate_flop
from poker_bot.program3_turn import rate_turn
from poker_bot.program4_river import rate_river

# Program 1
print(rate_preflop(["As", "Kh"]))        # → "Raise 1.5x pot"

# Program 2
print(rate_flop(["As", "Kh"], ["Ac", "7d", "2s"]))   # → "Raise 2x pot"

# Program 3
print(rate_turn(["As", "Kh"], ["Ac", "7d", "2s", "Ks"]))

# Program 4
print(rate_river(["As", "Kh"], ["Ac", "7d", "2s", "Ks", "3h"]))
```

### Program 6 (full bot)

```python
from poker_bot.bot import PokerBot

bot = PokerBot()

game_state = {
    "hole_cards":    ["As", "Kh"],
    "board_cards":   ["Ac", "7d", "2s"],
    "pot":           150,
    "stack":         1000,
    "to_call":       0,
    "opponent_id":   "player_2",
    "facing_all_in": False,
    "n_opponents":   1,
}
action = bot.decide(game_state)
print(action)

# After observing opponent actions, record them:
bot.record_opponent_action("player_2", "fold", context="facing_raise")
```

## Rating System Design

### Win-Rate Engine (Programs 1–4)

All four programs share one Monte Carlo engine (`monte_carlo.py`):

1. Take the known cards (hole + board) out of the deck.
2. Randomly deal opponent hole cards + remaining community cards from what's left.
3. Evaluate all hands with `treys.Evaluator`.
4. Repeat 10,000 times; return `(wins + 0.5 * ties) / trials`.

This approach is correct for all streets with zero extra complexity — preflop samples both opponent holes and all 5 community cards; the river samples only opponent holes.

### Threshold Justification

| Win Rate | Action        | Rationale |
|----------|---------------|-----------|
| < 30%    | Fold          | Statistically behind most ranges; continuing costs expected value |
| 30–45%   | Check         | Marginal; worth free cards but not worth investing |
| 45–60%   | Raise ½ pot   | Decent hand; small bet extracts value and defines pot |
| 60–75%   | Raise pot     | Strong; charges draws the wrong price to continue |
| 75–90%   | Raise 1.5× pot | Very strong; maximize extraction while still getting calls |
| > 90%    | Raise 2× pot  | Near-nuts; overbet for maximum value |

### Program 6 Enhancements

Beyond Programs 1–4, the full bot adds:

1. **Opponent Modeling** — Tracks VPIP, fold-to-raise %, and raise frequency per opponent. After 10+ hands of data, adjusts thresholds: raise more against high-fold opponents, be more conservative against calling stations.

2. **Controlled Unpredictability** — With 12% probability, deviates one tier up or down from the computed action. Prevents the bot from becoming a predictable read over many hands.

3. **Edge-Case Guards**:
   - Cannot afford raise → all-in if strong, else fold/check
   - Facing all-in → call if win-rate > 45% (pot-odds justified), else fold
   - Never fold when checking is free (minimum sanity check)

## Running Tests

```bash
# From the PokerHands directory:
python -m pytest poker_bot/tests/ -v
```

## Known Limitations

- Monte Carlo assumes unseen opponent cards are uniformly random (not a Nash equilibrium solver). The opponent model partially corrects this by adjusting thresholds based on observed behavior, but it is still a heuristic, not a GTO solution.
- Opponent modeling requires ~10 hands before it activates; play falls back to baseline thresholds in early hands.
- Designed to beat static/naive bots reliably. Against another serious opponent-modeling bot, outcomes are less predictable — that's a substantially deeper research problem.

## Program 5 — Note (No Code)

Program 5 is intentionally left as a comment. The assignment marks it as a design exercise or commentary without a code deliverable. The relevant insight: Programs 1–4 treat opponents as random card holders. Program 6 begins to model them as agents with behavioral patterns — that's the conceptual bridge Program 5 describes without implementing.
