# TradeThesis Trading Path — production integration notes

This website package updates the public-facing product presentation from the uploaded `starter-drip-course` package. It intentionally does **not** place all paid Markdown lessons in the public web root.

## Product facts taken from the course package
- Price: ₹999, one-time; lifetime access is stated in `FAQ.md` and `VALUE-STACK.md`.
- 30 written lessons across four levels, scheduled as one lesson per day.
- Planned delivery: scheduled Telegram course-delivery messages. This is for releasing lessons and is separate from the TradeThesis trading bot; Trading Path enrolment does **not** grant trading-bot access. The drip is pacing, not a deadline; a learner who falls behind retains access.
- Study time in the course FAQ: 15–20 minutes for the lesson plus about 10 minutes for the action step.
- Checkpoints: Days 8, 16, 24 and 30.
- Included resources: six cheat sheets, glossary, journal CSV, position-size calculator CSV, checklist, playbook, completion tracker, quiz bank, trade-review cards, myths/facts guide, curated resources, post-course plan and certificate template.

## Required production connections before taking payment
1. Create or confirm the product and price in checkout; route successful payment webhooks to a durable enrollment record.
2. Associate the enrollment with the Telegram user/chat identity, with a clear opt-in and recovery path.
3. Schedule one release per day at a configured local time; make release idempotent so retries do not duplicate lessons.
4. Persist release/progress/quiz state. Apply the checkpoint rules on Days 8, 16, 24 and 30 and define how a learner retakes a quiz.
5. Generate/send the completion certificate and any post-course follow-up only after the required completion state is met.
6. Gate paid downloads and lesson content. Keep the source Markdown and paid assets outside the publicly served static directory.
7. Confirm the refund policy and support contact before checkout is enabled.
8. Verify position-sizing/lot-size examples against current contract specifications before release.

## Chart asset readiness
The course's `CHART_GUIDE.md` lists 21 expected TradingView exports. The supplied `charts/generated/` directory contains five generated images, leaving 16 specified exports still to create or explicitly remove from the lesson requirements. Do not interpret the site preview as proof that all lesson media is production-complete.

## Public website changes in this package
- Course overview and Trading Path page describe the daily drip, lifetime access, 30 lesson titles, quizzes and included resources.
- A short Day 1 excerpt is shown as a sample lesson; the full paid lessons are not included in the public website folder.
- The enrolment buttons remain preview actions until connected to payment/enrollment.
- `curriculum.json` is a metadata manifest for later use by the Django model/seed process; it contains lesson titles, day, level, duration and source file names—not the paid lesson bodies.

## Product boundary: no trading-bot entitlement
The ₹999 Trading Path enrolment grants access only to the course lessons and the resources explicitly listed on the public offer. **Do not grant or infer access to the TradeThesis trading bot** from this enrolment. Keep bot permissions as a separate, explicit entitlement if a bot product is offered elsewhere. Test that a Trading Path enrolment cannot call bot-only pages, APIs, keys or execution services. The public catalogue and course detail FAQ must continue to state this exclusion clearly.
