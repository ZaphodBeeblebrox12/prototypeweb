# TradeThesis Customer Experience Audit

**Review date:** 31 October 2026  
**Repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Integration target:** `my-new-branch`  
**Purpose:** Treat discovery, enquiry, enrolment, onboarding, learning, support and retention as one customer journey. This is a source/PR audit, not a claim of production or staging acceptance.

## Executive view

TradeThesis has a distinctive educational position, substantive learning content and increasingly capable Academy/operations infrastructure. The remaining customer-experience risk is consistency: product promises, form actions, access state and customer follow-up must all describe the same real service.

The priority is not another redesign of the Admin Desk. It is to make every customer-facing step dependable, clear and recoverable, while ensuring internal staff can follow up without exposing member support or private operational data.

## Findings and priorities

### P0 — Keep product promises accurate

1. **Trading Path offer truth.** The current offer is free, self-paced, permanently accessible and has all 30 lessons available immediately. The optional 30-day study plan is a suggested rhythm, not a timed release schedule. The course does not include community or trading-bot access. Do not promise Telegram lesson delivery unless verified end to end.
   - Updated in this branch: `site/assets/course-catalogue-data.js`, `README.md` and `docs/architecture/FRONTEND_BACKEND_INTEGRATION.md`.
   - Acceptance: public course cards, detail pages, backend access policy, emails and help content agree.

2. **Programme enquiries must reach a real workflow.** The previous static enquiry interactions were preview-only. PR #35 now proposes the canonical public enquiry flow using the existing Support app: separate `CourseEnquiry` records, exact public-origin allowlisting, consent, honeypot, per-email/programme throttling, staff permissions, assignment, internal notes and logged email replies.
   - Prefer PR #35's existing Support-app implementation over a second, parallel prospect app.
   - Acceptance: a real staging form submission creates one record, a staff member can claim/assign and reply, the accepted/failed mail state is explicit, and the customer sees a server-confirmed receipt.

3. **Never report delivery without evidence.** Email backend acceptance is not inbox delivery. Payment return pages are not proof of payment. A button click is not proof of a Telegram link or community entitlement.
   - Acceptance: customer-facing status messages reflect a confirmed server-side state and offer a safe recovery path.

### P1 — Make the first learning session feel guided

4. **First-session orientation.** PR #36 proposes an orientation for enrolled learners who have not yet opened an accessible lesson. It uses existing server-side progress, keeps the primary action state-aware and does not add a dismiss cookie or extra model.
   - Acceptance: after enrolment the learner sees a manageable first step; opening the first lesson records progress; returning to the course overview changes the action to Continue learning.

5. **Learner home should answer four questions.** What am I enrolled in? Where did I stop? What should I do next? Where do I get help?
   - Acceptance: course entitlements, resume links and progress come from backend state; empty, locked, failed and completed states are understandable.

6. **Verify CONSTRUCT's full offer bundle.** The public offer includes 12 months of The Wobbling Candle community access. The integration notes identify this as a distinct entitlement from the course itself.
   - Acceptance: provider-confirmed payment grants course and community entitlements exactly once; expiry, refunds and chargebacks adjust the correct entitlements; support can inspect the resulting state.

### P1 — Make integrations and support predictable

7. **Telegram states must remain distinct.** Telegram login identity, verified bot connection, managed community membership and course notifications are separate things. PR #33 addresses disconnect, revoke/reconcile, stale verification and legacy callback consistency.
   - Acceptance: unlink is not reported as successful until access revocation is verified; partial failures stay visible and recoverable.

8. **Keep prospect enquiries separate from member support.** Public prospects should not need an account or create a member support ticket. Staff-only replies and notes must remain private.
   - Acceptance: separate permissions, queues and audit trails; no public access to internal notes or customer records.

9. **Review failure and recovery states.** Cover email verification pending, payment pending/failed, payment succeeded but entitlement delayed, duplicate enrolment, Telegram unavailable, locked lesson, missing media, progress save failure and expired access.
   - Acceptance: each state explains what happened, whether an action is needed, whether retry is safe and how to reach support.

### P2 — Measure customer outcomes

10. **Create a privacy-conscious journey scorecard.** Track course detail views, enquiry submissions and response time, signup and verification, checkout and provider-confirmed payment, entitlement grant, first lesson, return within 7 days, course completion and support resolution.
    - Do not collect chart contents, trading account data or sensitive financial details for marketing analytics.

## Current parallel implementation checkpoints

- [PR #35 — Public programme enquiry workflow](https://github.com/ZaphodBeeblebrox12/prototypeweb/pull/35) is open as a draft and targets `my-new-branch`. Its description reports 11 enquiry regression tests passed, browser smoke passed and static checks passed. It records the same 29 broader account/dashboard/Telegram/Resend failures on both its branch and the target base, with zero PR-only or base-only failures. It has not been staged or deployed.
- [PR #36 — First-session learner orientation](https://github.com/ZaphodBeeblebrox12/prototypeweb/pull/36) is open as a draft and targets `my-new-branch`. It adds the orientation using existing server-side progress; CI and staging acceptance are still pending.
- [PR #33 — Telegram lifecycle hardening](https://github.com/ZaphodBeeblebrox12/prototypeweb/pull/33) is open and targets `my-new-branch`. It addresses unlink/revoke/reconnect and legacy Discord/Telegram consistency; authenticated staging acceptance remains pending.

These are separate in-flight changes. Review and integrate them into `my-new-branch` in a controlled order; do not duplicate their functionality in another app or merge into `main`.

## Required staging acceptance

1. Apply `support.0009_course_enquiries` from PR #35.
2. Configure `TRADETHESIS_PUBLIC_SITE_ORIGINS` with the exact deployed public-site origin(s), and configure the Academy base URL.
3. Ensure the transactional email backend/sender is configured, then test customer receipt, staff alerts and staff replies. Treat backend acceptance as distinct from inbox delivery.
4. Grant the designated sales/reviewer group `support.view_courseenquiry` and `support.change_courseenquiry`.
5. Verify public form submission, queue visibility, assignment, private notes, reply history, status changes and audit events on staging.
6. Test the first-session flow from a real free enrolment through first lesson open and resume.
7. Verify CONSTRUCT payment-to-course-plus-community entitlements and the Telegram disconnect/reconnect lifecycle.
8. Run mobile and desktop acceptance on the actual public and Academy hosts.

## Minimum end-to-end customer journeys

- **Free learner:** Trading Path page → account creation → email verification → free enrolment → first-session orientation → first lesson → progress saved → return and resume.
- **CONSTRUCT prospect:** programme page → enquiry form → server receipt → staff assignment → human reply → follow-up recorded.
- **CONSTRUCT buyer:** accurate offer → checkout → provider-confirmed payment → course and included community entitlements → orientation → first lesson.
- **Live Classroom prospect:** six-week programme page → distinct enquiry → confirmed dates/fees/format in staff follow-up.
- **Recovery:** simulate email failure, payment pending, delayed entitlement, Telegram revoke failure, locked lesson and progress-save failure; verify safe explanations and retry paths.

## Boundaries

- A draft PR, passing isolated test or static preview is not proof of production behaviour.
- Do not publish paid lesson bodies, answer keys, instructor-only notes or private support data in static assets.
- Do not merge or deploy to `main`; this work targets `my-new-branch`.
- Keep enquiry and onboarding changes in their respective current PRs rather than creating duplicate implementations.