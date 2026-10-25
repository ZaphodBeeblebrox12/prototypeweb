# Course card alignment — Pass 1

Date: 13 October 2026

## Design decision

The ₹999 Trading Path and ₹17,000 CONSTRUCT programme should look like two offers from the same TradeThesis design system, not like unrelated page components. The shared principles are:

- The same rounded outer frame, border weight, restrained shadow and internal padding.
- A matching two-column rhythm: programme story and outcomes on the left; fee and offer details on the right.
- Shared serif heading treatment, eyebrow labels, price typography, compact feature chips and full-width primary action.
- The same responsive rule: the offer panel stacks under the programme story on smaller screens.
- The same quiet cream, sage, green and gold palette.

## What intentionally differs

**Trading Path · ₹999:** emphasizes independent study, the 30-lesson sequence, four stages, checkpoints, reference materials and lifetime course access.

**CONSTRUCT · ₹17,000:** emphasizes 70 days of guided practice, weekend assignments, thesis reviews, risk audits, Review Clinics and the defended capstone. The Wobbling Candle panel explicitly states that 12 months of community access are included and that there is no separate community fee.

This creates a clear step-up in the *learning support*, not a superficial “premium colour” treatment. CONSTRUCT is also explicitly described as guided practice rather than a signals or trade-calls service. The ₹28,000 Income Desk remains a separate advanced tier.

## Pages updated

- `site/index.html` — the CONSTRUCT teaser is now a full companion card rather than a thin promotional strip.
- `site/courses.html` — the two course offers share framing, column proportions, price-panel logic and mobile treatment.
- `README.md`, `PROJECT_CONTENTS.md` and `course-integration/CONSTRUCT_INTEGRATION.md` — handoff notes updated.

## QA performed

- Parsed the updated HTML pages and confirmed no duplicate IDs on the reviewed public pages.
- Checked local links from the reviewed pages; no missing relative targets were found.
- Confirmed the course catalogue and homepage include ₹999, ₹17,000 and The Wobbling Candle community wording.
- Checkout, enquiries, account access and scheduled course delivery remain prototype functionality and are not activated by this design pass.
