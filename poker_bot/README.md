# Texas Hold'em Poker Bot

Poker bot for the William Gasarch research project at UMD.
Programs 1-4 rate hands at each street; Program 6 is a full stateful bot.

## Setup

```
pip install treys
```

## Usage

```
python play.py
```

Or use the library directly:

```python
from poker_bot.bot import PokerBot

bot = PokerBot()
action = bot.decide({
    "hole_cards": ["As", "Kh"],
    "board_cards": ["Ac", "7d", "2s"],
    "pot": 150,
    "stack": 1000,
    "to_call": 0,
    "opponent_id": "player_2",
    "facing_all_in": False,
    "n_opponents": 1,
})
print(action)
```

## Files

```
poker_bot/
  cards.py              -- treys card conversion
  evaluator.py          -- hand ranking wrapper
  monte_carlo.py        -- Monte Carlo win-rate estimator
  thresholds.py         -- maps win-rate to actions
  program1_preflop.py   -- preflop rater
  program2_flop.py      -- flop rater
  program3_turn.py      -- turn rater
  program4_river.py     -- river rater
  opponent_model.py     -- per-opponent stat tracking
  bot.py                -- Program 6 full bot
  baseline_bots.py      -- simple bots for testing
  tests/
    test_evaluator.py
    test_monte_carlo.py
    test_bot.py
```

## Running Tests

```
python -m pytest poker_bot/tests/ -v
```

## Thresholds

| Win Rate | Action |
|----------|--------|
| < 30% | Fold |
| 30-45% | Check |
| 45-60% | Raise 1/2 pot |
| 60-75% | Raise pot |
| 75-90% | Raise 1.5x pot |
| > 90% | Raise 2x pot |
