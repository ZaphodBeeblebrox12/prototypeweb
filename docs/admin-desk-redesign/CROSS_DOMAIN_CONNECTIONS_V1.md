# TradeThesis Admin Desk — Cross-Domain Connections v1

**Status:** First-pass operating model  
**Branch:** admin-desk-redesign-planning  
**Purpose:** Define how the six workspaces share records and move operators through end-to-end work without duplicating data or responsibilities.

## 1. Core principle

The six domains are separate workspaces over connected business records. They are not six independent systems.

A record has one canonical owner and one source of truth. Other domains may show a concise context panel, metric or event with a link to the canonical record. They must not create competing editable copies.

## 2. Record relationship map

The central relationship is the learner account, but the domain records around it remain distinct:

- Customers owns the User record and the support relationship.
- Academy owns Course, CourseModule, Lesson, CourseImport, CourseOffer, CourseEntitlement, CourseEntitlementEvent and LessonProgress.
- Revenue owns Product, Plan, PlanPrice, GeoPlanPrice, Subscription, PaymentIntent, Refund and Invoice.
- Growth owns ReferralCode, Referral, ReferralReward, reward ledger, GiftInvite, PendingGiftClaim, MarketingPreference, Suppression and performance reporting.
- Platform owns Job, PeriodicJob, ProvisioningOperation, AuditLog, SecurityEvent and operational integration state.
- Command Centre is an aggregation and navigation layer. It does not own the underlying business record.

Key record links verified in the source baseline:

- CourseOffer has a Course relationship and a one-to-one Plan relationship.
- CourseEntitlement links User, Course, optional CourseOffer and optional PaymentIntent; it can record purchase/admin/migration/complimentary source and access dates.
- Verified fulfilment path: `payment_confirm` calls `activate_paid_subscription`; a matching CourseOffer dispatches to `apps.academy.services.activate_course_payment`, which atomically claims the verified PaymentIntent and grants/links the CourseEntitlement.
- PlanCourseAccess links a Plan to a Course for membership-plan inclusion.
- Subscription links User, Plan, Product and its selected price snapshot; it records gift/admin-grant/trial provenance.
- PaymentIntent links User and Plan, stores the amount/currency/provider/price and tax snapshots, and can store referral discount provenance and refund/chargeback state.
- SupportTicket links User, optional AffiliateLink and Plan, and stores reviewer assignment, priority, due time and status.
- Referral links a referrer User and a referred User. ReferralReward is linked to the referral and can connect to a triggering subscription.
- GiftInvite/PendingGiftClaim resolve to a recipient/claim lifecycle; gifted Subscription carries gift provenance.
- ProvisioningOperation stores a user identifier and external channel operation state. Job is the durable background-work record.
- Notification is addressed to one user; it can link to a source record by URL/metadata.
- AuditLog links an actor to an action/object type/object ID.

## 3. Canonical ownership and visibility matrix

| Canonical record | Owning domain | Contextual surfaces |
|---|---|---|
| Learner account | Customers | Customer 360, ticket detail, Academy, Revenue, Growth, Platform |
| Support ticket/message | Customers | Command Centre, Customer 360, Operations Timeline |
| Course/content/import | Academy | Command Centre, Customer 360 progress, SEO, Revenue offer context |
| CourseOffer | Academy | Revenue linked Plan/price, Customer 360 payment context |
| Product/Plan/prices | Revenue | Academy offers/membership mapping, Customers subscription context, Growth purchase attribution |
| Subscription/history | Revenue | Customer 360, Academy membership access, Growth gifts/rewards |
| PaymentIntent/refund/invoice/dispute | Revenue | Customer 360, Support ticket, Command Centre |
| Direct course entitlement/progress | Academy | Customer 360, Revenue purchase context |
| Referral/reward/gift | Growth | Customers, Revenue, Command Centre only for actionable exceptions |
| Email log/suppression | Growth | Customer context, Platform provider health, Command Centre actionable exceptions |
| Job/provisioning operation | Platform | Command Centre, Customer 360 safe summary, Support ticket context |
| Notification | Recipient's notification feed | Command Centre entry point; source domain owns action |
| Audit/security/domain event | Platform or originating event source | Command Centre timeline and relevant record detail |

## 4. Cross-domain hand-off rules

### 4.1 Command Centre is the router, not the resolver

The Command Centre may rank and summarise cross-domain work. It must link to the owner domain for the actual action.

Examples:
- Course submission awaiting review → Academy approval detail.
- First-response SLA overdue → Customers ticket detail.
- Payment status exception → Revenue payment detail.
- Missing or inconsistent learner course access → Academy entitlement view, with linked Revenue payment.
- Unknown external provisioning state → Platform operation detail, with a link to Customers account/ticket.
- Email delivery failure requiring follow-up → Growth email detail, optionally linked to Platform job/provider event.

### 4.2 Customer 360 is a read-oriented relationship hub

Customer 360 gathers permission-scoped facts from multiple domains. It should not become the place where every underlying object is edited.

Examples:
- Payment row opens Revenue payment detail.
- Subscription row opens Revenue subscription detail.
- Course entitlement opens Academy access detail.
- Ticket opens Customers support detail.
- Provisioning state opens Platform operation detail.
- Referral relationship opens Growth referral detail.

### 4.3 Cross-domain summary versus canonical action

A contextual panel may show status, key date, amount, count or short description only if that field is available to the current user. Any edit or sensitive action should take place at the canonical owner destination unless the existing workflow expressly supports it in the current context.

### 4.4 One activity stream does not mean one event type

Keep these separate and label them:
- Business domain event.
- Staff notification.
- User notification.
- Audit action.
- Security event.
- Durable job status.
- External provisioning state.
- Public support message.
- Internal support note.

A single UI timeline can render several sources, but must preserve event type, visibility and provenance. Internal notes must never appear as public/member activity.

## 5. Important lifecycle distinctions

### 5.1 Course publication versus public discoverability versus saleability versus access

These are four distinct checks:

1. **Published content:** Course, modules and lessons have the relevant published states.
2. **Discoverability:** global indexing, course SEO flag, catalogue role, published lesson presence and public content checks permit indexability.
3. **Saleability:** an individual CourseOffer has its required hidden Plan and active one-time price, and the linked course is published with Paid/Mixed access type.
4. **Learner access:** a direct CourseEntitlement is active at the relevant time, or a current Subscription plan includes the course through PlanCourseAccess.

Do not collapse these into one green “course active” status.

### 5.2 Course purchase versus membership subscription

**Individual course purchase**
Course → CourseOffer → dedicated hidden Plan → one-time PlanPrice/GeoPlanPrice → PaymentIntent → provider verification → `activate_course_payment` (atomic claim + entitlement grant) → CourseEntitlement → LessonProgress.

**Recurring membership**
Product → Plan → recurring PlanPrice/GeoPlanPrice → PaymentIntent → Subscription → PlanCourseAccess → course availability/progress.

These may show together in a member's learning view, but their commercial and access records are different.

### 5.3 Access-request approval versus course purchase

**Access request**
SupportTicket → eligible hidden Plan (possibly selected from AffiliateLink default) → authorised reviewer → approve_ticket service → subscription grant → durable reconciliation Job → external provisioning where configured → notification to member.

**Course purchase**
CourseOffer → PaymentIntent → provider verification → `activate_paid_subscription` dispatches the CourseOffer path to `activate_course_payment` → atomic CourseEntitlement grant.

An access-request approval must not be rendered as a course purchase. It grants a hidden plan and may lead to subscription/community access according to the existing plan configuration.

### 5.4 Payment success versus access completion

Payment is a financial state. Subscription or course entitlement is an application-access state. Community provisioning is an external side-effect state. They can progress at different times and must be shown independently.

### 5.5 Notification read state versus operational resolution

Marking a Notification read changes its read state. It does not resolve the linked ticket, payment, job or provisioning operation.

### 5.6 Email delivery versus in-app notification

EmailLog records email status and webhook delivery/bounce/complaint evidence. Notification is an in-app message addressed to a user. They may be created from one business event, but one must not be used as proof of the other channel's success.

### 5.7 Referral reward versus discount versus gift

- Referral discount is purchase provenance on a payment.
- Referral reward is an earned ledger balance with eligibility/unlock status.
- Gift is an invite/claim lifecycle that can result in a gifted subscription.
These records can relate to the same learner journey without being interchangeable.

## 6. End-to-end workflow tests

Use one coherent fictional record set through the prototype. Every screen should resolve the same IDs, dates and states when a record is opened from a different domain.

### Test 1 — Publish and sell a mini-course

Academy Builder → CourseImport review → approval/publish → catalogue/SEO check → CourseOffer setup → Revenue hidden Plan/one-time price → successful PaymentIntent → Academy CourseEntitlement → Customer 360 progress.

Checks:
- The source-verified one-time payment fulfilment path is represented accurately: provider verification, atomic PaymentIntent claim and entitlement grant.
- New versus revision submission is clear.
- Return requires reviewer feedback.
- Test-import permanent cleanup is separate.
- Offer constraints are visible before activation.
- Payment and learner access are distinct.

### Test 2 — Membership purchase and community access

Revenue Plan/price → PaymentIntent → Subscription activation → Academy PlanCourseAccess → Customer 360 → Platform provisioning → Command Centre only if an actionable exception occurs.

Checks:
- Historical price snapshot remains unchanged.
- Geo price used is visible.
- Course inclusion is not shown as a direct purchase entitlement.
- External provisioning can be pending/unknown after payment success.

### Test 3 — Referral-driven acquisition

Growth Referral → referred Customer account → Revenue PaymentIntent with referral attribution/discount → ReferralReward pending/unlock → reward ledger → Customer 360 and Growth analytics.

Checks:
- Discount and reward are separately represented.
- Reward is not available before its actual unlock conditions.
- Refund/chargeback state is visible to reward operations where the service uses it.

### Test 4 — Support access request

Customers ticket queue → ticket detail → Customer 360 → eligible hidden Plan → approval service → Subscription grant + reconciliation Job → Platform provisioning → user notification/email/Telegram → Customer 360 updated.

Checks:
- Ticket reviewer scope is preserved.
- Plan-specific reviewer permissions apply.
- Approval and provisioning are separate milestones.
- Failure in enqueue prevents the subscription grant/ticket approval from partially committing.

### Test 5 — Billing issue with refund/dispute

Customers ticket → Customer 360 → Revenue PaymentIntent → Invoice/Refund/Dispute detail → support response/status transition → audit record.

Checks:
- Payment source record is canonical.
- Internal note and public reply are visibly distinct.
- Refund/chargeback status isn't confused with ticket resolution.

### Test 6 — Community access failure

Command Centre exception → Platform ProvisioningOperation → Customers account/Customer 360 → Support ticket if member needs help → job/operation history → audit trail.

Checks:
- Unknown external state is not treated as a safe retry.
- Provider IDs/invite links are not leaked into broad queues.
- Only verified safe service actions are offered.

### Test 7 — Email delivery failure

Growth EmailLog → webhook/bounce/complaint state → suppression/preference context → Customers learner if relevant → Platform durable job only if correlated by source evidence → Command Centre only if action is required.

Checks:
- queued/sent/bounced/complaint status definitions are clear.
- Transactional and marketing preference semantics remain separate.
- Suppression evidence cannot be casually deleted.

## 7. Navigation and state contract

Before a badge, count or alert appears in the shell, document:

- Canonical source model/query.
- Statuses included/excluded.
- Time window.
- User permission scope.
- Whether the count means unread, actionable, overdue, failed or merely recent.
- Refresh/polling method.
- Destination and applied filter.
- Whether the underlying record has an assigned owner.

Before a cross-domain detail link is created, document:

- Source record and destination record.
- Whether a direct foreign key exists or the relationship is derived.
- Which fields the viewer may see.
- Whether the destination is a canonical page or contextual preview.
- Return path behaviour.

## 8. Open technical/design questions

- Full role/group and model permission map for all six domains.
- Whether staff My Work expands beyond current support assignments.
- Complete event-source map for staff notifications and operational alerts.
- Search engine/index strategy and permission-safe global search.
- Exact campaign/promotion schema and attribution.
- Full payment/refund/dispute action and confirmation rules.
- Which job/provisioning operations can be retried safely by staff.
- Whether any customer-facing activity event can be shared with internal audit without leaking notes or security metadata.
- Performance/query budgets for cross-domain overview counts and Customer 360 aggregation.
- Migration order and parity requirements for Django Admin features.

## 9. Design acceptance

The holistic prototype is ready for review when:

- Each record has one canonical owner.
- The same fictional entity is recognisable across every domain.
- Every cross-link opens a real destination concept and preserves context.
- Course publication, SEO, saleability and access remain distinct.
- Course purchase, membership subscription and support access grant remain distinct.
- Payment, application access and external provisioning remain distinct.
- Notification read state does not change work state.
- Public/internal support messages remain separate.
- Role permissions are respected in counts, search, linked panels and details.
- No mockup implies an action or route already exists when it is proposed.

This document is a design contract for future mockups. It does not authorise implementation.


## 10. Verified one-time course purchase implementation path

The current source baseline confirms this specific sequence:

1. The checkout path detects a CourseOffer by the selected Plan and enforces saleability and access checks.
2. It creates a PaymentIntent with a one-time price snapshot and identifies the product type as a course.
3. `payment_confirm` verifies the provider's payment state.
4. It calls `activate_paid_subscription`.
5. `activate_paid_subscription` detects the matching CourseOffer and dispatches to `apps.academy.services.activate_course_payment`.
6. The atomic course payment service claims the PaymentIntent as successful and calls the entitlement grant service with Purchase source and the linked PaymentIntent.
7. It records the entitlement event/domain event and queues personalised-video work when the entitlement is newly created. A non-simulated purchase receipt is attempted after commit.

This confirms the intended direct course purchase path in the source baseline. It does not mean membership subscriptions or access-request approvals use the same entitlement path; those remain separate flows.


## 11. Customer identity and support workflow contract

The Customers screen design is grounded in these source rules:

- The general learner directory excludes `is_staff` and `is_superuser` accounts. A staff/superuser requester can be resolved only through a ticket visible to the current reviewer, and that internal profile is restricted to identity plus reviewer-visible support history.
- Support queue, counts and ticket detail use the same reviewer-scope logic. A configured Plan `ticket_approvers` list restricts access; an empty list retains current any-staff behaviour; superusers retain their established wider scope.
- First-response SLA targets are 2h / 8h / 24h / 72h for Urgent / High / Normal / Low. A response timestamp stops the first-response-overdue calculation; an Awaiting Member ticket with a recorded first response is not first-response-overdue.
- A staff public reply is member-visible, append-only, changes an open ticket to Awaiting Member and records first response if not already set. An internal `TicketMessage` is append-only, private and does not itself notify the member.
- The reviewer/resolution `admin_notes` summary is separate from private internal `TicketMessage`. Do not use one generic “note” label for both.
- Access-request approval can grant a hidden subscription Plan and enqueue reconciliation atomically; Billing/Technical approval resolves a ticket without a plan grant.
- Customer 360's Academy, Revenue, subscription, invoice and security panels are independently permission-gated. Internal staff requester profiles do not show learner commercial, course, community or security records.
- Customer 360 activity includes public support conversation, but excludes internal ticket notes and raw security/payment-provider identifiers.

The Customers prototype keeps these boundaries visible and links to Academy, Revenue and Platform for canonical record work.


## 12. Revenue record and lifecycle contract

Revenue screen design is grounded in these distinctions:

- PaymentIntent is the transaction snapshot; Refund is a separate append-only ledger row. A refunded PaymentIntent retains its original successful status.
- A simulated PaymentIntent success is not money collected.
- Partial refund leaves the associated application access unchanged under the current policy. A cumulative full refund cancels the relevant paid Subscription or revokes a direct course entitlement through the canonical service.
- A full manual refund record is available today only through a Django Admin PaymentIntent action and must be used after the provider refund has already been processed. It does not initiate a Stripe/Razorpay refund. The current Admin Desk finance page remains read-only.
- Subscription is an application access record, not proof of a payment. Its purchased price/currency snapshot is immutable. Product-level active subscription rules are distinct from CourseEntitlement.
- Plan and price configuration are currently managed through Django Admin. Country-specific GeoPlanPrice overrides region overrides, which override global base PlanPrice. Geo pricing is not a second base price; one active global base row per Plan+interval is allowed.
- Invoice is an immutable snapshot generated from a verified payment. Changing BillingSettings affects future invoices only.
- Dispute is a separate case state machine linked to PaymentIntent. Opening or funds-withdrawn events are not final outcomes and do not revoke access.
- Won clears chargeback state and leaves access unchanged. Confirmed Lost/Accepted calls the canonical exactly-once chargeback action, which cancels the affected Subscription or revokes the affected course entitlement. Do not add a second independent revoke button.
- Dispute evidence packages are content-hashed; a submitted package is immutable. The application's submit action records an external provider submission reference. It does not upload evidence to the PSP.
- BillingSettings tax calculation is currently a single fixed percentage, not a jurisdiction-aware GST/place-of-supply engine. Tax is disabled by default and the first enable requires explicit accountant confirmation.

### Revenue end-to-end validation sequence

1. Academy CourseOffer → Revenue dedicated hidden Plan/one-time price → PaymentIntent → provider verification → Academy CourseEntitlement.
2. Revenue membership Plan/price → PaymentIntent → Subscription → Academy membership access where supported → Platform provisioning if configured.
3. Provider-side refund → Refund ledger row → full/partial policy → affected Subscription/Entitlement consequence → reconciliation where required.
4. PaymentIntent dispute flag → Dispute evidence case → external submission reference → final outcome → exactly-once access effect only for confirmed Lost/Accepted.
5. Revenue Plan/price configuration → later checkout uses country/region/global resolution → PaymentIntent/Subscription preserve the selected historical price snapshot.
6. BillingSettings updates → future invoice snapshots only; existing invoices remain unchanged.

All hand-offs must open the canonical record. Customer 360 may show permission-safe context; it does not replace Revenue detail.


## 13. Growth record and lifecycle contract

Growth has its own acquisition/conversion and communication provenance, but it does not own the underlying learner payment, subscription, course or access records.

Key contracts:
- `SignupAttribution` is first-touch UTM + optional referring Campaign; first touch wins.
- Last-touch email credit is the most recent marketing `Delivery` in SENT state before purchase, linked through CampaignRecipient or AutomationRun. It is not proof of message read or causality.
- `CampaignRecipient` is the frozen schedule-time audience snapshot. `Campaign` model state and recipient state are not the same as a provider's Delivery state.
- G2 send sweep uses provider=stub and marks Delivery SENT. This must not be interpreted as real provider send or delivery. Telegram/in-product CampaignAction records are staged and not wired into the campaign send sweep.
- `Coupon` is checkout eligibility/configuration; `CouponRedemption` records the discount/base/final/currency snapshot after successful activation. Revenue PaymentIntent remains the transaction record.
- ReferralCode/Referral are attribution relationships. Referee checkout discount, referrer ReferralReward and optional referee bonus are separate benefits.
- ReferralReward is a currency-bearing bucket. UI totals must remain separated by currency; do not sum cents across INR/USD/EUR.
- Reward unlocking currently checks PaymentIntent statuses that do not exist in the PaymentIntent choice set; this requires a source fix before treating automatic unlock as authoritative. Missing triggering subscription leaves reward pending.
- Optional referee bonus helper currently logs only and does not persist an amount or ledger entry. Do not state that the bonus was credited.
- GiftInvite is the intended-recipient claim token lifecycle; resulting Subscription is Revenue-owned. Invite/email success and subscription state are separate.
- MarketingPreference opt-in defaults false; any global unsubscribe/bounce/complaint suppression overrides opt-in. Transactional EmailLog is not governed by the same marketing preference gate.
- G1 Delivery and legacy EmailLog are separate ledgers. Resend webhook updates Delivery, not EmailLog.
- TemplateVersion is an immutable snapshot; Campaign and Automation reference the frozen version.
- AffiliateCommission is Growth accounting, not a payment. Its Paid state is not proof of an external transfer.

### Growth end-to-end validation sequence

1. First-touch UTM/referring Campaign → SignupAttribution → campaign/affiliate attribution context → Customers learner record.
2. Campaign schedule → frozen CampaignRecipient snapshot → stub or real provider Delivery depending on verified provider → last-touch attribution → purchase.completed Event → Revenue PaymentIntent/Subscription.
3. Referral code capture → Referral pending → eligible paid subscription purchase → Referral completed → referee discount snapshot and referrer reward bucket → unlock validation → per-currency credited reward → FIFO debit/subscription extension.
4. Coupon eligibility → authoritative SignupAttribution campaign scope, plan tier, validity and stack caps → PaymentIntent coupon snapshot → CouponRedemption after successful activation.
5. Gift created → GiftSubscription + token GiftInvite → transactional EmailLog send result → email-matched claim → Revenue Subscription → Customers Customer 360.
6. Marketing opt-in check + global suppression → G1 Delivery eligibility; transactional EmailLog remains separately governed.
7. Durable Event → AutomationRun → delayed fire-time eligibility re-check → immutable TemplateVersion → idempotent Delivery.
8. Affiliate first-touch attribution → canonical Revenue PaymentIntent → one AffiliateCommission per affiliate/payment → controlled internal state transitions; payout rail is not verified.

All cross-links must open the canonical record in Customers, Revenue, Academy or Platform. Growth may display source-backed context but must not create duplicate editable copies.


## 14. Platform record and lifecycle contract

Platform is the operations/governance domain. It provides source-backed status and safe links, but it does not take ownership of customer, payment, subscription, course, campaign or support records.

Key contracts:
- Durable Job is worker-owned execution state. It is not editable business state and should not have an ordinary staff retry/replay/delete action without a new explicit safe-service contract.
- PeriodicJob is a separate lightweight scheduler configuration/state row. Its interval, enabled flag and API call budget are not the same as Job attempts/backoff.
- A scheduler reservation/last_run_at is not proof of successful completion; use last_status/error and any separate worker evidence.
- ReconcileState desired-state version, ProvisioningOperation external mutation lifecycle, UserChannelAssignment entitlement mapping and ChannelMembershipSnapshot observed membership are distinct.
- ProvisioningOperation UNKNOWN means the remote outcome could not be verified. It is not Failed. Do not send another invitation or claim member absence unless a subsequent membership probe returns a definite False.
- The existing provisioning recovery uses the stored invite link where possible and an atomic six-hour resend throttle. The control/admin channel cannot be a subscriber target.
- BotRuntimeState is legacy self-registered bridge diagnostic data. Native Telegram access currently calls Telegram Bot API directly from Django using BotConfig. Do not treat legacy bridge heartbeat as current native Telegram health.
- Google Drive OAuth belongs to Academy course-content administration; keep its credential/editor flow in Academy.
- Stripe/Razorpay WebhookEvent is durable and idempotent. On first receipt it enqueues process_webhook_event; duplicate provider event delivery reuses the same event row. Business mutation happens through the payment processor/service.
- Resend webhook updates G1 Delivery state; it does not create a generic webhook inbox row and does not update transactional EmailLog. Telegram webhook evidence is another separate path; no durable event inbox was verified.
- /health/ only verifies a SELECT 1 against the primary database. It does not test a worker, periodic scheduler, provider, storage, email, webhook or backup/restore.
- Runtime readiness checks inspect configuration presence, not successful authentication or an end-to-end provider transaction.
- AuditLog, SecurityEvent, BotAccessAudit, Event, WebhookEvent and PolicyAcceptance must remain distinct evidence sources. SecurityEvent and PolicyAcceptance have model-level write-once/append-only guards; AuditLog did not in the inspected source.
- Published PolicyVersion is intended as versioned immutable legal evidence, but the inspected model/admin path does not fully lock published content against changes. Treat that as an engineering hardening item.
- Staff access combines active account state, is_staff, application role, staff approval, superuser and Django Groups/model permissions. The IsRoleAdmin API class permission includes any is_staff user; do not collapse the source model into a clean role matrix before a complete audit.

### Platform end-to-end validation sequence

1. Revenue provider webhook → signature verification → idempotent WebhookEvent → durable process_webhook_event Job → canonical PaymentIntent/Refund/Dispute service → Revenue subscription/course access consequence.
2. Revenue Subscription/Academy Course entitlement → ReconcileState desired version → durable reconcile Job → ProvisioningOperation → external Telegram/Discord API → verified membership/role result → BotAccessAudit and safe operational timeline.
3. PeriodicJob becomes due → scheduler reserves it → registered light handler executes within configured budget → last_status/error/cursor records → Operations Timeline summary.
4. Worker crashes with Running lock → reaper resets stale Job to Pending; long-running video lease heartbeat reduces false stale detection.
5. SecurityEvent/AuditLog/domain Event/WebhookEvent → Audit & Security view with individual source type and permission filtering; raw IP, UA and provider payload stay restricted.
6. Active PolicyVersion → exact PolicyAcceptance at checkout → Revenue payment/dispute evidence; preserve version identity and acceptance time.
7. Staff approval request → staff-approval API → existing class-level IsRoleAdmin gate (currently admits is_staff/superuser as well as application Admin) → audited role change; redesign only after gate and maker/checker rules are approved.

All cross-links resolve to the canonical owner domain. Platform should not become an alternate payment, subscription, account-ban, course-entitlement or support-action interface.


## 15. Holistic six-domain walkthrough contract

The six domains are now connected in a single static walkthrough:

- `HOLISTIC_WALKTHROUGH_V1.md` — canonical ownership, seven end-to-end sequences, stable sample identifiers, permission boundaries and source-level gaps.
- `HOLISTIC_REVIEW_NOTES_V1.md` — browser validation, owner decisions and implementation blockers.
- `tradethesis_admin_holistic_workflow_v1.html` — clickable M50 board with 40 fictional records.

### The shared fictional record graph

Primary learner: Maya Chen / USR-1042. Secondary actors: Rohan Patel / USR-1008 and Dev Singh / USR-1177.

The same record IDs connect Academy, Customers, Revenue, Growth, Platform and the member-facing Notifications subsystem. The register uses canonical owner labels and linked record references. It is a design dataset, not a global-search grant or a statement that every staff user may see every record.

### The seven integrated paths

1. CourseImport IMP-241 → published Course CRS-017 → CourseOffer OFR-017 / hidden Plan PLN-COURSE-017 → provider-verified PaymentIntent PI-7001 → direct CourseEntitlement ENT-9001 → protected-video Job JOB-8421 → Customer 360.
2. Membership Plan PLN-MEMBER-01 / price PP-799 → PaymentIntent PI-7002 → Subscription SUB-8102 → Academy PlanCourseAccess PCA-014 → ProvisioningOperation PROV-8B21 → Customer 360.
3. Campaign CAM-018 / frozen CampaignRecipient CR-018-1042 → first-touch ATTR-1042 and Referral REF-551 → stub Delivery DLY-018 → membership checkout PI-7002 with referral + COHORT20 → CouponRedemption CRD-0702 + pending reward REW-552.
4. SupportTicket TCK-4402 → reviewer-scope check + hidden Plan PLN-ACCESS-04 → canonical Subscription grant SUB-8114 → reconcile Job JOB-8432 → ProvisioningOperation PROV-8C14 → ticket Approved.
5. SupportTicket TCK-4410 → PaymentIntent PI-7001 / Invoice INV-7001 → open Dispute DSP-0091 (funds withdrawn) → source-specific Audit/Event evidence → ticket work state changes independently.
6. Staff gift creation GST-019 → token GiftInvite GFT-0091 → transactional EmailLog LOG-7712 Failed → Customer 360 invitation context → existing SUB-8102 unchanged because the invite has not been claimed.
7. CampaignRecipient/Delivery DLY-018 → MarketingPreference/Suppression MKT-1042 → Resend Delivery update path vs Stripe/Razorpay WebhookEvent + durable Job path → Customer 360 communications context → Command Centre routes only when an actionable exception exists. Member Notification NOT-901 is not a staff work item.

### Additional source invariants surfaced during the integrated pass

**Course coupon and analytics split**
- The inspected payment-start path calculates referral and coupon discounts and stores a coupon code/discount snapshot on PaymentIntent before it knows which fulfilment branch will complete the purchase.
- The CourseOffer activation branch dispatches to `activate_course_payment`, which atomically claims the PaymentIntent and grants the CourseEntitlement, records an `academy.entitlement_granted` (or simulation) Event, queues personalized-video work and sends a receipt on commit.
- This course branch returns before the ordinary membership activation path's coupon-redemption block and `purchase.completed` Event write.
- Therefore a course PaymentIntent may contain coupon fields from checkout without the inspected branch creating a CouponRedemption row. The prototype course sample is coupon-free and the membership sample carries COHORT20. The intended course-coupon policy and analytics/attribution contract require an explicit owner/engineering decision; don't silently reconcile them in UI.

**Membership coupon/referral**
- The standard membership activation path calls ReferralService completion and the CouponRedemption service on successful activation.
- PI-7002 therefore connects the referral discount provenance to REF-551 and campaign coupon COHORT20 to CRD-0702, with a separate pending Rohan reward REW-552.
- The sample labels the coupon as stackable with referral because the Coupon configuration explicitly permits it; this is not a general stacking rule for all coupons.

**Worker and external provisioning**
- Support access approval enqueues reconciliation inside the transaction with the subscription grant and ticket update.
- JOB-8432 Succeeded records completion of the reconcile job handler; PROV-8C14 remains Unknown because the external membership result still needs a probe.
- The same distinction applies to Maya's membership SUB-8102 / PROV-8B21. A successful job, active Subscription or active UserChannelAssignment is not proof that a member is present in the external community.

**Communication and attention**
- CampaignRecipient status, G1 Delivery state, legacy transactional EmailLog, user Notification and staff Command Centre work state are different records.
- NOT-901 is a member-facing Notification. It must not be counted as a staff attention item or a support/work resolution.
- A Command Centre event should only be created from an approved source-to-work mapping with defined permission scope, actionable status, owner and deep link.

### Acceptance checklist for M50

- Each sample ID resolves to one canonical owner.
- A record referenced in multiple journeys uses the same ID and sample state.
- A cross-domain context panel does not create a duplicate editable record.
- All counts, search and record lists are permission-filtered in a real implementation.
- Course purchase, membership, support grant and gift claim paths remain distinct.
- Campaign stub Sent and provider-delivered are not conflated.
- Job completion and external provisioning are not conflated.
- Member Notification and staff work item are not conflated.
- Every activity item retains source, actor, visibility and lifecycle provenance.
- Any action goes through its owning domain's existing service and server-side permission boundary.

The M50 board is a design review artefact. It is not an implementation authorisation.
