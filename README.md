# TradeThesis — Full Design & Course Project

This package collects the current TradeThesis static website prototype, approved Pass 6 course-room redesign, source materials for the 30-day starter drip course, learner downloads, logo assets, and handoff notes in one place.

## Start here

1. Open `START_HERE.html` in a browser for links to the main parts of this package.
2. For the public website, open `site/00_OPEN_INTERACTIVE_PREVIEW.html` (or `site/MOBILE_PREVIEW.html` to review the mobile layout). The individual pages are also in `site/`.
3. For the learner-facing course-room prototype, open `course-room/TradeThesis_Course_Room.html`.
4. The full editable source package is in `course-source/starter-drip-course/`. Begin with its `README.md` and `COURSE_ROADMAP.md`.
5. Standalone learner downloads are in `learner-downloads/`, including the Excel journal and formatted glossary.

## Included

- **Website prototype:** homepage, course catalogue, Trading Path sales page, new CONSTRUCT 70-day guided programme page, separate live-class page, redirect page, desktop preview and mobile preview.
- **Course room:** the current Pass 6 HTML prototype, including the quarter-circle lesson motif, desktop navigation layout, mobile drawer, lessons, resource library, glossary and Excel workbook download.
- **Course source:** the latest supplied `starter-drip-course(4).zip` content, extracted without rewriting it, plus the supplied CONSTRUCT curriculum source: 30 Markdown lessons, generated chart images, bonus materials, templates, certificate sample, PDF course ebook, HTML ebook and delivery drafts.
- **Learner downloads:** Excel trading journal, CSV companion, formatted searchable glossary, position-size calculator and practical templates.
- **Brand assets:** horizontal logo, wordmark and monogram icon.
- **Integration documents:** curriculum manifest, production integration notes and source-sync notes.
- **Review screenshots:** the approved desktop layout, short viewport, and mobile drawer.

## Course catalogue design

The ₹999 Trading Path and ₹17,000 CONSTRUCT offers now share a course-card system: common outer framing, two-column layout, heading and price hierarchy, spacing, offer-panel geometry, and mobile stacking. Their differences are intentional and content-led: the Trading Path emphasizes self-study, lessons, checkpoints and permanent course access; CONSTRUCT emphasizes feedback, deadlines, Review Clinics, risk accountability and 12 months in The Wobbling Candle community with no separate fee. The homepage gives the ₹999 Trading Path the only detailed offer card; CONSTRUCT and the six-week live classroom are compact routes to explore when the visitor is ready for more support.

## Important status and access notes

This is a **design and content review package**, not a production backend. Checkout, authenticated learner accounts, server-side progress, scheduled daily release and production Telegram delivery are not connected. The course-room prototype deliberately has all 30 lessons available for review. The ₹999 Trading Path does **not** include trading-bot access; delivery of course lessons through Telegram is separate from access to any trading bot.

Do not publish the entire package to a public web server. The `course-source/` folder contains full paid-course content and internal delivery/production materials. Publish only the appropriate website pages and implement authenticated access and scheduled release before selling the course. The prototype's locally available lesson files are not access-controlled.

## Folder map

- `site/` — static public website pages and brand assets
- `course-room/` — current standalone course-room prototype
- `course-source/starter-drip-course/` — editable 30-day course source and supplied assets
- `course-source/construct/` — CONSTRUCT website curriculum and notes
- `learner-downloads/` — individual tools for easier review
- `brand-assets/` — logo artwork
- `course-integration/` — curriculum and production handoff documents
- `review/` — screenshots and design notes

## Local use

Use a modern browser such as Firefox or Chrome. The HTML previews are self-contained or use only relative assets included in this package. If a browser blocks a particular local-file action, run a simple static server from this directory, for example:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/START_HERE.html`.

## Pass 2 positioning note
The homepage features the ₹999 Trading Path as the only full-size offer. CONSTRUCT and the six-week live classroom are compact routes to explore when a visitor is ready for more support. The Courses catalogue keeps both detailed offers within a shared visual system, with distinct handwritten paper notes.

## Pass 2 content and presentation
The homepage gives the ₹999 Trading Path the only full-size offer card; CONSTRUCT and the six-week live classroom remain compact options. The Courses page keeps detailed cards for both priced courses in a shared design system. Small tilted paper notes add a handwritten editorial touch. CONSTRUCT is paper-trading-led, includes 12 months in The Wobbling Candle at no separate fee, lets learners bring questions to the instructor, and features live lessons demonstrating trade execution and management. The public copy does not state the number or calendar timing of those live lessons.
