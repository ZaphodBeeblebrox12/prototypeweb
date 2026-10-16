# CONSTRUCT — Trade Construction & Management

This folder preserves the source copy for the flagship TradeThesis programme. The current public page is `../../site/construct.html`.

## Current website-facing position

- The current page lists a one-programme fee of **₹17,000**.
- That fee includes **12 months of community access**; the page should not describe the community as a separately priced product.
- The current page describes a guided self-paced programme across **70 days**, with 43 core lesson topics, weekly lesson release, assignments, review clinics, risk audits and a capstone.
- The **Income Desk (₹28,000)** in the source copy is a separate advanced tier, not part of the core programme fee.
- A next cohort date has not been confirmed in the supplied source; do not invent one.

## Import and release boundary

`website-curriculum-source.md` is website copy plus a high-level curriculum outline. It is **not** a set of complete learner-facing lesson manuscripts, worked activities, or assessment/reveal data. Do not feed this file directly into the source-backed lesson importer, publish empty lesson shells as finished teaching content, or create a saleable `CourseOffer` solely because the marketing page exists.

Before backend catalogue import and publication, reconcile the final delivery format, canonical lesson sources, release schedule and entitlement terms. Earlier planning notes described a six-week live classroom format, while the current public page describes a 70-day guided self-paced format. Keep this as an explicit product decision to confirm rather than silently mixing both schedules.

When the offer is ready, model the programme fee and included community term separately: the existing `CourseOffer` supports a distinct `community_access_months` value, so the expected 12-month community access can be granted without making community a separate purchase or shortening the learner's course access. Keep the Income Desk as a separate offer/tier if it is retained.
