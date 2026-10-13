# 🎓 Starter Trading Course — Complete Standalone Package (v3, Story Edition)

A BabyPips-style, 30-day course priced at ₹999 — **fully standalone**: no Telegram, no
bot, no members area required. Students receive a PDF + HTML ebook immediately, and one
drip email per day for 30 days.

## What's in the package

```
starter-drip-course/
├── delivery/                        ← THE PRODUCT (what buyers receive)
│   ├── Starter-Trading-Course-Complete.pdf    Styled ebook: cover, contents, level dividers,
│   │                                          captioned diagrams for every lesson, workbook, page numbers
│   ├── course-ebook.html                      Interactive edition: progress tracking + private notes
│   │                                          (saved on the reader's device), self-contained, mobile-first
│   └── email-sequence.md                      Day 0 welcome + 30 pre-written daily drip emails
├── COURSE_ROADMAP.md                Full 30-day curriculum
├── CHART_GUIDE.md                   21 TradingView chart specs (optional — you supply these)
├── FAQ.md                           Sales-page-ready FAQ
├── level-1-foundations/             Lessons 1–8
├── level-2-technical-toolkit/       Lessons 9–16
├── level-3-trading-mechanics/       Lessons 17–24
├── level-4-psychology/              Lessons 25–30
├── assets/
│   ├── cheatsheets/                 6 printable cheat sheets
│   ├── templates/                   Journal CSV (live formulas) · position-size calculator CSV ·
│   │                                checklist printable · playbook template · 30-day tracker
│   └── VALUE-STACK.md               Sales-page pricing copy (₹8,992 value → ₹999)
├── bonus/
│   ├── bonus-1-first-30-days-live.md        Week-by-week post-graduation plan
│   ├── bonus-2-quiz-bank.md                 50 practice questions + answer key
│   ├── bonus-3-myths-vs-facts.md            15 myths that drain Indian trading accounts
│   ├── bonus-4-resources.md                 Books/tools short list
│   └── bonus-5-trade-review-cards.md        10 annotated trade cards
├── certificate/CERTIFICATE-template.md      Fill-in completion certificate
└── charts/generated/                5 diagrams already made
```

## How selling works (no code needed)

1. Upload `delivery/Starter-Trading-Course-Complete.pdf` to your checkout (Gumroad,
   Razorpay Pages, Instamojo, or your own site).
2. Load the 30 emails from `delivery/email-sequence.md` into any email tool
   (MailerLite/ConvertKit free tiers work) as a 30-day automation, Day 1 instant.
3. Buyer pays → gets PDF link + Day 1 email → one email every morning for 30 days.
4. Day 30 email carries the graduation message + main-channel upsell.

## Editing workflow

Lessons are the source of truth (level-*/ folders, Markdown). After any edit, rebuild
the PDF + HTML with the build script (ask and I'll regenerate, or it's in the delivery
toolchain note below). Charts: drop your 21 TradingView exports into `charts/` per
CHART_GUIDE.md and I'll embed them.

## Verify before launch
- Lot sizes (Nifty 75 etc.) and margins against current NSE specs
- Your refund policy line in FAQ.md
- Story figures are real events — re-verify any you quote in marketing
