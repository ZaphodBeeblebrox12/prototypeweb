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
