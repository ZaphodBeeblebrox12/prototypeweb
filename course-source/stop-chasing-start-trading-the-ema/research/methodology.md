# TradeThesis EMA pullback — exploratory independent comparison

## Purpose

This test operationalises the actual TradeThesis Lesson 1.2 long-side trend-pullback setup. It does **not** attempt to reproduce DailyBulls' 1% proximity strategy. It compares two entries within the same trend/structure/pullback context:

- **Touch-only control:** enter at the next session's open after the first qualifying approach to the 20 EMA.
- **TradeThesis confirmation:** wait for a bullish rejection candle, then enter only after a break above that candle's high.

Only one attempt is permitted per identified pullback (one attempt per latest confirmed swing high). A fresh attempt requires a new confirmed swing high and a fresh pullback. This avoids repeatedly treating later days inside the same pullback as new setups.

## Data

- Period: 1 January 2016 to 14 January 2026.
- NIFTY 50 index: daily OHLC history from the \`Arjundas08/research-referee\` repository (Yahoo Finance \`^NSEI\` data).
- Reliance, HDFC Bank and Infosys: daily OHLC from \`qubiit/NIFTY-50-Stock-Market-Data\`, described by the repository as NSE bhavcopy-derived data.
- The stock-data repository says its NIFTY 50 member list reflects constituents as of 5 January 2026. It is not a point-in-time constituent database.
- The test is restricted to four named instruments and cannot be generalised to all NSE shares.

## Explicit rule translation

The course uses some judgement terms (rising trend, higher highs/higher lows, controlled pullback, rejection). To make the test deterministic, the following proxies were applied to **both** methods unless noted:

1. **Trend filter:** daily close above the 200-day SMA; the SMA is higher than it was 20 sessions earlier; the 20-day EMA is higher than it was 5 sessions earlier.
2. **Structure:** the two most recently confirmed swing highs are rising, and the two most recently confirmed swing lows preceding the latest swing high are rising. Swings use three bars to the left and three to the right; a swing is only available after the three right-hand bars have completed, avoiding look-ahead.
3. **Controlled pullback:** after the latest confirmed swing high, price pulls back for no more than 20 sessions, does not break the preceding confirmed higher low, and at least one low reaches within 0.5 ATR(14) above the 20 EMA. Two consecutive bearish candles each wider than 1.5 ATR are treated as an accelerating selloff and disqualify the pullback.
4. **Target / room:** the most recent prior confirmed swing high is the next obstacle. A setup is accepted only when the target offers at least 1R from the planned entry to the structural stop. This 1R minimum is a modelling choice; the course says to require sufficient room but does not prescribe a numerical threshold.
5. **Stop:** pullback low minus 0.10 ATR(14), fixed when the entry decision is made.
6. **Entry / confirmation method:** the rejection candle must close above the 20 EMA, close above its open and the previous close, and finish in the upper 45% of its range. A buy stop is placed one ₹0.05 tick above its high for the next five sessions. If the next session opens above the trigger, the opening price is used. The order is cancelled if price breaks the pullback low before entry.
7. **Entry / touch-only control:** no rejection candle or breakout is required. Entry is at the next session's open after the first qualifying 0.5 ATR approach to the EMA. The same pullback swing low stop, prior swing high target and 1R minimum room filter are used.
8. **Fills:** a stop or target is filled if touched. If both are touched in one daily bar, stop-first is assumed. A stop gap exits at the open; a target gap receives the opening price.
9. **Scope:** long-only. Short-side testing is not included because this data exercise uses cash-equity/index price series and does not model the borrow, futures or derivatives execution needed for realistic short exposure.

## Results

### Touch-only control

116 trades: 41 wins, 75 losses, 35.3% win rate, +0.449R mean return per trade and 1.465 profit factor (R-based).

### TradeThesis rejection-and-break confirmation

22 trades: 9 wins, 13 losses, 40.9% win rate, -0.023R mean return per trade and 0.962 profit factor (R-based).

The confirmation rule produced a higher win rate but a lower average R and lower profit factor in this sample. It also generated far fewer trades. On these assumptions, the rejection-and-break trigger did **not** demonstrate an improvement over entering at the pullback touch. This is an exploratory result, not proof that confirmation is harmful or that touch entries are generally better.

### Instrument comparison

- Touch-only: NIFTY 31 trades / 38.7% wins / PF 1.05; Reliance 32 / 28.1% / 1.16; HDFC Bank 29 / 31.0% / 1.63; Infosys 24 / 45.8% / 3.08.
- Confirmation: NIFTY 5 trades / 60.0% wins / PF 1.81; Reliance 6 / 16.7% / 0.33; HDFC Bank 9 / 33.3% / 0.83; Infosys 2 / 100% / not meaningful (two trades only).

The confirmation result is not consistently better across instruments. The two Infosys winners are far too few to support a 100% win-rate claim.

### Chronological split

This split is descriptive, not a clean pre-registered out-of-sample test: the rule choices were explored on the full period before this split was summarised.

- Touch-only, 2016–2021: 83 trades, 36.1% wins, PF 1.488, mean +0.466R.
- Touch-only, 2022–14 January 2026: 33 trades, 33.3% wins, PF 1.411, mean +0.406R.
- Confirmation, 2016–2021: 16 trades, 43.8% wins, PF 1.029, mean +0.016R.
- Confirmation, 2022–14 January 2026: 6 trades, 33.3% wins, PF 0.808, mean -0.128R.

The split suggests the confirmation method did not improve the recent-period outcome in this run. The second period has only six confirmed trades, so this is highly uncertain.

## Corporate-action price continuity adjustments

- **Reliance:** 1:1 bonus before 7 September 2017; 1:15 rights theoretical ex-right factor before 13 May 2020; demerger price factor before 20 July 2023 using ₹2,580 / ₹2,841.85; 1:1 bonus before 28 October 2024.
- **HDFC Bank:** 2:1 face-value split before 19 September 2019; 1:1 bonus before 26 August 2025.
- **Infosys:** 1:1 bonus before 4 September 2018.

These are split/bonus/rights/demerger price-continuity adjustments, not a total-return series. Dividends and the value/cashflows of the demerged Reliance entity are not credited as total shareholder returns. Corporate-action factors should be audited against primary issuer/exchange notices and a professional adjusted-price source before publication.

## Important limitations

- The confirmation sample is only 22 trades. It is too small to establish a reliable edge.
- Pivot width, EMA slope lookbacks, ATR proximity, the definition of a wide selloff, rejection-candle requirements, trigger expiry, stop buffer and the 1R minimum are operational definitions added to make the prose testable. They are not all numerically specified in the course.
- The stock-data repository's historical universe reflects the current (January 2026) NIFTY 50 list, creating survivorship/selection concerns for any broad historical-universe claim.
- No brokerage, STT, GST, exchange charges, taxes, spread, slippage, market impact, dividends, funding costs or capital constraints are included.
- Pooled figures are concatenated independent trades, not a simultaneous multi-asset portfolio backtest. Overlapping positions and portfolio capital allocation are not modelled.
- The index is a price series, not an executable NIFTY futures/options instrument. These results do not establish options-trading performance.
- The sample ends 14 January 2026 because that is the latest common endpoint in the stock dataset used here.
- The chronological split is not a blind holdout because the modelling choices were explored using the full period.

## Recommended course treatment

Do not market either method as a validated strategy. This is a useful research-method example: a touch-only rule and a more selective confirmation rule can produce materially different trade counts and outcomes; confirmation did not improve the tested results on these assumptions; and a small, pre-cost backtest cannot establish a durable edge. The learner should understand why the trigger, stop, target and market filters must be defined and tested rather than assume that a confirmation candle automatically improves results.

## Data repositories

- https://github.com/qubiit/NIFTY-50-Stock-Market-Data
- https://github.com/Arjundas08/research-referee/blob/main/data/nifty50_daily.csv

## Corporate-action references

- Reliance bonus issues: https://www.moneycontrol.com/company-facts/relianceindustries/bonus/RI/
- Reliance rights adjustment (NSE): https://nsearchives.nseindia.com/content/circulars/FAOP44356.pdf
- Reliance demerger date / contracts (NSE): https://archives.nseindia.com/content/circulars/FAOP57525.pdf
- HDFC Bank split (NSE): https://archives.nseindia.com/content/circulars/FAOP42168.pdf
- HDFC Bank 2025 bonus allotment: https://www.hdfcbank.com/content/bbp/repositories/723fb80a-2dde-42a3-9793-7ae1be57c87f/?path=%2FFooter%2FAbout+Us%2FOther+stakeholders%27+Information%2F2025%2Faug%2F28%2FSE-Disclosure-Allotment-Aug-28-2025.pdf
- Infosys 2018 bonus: https://www.nseindia.com/companies-listing/corporate-filings-actions?symbol=INFY&tabIndex=equity
