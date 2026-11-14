# TradeThesis Admin Desk — Revenue Workspace Specification V1

**Status:** First screen-level design proposal; owner review pending  
**Date:** 14 November 2026  
**Planning branch:** admin-desk-redesign-planning  
**Source baseline:** my-new-branch  
**Visual template:** Selected V2 forest-green / warm-ivory shell, restrained terracotta and sage, editorial serif headings and compact sans-serif controls.  
**Implementation status:** Planning and static mockup only. No application code, route, permission, API, database record or deployment setting has been changed.

## 1. Scope and design intent

The Revenue domain owns commercial and financial records. This first pass covers:

1. M14 — Revenue Overview.
2. M29 — Payments & Refunds register and payment detail.
3. M30 — Subscriptions.
4. M31 — Plans & Pricing.
5. M32 — Invoices and invoice detail.
6. M33 — Disputes and dispute evidence detail.
7. M15 — Business & Finance settings/readiness.

The goal is to show a connected commercial lifecycle without collapsing different records into one financial status. PaymentIntent, Refund, Subscription, CourseEntitlement, Invoice, Dispute and external community provisioning remain distinct records and state machines.

All names, IDs, amounts, dates, currencies, plans, case facts and counts in the prototype are fictional illustrative data. The prototype has no live API calls and performs no financial, subscription, access or configuration writes.

## 2. Source-verified Revenue model

### 2.1 PaymentIntent — canonical transaction snapshot

PaymentIntent is the canonical record of a checkout/payment attempt. Relevant fields include:

- User and Plan.
- Optional base PlanPrice and selected GeoPlanPrice.
- Base amount/subtotal/tax and total amount snapshots.
- Currency, provider, payment method and country.
- Is-simulated flag.
- Payment status: pending, success or failed.
- Provider reference and provider payment identifier.
- Applied coupon/referral discount provenance.
- Upgrade flag.
- Refunded cents and refund timestamp.
- Dispute/chargeback flags, confirmed state, reference and timestamp.

Important rules:
- Payment amount, currency, provider and historical checkout snapshots are financial evidence. They are not ordinary editable fields.
- The inspected PaymentIntent Django Admin makes every PaymentIntent field read-only. Payment state is set by the provider-verification flow, not by a staff typing Success or Failed into the admin.
- PaymentIntent cannot be deleted through Django Admin.
- A simulated payment must be labelled as such; the inspected model's provider display explicitly says no money was collected for the simulator. A simulated success must not be counted or worded as cash collected.
- A failed or pending PaymentIntent is not proof that access was granted.
- A successful PaymentIntent is not by itself proof that external community provisioning completed.

### 2.2 Refund — unified append-only ledger

Refund is a separate financial record linked to PaymentIntent. The source implements one unified refund ledger for trial, standard and upgrade transactions. Each row includes provider, provider_refund_id, amount, currency, source, refunded_at, commercial_context and metadata.

- Provider refund recording is idempotent per provider + provider_refund_id.
- Refund rows are not manually added or deleted from the Refund Django Admin.
- PaymentIntent remains in its original success status; refunded_cents/refunded_at and linked Refund rows record the financial return.
- Partial refund: application access is unchanged by the current policy.
- Full refund (cumulative refund amount >= charged amount): the affected paid subscription is canceled through the existing service, or a course entitlement is revoked when the payment's Plan belongs to a CourseOffer.
- Trial cancellation is distinct from a refund. CancellationRequest and cancel_subscription represent cancellation; a Refund row represents money returned.
- Refund context is stamped from the immutable checkout evidence pricing snapshot when available. Legacy fallback behaviour is documented in the service.

**Manual refund migration boundary — important source finding**

The current staff-facing Admin Desk finance page is read-only; it does not expose a refund initiation or refund-recording control.

However, PaymentIntent Django Admin does expose a bulk action named “Record FULL manual refund (use after refunding in the provider dashboard)”. That action:
- Assumes the actual refund has already been processed in the provider dashboard.
- Records the full remaining balance as a manual Refund ledger row.
- Writes an audit event.
- Applies the existing full-refund access policy.
- Sends the existing refund notification.

It does not send the refund request to Stripe or Razorpay. It is not a partial manual refund form. PaymentIntent Django Admin also provides a “Mark selected payments as CHARGED BACK” action which reuses the same confirmed-chargeback service and notification path. Do not create a second manual access-revoke path in Revenue; dispute outcomes and that legacy admin action must continue through the canonical exactly-once chargeback service. These actions are currently in Advanced Administration and must remain there until an equivalent workflow is designed, permission-audited, tested and explicitly migrated. The prototype deliberately does not offer either action.

### 2.3 Refund eligibility and policy evidence

The refund eligibility engine reads the per-transaction checkout evidence snapshot and the policy versions captured at purchase. It does not simply apply today's current Plan settings to yesterday's payment.

Possible results include:
- Eligible within the historical window.
- No refund terms configured.
- Not refundable by policy.
- Refund window expired.
- Already fully refunded.
- Manual review required when checkout evidence is absent.

The absence of historical evidence is not a basis to fabricate a policy acceptance or infer an eligibility result. The Revenue screen should show a source-backed eligibility evaluation only where the underlying evidence permits it. It must not create a universal static refund window or imply that the new UI can approve a refund.

### 2.4 Product, Plan and price records

Revenue owns:
- Product.
- Plan.
- PlanPrice.
- GeoPlanPrice.
- PlanFeature.
- PlanChannelMapping.

Plan contains product, tier, name/description, active state, display order, public/hidden visibility, trial configuration, hidden-plan grant duration, notice channel, ticket approvers and feature limits.

PlanPrice:
- Intervals: monthly, quarterly, yearly and one_time.
- Stores amount in minor units (price_cents) and ISO currency.
- Only one active global base price is allowed for a Plan + interval.
- Geo pricing is not another global base price.

GeoPlanPrice:
- Interval, amount and currency.
- Requires either a country or a region.
- Is an override for a country or region.
- The inspected source resolver checks, in order: exact active country-specific price → active region price with country null → active global PlanPrice.
- The model prevents a geo row with neither country nor region.

Plan trial configuration requires a positive trial duration when is_trial is true.

The current PlanAdmin provides Plan editing with inline:
- Global base PlanPrice rows.
- GeoPlanPrice overrides.
- PlanFeature display bullets.
- PlanChannelMapping direct channel/role targets.

No dedicated Admin Desk Plan/Product/pricing management route was found in the inspected URL map. M31 is therefore a proposed unified workspace over existing records. Until permission, audit, uniqueness, price resolution and migration parity are designed, plan creation/editing remains in Advanced Administration.

### 2.5 Subscription — access record, not payment record

Subscription is a canonical access record linked to User and Plan and stores:
- Product snapshot from Plan.
- Selected base/geo price references.
- Base price, discount/coupon and purchased price/currency snapshot.
- Status: active, canceled, expired or pending.
- is_active.
- Start, expiry and cancellation times.
- Provider, provider subscription identifier.
- Pricing country and region.
- Gift provenance and message.
- Admin-grant provenance and reason.
- Trial flag.

Important rules:
- The purchased price/currency snapshot is immutable after creation.
- Active-subscription mutual exclusion is scoped by Product. If Product is null, legacy global behaviour remains.
- A subscription grant is not a payment and does not create a new charge.
- A course-purchase entitlement is not a recurring membership Subscription.
- Gift, trial and administrator grant are separate provenance markers and must be shown clearly.

SubscriptionHistory is the durable lifecycle history, including Created, Activated, Renewed, Canceled, Expired, Pending, Upgraded, Downgraded, Trial Started/Expired, Admin Granted and Gift Received events.

### 2.6 Existing staff subscription workflow

The current staff route is /staff/admin-desk/subscriptions/.

Read access requires subscriptions.view_subscription.

The current list supports:
- Search by learner username, email or plan name.
- Status filter: active, pending, expired, canceled.
- Expiring soon filter (active subscriptions with expiry within seven days).
- Recently expired filter.
- 30 rows per page, newest-created first.
- Summary counts for active, expiring, expired and canceled.

Grant:
- Requires subscriptions.add_subscription.
- Form requires an active learner; staff, superuser and banned users are excluded.
- Plan choices are active, hidden and non-trial only.
- Duration is 1–365 days.
- Reason is mandatory (minimum five characters).
- If the learner already has active access in the same Product, a replacement grant is blocked.
- Uses grant_subscription_by_admin, then writes an audit record.

Extend / cancel:
- POST action route: /staff/admin-desk/subscriptions/<uuid:subscription_id>/action/.
- Requires subscriptions.change_subscription.
- Both require a reason of at least five characters.
- Extend accepts 1–365 days and uses extend_subscription.
- Cancel uses cancel_subscription; active access is ended immediately and community reconciliation is queued.
- Only active access can be extended/canceled; otherwise no change is made.
- These operations are not refunds and do not create a payment.

Django Admin also has bulk cancel, expire, extend (+30 days) and reconcile actions on SubscriptionAdmin. Ordinary Subscription financial/lifecycle fields remain read-only; lifecycle is changed through controlled services/actions. The Admin Desk grant/extend/cancel workflow should be retained and redesigned rather than replaced with direct model editing.

### 2.7 Invoice — immutable historical document

Invoice is the saved invoice snapshot linked to its PaymentIntent.

The current invoice register is part of /staff/admin-desk/finance/?tab=invoices, and detail is /staff/admin-desk/invoices/<uuid:invoice_id>/.

The detail page supports viewing and printing/saving as PDF. Invoice model fields are read-only in Django Admin; the model has no normal add/delete path. The snapshot includes seller identity/address, customer identity, transaction description/reference, issue date, currency, subtotal, tax details and total.

Changing BillingSettings affects future invoice snapshots only. It must not rewrite an existing invoice.

### 2.8 Dispute — separate chargeback case state machine

The current dispute dashboard is at /admin-disputes/ and detail is /admin-disputes/<uuid:pk>/. It is a separate staff-facing dispute workflow, not a tab within the Admin Desk today.

Dispute is linked to PaymentIntent and stores:
- Provider and provider dispute identifier.
- Network, raw reason and mapped reason category.
- Disputed amount/currency.
- Case status.
- Opened time, provider evidence deadline, funds-withdrawn time, resolved time.
- Claim text and assignee.
- access_actioned exactly-once guard.

Reason categories include fraud, unrecognized, service not received, not as described, recurring/canceled, credit not processed, duplicate, customer initiated and other.

Statuses:
- Opened.
- Evidence preparation.
- Ready for review.
- Submitted.
- Won.
- Lost.
- Withdrawn.
- Accepted (merchant conceded).

Terminal statuses are Won, Lost, Withdrawn and Accepted.

Current dashboard:
- Counts Open, Needs response, Due within 72h, Won and Lost.
- Uses active case statuses Opened, Evidence preparation and Ready for review for response/deadline buckets.
- Orders rows by evidence_due_at.
- Limits displayed rows to 100.

Permissions:
- Read routes use staff_member_required.
- Note, generate evidence package, submit package and resolve require disputes.change_dispute.

Dispute detail:
- Displays transaction/customer, historical agreement, plan type facts, evidence readiness, timeline and packages.
- Evidence readiness is source-based. Missing checkout/auth/fulfillment records must be shown as missing; never fabricate them.
- Evidence package generation creates a new immutable snapshot with content hash.
- Submitted packages are immutable; regenerating makes a new package row.
- “Submit latest” records the submission event/reference in the application. The page explicitly tells staff to submit the same evidence through the PSP dashboard/API. It does not call Stripe/Razorpay to upload evidence.
- Manual resolution accepts only terminal statuses.

Critical chargeback/access rules:
- Opening a dispute flags the payment but does not revoke access.
- Provider funds-withdrawn is not a final decision; access intentionally remains unchanged.
- Won clears the dispute flags and leaves access unchanged.
- Confirmed Lost or Accepted invokes the single atomic confirm_chargeback service exactly once. It cancels the affected Subscription or revokes the direct course entitlement and triggers the existing reconciliation/notification flow.
- Do not offer an access-revoke control separate from the chargeback state machine.

### 2.9 Business and billing settings

Current route: /staff/admin-desk/business/.

The staff BillingSettings form supports:
- Public seller name.
- Legal seller name.
- Business address.
- Seller country (two-letter ISO code).
- Customer support email.
- Tax registration number.
- Invoice prefix.
- Tax enabled.
- Tax label.
- Tax rate percentage.
- Tax-inclusive flag.

When tax is first enabled, the form requires a separate confirmation checkbox stating the rate/treatment has been confirmed with an accountant. Tax is disabled by default.

The source explicitly states the current tax calculation is one fixed percentage for new checkouts; it is not a full jurisdiction-aware GST/place-of-supply system. The UI must not overstate compliance or readiness.

Use distinct terms:
- Configured: required settings/credentials are present.
- Tested: an actual invoice, test checkout, webhook or delivery check passed.
- Blocked: a required value/check is missing or invalid.
- Not verified: the current source has no test evidence.

### 2.10 Permission and route boundaries

Existing Admin Desk:
- Finance / Payments / Invoices: payments.view_paymentintent and payments.view_invoice respectively.
- Subscriptions: subscriptions.view_subscription; change/grant actions use subscriptions.change_subscription / subscriptions.add_subscription.
- Business settings: payments.add_billingsettings when no row exists; payments.change_billingsettings once it exists.
- Invoice detail requires payments.view_invoice.

Current Django Admin / Advanced Administration:
- Product and Plan configuration, global base prices, geo overrides, feature bullets and PlanChannelMapping.
- PaymentIntent bulk actions, including full manual refund recording (only after a provider refund) and manual chargeback confirmation.
- Read-only PaymentIntent and Refund financial evidence.
- Subscription bulk actions and other advanced model administration.
- Preserve these actions until a separately reviewed replacement has parity.

Current dispute app:
- /admin-disputes/ and its detail/action routes.
- Staff visibility and disputes.change_dispute action permission.
- Propose mapping into Revenue navigation while preserving the underlying case service and role enforcement.

Member-facing checkout, plan APIs and payment webhooks are not staff workspace routes and must not be shown as admin destinations.

## 3. M14 — Revenue Overview

**Purpose:** Answer “What financial or access issue needs a decision now, and where does the canonical record live?”

Recommended order:
1. Dispute evidence approaching deadline.
2. Failed or pending payment exceptions.
3. Full/partial refund state that needs reconciliation/investigation.
4. Subscription expiry or cancellation review.
5. Business readiness blockers with a verified test/source.
6. Compact commercial context: payment totals, active subscriptions and refund/chargeback totals.

Rules:
- All counts in the mockup are illustrative.
- Avoid a topline revenue number without defining paid/simulated treatment, refund netting, currency conversion and time-window semantics.
- Never aggregate INR, USD and EUR without a documented conversion source/rate/timestamp.
- Simulated successes are not cash collected.
- The overview routes to canonical payment, subscription, invoice, dispute or business record. It does not resolve those records itself.

## 4. M29 — Payments & Refunds

**Purpose:** Search the canonical PaymentIntent register and inspect the separate Refund ledger.

Existing staff route:
- /staff/admin-desk/finance/ (Payments tab).

Current behaviour:
- Permission-gated payment register.
- Search learner, email, plan, provider reference or provider payment identifier.
- Filter pending/success/failed.
- Newest-first, 30 rows/page.
- Global counts by PaymentIntent status.
- CSV export link when permitted.
- Payment register and invoice register are separate tabs on the same page.

Proposed layout:
- Compact summary indicators, with clear time-window/source labels.
- Search/status filters.
- Dense payment table showing payment identity, learner, plan/offer, amount/currency, status, provider/method, refund state and dispute/chargeback state.
- Refund ledger below or as a sibling tab; row fields: payment, amount, provider, source, commercial context, timestamp.
- Detail opens the canonical transaction record and links to Customer 360, Academy entitlement, Invoice and Dispute where those relationships are source-backed.

Payment detail:
- Immutable charged amount/currency/provider/price/tax/discount/geo snapshot.
- Provider verification status.
- Simulated/staging flag.
- Refund ledger rows and cumulative refunded amount.
- Dispute and chargeback flags.
- Related subscription/course entitlement state shown separately.
- Timeline based on real event sources if implemented.

No payment edit controls:
- Do not manually set success/failed.
- Do not edit amount, currency, provider, reference or price snapshots.
- Do not delete payments/refunds.
- Do not initiate a PSP refund from this screen.
- Do not offer a manual refund recording control in the redesigned finance register until that Advanced Administration action has been separately migrated and reviewed.

## 5. M30 — Subscriptions

**Purpose:** Inspect membership/granted access and perform the existing audited lifecycle actions.

Recommended queue columns:
- Learner.
- Product and Plan.
- Status / is_active.
- Historical price and currency snapshot.
- Started / expires / canceled dates.
- Source (paid, trial, gift, admin grant).
- Linked access/reconciliation context only where the source supports it.

Filters:
- Search learner/email/plan.
- Active, Pending, Expired, Canceled.
- Expiring within 7 days.
- Recently expired.

Detail should show immutable price snapshot, plan/product relationship, history, gift/trial/admin-grant provenance and permission-safe community-access context.

Actions:
- Grant (existing hidden-plan, learner, duration and reason constraints).
- Extend (1–365 days and reason).
- Cancel (reason; immediate access end/reconciliation).
- Make action availability visibly permission-dependent.
- Explicitly separate cancellation from refund and price editing.

The prototype includes sample inspection and a proposed grant form illustration, but all actions are preview-only. The current live actions remain the existing source-backed grant/extend/cancel workflow.

## 6. M31 — Plans & Pricing

**Purpose:** Provide a proposed unified view of Products, Plans and global/geo price relationships.

Register fields:
- Product / Plan.
- Tier.
- Public vs hidden.
- Active/inactive.
- Trial and duration.
- Base price intervals.
- Geo override count/summary.
- Direct channel mapping summary where permission allows.

Plan detail sections:
- Product and plan identity.
- Public/hidden and active state.
- Tier/trial.
- Base PlanPrice rows.
- GeoPlanPrice overrides.
- Feature bullets.
- Channel mappings.
- Subscriptions using the plan.
- CourseOffer relation where a hidden plan is dedicated to a one-time Academy course offer.
- Ticket approver scope and grant duration for hidden access plans.

Pricing rules should be explained directly:
- Country-specific override.
- Regional override.
- Global base fallback.
- Only one active global base price per plan+interval; a different market/currency price should be a geo override.
- Geo rows must include a country or region.
- Historical PaymentIntent and Subscription price snapshots are immutable.

Migration status:
- Current configuration is in Django Admin.
- M31 is proposed, not an existing Admin Desk route.
- Do not imply plan editing is available in this prototype or current production Admin Desk.

## 7. M32 — Invoices

**Purpose:** Inspect immutable invoice snapshots linked to verified successful payments.

Register:
- Invoice number.
- Issue date.
- Customer identity.
- Description.
- Total/currency.
- Transaction reference.
- Open/view/print.

Detail:
- Seller snapshot.
- Customer snapshot.
- Transaction description/reference.
- Subtotal, tax label/rate/treatment and total.
- Print / Save as PDF.
- Link to the source PaymentIntent.

No create/edit/delete/refund control is shown. Changing BillingSettings only affects future invoice snapshots.

## 8. M33 — Disputes

**Purpose:** Manage evidence preparation, provider deadlines, recorded submission references and case outcomes without conflating interim events and final decisions.

Queue:
- Case/provider.
- Customer and linked payment.
- Disputed amount/currency.
- Reason category.
- Evidence deadline.
- Funds withdrawn / not withdrawn.
- Case status.
- Assigned operator if source supports it.
- Due-date ordering and current status filters.

Detail:
- Payment and customer summary.
- Exact historical Terms/Refund/Risk acceptance where CheckoutEvidence exists.
- Evidence readiness items with source/present/missing.
- Timeline labelled by source.
- Evidence package list, generated timestamp, content hash, readiness and submitted status.
- Add audited case note.
- Generate new evidence package.
- Record external submission reference.
- Resolve to terminal state with permission.

Critical semantics:
- Funds withdrawn ≠ dispute lost.
- Opened dispute ≠ access revoked.
- Won ≠ revoke; it clears flags and leaves access.
- Lost/Accepted = confirmed chargeback access policy, performed exactly once.
- Withdrawn is terminal but is not mapped to confirmed loss unless the underlying service says so.
- Record external provider submission; do not imply the current route uploads package to PSP.

Current routes are /admin-disputes/ and /admin-disputes/<uuid>/ with note/generate/submit/resolve actions. Map into the Revenue shell without creating a duplicate Dispute model or new state machine.

## 9. M15 — Business & Finance

**Purpose:** Control seller/invoice/tax settings and communicate operational readiness honestly.

Fields:
- Public seller name.
- Legal seller name.
- Address.
- Country code.
- Support email.
- Tax registration.
- Invoice prefix.
- Tax enabled.
- Tax label.
- Tax percentage.
- Tax-inclusive.

Interactions:
- First activation of tax requires the explicit accountant confirmation field.
- Changing values affects future checkouts/invoices only; historical Invoice and PaymentIntent snapshots are not rewritten.
- Show configured/tested/blocked/not-verified with source/time/evidence, not a generic green “ready”.

Current BusinessSettingsForm saves through the staff Business route and writes an audit event. The prototype does not save.

## 10. Cross-domain hand-offs

| Revenue context | Canonical owner | Other domains that may show safe context |
|---|---|---|
| PaymentIntent / Refund / Invoice / Dispute | Revenue | Customers, Command Centre, Platform |
| Product / Plan / base & geo prices | Revenue | Academy, Customers, Growth |
| Subscription / SubscriptionHistory | Revenue | Customers, Academy, Growth, Platform |
| CourseOffer relationship | Academy | Revenue |
| CourseEntitlement / learning progress | Academy | Customers, Revenue |
| User identity and support ticket | Customers | Revenue, Academy |
| Community provisioning / reconciliation | Platform | Revenue, Customers, Command Centre |
| Referral discount provenance | Growth | Revenue, Customers |

Key journeys:
1. Course purchase: Academy CourseOffer → Revenue hidden Plan/one-time price → PaymentIntent verified → Academy CourseEntitlement → Customers Customer 360.
2. Membership purchase: Revenue Plan and price → PaymentIntent → Subscription → Academy access where supported → Platform provisioning if mapped.
3. Full refund: provider-side refund → Refund ledger row → full-refund policy → affected Subscription canceled or course entitlement revoked → Platform reconciliation if applicable.
4. Dispute: PaymentIntent → Dispute opened → evidence preparation → external provider submission (recorded in app) → final outcome → exactly-once access consequence only for confirmed loss/accepted.
5. Support billing case: Customers ticket → Customer 360 → Revenue payment/invoice/dispute → public support response remains in Customers.
6. Plan configuration: Revenue plan/pricing workspace → base/geo validation → future checkout price resolution; historical snapshots remain unchanged.

## 11. Prototype artefact and validation

**HTML:** tradethesis_admin_revenue_workspace_v1.html

Includes:
- Revenue Overview.
- Payments & Refunds register and refund ledger.
- Payment detail.
- Subscriptions list and inspection/grant-form preview.
- Plans & Pricing register and resolution model.
- Invoice register and invoice detail.
- Disputes list and case detail/evidence workflow.
- Business & Finance sample form with tax-enable confirmation.
- V2 shell, six-domain navigation and mobile drawer.

Browser smoke tests:
- All Revenue destinations open.
- Payment search/filter and detail navigation.
- Subscription search/filter and inspection modal.
- Hidden-plan filter and pricing inspect.
- Invoice detail.
- Dispute filter and case detail.
- External submission-reference preview interaction.
- Tax enable shows accountant confirmation row.
- Mobile navigation opens and closes after destination selection.
- 390px mobile viewport has no horizontal overflow.
- No JavaScript page errors or console errors in exercised flows.

Not tested/claimed:
- Authenticated live staging parity.
- All Revenue permission roles.
- Provider webhook integration or live finance actions.
- Accessibility, screen-reader, keyboard-only and measured contrast audit.
- Actual Stripe/Razorpay refund or dispute submissions.
- Tax/legal compliance.
- Full route-level implementation parity.

## 12. Review decisions requested

1. Is the Revenue Overview action-first hierarchy useful, or should disputes/payment exceptions dominate more strongly?
2. Are Payments & Refunds presented as one workspace with a separate ledger, or should refunds have a separate destination?
3. Does the separation between PaymentIntent, Refund and resulting access state read clearly?
4. Should Subscriptions be one table with grant/extend/cancel actions or a list plus dedicated detail page?
5. Is Plans & Pricing sufficiently understandable while visibly retaining its Django Admin migration boundary?
6. Does the dispute screen communicate interim funds withdrawal vs final outcome strongly enough?
7. Is the evidence package submission language clear that the current app only records the external submission reference?
8. Does Business & Finance correctly distinguish configured from tested and explain the current fixed-rate tax limitation?
9. Which Revenue screen needs a higher-fidelity follow-up before proceeding to Growth?

This is a design specification for review, not implementation authorisation.
