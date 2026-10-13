---
lesson: 21
level: 3
title: "Risk:Reward & Expectancy — The Math of Profitability"
day: 21
duration: "~13 min"
edition: "3.0 — story edition"
---

# Day 21 — Risk:Reward & Expectancy: The Math of Profitability

**🎬 Why the casino never worries about your winning streak**

Walk into any casino in the world and watch the roulette table. Bet on red or black, and
the casino pays you even money — a "fair" 1:1 bet. Except it isn't fair: the wheel also
has the green zero (and double-zero in America). Your true odds of winning are 18 out of
38 — **47.4%**, not 50%. That tiny 2.6% disadvantage, repeated thousands of times a night
across thousands of tables, is worth billions. The casino doesn't predict spins. It
doesn't need to. It has **positive expectancy** — a bet structure that pays less than the
true odds, repeated at volume.

Now the uncomfortable mirror: a trader with no edge is just a casino patron — except the
trader *chooses* their own odds on every bet. Today you learn to compute your odds, so
you stop being the roulette player and start being the house. One formula does it.

> 💬 **Ten seconds, big prize:** the casino wins only 52.6% of even-money roulette bets — barely better than a coin flip. So why does the house *always* end up ahead? Think before reading on — reply with your answer. Whatever you just realized… that single insight is worth more than every formula today. (And it's a formula.)

## What you'll learn
- R-multiples: the currency of trading
- The expectancy formula with worked numbers
- Breakeven win rates for different risk:reward ratios

## R-multiples: think in units of risk

Stop measuring trades in rupees. Measure them in **R** — multiples of what you risked:

- Risked ₹3,000, made ₹6,000 → **+2R**
- Risked ₹3,000, stopped out → **−1R**
- Risked ₹3,000, scratched at breakeven → **0R**

R normalizes everything: a ₹50,000 account and a ₹5,00,000 account taking the same +2R
trade had identical *decisions*. Journaling in R (Day 27) is how you compare your
performance across time and sizes honestly.

✅ Diagram already made: `charts/generated/L3-21-risk-reward.png`
(1R risk / 3R reward. Keep it in mind through the next section.)

## The expectancy formula

> **Expectancy = (Win% × Average Win) − (Loss% × Average Loss)** …all in R.

Positive = you have an edge. Negative = you're donating, no matter how often you win.

### Worked example A — the "accurate" trader
Wins 70%, avg win +0.8R (tiny profits) · losses 30%, −1R.
Expectancy = (0.70 × 0.8) − (0.30 × 1.0) = **+0.26R** — profitable, *barely*. One habit
change flips it negative. Fragile — this is the roulette player who wins often and still
feeds the house over time.

### Worked example B — the "lazy accuracy" trader
Wins only 40%, avg win +2.5R · losses 60%, −1R.
Expectancy = (0.40 × 2.5) − (0.60 × 1.0) = **+0.40R** — *more profitable than the 70%
winner.* This is the house. You don't get paid for being right; you get paid for
asymmetry — small controlled losses, large patient winners. The 40% trader loses *more
often* and makes *more money*.

### Worked example C — the breakeven illusion
Wins 55%, +0.9R · losses 45%, −1R → +0.045R → after costs ≈ **negative**. "Slightly
positive before costs" is a slow bleed. Costs are part of the formula in the real world —
the casino's edge *is* the cost layer.

## Breakeven win rates

| Risk:Reward | Breakeven win rate | Comfortable target |
|---|---|---|
| 1:1 | 50% (+ costs → ~53%) | 57%+ |
| 1:2 | 33% (~36%) | 42%+ |
| 1:3 | 25% (~28%) | 35%+ |

Read it twice: with 1:3 trades, **you can be wrong two times out of three and still make
money.** That's the house math. This is why Day 17's exits matter more than entries, and
why "being right" is the wrong goal.

## Using expectancy live

1. **Before a setup:** estimate honestly — "this pattern wins ~45%, pays ~2R" → check
   against the breakeven table. Clears with margin = tradeable.
2. **After 30 trades (your journal):** compute your real expectancy. Above +0.15R after
   costs = working edge; scale carefully. Below zero = stop trading live, backtest and
   fix (Day 28) before another rupee goes in.

> ⚠️ **Common beginner mistakes**
> 1. Chasing win rate as the goal — the 70%-win trader is one bad month from bust. Win
>    rate is a vanity metric; expectancy is the bank metric. (The casino wins 52.6% of
>    even-money bets and owns the building.)
> 2. Taking 1:0.5 trades ("it'll pop a little") — you need ~70% before costs just to
>    break even, and no beginner wins 70%.
> 3. Computing expectancy after 5 trades and declaring a system broken (or golden).
>    Thirty trades minimum before the number means anything.

## 🇮🇳 The Indian story: SEBI counted the casino's books

Here is the Indian house edge, measured by the regulator itself. SEBI's FY22–FY24 study
of the equity F&O segment found: **93% of individual traders lost money**, only about 1%
won more than ₹1 lakh in a year, and the winners' total profits (around ₹9,700 crore)
were dwarfed by the losers' losses (over ₹1.8 lakh crore) — with brokers and the
government collecting **~₹34,000 crore in transaction charges and taxes** over the period.
Strip the jargon: retail F&O in India IS a casino with negative expectancy, and the
house takes a cut of every spin via STT, exchange fees, GST, and stamp duty — the same
cost layer that turns +0.045R strategies negative in our formula. Your only escape from
being the patron is the one the casino can't tax: refusing bets whose expectancy is
negative. That is what this lesson's formula is for.

## Key takeaways
- Think in R. Every trade is a bet of 1R for some multiple back.
- Expectancy = (Win% × AvgWin) − (Loss% × AvgLoss). Positive after costs = edge. (The
  casino's edge is 2.6% per spin; yours needs to survive costs too.)
- You can lose 60% of the time at 1:2+ and still print money. Asymmetry pays, not accuracy.

## Quick check ✅
1. Win 45%, avg win +2R, loss 55%, avg loss −1R. Expectancy? Tradeable?
2. Why is a 65% win rate with +0.6R wins dangerous?
3. At 1:3 risk:reward, what win rate breaks even (ignoring costs)?

## Today's action step
Compute the expectancy of your last 20 trades (approximate R per trade is fine). Most
students discover their "good" strategy is breakeven and their "lucky" month was noise.
That discovery — however uncomfortable — is your first honest map of your real skill,
and it's the same math the casino runs every night.

Answers: 1 — (0.45×2) − (0.55×1) = +0.35R → tradeable ·
2 — (0.65×0.6) − (0.35×1) = +0.04R → costs likely flip it negative; extremely fragile ·
3 — 25%
