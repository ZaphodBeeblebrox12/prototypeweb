---
lesson: 18
level: 3
title: "Stop Losses — Placement Rules That Survive"
day: 18
duration: "~14 min"
edition: "3.0 — story edition"
---

# Day 18 — Stop Losses: Placement Rules That Survive

**🎬 The man who moved his stops — and took down a 233-year-old bank**

Nick Leeson was a 28-year-old derivatives trader in Singapore for **Barings Bank** — the
UK's oldest merchant bank, founded in 1762, banker to the Queen. In 1994 he began betting that a Japanese stock-market index would stay calm and move sideways. When the Kobe earthquake hit in January 1995, the index crashed right through his comfortable range — and instead
of taking the controlled loss, Leeson did the thing you're about to learn is forbidden:

He hid the losing trades in a secret account ("Error Account 88888")… and *doubled down*, taking bigger positions as the market fell, moving his exits further away, betting on a recovery that kept not coming. The losses snowballed from ~£20 million to
**£827 million**. Barings — two centuries of history — was bankrupt within weeks, sold
to ING for £1.

The fascinating part: Leeson's *initial* trades weren't crazy. Selling premium on a
range-bound index was a standard strategy. What destroyed a 233-year-old institution
wasn't the entry — it was refusing to define invalidation, then moving the exit to avoid
realizing pain. Today you learn the discipline that would have saved Barings: where
"wrong" actually lives on a chart, written before the trade.

> 💬 **Answer this honestly:** in your last losing trade, did you know *exactly* where you were wrong before you entered — down to the price — or did you figure it out somewhere in the middle of the loss growing? Note "before" or "during." No shame either way. Today makes sure it's always "before."

## What you'll learn
- The three valid stop placement methods
- Volatility-based stops (ATR) and when structure is ambiguous
- The four stop sins that destroy accounts

## Method 1 — Beyond structure (the default)

Your stop goes where the *idea* is invalidated — and ideas live at structure:

- **Long at support/zone/trendline:** stop **below the zone's low** — beyond where the
  stop-hunt pokes. If price trades through the whole zone, the defense failed; you're out.
- **Long at a pullback to the 20 EMA:** stop below the pullback's swing low.
- **Breakout long:** stop back inside the pattern, beyond the opposite boundary.

Common thread: **the stop belongs on the far side of the thing you traded, plus a buffer**
(0.25–0.5× ATR(14) is a sane default) — the buffer absorbs the stop-hunt poke from Day 9.

## Method 2 — Volatility stops (ATR)

When structure is messy — ranges, fast markets — use the market's own noise level:

> **Stop distance = 1.5–2 × ATR(14) from entry.**

If normal noise is 40 points, a 15-point stop is a donation to randomness. ATR also
scales targets: a 1× ATR target inside a 2× ATR noise market is a coin flip.

## Method 3 — Time-based invalidation

Some ideas expire: "if it doesn't break out within 3 days, the momentum is gone."
Exiting on time avoids slow-motion losses where price bleeds theta, attention, and
opportunity.

## Position size comes FROM the stop — not before it

The sequence (most people get this backwards):

1. Entry level (from your setup).
2. Invalidation level (structure/ATR) → **risk per unit**.
3. Risk in rupees (Day 19's 1–2% rule).
4. **Size = risk ₹ ÷ stop distance in ₹ per unit.** (Day 20 does this math in full.)

A wide stop doesn't mean a big loss — it means a *smaller size*, same rupee risk.

## The four stop sins

1. **No stop at all.** One gap ends the conversation — this is how Barings died. Every
   position has a live stop from the first second.
2. **Stop inside the noise.** Too tight = normal breathing stops you out, then price goes
   your way without you. The most painful loss in trading: right idea, no position.
3. **Moving the stop away.** Never. Only toward the target (trailing). Leeson's entire
   catastrophe is this sin, repeated with size.
4. **Instant revenge re-entry** after a stop-out at the same level. If the idea still
   stands, wait for a **new** trigger (a fresh rejection). One re-entry maximum, then the
   level is dead for the day.

📊 CHART NEEDED: `charts/L3-18-stop-placement.png`
INSTRUMENT / TIMEFRAME: Two panels — same stock · 1H
MUST SHOW:
  - Panel A (BAD): stop inside a zone → stopped by a wick, then price rockets
    ("stop in the noise — right idea, no position")
  - Panel B (GOOD): same setup, stop beyond zone low + small ATR buffer → survives the
    poke, then wins ("beyond structure + buffer")
  - ATR(14) value visible

> ⚠️ **Common beginner mistakes**
> 1. Stop distance chosen by "how much I'm willing to lose" instead of structure — the
>    market doesn't respect your feelings.
> 2. Tightening the stop the moment the trade goes slightly green.
> 3. Treating a stop-out as failure — a clean stop executed per plan is a *successful*
>    trade with a negative outcome. (Barings' alternative wasn't a win; it was £827M.)

## 🇮🇳 The Indian story: the gaps that ignore your stop

India has its own brutal lesson in why stops are invalidation statements, not price
guarantees: **PC Jeweller fell over 30% in a single session in April 2018** on fraud-probe
news; **PNB lost roughly a third of its value in days** in February 2018 when the
₹14,000-crore Nirav Modi fraud surfaced. In both cases, the stocks *gapped* far below
where any structurally-placed stop had sat — traders who had correct stops at ₹330 didn't
exit at ₹330; they exited at ₹240, or ₹200, whatever the opening auction delivered. The
stop did its job (it got them out); the gap did its job too. The Indian lesson on top of
Barings: place stops beyond structure, size them so a gap through the stop *hurts, never
kills*, and never hold concentrated positions in single-name stories overnight — in
India, the gap is a recurring character, not a rare event.

## Key takeaways
- Stops go beyond the structure you traded + buffer (or 1.5–2× ATR when structure is
  unclear). They are invalidation statements, written before the trade.
- Size is derived FROM the stop, never the reverse.
- One re-entry maximum after a stop-hunt; widening a stop is forbidden, forever.
  (One man moving stops erased 233 years of banking.)

## Quick check ✅
1. You buy at a support zone of 500–502. Where does the stop go, and why not at 499?
2. ATR(14) on your timeframe is 30 points. What's a sane stop distance and why?
3. Your stop got hit by a wick and price reversed exactly as planned. What was the flaw?

## Today's action step
Open your last five trades (real or paper). For each: "was my stop beyond structure with
a buffer, or inside the noise?" Count the noise stops. That number, almost always, is the
gap between your current results and your planned results — and it's the gap Nick Leeson
never measured.

Answers: 1 — Below ~500 minus a buffer (e.g., 498.8); 499 is inside the stop-hunt zone ·
2 — ~45–60 points (1.5–2× ATR) — inside that, normal volatility stops you out ·
3 — Stop placed inside the noise, not beyond structure
