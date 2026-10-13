---
lesson: 2
level: 1
title: "Brokers & Order Types"
day: 2
duration: "~10 min"
edition: "3.0 — story edition"
---

# Day 2 — Brokers & Order Types

**🎬 The 45 minutes that cost $440 million**

On August 1, 2012, Knight Capital — one of the largest market makers in America,
handling trades for everyday investors — deployed a software update. One line of dead
code from an old module woke up. Within **45 minutes**, Knight's machines had sent
millions of unintended orders into the stock market, buying high and selling low in a
loop it couldn't stop. By the time engineers killed it: **$440 million gone — roughly
$170,000 per second**. Knight's stock collapsed 60%+ and the firm was rescued in a
fire-sale merger days later.

Here's why this story opens a lesson for *you*: Knight's disaster wasn't about analysis.
It was about **the plumbing** — what happens between your finger pressing "buy" and the
exchange matching your order. That plumbing is the broker's world, and you live in it
every trade. Today you learn the four order types that control exactly how your bid
enters that auction.

> 💬 **Quick honesty check:** when you open your trading app, do you actually know *where your shares are held*? If your broker's app vanished tomorrow, could you get your holdings back? Jot your guess in your head — today's two stories will make you want to check. What do you think — safe, or "never thought about it"?

## What you'll learn
- What a broker actually does (and Knight's place in the chain)
- Market, limit, stop-market and stop-limit orders
- Which order type to use when

## What a broker does

You can't walk up to the exchange and shout your order. A **broker** is your licensed
gateway: your app sends an order → the broker validates and routes it → the exchange
matches it against another order → the fill comes back to you — all in milliseconds.

In the chain, your broker also: holds your money, calculates margin, sends contract
notes, and reports your trades to tax authorities. (And a broker's own systems can fail —
Knight's did; so can your app's. **Choose a broker you trust with money and data.** On
volatile days in India, you've probably seen screenshots of broker outages; the traders
who planned for it had phone-trade backups. The plumbing matters.)

## The four order types

### 1. Market order — "Get me in NOW"
You accept whatever price is available right now.
- ✅ Guaranteed fill, instantly
- ❌ No price guarantee — in a fast market you get a worse price (*slippage*, Day 6).
  Knight's rogue orders were effectively toxic market orders.
- **Use when:** exiting a losing trade fast. *Never* for careful entries.

### 2. Limit order — "Only at my price (or better)"
You name your price. The order sits in the queue until someone accepts it.
- ✅ Guaranteed price (or better)
- ❌ Not guaranteed to fill — price may run away without you
- **Use when:** planning an entry at a level you chose in advance. **Your default order
  type for entries.**

### 3. Stop-market order — "If price hits X, get me out NOW"
Dormant until price touches your *trigger*, then becomes a market order.
- ✅ Your safety net — this is what a stop loss is
- ❌ In a panic, fills can be far from the trigger price
- **Use when:** always, on every trade, no exceptions.

### 4. Stop-limit order — "If price hits X, place a limit at Y"
Dormant until trigger, then becomes a *limit* order.
- ✅ Price control after the trigger
- ❌ Dangerous: in a crash your limit may never fill and you ride the whole fall
- **Use when:** rarely, only once experienced. Beginners skip this.

📊 CHART NEEDED: `charts/L1-02-order-types.png`
INSTRUMENT / TIMEFRAME: Any liquid stock · 15-minute
MUST SHOW:
  - Current price marked clearly
  - Dashed line above price: "Stop-market trigger (buy stop / stop loss for shorts)"
  - Dashed line below price: "Limit buy entry"
  - Dashed line lower: "Stop loss trigger (sell stop)"

## 📌 Case file: January 2021 — the buy button disappeared

During the GameStop mania, on January 28, 2021, Robinhood — the broker of millions of
new traders — suddenly *removed the buy button* on GameStop and a handful of other
stocks. Traders could sell, not buy. Furious users sued; Congress held hearings. Robinhood
said margin requirements from its clearinghouse had exploded overnight — the plumbing
again: when volatility explodes, the system demands more collateral, and brokers can
choke. Whatever you think of the politics, the lesson for a trader is permanent:
**know your broker's rules, know the order types cold, and never assume the button will
be there when you most need it.**

## 🇮🇳 The Indian story: Karvy and the broker you trusted

India got its own plumbing scandal. Karvy Stock Broking — a **90-year-old, respected
hyderabad brokerage** — was barred by SEBI in late 2019 for pledging client securities
worth roughly **₹2,300 crore** to raise loans for itself. Clients who thought their
shares sat safely in their accounts discovered they'd been mortgaged. The lesson is
Knight Capital's lesson at Indian scale: the chain between you and the exchange —
broker, depository, margins, order routing — is invisible until the day it matters.
Know your broker's financial health, keep your holdings visible in your own demat
statements, and always know which of your order types protects you when the app hangs
on a circuit day.

## Key takeaways
- Market = speed, limit = price, stop-market = protection, stop-limit = advanced.
- Your default entry: limit order at a level you chose. Your default protection:
  stop-market on every single trade.
- The Knight/Robinhood stories: the plumbing IS the product. Respect it.

## Quick check ✅
1. You want to buy Reliance only if it drops to ₹2,900. Which order?
2. You own a stock at ₹500 and want to auto-exit if it falls to ₹480. Which order?
3. Why is stop-limit risky as a stop loss in a crash?

## Today's action step
Open your broker's order window (don't place anything) and identify every field:
instrument, quantity, order type, price, trigger price, validity (DAY/IOC). Touch each
one so the screen feels familiar before real money is involved. Then find your broker's
policy page on margin and outages — two minutes of boredom that might save your account
one day.

Answers: 1 — Limit buy at ₹2,900 · 2 — Stop-market, trigger ₹480 ·
3 — The limit may never fill in a fast fall, leaving you exposed
