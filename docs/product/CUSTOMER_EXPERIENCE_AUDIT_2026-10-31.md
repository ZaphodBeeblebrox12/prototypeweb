# TradeThesis Customer Experience Audit

**Review date:** 31 October 2026  
**Repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Working branch:** `my-new-branch`  
**Purpose:** Prioritise customer-facing work across discovery, purchase, onboarding, learning, support and retention. This is a source-based audit, not a claim that staging or production has passed live acceptance.

## Executive view

TradeThesis has a differentiated teaching position, substantial course content, a growing Django Academy and stronger internal operations. The main remaining weakness is continuity: the customer's promises, next actions and actual service are not yet consistently joined into one dependable journey.

The next phase should optimise for a learner who can discover the right offer, understand it, enrol or enquire, receive a useful welcome, start a lesson, see progress saved, and get help without learning how the underlying systems work.

## Findings and priority

### P0 — Remove broken or misleading customer actions

1. **Product truth must agree everywhere.** The Trading Path is currently free, self-paced and permanently accessible, with all 30 lessons available immediately. The optional 30-day study plan is guidance, not a drip schedule. The course does not include community or bot access. Do not promise Telegram lesson delivery until that path is verified. Keep catalogue data, sales pages, checkout, emails and internal handoffs aligned.
   - Evidence: `site/trading-path.html`, `site/assets/course-catalogue-data.js`, `backend/apps/academy/migrations/0014_make_trading_path_free.py`.
   - Acceptance: a single product fact set is reflected consistently in the public catalogue, detail page, Academy state, transactional messages and support responses.

2. **CONSTRUCT must have a real prospect next step.** The current CONSTRUCT enquiry button opens a modal explaining that enquiry is not connected. A ₹17,000 product must not invite a customer to enquire and then stop.
   - Evidence: `site/construct.html`.
   - Acceptance: an anonymous visitor can submit a validated enquiry; the server stores it, sends a staff notification, confirms receipt to the visitor and provides a traceable follow-up path. Include spam/rate protection, privacy notice and consent appropriate to the actual follow-up. Do not route prospects into member support tickets or invent an endpoint.

3. **Live Classroom lead capture must work.** Its form is explicitly preview-only and states that it does not send or store the visitor's details.
   - Evidence: `site/live-class.html`.
   - Acceptance: the same lead-capture standards as CONSTRUCT, while preserving the distinction between the six-week live classroom and the 70-day CONSTRUCT programme. A visitor should receive confirmed dates, fees, format and next steps—not a generic submission toast.

4. **Production route configuration must be verified.** `site/assets/academy-config.js` intentionally disables Academy links on unknown hostnames unless an explicit Academy base URL is supplied. This is safer than silently sending production customers to staging, but it means a missing production setting can make member actions inert.
   - Acceptance: test the actual public hostname and Academy hostname, login/signup return paths, cookies/session boundaries, CSRF and every `data-academy-path` action. No public CTA may silently point to staging or remain disabled without an understandable explanation.

### P1 — Make the first session feel guided

5. **Build a short, useful first-run orientation.** After free enrolment or paid purchase, explain where the learner is, what is included, how long a typical lesson takes, how to use the action steps and where to ask for help. Ask at most one or two optional questions that materially improve the route; do not gate access behind a lengthy questionnaire.
   - Acceptance: the first screen has one clear next action; a learner can start the first lesson immediately; orientation can be revisited.

6. **Make the learner home answer four questions.** What am I enrolled in? Where did I stop? What should I do next? Where do I get help?
   - Acceptance: server-backed course entitlements, progress and resume links; honest empty/locked/error states; a clear next lesson; no hard-coded demo progress.

7. **Make lesson completion feel reliable.** A learner should see saved/completed states only after server confirmation, with a visible retry path on failure.
   - Evidence: the Academy has server-side progress routes and a resume service; the integration map already describes the required boundary.
   - Acceptance: test progress across refresh, logout/login and a second device; test duplicate submissions, timeouts and offline/retry behaviour.

### P1 — Make the paid flagship proposition complete

8. **Verify CONSTRUCT's full entitlement bundle.** The public promise includes 12 months of The Wobbling Candle community access. The integration map notes that the existing one-course offer model does not by itself grant this separate community entitlement.
   - Acceptance: a successful, provider-confirmed payment grants course access and the correct 12-month community entitlement exactly once; refunds, chargebacks and expiry revoke or adjust the right entitlements; support can inspect the result in Customer 360.

9. **Replace vague programme detail with inspectable evidence.** Show a representative lesson, a sample assignment, the feedback format, the cadence of clinics, instructor involvement and a real example of learner work. Only use genuine learner work/testimonials with permission. Clearly distinguish illustrative charts from historical market data.
   - Acceptance: a prospect can assess the teaching method and expected work before paying; no profit promises, invented testimonials or implied guaranteed outcomes.

### P2 — Make support and integrations predictable

10. **Keep Telegram states distinct.** A linked Telegram login identity, verified bot connection, membership in a managed channel and course notification delivery are different states.
    - Acceptance: each state is shown separately and derived from canonical backend records; link/unlink, expired verification, blocked bot, provisioning delays and partial failure have clear recovery instructions.

11. **Make support easy to find and trustworthy.** Keep public prospect enquiries distinct from authenticated member support. On a ticket, show its current status, expected next step, public reply history and where to continue the conversation. Never expose internal notes.
    - Acceptance: all support links stay in the TradeThesis Admin Desk/member experience; permission scopes and private-note boundaries remain enforced.

12. **Review all failure and recovery states.** Include payment pending/failed, payment succeeded but entitlement delayed, enrolment already exists, email verification pending, Telegram unavailable, locked lesson, missing media, progress save failure and expired access.
    - Acceptance: each state explains what happened, whether the customer needs to act, whether a retry is safe, and how to reach support.

### P2 — Measure the experience rather than guessing

13. **Add a privacy-conscious customer journey scorecard.** Track funnel and product-health events with clear consent and retention rules:
    - public course detail viewed;
    - enquiry started/submitted and response time;
    - signup started/completed and email verified;
    - checkout started, provider-confirmed payment and entitlement granted;
    - first lesson opened/completed;
    - learner returned within 7 days;
    - course progress and completion;
    - support ticket opened, first response and resolution.
    
    Do not collect chart contents, trading account data or sensitive financial details for marketing analytics.

## Recommended implementation sequence

1. Fix product facts and remove dead-end or misleading CTAs.
2. Implement one reusable, abuse-resistant public enquiry workflow for CONSTRUCT and Live Classroom, with separate product identifiers and staff routing.
3. Verify production domain routing and the complete signup/enrolment/first-lesson journey on staging.
4. Implement the first-run orientation and learner-home improvements against real backend state.
5. Verify CONSTRUCT's course-plus-community entitlement lifecycle.
6. Run mobile and desktop acceptance passes, then add the journey scorecard.

## Minimum end-to-end acceptance journeys

- **Free learner:** public Trading Path page → create account → verify email → enrol without payment → open first lesson → complete an action/knowledge check → refresh → progress remains → return to the course and resume.
- **CONSTRUCT prospect:** view programme → inspect sample and terms → submit enquiry → receive confirmation → staff can see and follow up → prospect receives a human response.
- **CONSTRUCT buyer:** view accurate offer → start checkout → provider confirms payment by webhook → course entitlement and included community entitlement are granted exactly once → learner lands on orientation → first lesson is accessible.
- **Live Classroom prospect:** view six-week programme → submit enquiry → receive confirmation and verified next-intake details → staff can follow up.
- **Recovery:** simulate pending/failed payment, delayed entitlement, email verification delay, Telegram failure, a locked lesson and a failed progress save; confirm the customer sees a safe and actionable explanation.

## Boundaries

- Static previews and passing browser checks are not proof of live payment, email, session, progress, storage or Telegram behaviour.
- Do not merge to `main`; all proposed changes and PRs target `my-new-branch`.
- Do not expose paid course material, answer keys, instructor notes, private support data or internal operational payloads to public pages.
- Do not mark an enquiry, payment, community link, entitlement or progress action successful until the server confirms it.
