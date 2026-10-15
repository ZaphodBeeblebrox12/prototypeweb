# Sources and Data Provenance

## Intellectual sources

- John J. Murphy, *Technical Analysis of the Financial Markets*: https://books.google.com/books/about/Technical_Analysis_of_the_Financial_Mark.html?id=ojTgDwAAQBAJ
- Adam Grimes, *The Art and Science of Technical Analysis*: https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202837
- Adam Grimes, “Interfaces between Trends and Ranges”: https://onlinelibrary.wiley.com/doi/10.1002/9781119202837.ch5
- Adam Grimes, “Practical Trading Templates”: https://onlinelibrary.wiley.com/doi/10.1002/9781119202837.ch6
- Adam Grimes, “The Failure Test”: https://www.adamhgrimes.com/failure-test-2/
- Adam Grimes, “Fundamental Trading Patterns”: https://www.adamhgrimes.com/fundamental-trading-patterns/
- Jack Schwager and Mark Etzkorn, “Support and Resistance,” Chapter 8: https://onlinelibrary.wiley.com/doi/10.1002/9781119209713.ch8
- Jack Schwager and Mark Etzkorn, “The Most Important Rule in Chart Analysis,” Chapter 15 preview: https://www.oreilly.com/library/view/a-complete-guide/9781118853757/c15.xhtml
- Brian Shannon, “6 Ways to Trade Using Multiple Timeframes”: https://alphatrends.net/archives/6-ways-you-can-trade-with-multiple-timeframes/
- Brian Shannon interview on price and volume: https://alphatrends.net/archives/interview-stockbsessed-03112023/
- IG Academy, “Breakouts and fakeouts”: https://www.ig.com/en/ig-academy/the-basics-of-technical-analysis/breakouts-and-fakeouts

These references inform original explanations. No book prose or textbook figures are reproduced.

## Historical price data

- Instrument: NIFTY 50 Index.
- Frequency: Daily OHLC.
- Source file: `NIFTY 50.csv` from `VatsalSin/Stock-Market-Indices-Dataset` on GitHub: https://github.com/VatsalSin/Stock-Market-Indices-Dataset/blob/main/NIFTY%2050.csv
- The raw data spans 2000-01-03 to 2019-12-02. This module uses excerpts in 2014, 2016 and 2017–2018, as recorded in each data file.
- The chart generator uses the source's recorded Open/High/Low/Close values. It does not randomly modify candle prices. Horizontal zones are instructional annotations selected for the teaching question; they are not official levels.
- The upstream repository did not visibly state a data licence when reviewed. The user approved use as temporary internal teaching examples and plans to replace the charts with their own later. Do not publish/distribute the OHLC extracts or exported charts until rights are confirmed or authorised replacement data is used.

## Chart-stage boundaries

The initial stage hides future candles beyond its cut-off date. Later stage images add only subsequent observations; they do not change the OHLC data. The lesson script must preserve the order and make it clear what the learner could know at each stage.
