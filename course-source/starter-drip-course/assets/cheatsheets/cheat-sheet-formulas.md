# 📐 Formula Cheat Sheet — every number in the course, one page

Print this. Tape it next to your screen.

## P&L
**P/L = Points gained × Lot size × Number of lots**
Stock version: P/L = Price move × Number of shares
Reverse (short): Points gained = Entry − Exit

## Position size (Day 20)
**Size = Risk ₹ ÷ (Stop distance in points × Value per point per unit)**
- Risk ₹ = Account × Risk% (use 1.5% default)
- Stop distance = |Entry − Stop|
- Value per point = Lot size for futures/options · 1 for shares
- Round DOWN. If nothing fits → trade size is ZERO (a valid decision).

## R-multiples (Day 21)
**R = Rupee risk of the trade.** +2R = won twice what you risked. Always journal in R.

## Expectancy (Day 21)
**Expectancy = (Win% × Avg Win R) − (Loss% × Avg Loss R)**
Go-live threshold: > +0.15R after costs, profit factor > 1.5.

## Breakeven win rates (before costs — add ~3%)
| R:R | Breakeven |
|---|---|
| 1:1 | 50% |
| 1:2 | 33% |
| 1:3 | 25% |

## Recovery math (Day 19)
| Loss | Gain needed to recover |
|---|---|
| −10% | +11% |
| −25% | +33% |
| −50% | +100% |
| −75% | +300% |
| −90% | +900% |

## Stops (Day 18)
- Default: beyond structure + buffer (0.25–0.5 × ATR)
- Messy structure: Stop distance = 1.5–2 × ATR(14)
- Stops only move toward the target. Never away.

## Standing risk rules (Day 19)
- Risk per trade: 1–2% (1.5% default)
- Correlated positions = ONE trade (Nifty + BankNifty long = one bet)
- Day trading: max 3 trades/day · Swing: max 5–8 open positions
- Circuit breaker: 3 straight losses OR −3% day → terminal CLOSED

## Costs (Day 4/26)
Every trade pays: brokerage + exchange fees + STT/CTT + GST + stamp duty + spread +
slippage. Under ~1R target ⇒ costs dominate ⇒ skip.
