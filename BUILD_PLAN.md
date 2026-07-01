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

The assignment explicitly notes that Programs 1–4 ignore how other players bid. Program 6 is where that gap gets closed — and it's the actual differentiator in a live tournament against classmates. The plan below is built in layers:

1. **Baseline hand-strength signal** (Monte Carlo win-rate via `treys`) — required for Programs 1–4, correct and defensible on its own.
2. **Opponent modeling** — adjusts the baseline once live betting history exists.
3. **Controlled unpredictability** — prevents the bot itself from becoming an easy read.
4. **Defensive engineering** — no crashes, no dumb misplays, handles all edge cases.

Most classmates will likely submit static win-rate bots. Beating them is less about deeper math and more about not being predictable and not making mistakes.

---

## 3. Known Limitations

- Monte Carlo win-rate assumes opponents' unseen cards are uniformly random unless adjusted by the opponent model — it is not a full game-theory-optimal (Nash equilibrium) solver.
- Opponent modeling requires several hands of history before it's reliable; early-match play falls back to baseline thresholds.
- Designed to beat static/naive bots reliably; not guaranteed against another bot that also does serious opponent modeling and exploit play.
