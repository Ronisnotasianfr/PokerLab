# Texas Hold'em Betting Bot — Build Plan
**Course:** William Gasarch — Research Project
**Language:** Python (using `treys` for hand evaluation)
**Goal:** Build Programs 1–6 as specified, with Program 6 designed to be competitive in a class tournament.

---

## 1. Assignment Recap

| # | Program | Input | Output |
|---|---------|-------|--------|
| 1 | Preflop rating | 2 hole cards | fold / check / raise ½ / raise 1x / raise 1.5x / raise 2x |
| 2 | Flop rating | 2 hole cards + 3 board cards | same action set |
| 3 | Turn rating | 2 hole cards + 4 board cards | same action set |
| 4 | River rating | 2 hole cards + 5 board cards | same action set |
| 5 | *(comment only — no code)* | — | — |
| 6 | Full playing bot | game state over time | plays full hands, competes vs. classmates |

Betting actions available: **Fold, Check, Raise ½ pot, Raise pot, Raise 1.5× pot, Raise 2× pot.**

---

## 2. Design Philosophy

The assignment explicitly notes that Programs 1–4 ignore how other players bid ("*We may add that later*"). Program 6 is where that gap gets closed — and it's the actual differentiator in a live tournament against classmates. The plan below is built in layers:

1. **Baseline hand-strength signal** (Monte Carlo win-rate via `treys`) — required for Programs 1–4, correct and defensible on its own.
2. **Opponent modeling** — adjusts the baseline once live betting history exists.
3. **Controlled unpredictability** — prevents the bot itself from becoming an easy read.
4. **Defensive engineering** — no crashes, no dumb misplays, handles all edge cases.

Most classmates will likely submit static win-rate bots. Beating them is less about deeper math and more about not being predictable and not making mistakes.

---

## 3. Environment Setup

```bash
pip install treys
```

Project structure:

```
poker_bot/
├── cards.py            # format conversion: our card repr <-> treys
├── evaluator.py         # thin wrapper around treys.Evaluator
├── monte_carlo.py        # win-rate simulation engine
├── thresholds.py         # win-rate -> action mapping
├── program1_preflop.py
├── program2_flop.py
├── program3_turn.py
├── program4_river.py
├── opponent_model.py      # per-opponent stat tracking
├── bot.py             # Program 6 — full stateful playing bot
├── baseline_bots.py       # simple bots for testing (always-raise, always-call, etc.)
├── tests/
│   ├── test_evaluator.py
│   ├── test_monte_carlo.py
│   └── test_bot.py
└── README.md            # writeup: thresholds, design rationale
```

---

## 4. Phase-by-Phase Build Plan

### Phase 1 — `treys` Wrapper (30–60 min)
- `cards.py`: convert between your own card representation (e.g. `"As"`, `"Td"`) and `treys.Card.new(...)` ints.
- `evaluator.py`: wrap `treys.Evaluator().evaluate(board, hand)`; expose a clean `rank_hand(hole, board) -> int` (lower = better, per treys convention).
- **Test:** confirm known hands rank correctly (royal flush beats quads beats full house, etc.).

### Phase 2 — Monte Carlo Win-Rate Engine (3–4 hrs)
- Core function: `win_rate(hole_cards, board_cards, n_opponents=1, trials=10000) -> float`
- Sample unseen cards for opponent hole cards + remaining board using `random.sample` on the deck minus known cards.
- Evaluate every simulated showdown with `treys`, tally win/tie/loss, return win probability.
- Works for 0, 3, 4, or 5 known board cards — this single function powers Programs 1–4.
- **Test:** pocket aces preflop should show ~85% win rate heads-up; 7-2 offsuit should show ~35%.

### Phase 3 — Baseline Threshold Mapping (1–2 hrs)
- `action_from_win_rate(win_rate: float) -> str` returning one of the 6 allowed actions.
- Example starting thresholds (tune later):

| Win rate | Action |
|---|---|
| < 30% | Fold |
| 30–45% | Check (if free) / Fold (if facing bet) |
| 45–60% | Raise ½ pot |
| 60–75% | Raise pot |
| 75–90% | Raise 1.5× pot |
| > 90% | Raise 2× pot |

- Document *why* these cutoffs were chosen in the README (Gasarch will want this reasoning, not just the numbers).

### Phase 4 — Programs 1–4 (1–2 hrs)
- Thin wrappers: call `win_rate(...)` with 0/3/4/5 board cards → `action_from_win_rate(...)`.
- Each program is ~10 lines once Phases 1–3 are solid.
- **Deliverable checkpoint:** these four satisfy the assignment's literal requirements even before Program 6 is built.

### Phase 5 — Opponent Modeling (4–6 hrs)
- `opponent_model.py`: per-opponent running stats across the match.
  - **VPIP** (voluntarily put money in pot %) — how loose/tight they are.
  - **Fold-to-raise %** — how bluffable they are.
  - **Raise frequency** — how aggressive they are.
- Adjust Phase 3 thresholds per opponent:
  - High fold-to-raise → bluff more (lower raise thresholds).
  - Low fold-to-raise (calling station) → bluff less, only bet for value.
- Require a minimum sample (~10–15 hands) before trusting a read; use baseline thresholds until then.

### Phase 6 — Controlled Unpredictability (2–3 hrs)
- With small probability (~10–15%), deviate one tier up or down from the "correct" threshold action.
- Keeps the bot from being perfectly predictable to an opponent (or grader) running it many times.
- Keep this rate low — it's a safeguard against exploitability, not a strategy in itself.

### Phase 7 — Program 6: Full Playing Bot (3–4 hrs)
- `bot.py`: stateful class tracking pot size, stack, current street, betting history, opponent stats.
- Each decision point: get win-rate (Phase 2) → baseline action (Phase 3) → opponent adjustment (Phase 5) → noise (Phase 6) → final action.
- **Edge cases to handle explicitly:**
  - Can't afford the sized raise → go all-in instead of crashing.
  - Opponent already folded / hand ends early.
  - Heads-up vs. multi-way pot sizing differences.
  - Facing an all-in.

### Phase 8 — Defensive Testing (3–4 hrs)
- `baseline_bots.py`: build simple reference bots — always-raise, always-call, tight-fold-heavy, random-action.
- Run your bot vs. each reference bot for many simulated hands; it should win decisively against all of them.
- Check for exploitability: does the bot show an obvious pattern within ~20 hands? If so, increase noise or tighten a threshold.
- Stress-test: short stack, all-in scenarios, minimum-raise edge cases.

### Phase 9 — Polish, README, Submission (1–2 hrs)
- Write `README.md` covering:
  - Rating system design and threshold justification (explicitly requested by the assignment).
  - How opponent modeling adjusts behavior.
  - Known limitations (does not compute exact game-theory-optimal play; heuristic + Monte Carlo based).
- Clean up code, add docstrings, remove dead code/print statements.

---

## 5. Time Estimate Summary

| Phase | Hours |
|---|---|
| 1. treys wrapper | 0.5–1 |
| 2. Monte Carlo engine | 3–4 |
| 3. Threshold mapping | 1–2 |
| 4. Programs 1–4 | 1–2 |
| 5. Opponent modeling | 4–6 |
| 6. Unpredictability | 2–3 |
| 7. Program 6 bot | 3–4 |
| 8. Defensive testing | 3–4 |
| 9. Polish & README | 1–2 |
| **Total** | **18–25 hrs** |

---

## 6. Known Limitations (be upfront about these in the README)

- Monte Carlo win-rate assumes opponents' unseen cards are uniformly random unless adjusted by the opponent model — it is not a full game-theory-optimal (Nash equilibrium) solver.
- Opponent modeling requires several hands of history before it's reliable; early-match play falls back to baseline thresholds.
- Designed to beat static/naive bots reliably; not guaranteed against another bot that also does serious opponent modeling and exploit play — that is a substantially deeper research problem (weeks, not hours).

---

## 7. Next Steps

1. Confirm the game-engine interface Gasarch's tournament uses (how bots receive state, how actions are submitted) — this shapes Phase 7 exactly.
2. Scaffold `cards.py` and `evaluator.py` first — everything else depends on these.
3. Build and test the Monte Carlo engine before writing any of Programs 1–4, since they're thin wrappers around it.
