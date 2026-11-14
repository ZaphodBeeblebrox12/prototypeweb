# TradeThesis Admin Desk — Holistic Workflow Walkthrough V1

**Status:** First integrated six-domain design pass; owner review pending  
**Date:** 14 November 2026  
**Planning branch:** `admin-desk-redesign-planning`  
**Source baseline:** `my-new-branch`  
**Prototype:** `tradethesis_admin_holistic_workflow_v1.html`  
**Dataset:** 40 linked fictional records across six domains and the Notifications subsystem  
**Implementation status:** Static architecture walkthrough only. No application code, APIs, provider calls, jobs, notification sends or database writes were connected.

## 1. Purpose

The six domain mockups have each been designed individually. The next question is whether they behave as one coherent operating system when the same learner, payment, subscription, ticket, campaign, gift, job and provisioning operation are opened from different places.

This board is an integration and ownership test, not another Admin Desk landing page. It deliberately reuses the same fictional record IDs throughout seven journeys and a shared record register.

The walkthrough tests:
- canonical ownership: one record, one owning domain;
- cross-domain context and deep links;
- state transitions that must remain separate;
- role/permission-safe summaries;
- the difference between financial success, application access, provider execution and observed external membership;
- how Command Centre routes action without becoming the owner of the underlying record;
- where current source behaviour or source gaps should block premature implementation.

All people, emails, identifiers, amounts, coupon codes, timestamps, statuses, activity and record relationships in this prototype are invented sample data. It is not a live customer/admin console.

## 2. Top-level domains and ownership rule

| Top-level domain | Canonical ownership in the walkthrough | Main destinations |
|---|---|---|
| Command Centre | Cross-domain attention, prioritisation and routing only | Work queue, notification entry, Operations Timeline hand-offs |
| Academy | CourseImport, Course, CourseModule/Lesson, CourseOffer, CourseEntitlement, progress | Review/publish, catalogue, course detail, offer/access, learner progress |
| Customers | User, SupportTicket, TicketMessage, Customer 360 relationship view | Learners, ticket queue/detail, customer context |
| Revenue | Product, Plan, PlanPrice/GeoPlanPrice, PaymentIntent, Subscription, Refund, Invoice, Dispute | Payments, subscriptions, pricing, invoices, disputes, business |
| Growth | Campaign/Audience/recipient, attribution, Coupon/Redemption, Referral/Reward, GiftInvite, email Delivery/consent | Analytics, campaigns, promotions, referrals, gifts, Email Delivery |
| Platform | Job, PeriodicJob, ProvisioningOperation, ReconcileState, integration and audit/security evidence | Operations, jobs/scheduler, provisioning, integrations, audit/security, readiness |

**Notifications is a separate subsystem** used in the examples as a record owner for a member-facing Notification. It is not a seventh top-level domain, and it is not Command Centre work. A member's notification and an actionable staff work item may relate to the same business event, but they have separate audiences, state and permissions.

Core rule: another domain may display a concise, permission-safe summary and a link to the canonical owner record. It must not create a second editable copy or imply that the summary status is the underlying source status.

## 3. Fictional people and shared record set

Primary learner:
- **Maya Chen — USR-1042.** Buys an individual course, later purchases membership, has first-touch campaign attribution and a referral, is the intended recipient of a gift invitation, and raises a billing-support ticket.

Secondary actors:
- **Rohan Patel — USR-1008.** Refers Maya through code ROHA2048.
- **Dev Singh — USR-1177.** Requests community access through Support and is approved by an appropriately scoped reviewer.
- A staff operator creates a gift invitation and an authorised reviewer approves Dev's access request.

The register contains 40 sample records. IDs are stable across all journeys:

| ID | Record | Owner | Sample state |
|---|---|---|---|
| USR-1042 | Maya Chen | Customers | Active learner; primary actor |
| USR-1008 | Rohan Patel | Customers | Referrer |
| USR-1177 | Dev Singh | Customers | Support access requester |
| IMP-241 | Mini-course submission | Academy | Review → approved |
| CRS-017 | Reading Price Action | Academy | Published mini-course |
| PCA-014 | PlanCourseAccess mapping | Academy | Active membership inclusion |
| OFR-017 | Course sale offer | Academy | Active one-time offer |
| ENT-9001 | Course entitlement | Academy | Active direct purchase access |
| PLN-COURSE-017 | Hidden course Plan | Revenue | INR 2,499 base |
| PLN-MEMBER-01 | Membership Plan | Revenue | Active monthly Plan |
| PP-799 | Membership price snapshot | Revenue | INR 799 monthly |
| PLN-ACCESS-04 | Hidden access Plan | Revenue | Eligible for reviewer-scoped grant |
| PI-7001 | Course PaymentIntent | Revenue | Success · INR 2,499 |
| INV-7001 | Course invoice | Revenue | Issued snapshot |
| DSP-0091 | Provider dispute | Revenue | Funds withdrawn · still open |
| CAM-018 | Market Prep Week Campaign | Growth | Frozen audience; stub provider |
| ATTR-1042 | SignupAttribution | Growth | First touch: CAM-018 |
| MKT-1042 | MarketingPreference/Suppression context | Growth | Opted in; no global suppression |
| CR-018-1042 | CampaignRecipient | Growth | Sent by inspected stub path |
| DLY-018 | G1 Delivery | Growth | Sent · provider stub |
| COHORT20 | Campaign coupon | Growth | 20%; campaign-scoped; stackable with referral |
| REF-551 | Referral relationship | Growth | Completed after membership purchase |
| PI-7002 | Membership PaymentIntent | Revenue | Success · INR 799/month, referral + coupon snapshot |
| CRD-0702 | CouponRedemption | Growth | Finalized for PI-7002 |
| SUB-8102 | Membership Subscription | Revenue | Active |
| REW-552 | ReferralReward bucket | Growth | Pending · 72-hour delay · INR |
| GFT-0091 | GiftInvite | Growth | Pending; invite email failed |
| GST-019 | GiftSubscription | Revenue | Gift created; awaiting claim |
| LOG-7712 | Transactional EmailLog | Growth/Notifications subsystem | Failed gift invitation |
| TCK-4402 | Access-request SupportTicket | Customers | Pending review → approved |
| TCK-4410 | Billing SupportTicket | Customers | In progress → awaiting member |
| SUB-8114 | Access-grant Subscription | Revenue | Granted on ticket approval |
| JOB-8432 | Reconciliation Job | Platform | Succeeded · handler processed |
| PROV-8B21 | Maya community access operation | Platform | Unknown external state |
| PROV-8C14 | Dev community access operation | Platform | Unknown external state |
| JOB-8421 | Protected lesson video Job | Platform | Failed · 5/5 attempts |
| EVT-7001 | `academy.entitlement_granted` Event | Platform/event evidence | Recorded |
| AUD-201 | Support approval AuditLog | Platform | Recorded |
| SEC-401 | `login_failed` SecurityEvent | Platform | Restricted evidence |
| NOT-901 | Learner Notification | Notifications | Unread · member-facing |

The source owner of each record controls the actual detail and action permissions. The illustrative record register is a relationship test and not a proposed global search permission bypass.

## 4. Seven end-to-end journeys

### Journey 01 — Publish and sell a mini-course

**Path:** Academy → Revenue → Academy → Customers → Platform

1. `IMP-241` arrives for review. A reviewer inspects the import and approves it; returning to the editor requires feedback.
2. The canonical course `CRS-017` becomes Published after the approved publication service.
3. `OFR-017` links the course to hidden one-time Plan `PLN-COURSE-017` and its active one-time price.
4. Revenue PaymentIntent `PI-7001` succeeds after provider verification: INR 2,499 in the illustrative record.
5. `activate_paid_subscription` detects the CourseOffer and dispatches to `activate_course_payment`. It atomically claims the PaymentIntent as Success and grants `ENT-9001`.
6. The course-purchase path may enqueue personalised protected-video work. `JOB-8421` reaches Failed after five attempts; this does not rewrite the successful PaymentIntent or active CourseEntitlement.
7. Customer 360 for `USR-1042` shows the permission-safe course context and 6/18 lesson progress, with links to Academy entitlement and Revenue payment.

**Source-backed contract**
- CourseImport review and canonical publish are distinct from editing the current Course.
- A CourseOffer maps Course to a dedicated hidden Plan and active one-time price.
- Course purchase fulfilment is an atomic PaymentIntent claim plus CourseEntitlement grant, not a recurring membership Subscription.
- `activate_course_payment` writes an `academy.entitlement_granted` Event for a real purchase (or `academy.entitlement_simulated` for staging simulation).
- It can enqueue personalized protected-video jobs after the entitlement is granted. Job failure is not entitlement revocation.

**Important gap found during holistic review**
- Payment start computes and snapshots an optional coupon on the PaymentIntent before the CourseOffer activation branch. However, the inspected CourseOffer path returns through `activate_course_payment` before the ordinary membership branch that calls `redeem_coupon` and writes `CouponRedemption`.
- The course sample deliberately has **no coupon**. Whether course coupons should be disallowed or should produce a corresponding redemption needs a separate implementation/business-rule decision.
- The course-activation service records `academy.entitlement_granted`, not the `purchase.completed` Event used by the current Growth purchase analytics report. Course purchase analytics/attribution therefore cannot assume every paid course fulfilment emits that event.

**Checks**
- Published ≠ discoverable ≠ saleable ≠ accessible.
- Payment success ≠ course entitlement ≠ video processing success.
- A protected-video job error must not erase an active entitlement.
- Don't show a subscription row for a one-time course purchase.

### Journey 02 — Membership purchase and community access

**Path:** Revenue → Academy → Platform → Customers

1. Maya selects membership Plan `PLN-MEMBER-01` and price `PP-799`.
2. `PI-7002` is provider-verified Success.
3. Revenue creates/activates canonical membership `SUB-8102`.
4. Academy mapping `PCA-014` provides membership inclusion for course `CRS-017`; this is not a second direct-purchase entitlement.
5. Platform reconciliation opens `PROV-8B21`. External status is Unknown because membership could not be verified.
6. Customer 360 may show the active Subscription and a safe “external access awaiting verification” summary linking to Platform.

**Source-backed contract**
- Membership purchase is PaymentIntent → Subscription.
- Academy membership access is mediated by PlanCourseAccess where configured.
- External Telegram/Discord access is a later reconciliation/provisioning state and may be behind the commercial Subscription.

**Checks**
- An active Subscription does not prove the learner is in a Telegram channel or has a Discord role.
- Provisioning Unknown is not Failed.
- Do not offer an ordinary manual grant/retry button; current reconciliation probes membership, reuses the persisted invite link and has a six-hour resend throttle.

### Journey 03 — Campaign and referral-driven acquisition

**Path:** Growth → Customers → Revenue → Growth

1. Campaign `CAM-018` freezes its Audience and TemplateVersion. Its recipient record `CR-018-1042` is marked Sent by the inspected campaign sweep, which uses provider=stub.
2. `ATTR-1042` captures Maya's first-touch campaign context. Campaign-scoped coupon eligibility uses this authoritative SignupAttribution.
3. `REF-551` links Rohan (`USR-1008`) to Maya (`USR-1042`) via referral code ROHA2048.
4. `DLY-018` is the latest marketing Delivery in Sent state before membership purchase. The attribution service can assign last-touch credit to it, but a stub Sent state is not proof of external delivery or causality.
5. Membership checkout creates `PI-7002` with both the eligible referee referral discount and campaign coupon `COHORT20`. The sample coupon is campaign-scoped and configured stackable with referral.
6. Successful paid membership activation completes the Referral and creates `REW-552` as a pending, INR-denominated reward bucket with a 72-hour unlock delay, subject to unlock checks.
7. Successful membership activation also records `CRD-0702`, the CouponRedemption snapshot for COHORT20 with base/discount/final/currency values.

**Source-backed contract**
- First-touch SignupAttribution and last-touch marketing Delivery are two separate attribution rules.
- Referral referee checkout discount, referrer reward and Coupon are different benefits.
- Coupon validation can require campaign first-touch match, plan-tier eligibility, date validity, usage caps and explicit referral stacking permission.
- Ordinary membership activation records coupon redemption after successful activation; CouponRedemption is not another payment.
- Referral completion can create a reward bucket. It is not immediately available to spend.

**Important gap found**
- The inspected reward-unlock service checks PaymentIntent states `refunded` and `canceled`, but PaymentIntent defines Pending, Success and Failed. This is a source mismatch that must be fixed/tested before relying on automatic reward unlock.
- A missing triggering Subscription leaves a reward pending. `UserRewardBalance` currently sums cent amounts across currencies; UI must display per-currency balances.
- Optional referee bonus credit helper currently logs only; it is not a persisted balance/ledger and is not included as an earned credit in the sample.

**Checks**
- Referral discount ≠ coupon discount ≠ referrer reward.
- Campaign stub Sent ≠ real provider delivery.
- The sample coupon stacks only because `stackable_with_referral` is explicitly true.
- Reward Pending stays Pending until reliable unlock conditions are satisfied.

### Journey 04 — Support access request and reviewer approval

**Path:** Customers → Revenue → Platform → Customers

1. `TCK-4402` is submitted by fictional learner Dev Singh (`USR-1177`).
2. Reviewer scope is checked against the current ticket and selected Plan's approver scope. An eligible hidden Plan `PLN-ACCESS-04` is selected.
3. The canonical `approve_ticket` service grants `SUB-8114`, writes ticket state/reviewer and enqueues reconciliation inside the same transaction.
4. The durable `JOB-8432` executes the reconcile handler and reaches Succeeded.
5. The external `PROV-8C14` state remains Unknown because external membership has not been verified.
6. Ticket `TCK-4402` may be Approved while external community provisioning remains unresolved. The member notification is a separate channel outcome.

**Source-backed contract**
- Ticket visibility and reviewability depend on staff state, superuser exception and plan/affiliate-plan approver rules.
- Access-request approval requires a hidden Plan.
- Subscription grant, job enqueue and ticket state are transactional: enqueue failure rolls back the grant and ticket approval.
- The reconciliation Job and the ProvisioningOperation are separate lifecycle records.
- Public reply and private internal note are separate TicketMessage visibility types.

**Checks**
- Access-request approval is not a purchase.
- Job Succeeded means the handler completed, not that the remote member joined.
- External provisioning can remain Unknown after the ticket is Approved.
- A Customer 360 action must not bypass the ticket approval service.

### Journey 05 — Billing issue, refund and dispute

**Path:** Customers → Revenue → Command Centre routing → Customers

1. Maya opens billing ticket `TCK-4410`.
2. Revenue PaymentIntent `PI-7001` and Invoice `INV-7001` are inspected from their canonical Revenue details.
3. Provider dispute `DSP-0091` has funds withdrawn, but remains open.
4. No Refund row exists yet in the sample. “Funds withdrawn” is not equivalent to confirmed loss.
5. Platform evidence `AUD-201` and source-specific domain Events may be linked from the timeline; they remain distinct records.
6. Support ticket moves to Awaiting Member after a public response. The ticket work state is independent from payment/dispute state.

**Source-backed contract**
- PaymentIntent remains Success after refund is recorded; Refund is a separate idempotent ledger.
- Partial refund leaves access unchanged; full cumulative refund follows canonical policy and revokes/cancels the affected course entitlement or Subscription.
- Dispute opened/funds-withdrawn is not final loss and does not revoke access.
- Dispute Won clears dispute flags and leaves access unchanged.
- Confirmed Lost/Accepted invokes the exactly-once chargeback consequence.
- Manual full refund recording in Django Admin is used only after processing the refund at the provider; it does not initiate a PSP refund.

**Checks**
- Ticket resolution ≠ refund processed ≠ dispute closed.
- Funds withdrawn ≠ confirmed loss.
- Don't add a duplicate manual refund or access revocation action on the Support ticket.

### Journey 06 — Gift invitation and email failure

**Path:** Growth → Customers → Revenue → Growth

1. Staff creates `GST-019`, a GiftSubscription, for Maya's intended email.
2. `GFT-0091` is created as a token-based GiftInvite, with 30-day expiry and email binding.
3. Transactional `EmailLog LOG-7712` records Failed.
4. Customer 360 may show an invite context if permitted, but must not mark an active Subscription as granted solely because the invite exists.
5. Maya's existing `SUB-8102` remains unchanged until a successful claim.
6. The sample stops with `GFT-0091` still Pending and no claim, no extension and no new access.

**Source-backed contract**
- GiftService creates GiftSubscription + GiftInvite; email send is a separate step.
- Gift can exist even when invitation email fails; current staff success page may expose the claim URL to the sending operator in that specific context.
- Recipient email must match the invite, self-gifting is blocked and token flow can extend an existing active Subscription when successfully claimed.
- No staff resend UI was verified; modern token invite and legacy gift_code claim remain separate.

**Checks**
- Gift creation ≠ email accepted ≠ recipient claim ≠ resulting Subscription.
- Pending Invite does not extend the subscription.
- Do not expose raw tokens/URLs in broad register/search.
- Do not invent a resend action absent an approved permission/service design.

### Journey 07 — Email delivery and operational evidence

**Path:** Growth → Platform → Customers → Command Centre

1. `CR-018-1042` is a frozen CampaignRecipient marked Sent by the inspected provider=stub send sweep.
2. `DLY-018` is the linked G1 Delivery. The Resend webhook path may update Delivery state where its provider/message ID matches.
3. `MKT-1042` shows an opted-in marketing preference with no global suppression. Transactional EmailLog has separate gating.
4. Resend callback updates Delivery directly; Stripe/Razorpay provider events use a durable WebhookEvent + Job; Telegram webhook has a separate secret-header path and no durable inbox was verified.
5. Customer 360 may show permission-safe communication context; it must not expose another recipient's information or raw payloads.
6. Command Centre routes only an actionable exception to its owning Growth/Platform destination. The sample has no new staff notification record. `NOT-901` is a learner-facing Notification owned by the Notifications subsystem, not staff work.

**Checks**
- CampaignRecipient Sent ≠ provider-delivered.
- G1 Delivery ≠ legacy transactional EmailLog.
- Resend webhook updates Delivery, not EmailLog.
- Marketing opt-in/suppression and transactional email are different.
- Member Notification read state ≠ staff work status or issue resolution.
- A single visual timeline must retain source type, visibility and provenance.

## 5. Cross-domain issues discovered

| Issue | Source-level finding | Design consequence | Before implementation |
|---|---|---|---|
| Course coupon lifecycle | Payment start can snapshot a coupon on the CourseOffer PaymentIntent; CourseOffer activation returns through Academy before ordinary membership coupon-redemption code | Sample course PI is coupon-free. CouponRedemption is shown on membership PI-7002 only | Decide whether course coupons are disallowed or require dedicated redemption logic and tests |
| Course purchase analytics | `activate_course_payment` records academy entitlement Event, not `purchase.completed` | Do not assume current Growth purchase analytics counts one-time course payments | Define course-purchase analytics and attribution event contract |
| Reward unlock | Reward service queries PaymentIntent states absent from PaymentIntent choices | Pending reward remains visibly pending in sample | Correct state/refund test against canonical Refund/PaymentIntent fields and add tests |
| Reward currency | Helper sums cents across currencies | UI uses currency-specific buckets; no cross-currency wallet total | Reconcile query/service and aggregation |
| Campaign delivery | G2 campaign sweep uses provider stub, marks Delivery Sent | Sample marks Sent with provider stub; no delivered claim | Define/test a real provider path and metrics reconciliation |
| Staff/member notifications | Notification is user-addressed; Command Centre is staff action queue | NOT-901 appears as member-facing, not staff work | Complete notification event-source and staff-recipient mapping |
| Reconciliation Job vs external operation | Worker handler can finish while ProvisioningOperation remains Unknown | JOB-8432 Succeeded and PROV-8C14 Unknown shown together | Define operator-visible convergence status and safe remediation contract |
| Policy and security evidence | AuditLog/published PolicyVersion enforcement gaps; IsRoleAdmin accepts any staff | Migration boundary holds these controls in Advanced Administration | Hardening review: audit append-only/privacy, policy content lock, permissions maker/checker |

## 6. Permission and visibility contract

The prototype does not execute permission logic. It documents where the real application must enforce it:
- Command Centre counts, search and notifications must use current user's permitted scope.
- Academy review and course-content data retain Academy permissions.
- Customers support ticket lists/details retain plan/affiliate-plan reviewer scope; internal notes never become public activity.
- Revenue payments, subscriptions, invoice, refund and dispute data retain their model and route permissions.
- Growth campaign/recipient, referral and email data retain owner-domain permissions; raw recipient and suppression details need deliberate restrictions.
- Platform job/provisioning, event, audit and security summary panels retain each existing model permission gate independently.
- Staff and permission screens must not infer access from a single app-role badge.
- A UI that hides an action is never a substitute for server-side authorization.

The sample record register is for relationship testing. It does not establish that every staff member can see all 40 records.

## 7. Prototype behaviour and validation

The HTML prototype contains:
- M50 Overview and architecture map.
- Seven journey pages with linked source-derived steps.
- Shared 40-record register with search and canonical-owner filter.
- Detail previews for linked IDs.
- Six-domain ownership and lifecycle guardrails.
- Responsive mobile drawer.

Browser smoke test (14 November 2026):
- **159/159 checks passed.**
- All seven journey pages and their linked Inspect previews open/close.
- Shared record register shows 40 illustrative records.
- Search and Revenue-owner filters work.
- Mobile drawer opens and closes after navigation.
- All 9 top-level screens/views fit a 390px viewport with no horizontal overflow.
- Desktop 1440px shell geometry is checked: 250px sidebar, main begins at x=250, main/content remains full width.
- No JavaScript page errors or browser console errors in exercised flows.

Not tested/claimed:
- Authenticated staging UI, real staff users and object/model permissions.
- Any actual API, job, provider send, purchase, refund, gift claim, role grant or provisioning action.
- Real-time data consistency, live event feeds or production polling.
- Keyboard-only, screen-reader, contrast certification or exhaustive browser testing.

## 8. Owner review prompts

1. Is the six-domain ownership and same-learner record map coherent?
2. Does the course purchase path need an explicit coupon rule before the first implementation slice?
3. Should course purchases write a unified purchase event for analytics/attribution, or retain the current Academy entitlement event and add an analytics bridge?
4. Is separating campaign Sent, provider Delivery, EmailLog and Notification sufficiently clear?
5. Does the access-request journey correctly show the ticket Approved while external provisioning remains Unknown?
6. Does the billing/dispute journey preserve the distinction between funds withdrawn, final dispute loss, refunds and ticket resolution?
7. Is the gift-email failure outcome understandable without adding a resend button?
8. Which cross-domain contexts should be visible in Customer 360, with which independent permission gates?
9. Which issues in Section 5 must block a first implementation slice?
10. Which end-to-end journeys should be included in implementation acceptance tests?

This walkthrough is a design contract for discussion. It does not authorise implementation.
