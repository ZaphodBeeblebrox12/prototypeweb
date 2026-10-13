---
lesson: 20
level: 3
title: "Position Sizing (Interactive Calculator Day)"
day: 20
duration: "~15 min"
edition: "3.0 — story edition"
---

# Day 20 — Position Sizing: The Calculator Day ⭐

**🎬 The Turtles' secret weapon — it wasn't the entry, it was the size**

Back to the Turtle experiment from Day 8, because the part everyone misses is the part
that matters most. Richard Dennis didn't just hand the novices a trend-following entry
rule. He drilled into them a rigid position-sizing protocol:

- Risk a **fixed fraction of the account** on every trade (their system used roughly 2%
  per "unit" at reduced settings, and they pyramided in pre-defined steps).
- Size each market by its **volatility** — the more a market moved, the *smaller* the
  position, so that one "normal" adverse move cost the same across every instrument.
- Never, ever override the number because of a feeling.

The Turtles' edge was mostly just a moving-average breakout — a system so simple it's
published in books. Thousands of traders knew the entry rules. The Turtles made
$175 million because their *sizing* let them survive the long losing streaks that the
same system inevitably produces, while the confident amateurs running the same entries
with random sizes blew up on trade #23 of a 12-loss streak. Today you get the machine
that did it — three inputs, one formula, zero feelings.

> 💬 **The uncomfortable one:** the Turtles' formula would have told most of SEBI's 93% *not to take* most of their trades. Do you think you could handle a formula saying "no trade today" five days in a row? What would you honestly do on day six? Note your plan — we'll stress-test it today.

## What you'll learn
- The position sizing formula (all three versions)
- Worked examples: futures, stocks, options
- The reverse check: from size back to risk

## The master formula

> **Position size = Risk in ₹ ÷ (stop distance in points × value per point per unit)**

In plain language: *"How many units can I hold such that if my stop is hit, I lose
exactly my allowed risk?"*

Inputs, in order:
1. **Risk in ₹** = account × risk% (Day 19).
2. **Stop distance** = entry − stop, in points (Day 18).
3. **Value per point per unit** = lot size for futures; 1 per share for equities.

## Worked example 1 — Nifty futures

- Account ₹2,00,000 → 1.5% risk = **₹3,000**
- Entry 24,100, stop 24,040 → distance **60 points**
- Nifty lot 75 → value per point per lot = **₹75**

**Size = 3,000 ÷ (60 × 75) = 0.67 lots → you can't trade 0.67 lots. Options:**
- 1 lot = ₹4,500 risk (2.25%) — over budget, or
- **This trade doesn't fit your account.** Find a tighter-structure setup, or a
  smaller-lot instrument.

This is the moment beginners cheat ("it's just one lot, what's the harm?") and pros —
and Turtles — pass the trade. **Sizing discipline means sometimes not trading. That's a
feature.**

## Worked example 2 — Equity swing trade

- ₹2,00,000 → 2% risk = **₹4,000**
- Entry ₹520, stop ₹500 → distance **₹20**
- Shares: 4,000 ÷ 20 = **200 shares** → position value ₹1,04,000

The magic: you control a ₹1 lakh position while risking only ₹4,000 — the stop, not your
account size, sets your exposure.

## Worked example 3 — Options buying

- Risk budget ₹3,000 (1.5% of ₹2,00,000)
- Premium ₹120 → max 25 contracts by premium… but plan the exit at the *chart* stop,
  not zero. If the underlying hits your stop and the option is ~₹70, real loss = ₹50 ×
  lot (say 50) = ₹2,500 per contract → **1 contract**. Options sizing is always
  *worst-case aware* — premium can gap through your mental stop overnight.

## The reverse check (do this every time)

> **Expected loss if stopped = size × stop distance × value per point**
> Must be ≤ your risk budget. If over — reduce size or skip.

One line that has prevented more damage than every indicator ever built.

## Your calculator

- **Spreadsheet version:** the `position-size-calculator.csv` in this package — three
  input cells, outputs max size for 1/1.5/2%, live formulas. Takes 10 minutes to set up;
  use it daily.
- **Calculator:** your bonus pack includes `assets/templates/position-size-calculator.csv` —
  open it in Google Sheets, enter account, entry, stop, and it computes your size for
  1/1.5/2% instantly.

📊 No TradingView chart today — the math IS the picture.

> ⚠️ **Common beginner mistakes**
> 1. **Sizing by round numbers:** "2 lots feels right." Feelings don't have a formula;
>    the Turtles had a formula and novices beat professionals.
> 2. **Same size every trade regardless of stop distance** — a 30-point stop and a
>    120-point stop sized identically are wildly different risks.
> 3. **Averaging down to "fix" the size mistake** — adding to a loser changes the trade's
>    math and psychology. Forbidden. (Day 26 covers why.)

## 🇮🇳 The Indian story: the ₹2-lakh account and one BankNifty lot

Meet the most common trader in SEBI's data. Account: ₹2 lakh. Trade: **one lot of
BankNifty weekly options**, bought Monday, held into expiry. Lot size 15 (now 30+),
premium say ₹200 → ₹3,000–6,000 at risk per lot on a typical buy. Sounds small — until
the index gaps 1.5% on a Tuesday and the premium halves. Risk taken: 3–5% of account.
Loss streaks of 4–5 such trades: −20% of the account — inside two weeks, entirely
normal. Now apply the Turtle formula: 1.5% of ₹2 lakh = ₹3,000 risk budget; chart stop
on the underlying = 300 points; value per point ₹15 (lot 15) → 3,000 ÷ (300 × 15) = **0.67
lots — which rounds down to zero lots.** The formula would have skipped half the trades
that destroyed accounts in SEBI's study. That's the entire story of this lesson: the
math says "no" more often than your gut does, and every "no" is free.

## Key takeaways
- Size = risk ₹ ÷ (stop distance × value per point). Always round DOWN. Zero is a valid
  size. (The Turtles' real edge.)
- If no size fits the risk budget, the correct trade is skipping it.
- Reverse-check every order: expected stop-loss in ₹ ≤ risk budget.

## Quick check ✅
1. Account ₹3,00,000, risk 1.5%, entry 100, stop 97, value ₹10/point/share. Size?
2. Your computed size is 2.4 lots. What do you take — and what if 2 lots still exceeds budget?
3. Why is the reverse check non-negotiable?

## Today's action step
Build the 3-cell spreadsheet now (10 minutes, before tomorrow's lesson — the file is in
your package). Then run your three most recent trades through it: what size *should* you
have taken vs what you took. The gap is your leak. Fix the process, not the trades.

Answers: 1 — ₹4,500 ÷ (3 × 10) = 150 shares ·
2 — Take 2 lots; if still over budget, skip — size zero is a valid position ·
3 — It converts theory into a pre-order verification that catches rounding, lot-size and
correlation mistakes while they're still free
