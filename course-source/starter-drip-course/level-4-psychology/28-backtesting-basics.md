---
lesson: 28
level: 4
title: "Backtesting Basics"
day: 28
duration: "~14 min"
edition: "3.0 — story edition"
---

# Day 28 — Backtesting Basics

**🎬 The models were right. The data was wrong.**

We met Long-Term Capital Management on Day 19 — the fund with two Nobel laureates, ~40%
annual returns, and leverage near 25×. Here's the part of the story that belongs to today:
LTCM's models were built on historical data, and their core assumption was that markets
in the 1990s behaved like the data said markets had *always* behaved. Correlations,
volatility, spread relationships — the models "knew" their normal ranges from history.

Then Russia defaulted in August 1998 — an event that wasn't in the data in that form —
and every relationship the fund traded blew past its historical range *simultaneously*.
Positions that had "never" moved together moved together. The models hadn't made an
arithmetic error; they'd made a *sampling* error. They had memorized one regime and
called it the truth.

This is the deepest lesson in backtesting: a test doesn't prove your system works. It
proves your system worked *in the specific past you tested* — IF you ran the test
honestly. Today you learn to run it honestly, and to extract the one thing a backtest
can actually give you: evidence, not certainty.

> 💬 **Hold that thought:** LTCM's models were built by Nobel Prize winners using the best data money could buy — and they still got fooled by their own backtest. So here's the question: if the smartest team in history got fooled, what chance does an untested *feeling* have? Note your answer — then learn the protocol they skipped.

## What you'll learn
- Manual backtesting: the 50–100 trade protocol
- The statistics to collect and the thresholds that matter
- The four biases that fake results (and how to neutralize each)

## Why backtest at all?

Because 30 live trades is anecdote; 100 tested trades is evidence. Backtesting answers:
*does this setup actually have positive expectancy — in this instrument, on this
timeframe — before I risk money discovering the answer live?*

## The manual backtesting protocol (no code needed)

1. **Define the setup precisely — in writing, before touching a chart.** Entry rule,
   stop rule, target rule. If any rule contains the word "maybe," stop. Example:
   - *Setup: pullback to 20 EMA in daily uptrend (price > 200 MA, 50 rising)*
   - *Entry: bullish engulfing at/below 20 EMA, buy its high*
   - *Stop: below pullback low · Target: prior swing high, minimum 2R or skip*
2. **Open a chart, hide recent data.** Scroll to a random point 1–2 years back.
3. **Walk forward candle by candle.** At each candle ask only: "did my rules fire here?"
   If yes — log the trade, mark entry/stop/target, then *let the chart play out* and
   record the result in R. **Never peek ahead** before the trade is logged.
4. **Repeat to 50–100 samples** — minimum 50; 100 is meaningfully better. Spread across
   market phases: at least one trend and one range. (Testing only a bull run gives you
   a bull-market system — the LTCM error at small scale.)
5. **Compute:** win rate, average R win/loss, expectancy, profit factor, max consecutive
   losses (compare with your Day 19 risk — can you survive your own system's worst streak?).

## The go/no-go thresholds

| Result | Verdict |
|---|---|
| Expectancy > +0.15R after estimated costs, profit factor > 1.5 | Trade it small live + forward test |
| Expectancy 0 to +0.15R | Marginal — costs/execution decide; refine or skip |
| Expectancy < 0 | Thank the test — it just saved you real money |

**Forward test before scaling:** paper-trade or minimum-size the validated setup for
10–20 live trades. Backtests don't include your slippage, your missed fills, your 3 AM
self. Live results within shouting distance of the backtest → graduate the size slowly
(25% steps), never in leaps.

## The four biases that fake results

1. **Hindsight bias:** knowing how history went, you subconsciously take trades you
   "would have seen." *Neutralizer:* strict candle-by-candle walking, decisions logged
   *before* scrolling forward.
2. **Curve-fitting (overfitting):** keep tweaking rules until the past looks perfect. A
   10-rule system tuned on 50 trades has memorized noise — LTCM's data regime error in
   miniature. *Neutralizer:* rules frozen before testing; any tweak → re-test from
   scratch. **3–5 rules maximum.**
3. **Sample bias:** testing only in one market phase. *Neutralizer:* force coverage
   across at least one trend and one range.
4. **Survivorship bias in instruments:** testing only on the stocks that "worked."
   *Neutralizer:* test the setup on everything your watchlist rule produces.

📊 CHART NEEDED: `charts/L4-28-backtest-sample.png`
INSTRUMENT / TIMEFRAME: Nifty 50 · daily · 12 months
MUST SHOW:
  - 15–20 marked sample trades from the pullback protocol (green = win, red = loss)
    across mixed market conditions
  - A text box: "Win rate __ · Avg win __R · Avg loss __R · Expectancy __R"

> ⚠️ **Common beginner mistakes**
> 1. Testing with fuzzy rules and calling it intuition. Intuition is compressed
>    experience; you don't have the experience yet — that's the point of the test.
> 2. Stopping at 15 trades because "the pattern is obvious." Fifteen trades is a
>    weekend's variance, not evidence. (LTCM had four YEARS of evidence. It wasn't
>    enough, and they were the smartest team alive. Test honestly, size humbly.)
> 3. Deleting the losers from the log "because the setup wasn't clean." The unclean
>    cases are the strategy too — if you can't identify them in advance, they count.

## 🇮🇳 The Indian story: the strategy that only knew a bull market

Between April 2020 and late 2021, nearly everything worked in India: buying every Nifty
dip, buying every breakout, buying every 20-EMA touch on high-beta midcaps. A trader who
backtested a momentum system on 2020–2021 data alone would have seen a golden system —
and then watched it get shredded in 2022's sideways chop and -17% drawdown. India's
market changes regimes violently: 2008 (−60%), 2011 (range), 2013 (currency crisis),
2018 (√) midcap crash, 2020 (V-shape), 2022 (global tightening), 2024 (election-day
crash, then melt-up). That's exactly LTCM's sample-bias lesson at home: a system trained
on one regime of the Indian market is a bull-market system wearing a lab coat. Your
50-sample protocol must span at least one trend AND one range — in India, that means
data across different years, not different weeks.

## Key takeaways
- Rules frozen in writing → 50–100 walked-forward samples → compute expectancy.
  A backtest gives evidence for one regime, never certainty for all regimes.
- Threshold: > +0.15R and profit factor > 1.5 after costs, or don't trade it.
- Four biases: hindsight, curve-fitting, sample, survivorship — each has one
  neutralizer: process beats cleverness.

## Quick check ✅
1. Why must rules be written before the test begins?
2. What's the minimum sample and why isn't 20 trades enough?
3. Your backtest shows +0.3R expectancy. What's the next step before full size?

## Today's action step
Run the protocol on the pullback setup from this course, on Nifty daily, for 50 samples.
Two to three focused hours. When you're done you'll hold something most retail traders
never will: your own, honest, positive-expectancy number — and the humility about its
limits that LTCM's Nobel committee never had. Tomorrow we assemble everything into your
playbook.

Answers: 1 — Otherwise hindsight edits the rules mid-test and the result is fiction ·
2 — 50 minimum; 20 samples can't distinguish edge from variance — one hot streak
contaminates the stats · 3 — Forward test at minimum size for 10–20 live trades, then
scale in 25% steps
