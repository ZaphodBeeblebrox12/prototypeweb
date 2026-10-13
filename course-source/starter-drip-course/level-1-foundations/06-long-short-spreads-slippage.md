---
lesson: 6
level: 1
title: "Long vs Short, Spreads & Slippage"
day: 6
duration: "~10 min"
edition: "3.0 — story edition"
---

# Day 6 — Long vs Short, Spreads & Slippage

**🎬 The 15 minutes that broke currency brokers**

On January 15, 2015, at 9:30 AM Swiss time, the Swiss National Bank — without warning — cancelled its three-year-old promise to keep the Swiss franc from rising too fast against the euro. In roughly **15
minutes**, the franc surged 30–40%. Within days, **Alpari UK was bankrupt** and
FXCM — the largest US retail forex broker — needed a **$225 million emergency loan** to
survive. What killed them wasn't the direction — it was the **plumbing**: during those
minutes, bid-ask spreads on EUR/CHF blew from fractions of a pip to several *dollars*
wide, and stop losses filled miles from their triggers. Slippage did the rest.

The SNB shock is the perfect story for today, because it contains all three of our
subjects: making money in both directions (franc *buyers* made fortunes that day),
the spread, and slippage — the two hidden costs that quietly tax every trade you place.

> 💬 **Have you ever…** bought a stock, watched it go UP, and *still* lost money on the trade? If yes, today's lesson will feel like someone reading your diary. If no — it's coming for you eventually, and the Swiss franc story is why. What's your guess: what invisible thing ate that profit?

## What you'll learn
- Going long vs going short
- The bid-ask spread (and how it blew out on January 15, 2015)
- Slippage — and when it hurts most

## Long vs short

**Going long** = buying first, selling later. Profit when price rises.
*(Buy at 100, sell at 110 → +10.)*

**Going short** = selling first, buying back later. Profit when price falls.
*(Sell at 100, buy back at 90 → +10.)*

Shorting feels strange to beginners ("how can I sell what I don't own?"), but in futures
and intraday equity your broker facilitates it — you settle the difference in cash.
And the franc story shows why it matters: while EUR/CHF longs were being destroyed,
traders short EUR/CHF — or long CHF — made some of the fastest money in currency history.
> **Key insight:** long and short are symmetric. Professionals are as comfortable
> shorting as buying.

## The bid-ask spread

At any moment there are two prices:

- **Bid** — the highest price a buyer is currently offering
- **Ask** — the lowest price a seller is currently accepting

The gap = the **spread**, and you always pay it: buyers lift the ask, sellers hit the bid.

| | Bid | Ask | Spread |
|---|---|---|---|
| Liquid stock (e.g., Reliance) | 500.00 | 500.05 | ₹0.05 (tiny) |
| Illiquid stock | 100.00 | 101.20 | ₹1.20 (1.2%!) |
| EUR/CHF, Jan 15 2015, ~9:31 AM | "who knows" | "who knows" | effectively unmeasurable |

On liquid instruments the toll is negligible. On illiquid ones — and in panics — the
spread alone can exceed your entire expected profit.

## Slippage

**Slippage** = the difference between the price you *expected* and the price you *got*:

- **Market orders** in fast markets (you take whatever's left in the queue)
- **Gaps** — price jumps over your level between click and fill
- **News shocks** — liquidity vanishes for seconds (the SNB morning)

> Slippage is usually tiny — until the one day it isn't. Stops don't guarantee prices;
> they guarantee *an exit*, at whatever the market gives. On January 15, 2015, many
> stop losses on CHF pairs filled 10–20% away from their triggers. The stops worked
> exactly as designed. The design has limits.

## The practical rules

1. Trade liquid instruments only — check average daily volume first.
2. Limit orders for entries (you choose your price).
3. Size positions so a slippy stop *hurts, never kills*.
4. No new trades into major news events — the SNB taught the world that lesson free of charge.

📊 CHART NEEDED: `charts/L1-06-spread-slippage.png`
INSTRUMENT / TIMEFRAME: Two 1-minute panels — one very liquid stock, one illiquid stock
MUST SHOW:
  - Bid/ask levels marked on both
  - Liquid panel: tight spread, "≈ 0.01%"
  - Illiquid panel: wide spread, "≈ 1.2% — profit gone before you start"

## 🇮🇳 The Indian story: Yes Bank's circuit-locked exits

India's own slippage machine is the **price circuit**. When Yes Bank collapsed in March
2020, the stock hit its lower circuit day after day — meaning the price was *locked* at
the day's limit with a queue of sellers and almost no buyers. Stop losses were useless:
you couldn't exit at any price, because the exchange wouldn't let the price fall further
that session. Sellers watched helplessly as the stock ground from ₹30 to ₹20 to ₹12 over
circuit-locked sessions. That's slippage in its purest Indian form — the market not
filling you at your price, but refusing to fill you at *any* price. Liquidity isn't a
theory here; on NSE, some days it simply switches off.

## Key takeaways
- Short = selling first; symmetric to long (the franc surge rewarded shorts brutally).
- Spread is a toll on every trade; slippage is a tax on fast markets — both were weapons
  on Jan 15, 2015.
- Liquidity is protection. Thin markets are where beginners donate money.

## Quick check ✅
1. Stock bid 250.00 / ask 250.10. You market-buy 100 shares, then market-sell instantly. P/L before charges?
2. Why do stop losses sometimes fill far below the trigger?
3. Long or short: you profit if price *falls*?

## Today's action step
Watch the order book (market depth) of a liquid stock for 5 minutes — see the spread
breathe. Then open an illiquid stock's depth. That visual difference is the SNB story
at 0.01% scale. You'll never trade illiquid again.

Answers: 1 — buy 250.10, sell 250.00 → −₹10 (the spread) ·
2 — Stop becomes a market order; price gaps/slips before your exit fills · 3 — Short
