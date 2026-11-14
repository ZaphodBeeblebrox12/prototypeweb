# TradeThesis Admin Desk — Domain Workspace Blueprint v1

**Status:** First holistic workspace specification for discussion  
**Branch:** admin-desk-redesign-planning  
**Design foundation:** M01/M02 V2 — forest-green sidebar, warm-ivory workspace, restrained terracotta, sage status accents, editorial serif headings, compact sans-serif controls.  
**Implementation status:** Planning only. No application code, API, permission or deployment changes are authorised by this document.

## 1. What this blueprint establishes

The six top-level domains and their order are approved:

1. Command Centre
2. Academy
3. Customers
4. Revenue
5. Growth
6. Platform

This document develops the responsibilities, landing pages, child destinations, record ownership and cross-domain navigation of each domain. The goal is one coherent operating environment, not six unrelated dashboards.

The design must distinguish three things:

- **Existing capability:** a route, model, action or workflow verified in the current source baseline on my-new-branch.
- **Proposed Admin Desk experience:** a new way to organise or present existing capability inside the shared shell.
- **Unverified or future capability:** something that needs further source/role audit or a separately approved product decision. A mockup must not present it as live.

The V2 shell is the selected shared visual template for all six domains. The content hierarchy, operational rules, detailed actions and screen layouts remain subject to review.

## 2. The operating model

### 2.1 One shell, six homes, one source of truth per record

Each domain owns a clear operational responsibility. The same underlying record may be visible from multiple places, but it must not be copied into parallel admin records or given conflicting action controls.

Examples:

- A course is owned by Academy. Revenue may show its linked one-time offer plan and payment history, while Customers may show which learners have access.
- A learner account is owned by Customers. Academy shows that learner's course progress, Revenue shows payment/subscription history, and Platform shows community provisioning state.
- A payment is owned by Revenue. A Customer 360 timeline may display a permission-safe summary, and Command Centre may surface an exception requiring investigation.
- A support ticket is owned by Customers. Command Centre can prioritise it and Customer 360 can show its history, but its status, reply and review actions remain on the canonical ticket screen.
- A job or provisioning operation is owned by Platform. Command Centre may surface a failure, and a customer record may link to the affected operation, but retry/reconcile controls belong only to the supported Platform workflow.

### 2.2 Standard structure for every domain landing page

Use a consistent page pattern inside the V2 shell:

1. **Domain heading:** clear name, short purpose statement and current location breadcrumb.
2. **Action summary:** only counts that indicate real work, a defined time window and a clear source. Avoid decorative KPI tiles.
3. **Primary work area:** the queue, catalogue, register or operational list that staff came to use.
4. **Context rail:** related status, quick filters, relevant readiness or linked-record context. This is supporting information, not a second dashboard.
5. **Recent activity:** recent events from that domain, with source links and permission-safe descriptions.
6. **Related workspaces:** direct links to connected records in other domains.
7. **State handling:** empty, loading, error, no permission, stale data and success states.

A domain landing page should answer three questions: what is this area responsible for, what requires attention here, and where does the operator go to complete the work?

### 2.3 Common record page pattern

A detail page should use the same structure across domains:

- Identity strip: record name, canonical ID/short ID, status, owner and key date.
- Primary action area: only actions supported by the current business workflow and the staff member's permission.
- Record facts: fields needed to make the decision.
- Relationships: linked records in the owning and adjacent domains.
- Activity and audit: a chronological history with public/internal visibility clearly distinguished.
- Return path: preserve the originating queue, search and filter context when the operator returns.

The same record must resolve to one canonical URL even when opened from a different domain. A contextual panel may preview it, but should link to the canonical detail page for full work.

### 2.4 Common navigation and interaction rules

- The six domains remain in the approved order in the persistent sidebar.
- Child destinations appear under their owning domain; high-frequency cross-domain links may appear contextually but do not create duplicate ownership.
- Search is global in the shell, but results must be limited to records the current staff member is permitted to discover and open.
- Breadcrumbs show the current domain and record hierarchy.
- A badge is a meaningful count, not decoration. Define its query, time window, role scope, refresh semantics and destination before displaying it.
- Notifications inform an operator; queues contain work; audit entries explain what happened. Do not merge these concepts.
- Command Centre cards and domain summaries navigate to the canonical queue/detail. They do not create a second version of the underlying workflow.
- Permission enforcement remains server-side. Hiding a menu item or button is not an authorisation control.
- Sensitive actions require the existing business validation, confirmation and audit behaviour. Do not invent one-click actions for publishing, financial changes, grants, revocations or operational retries.

## 3. Domain 1 — Command Centre

**Responsibility:** Give the operator one place to understand what needs attention across the whole business and move directly to the workspace that owns the issue.

**Primary question:** What needs my attention now?

### 3.1 Child destinations

- **Overview** — action-first cross-domain queue.
- **My Work** — a personal filter over work that has a real assignment/ownership field. It is not a promise of a universal task engine.
- **Notifications & Alerts** — personal notifications and operational signals, with their different meanings preserved.
- **Operations Timeline** — cross-domain event and incident stream.

### 3.2 Overview layout

Recommended hierarchy:

1. Critical and overdue items.
2. Time-sensitive work approaching a defined due time or SLA.
3. Blocked decisions that need a specific operator.
4. Remaining actionable work.
5. Compact domain pulse and recent activity as secondary context.

Each queue row must answer:

- Which domain owns this item?
- What record is affected?
- Why is it in the queue?
- What is its current state and how old is it?
- Is there a due time or SLA, and what does that deadline mean?
- Who owns the next action, or is it unassigned?
- What is the safest next step?
- Which canonical detail page will open?

Potential source records already present in the code baseline include reviewable course submissions, staff-visible support tickets and first-response SLAs, payment exceptions, failed/stalled jobs, failed/unknown provisioning operations, periodic-job errors and selected business-readiness blockers. The exact inclusion rules and role scope must be specified before any count is treated as authoritative.

Do not assign a hidden severity score without explaining it. The first prioritisation model should use transparent ordering: hard critical states, overdue deadlines, explicit priority, then oldest due/actionable item. Customer impact may be a tie-breaker only where the source data supports it.

### 3.3 My Work

Existing assignment semantics are uneven across domains. SupportTicket has an assigned_to field and a mine filter. Course review records store the reviewer after review; the inspected baseline does not establish a general pre-review assignment workflow. Jobs and provisioning operations are not staff task assignments.

Therefore:

- V1 My Work can surface work that is genuinely assigned to the current user, initially including support tickets.
- Other work can appear only if a current source explicitly records an owner or if a future assignment capability is separately approved.
- Do not create fake checkboxes or imply a task has been assigned merely because an item is visible to the staff member.
- Provide a clear link from My Work to the team queue and unassigned work where permitted.

### 3.4 Notifications & Alerts

The current system has a per-user Notification model and a notification list/read API. The support workflow also creates staff in-app notifications and attempts email delivery for new tickets, with staff recipients scoped by the ticket's reviewer plan where configured.

That is useful existing infrastructure, but it does not by itself establish a complete cross-domain operational alert centre. The design must distinguish:

- Personal notifications: messages addressed to the current user.
- Staff alerts: currently evidenced at least for support-ticket events.
- Operational exceptions: failed jobs, unknown provisioning, payment failures and other conditions that may need an owner or investigation.
- Work items: records that require a staff action and have a canonical queue/detail.

The inbox should deep-link to the source record. Read/acknowledged state must not silently resolve the underlying work. A user marking an alert read does not mean a failed job, overdue ticket or pending approval has been fixed.

Further decisions needed: event sources, recipient rules, severity, deduplication, unread semantics, acknowledgement, escalation, retention, refresh and ownership.

### 3.5 Operations Timeline

The existing route already combines permission-scoped support issue clusters, recent tickets, job incidents, provisioning incidents, periodic-job errors, domain events, audit events and security summaries over a 24-hour or 7-day window.

Retain this as an observability surface:

- Show event time, domain, event type, impact/affected record, state and source.
- Allow filtering by window and event family.
- Distinguish a signal from an actionable operation.
- Link to the owning detail page where one exists.
- Do not expose raw provider IDs, secrets, internal message text or security identifiers to people without the corresponding permission.
- Keep detailed job/provisioning management in Platform.

### 3.6 Cross-domain connections

- Academy: reviews waiting for approval, course publication/readiness problems.
- Customers: tickets, response SLAs, assigned/unassigned work.
- Revenue: failed/pending payments, refunds/disputes and reconciliation exceptions.
- Growth: delivery failures or campaign/referral anomalies where events support them.
- Platform: failed/stalled jobs, periodic errors and unknown/failed provisioning.
- Staff: current user's scope and assigned work.

**Existing foundations:** staff Admin Desk overview, permission-filtered support queue summary, operations timeline, per-user Notification model/API, support staff alerts.  
**Proposed experience:** unified priority queue, role-aware Command Centre shell, complete cross-domain alert taxonomy and a cohesive My Work destination.

## 4. Domain 2 — Academy

**Responsibility:** Own learning products from editorial creation through review, publication, catalogue visibility, offers and learner access.

**Primary question:** What learning content are we managing, and is it correctly published, discoverable and accessible?

### 4.1 Child destinations

- **Course Catalogue**
- **Course Approvals**
- **Course Builder**
- **Offers & Access**
- **Learner Access & Progress**
- **SEO & Discoverability**

### 4.2 Academy landing page

The landing page should prioritise work in this order:

1. Course submissions awaiting review.
2. Draft or published courses with a concrete content/publication blocker.
3. Course offers that are inactive or fail the conditions required to be saleable.
4. Learner-access exceptions that have a course/entitlement source.
5. SEO/indexability issues that affect published public course pages.
6. Compact catalogue context: flagship/supporting/mini/hidden distribution, draft/published/archived totals and published content coverage.

Keep content health and commercial readiness separate. A course may be editorially ready but not saleable; it may be saleable but not discoverable; it may be published but not included in a membership plan.

### 4.3 Course Catalogue

The catalogue is the canonical list of Course records. It should be a compact, filterable table rather than a wall of large course cards.

Recommended columns:

- Course title and slug.
- Catalogue role: Flagship, Supporting, Mini-course or Hidden.
- Publication status: Draft, Published or Archived.
- Access type: Free, Membership, Paid or Mixed.
- Published modules/lessons and content formats where reliable.
- Offer status: no individual offer, inactive or active.
- Public catalogue/SEO status where available.
- Last updated and responsible editor where the source supports it.

Filters:

- Status.
- Catalogue role.
- Access type.
- Offer state.
- Publication/content readiness.
- SEO attention/indexability.

The Course detail page should use internal tabs:

- **Overview:** purpose, catalogue role, status, access type and readiness summary.
- **Curriculum:** modules, lessons, formats, publication states and release days.
- **Catalogue & SEO:** title/summary/description, public visibility and search metadata.
- **Offers & Membership:** linked course offers, one-time commerce plan and membership-plan inclusion.
- **Learner activity:** active direct entitlements, lesson progress and completion context, permission-scoped.

Avoid copying authoring controls into every catalogue tab. Open the supported Course Builder when editing content.

### 4.4 Course Approvals

The existing review workflow is based on CourseImport records with status REVIEW. A submission may be a new course or a revision linked to a target Course.

Queue columns and context:

- Submission title.
- New course vs revision.
- Target course if one exists.
- Author/imported_by.
- Submitted/imported time.
- Current review status.
- Asset/content completeness indicators.
- Link to the review preview.

Review detail:

- Full submission preview and module/lesson outline.
- Protected review assets.
- Clear comparison/context for a revision where the source supports it.
- Validation and publication readiness.
- Reviewer identity and history.
- Approve and publish through the canonical publisher.
- Return to editor with mandatory, specific feedback.

Preserve the existing rules:

- Approval uses the canonical atomic publisher.
- Return requires reviewer feedback, records the reviewer and updates the import status.
- Permanent test-import cleanup is a separate, restricted workflow. It must not be presented as an ordinary reject/delete control; the source permits cleanup only for eligible unpublished/unlinked imports.
- The reviewer must have course-content-admin permission.

### 4.5 Course Builder

The Course Builder remains an authoring workspace launched from Academy. Preserve the supported legacy editing path as the production baseline.

- The Admin Desk provides course selection, draft/review status and a direct launch into the existing Builder.
- Do not label Tiptap as the default or production editor until the separate feature-flag, persistence, preview, validation and parity gates are approved.
- The builder handoff should preserve the course identity and return path to the Admin Desk.
- Admin Desk redesign does not silently redesign or replace the editor.

### 4.6 Offers & Access

This area must present distinct concepts rather than one ambiguous price/access form:

- Course: the learning product.
- CourseOffer: the individual-purchase offer connected to that course.
- Plan: the dedicated hidden commerce plan used by that offer.
- PlanPrice / GeoPlanPrice: the canonical global or regional price record.
- Subscription: recurring or granted plan access.
- CourseEntitlement: a direct user-to-course access record.
- PlanCourseAccess: the courses included by a subscription plan.

Existing validation rules that the UI must explain:

- An active CourseOffer must have a Plan.
- Its course must be published and have Paid or Mixed access type.
- Its linked plan must be hidden from the public subscription catalogue.
- It must have an active one-time PlanPrice or GeoPlanPrice.
- A plan with existing payment/subscription history cannot simply be reused for a new offer.
- Once a payment intent exists, the course, plan and access duration of the existing offer are constrained; future commercial changes may require a new offer.
- A blank access duration means permanent course access; a value means a time-limited term.

The Academy offer screen owns the CourseOffer-to-Course relationship and the course-specific access term. The linked Plan and price should open their canonical Revenue details. Do not duplicate price tables or create competing editable price values on both screens.

### 4.7 Learner Access & Progress

Show two access paths separately:

**Direct course entitlement**
- CourseEntitlement links a user to a course.
- Source may be purchase, administrator grant, migration or complimentary access.
- Display status, start time, expiry, revocation reason and grant actor where permitted.
- Show CourseEntitlementEvent history for grant, extend, reinstate and revoke events.
- Display derived access state as Active, Scheduled, Expired or Revoked, with the underlying stored fields available to explain it.

**Membership-plan inclusion**
- Subscription to a Plan may unlock a course through PlanCourseAccess.
- This is not the same object as a direct CourseEntitlement.
- Show the source subscription and plan relationship clearly.
- Avoid double-counting both paths as two separate course purchases.

Lesson progress uses LessonProgress linked to a user and lesson. Show published course progress, completed lessons, last activity and time spent only where the staff permission allows it.

Any grant, extend or revoke action must use an existing service/business workflow, require the correct permission and reason, and write the established event/audit record. Do not invent a bulk grant or revoke action.

### 4.8 SEO & Discoverability

The existing SEO dashboard evaluates:

- Site-wide indexing enabled/disabled.
- Course published status.
- Course seo_indexable flag.
- Hidden catalogue role.
- Published lesson presence.
- Public catalogue content checks.
- Search title and description, including fallbacks.
- Missing/long/short descriptions and long titles.
- Missing primary topic.
- Duplicate search titles and shared primary-topic overlap.

The SEO workspace should act as a diagnostic bridge to the Course detail and Course Builder. It should say why a course is or is not indexable, not merely show a green score.

### 4.9 Cross-domain connections

- Customers: learner entitlements, progress, enrolment questions and support requests.
- Revenue: CourseOffer's hidden Plan, canonical prices, PaymentIntent and refund history.
- Growth: referral discount attribution or campaigns that led to a course purchase, where the event data supports the connection.
- Platform: media/asset storage, publishing background jobs or operational failures only when a real event/source exists.
- Command Centre: pending reviews and concrete publishing/access blockers.

**Existing foundations:** Course, modules, lessons, CourseImport review, Course Builder, CourseOffer, CourseEntitlement and events, LessonProgress, PlanCourseAccess and SEO dashboard.  
**Proposed experience:** unified Academy landing, compact catalogue, coherent course record tabs and linked offer/access views.

## 5. Domain 3 — Customers

**Responsibility:** Own learner identity, account operations and the support relationship.

**Primary question:** Who is this learner, what do they need, and what is their current relationship with TradeThesis?

### 5.1 Child destinations

- **Learners & Accounts**
- **Support Tickets**
- **Customer 360**

### 5.2 Learners & Accounts

The list is the canonical entry point for learner accounts, not staff/admin accounts.

Recommended list fields:

- Name/username and email.
- Account state (active, inactive or banned where applicable).
- Joined date.
- Community connection summary where available and permitted.
- Open-ticket indicator.
- High-level access/subscription summary only if the current user has the corresponding permissions.

Search should support the account fields used by the existing route. Filters should distinguish active, inactive and banned records. Preserve account-detail actions exactly as implemented and verify each action, permission and audit effect before adding it to the new screen.

Do not expose staff/superuser accounts in the general learner list. Internal staff accounts may appear in a support context only when the reviewer is allowed to see that ticket, and their Customer 360 view is deliberately restricted.

### 5.3 Support Tickets

This is the canonical support workflow.

Categories:
- Access request / referral verification.
- Billing or payment issue.
- Technical issue, including community access.

Statuses:
- Pending.
- In Progress.
- Awaiting Member.
- Approved / Resolved.
- Rejected / Closed.
- Withdrawn by user.

Priority first-response targets:
- Urgent: 2 hours.
- High: 8 hours.
- Normal: 24 hours.
- Low: 72 hours.

Queue controls:
- Search.
- Status.
- Category.
- Priority.
- Assigned to me.
- Unassigned.
- Other authorised reviewers/assignment where visible.
- Pending/open/overdue/resolved summaries with the same permission scope as the queue.

Queue row must show ticket ID, member, category, concise request, priority, status, assigned reviewer, age, first-response deadline and overdue state.

Ticket detail:

- Conversation history with clear public vs internal messages.
- Attachments.
- Member identity and safe account context.
- Assignment and priority editing.
- Start review and awaiting-member transitions.
- Public reply and internal note.
- Approve/reject with required plan/reason rules.
- Reopen a closed ticket only under the existing service constraints.
- Link to Customer 360, payment history or provisioning details where the current reviewer can access those records.

Preserve critical existing workflow rules:

- The reviewer sees only tickets allowed by the plan's ticket_approvers configuration; an empty approver list preserves the current any-staff behaviour, and superusers retain their special scope.
- Assignment is restricted to active staff who can review the ticket.
- Access requests use hidden Plans only.
- Approval of an access request grants the selected hidden Plan through the established grant service and enqueues reconciliation in the same database transaction. If enqueue fails, the grant and ticket update roll back.
- The ticket is then marked approved and the member is notified after commit. The plan's notice_channel determines Telegram/email/both behaviour.
- Billing and technical tickets are resolved through the ticket service; they do not silently grant a subscription.
- Rejection requires an explanatory note.
- Public replies and internal notes must remain visibly different and have different member visibility.
- Reopening must preserve the existing service checks, including the duplicate-open-ticket check.

### 5.4 Customer 360

Customer 360 is the full record page. It is the central cross-domain view of one learner and the natural destination from a support ticket, payment, entitlement, subscription, referral or provisioning record.

Suggested sections:

1. **Identity & account:** member identity, account state and join date.
2. **Community:** Telegram and Discord community-account status, distinguished from a legacy login identity. “Login verified” is not the same as “community account linked”.
3. **Academy:** direct course entitlements, membership-plan course inclusion, course progress and entitlement event history.
4. **Revenue:** subscription/current plan and history, payment intents, refunds, chargebacks/disputes and invoices.
5. **Support:** open and historical tickets, assignment, status, priority and public conversation activity. Internal notes are not included in a member-facing/public activity stream.
6. **Security:** permission-scoped security events.
7. **Unified activity:** chronological, source-labelled events with safe deep links.

The existing Customer 360 source already applies separate permission checks for subscriptions, payments, invoices, Academy records and security events. It restricts internal staff profiles to identity plus reviewer-visible support history and does not show their personal community identities or learner commerce/progress data.

The new design must preserve this behaviour. A missing panel can mean no permission, no data or not applicable; these must be visually distinguishable.

### 5.5 Contextual Customer 360 inside a ticket

Recommended pattern: full Customer 360 page plus a compact member context panel in ticket detail.

The panel may show identity, account state, currently relevant access/community state and safe summary counts. It must link to the full record page. It should not duplicate the full payment, entitlement or security interface inside the ticket.

### 5.6 Cross-domain connections

- Academy: course entitlements, lesson progress, access requests and course-specific support.
- Revenue: subscriptions, payments, refunds, invoices and disputes.
- Growth: referral relationship, rewards, gift claims and marketing preference where permitted.
- Platform: Telegram/Discord provisioning operations and security events.
- Command Centre: SLA and priority queue; personal assigned tickets.
- Notifications: ticket acknowledgements, member updates and staff alerts.

**Existing foundations:** learner account list/detail/action routes, support queue/detail/actions, reviewer scoping, ticket SLA and status rules, Customer 360 aggregation and permission-scoped activity.  
**Proposed experience:** a coherent customer workspace and compact contextual customer panel in ticket review.

## 6. Domain 4 — Revenue

**Responsibility:** Own commercial configuration, payment records, subscriptions, invoices, refunds/disputes and business billing readiness.

**Primary question:** What was offered, what was paid, what access did it create, and what financial action remains?

### 6.1 Child destinations

- **Payments & Refunds**
- **Subscriptions & Plans**
- **Invoices & Disputes**
- **Business & Finance**

### 6.2 Payments & Refunds

PaymentIntent is the canonical payment record.

Recommended list/detail fields:

- Payment/customer ID and linked user.
- Plan and price selected.
- Amount, currency and country.
- Provider (Razorpay or Stripe) and payment method where reported.
- Pending, success or failed status.
- Whether the payment is simulated (staging-only; no money collected).
- Coupon/referral discount provenance where available.
- Tax snapshot.
- Provider reference fields only for authorised finance/operations roles; do not expose sensitive raw identifiers in generic queues.
- Refunded amount/date and linked Refund records.
- Chargeback/dispute state and reference, permission-scoped.

The detail page should show the commercial snapshot used for the transaction, not recompute a historical price using today's Plan configuration.

The course-purchase fulfilment path is source-verified: `payment_confirm` calls `activate_paid_subscription`; when the PaymentIntent maps to a CourseOffer, that path dispatches to `activate_course_payment`, which atomically claims the verified payment and calls the course-entitlement grant service. A failed or merely pending payment is not proof that access was granted. A successful course entitlement or membership subscription still does not prove external community provisioning completed. Surface payment, application access and external provisioning as linked but separate states.

Refund and dispute actions must use existing payment services and provider/webhook rules. The detailed action inventory, approval/confirmation and permission requirements must be verified before building a writable finance screen.

### 6.3 Subscriptions & Plans

Canonical records include Product, Plan, PlanPrice, GeoPlanPrice, Subscription, PlanFeature and PlanCourseAccess.

Separate plan types clearly:

- Public/available membership plans.
- Hidden plans used for access approval.
- Hidden one-time plans dedicated to CourseOffers.
- Trial or other special plan variants where configured.

Show a plan detail page with:

- Product and plan identity.
- Public/hidden and active/inactive state.
- Tier and trial configuration.
- Price intervals and currency.
- Geo overrides (these override a global/base price where applicable).
- Features.
- Courses included via PlanCourseAccess.
- Subscriptions using the plan.
- For course-offer plans, the linked CourseOffer and course-specific access duration.
- Historical purchase/subscription constraints.

Subscription list/detail should show the user, Product/Plan, stored price/currency snapshot, price/geo price selected, state, start/expiry/cancel dates, provider, gift/admin-grant/trial provenance and history where available.

Do not edit historical subscription price snapshots. Do not confuse current plan pricing with the price actually purchased by a subscriber.

### 6.4 Invoices & Disputes

- Invoice register and invoice detail linked to PaymentIntent.
- Refund history linked to the payment.
- Dispute/chargeback status and current case route.
- Clear distinction between an open provider dispute and a confirmed chargeback.
- Cross-link the customer and original commercial plan.
- Preserve the existing separate dispute route while mapping it into the unified Revenue shell.

A single payment should remain the source for its invoice/refund/chargeback relationships. Avoid separate duplicate financial summary records.

### 6.5 Business & Finance

This is the controlled configuration and readiness area.

Existing readiness surfaces include legal seller details, support contact and invoice prefix, policy readiness, runtime database/HTTPS/email/payment-provider configuration checks and billing settings.

Use explicit state language:

- **Configured:** required settings appear present.
- **Tested:** an actual delivery, payment, webhook or operational test has passed.
- **Blocked:** a required configuration or policy is missing/invalid.
- **Not applicable:** optional capability is not in the current commercial scope.

Never label a configuration as fully operational merely because credentials exist. For example, payment keys being present still requires a test purchase/webhook check; transactional email configuration still requires a real delivery test; a server database setting does not prove backup/restore.

### 6.6 Cross-domain connections

- Academy: CourseOffer and one-time hidden Plan; membership plans may map to courses through PlanCourseAccess.
- Customers: account, subscription owner, payer, ticket and Customer 360.
- Growth: referral discount, campaign/promotion provenance, reward eligibility and gift context.
- Platform: payment webhooks, provider events, durable reconciliation jobs and audit events.
- Command Centre: failed/pending payment exceptions and blocked readiness items.

**Existing foundations:** PaymentIntent, Refund, Invoice, plan/product/pricing/subscription models, geo prices, business/billing settings, payment/finance/business screens and separate disputes route.  
**Proposed experience:** one Revenue area with clear separation between recurring membership commerce and individual course purchases.

## 7. Domain 5 — Growth

**Responsibility:** Understand and operate acquisition, campaign/promotion performance, referrals, rewards, gifts and email delivery.

**Primary question:** Where are learners coming from, what growth mechanisms are working, and are our communications reaching them?

### 7.1 Child destinations

- **Analytics**
- **Campaigns & Promotions**
- **Referrals & Rewards**
- **Gifts**
- **Email Delivery**

### 7.2 Analytics

The current admin-only analytics endpoint returns reporting sections for signups, email, campaigns, promotions and referrals.

The redesigned analytics landing should:

- Use explicit time windows and comparison periods.
- Label the source and definition of each metric.
- Separate activity/volume from conversion and revenue.
- Link from a metric to the relevant campaign, referral, email log or payment record only when the underlying data supports it.
- Avoid presenting estimates as booked revenue.
- Keep the Command Centre focused on actions; Growth analytics is where deeper performance analysis lives.

Detailed metrics, attribution model and campaign records require further inspection before the final charts are specified.

### 7.3 Campaigns & Promotions

Treat campaign configuration, promotion configuration, and campaign/promotion performance as connected but distinct concepts.

The workspace should eventually show:

- Campaign identity and active period.
- Promotion/coupon identity and eligibility.
- Intended audience/channel.
- Resulting signups or purchases where attribution exists.
- Usage/discount and financial outcome where recorded.
- Links to the resulting PaymentIntent and customer.

Do not invent a campaign editor or claim every marketing metric is linked to a purchase until the source models and attribution are audited. Some growth configuration currently remains in Django Admin.

### 7.4 Referrals & Rewards

Existing model families include referral codes, referrer/referred-user relationships, referral status, referral settings, reward records and reward ledger entries. PaymentIntent can record the referral whose discount was applied. A reward may have a pending/unlock lifecycle and separate ledger entries.

The screen should present a connected referral record:

- Referrer and referred learner.
- Code/relationship and created/completed state.
- Whether the referred learner used an eligible discount.
- Qualifying purchase and payment record if present.
- Reward amount, currency, unlock state and ledger history.
- Referral settings and eligibility rules, permission-scoped.

Avoid showing a reward as available before its configured delay/eligibility conditions have passed. Refund/chargeback interactions must remain visible to the reward calculation and ledger process.

### 7.5 Gifts

Gift lifecycle connects GiftInvite and PendingGiftClaim to a claimed user and a gifted Subscription. The Subscription model stores gift provenance, including gift sender/message and gift state.

The gift workspace should distinguish:

- Invite created and recipient email.
- Claimable/expired/stale/pending claim state where source rules permit.
- Claimed-by member.
- Gifted plan/subscription status and duration.
- Sender and message where appropriate.
- Any delivery/claim failure requiring support.

A gift is not the same as a referral reward or an ordinary subscription purchase. It must link to the resulting Subscription rather than creating a parallel entitlement ledger.

### 7.6 Email Delivery

The current EmailLog tracks queued, sent, failed and bounced statuses. Resend webhook handling receives signed delivery/bounce/complaint events. Growth also contains MarketingPreference and Suppression records; suppression is compliance evidence and is configured read-only in Django Admin.

The redesigned view should support:

- Search by recipient/email, user, template, subject and status where permissions allow.
- Email event/detail with timestamps, provider delivery state and safe error summary.
- Distinguish queued/sent from actually delivered where the webhook data supports it.
- Show bounce/complaint and suppression state.
- Show marketing opt-in preference separately from transactional email eligibility.
- Never offer a casual delete action for suppression/compliance evidence.
- Link to the learner and originating support/payment/campaign record where metadata supports it.

### 7.7 Cross-domain connections

- Customers: referrer, referred learner, recipient, preferences and gift recipient.
- Revenue: PaymentIntent, discount, purchase, Subscription and reward-triggering events.
- Academy: course purchases and course offers where the campaign/referral points to them.
- Platform: email webhook delivery, provider failures and asynchronous jobs.
- Command Centre: operational email failures only when they require staff action, not every normal delivery event.

**Existing foundations:** admin analytics endpoint, referral/gift/marketing/suppression models and Django Admin configuration, EmailLog and signed Resend webhook.  
**Proposed experience:** one Growth workspace with performance, acquisition mechanisms and message delivery clearly separated.

## 8. Domain 6 — Platform

**Responsibility:** Keep the service operating safely: asynchronous jobs, external provisioning, integrations, security, audit, policy/runtime readiness and staff access.

**Primary question:** Is the platform functioning correctly, and can an operator investigate an issue without creating a second failure?

### 8.1 Child destinations

- **Background Jobs**
- **Provisioning & Integrations**
- **Security & Audit**
- **Policies & Readiness**
- **Staff & Permissions**
- **Advanced Administration** (separate, visually secondary during phased migration)

The cross-domain Operations Timeline remains in Command Centre for detection and understanding. Platform owns the detailed operational records and supported controls.

### 8.2 Background Jobs

The durable Job model records kind, status, payload, attempts, max attempts, next retry time, lock time, idempotency key and timestamps. PeriodicJob separately records scheduler configuration, enabled state, interval, last run and last status/error.

The queue should distinguish:

- Pending.
- Running.
- Succeeded.
- Failed.
- Stalled/long-running or retrying, as a derived operator signal rather than a new stored status.

Detail view:

- Job kind and safe identifier.
- Current state, attempt count and maximum attempts.
- Created/updated/next attempt/lock timestamps.
- Safe error summary and linked source business record where the payload/model permits it.
- Related PeriodicJob or provisioning operation where appropriate.

Do not expose raw payloads, tokens or secrets. The existing Admin Desk job-detail route is read-only; safe retry/cancel/replay actions are not established by that route and must not be invented in the design.

### 8.3 Provisioning & Integrations

ProvisioningOperation records grant/revoke intent and external side-effect progress. States include pending, creating, created, sending, sent, unknown external state, completed and failed. Retries reuse the same operation identity and persisted invite link; a new grant after a completed revoke uses a new operation.

The screen should explain:

- Which learner is affected.
- Which external channel/group is involved, within permission scope.
- Grant vs revoke.
- Current internal state vs unknown external state.
- Attempt count, last error summary and timestamps.
- Whether reconciliation or manual investigation is required.
- Link to Customer 360 and related support ticket.

Never show the persisted invite link, provider secrets or raw external identifiers in broad operational summaries. The current Admin Desk provisioning detail is intentionally read-only and omits external IDs/payloads. A retry or repair action needs a separately verified safe service operation.

Telegram/Discord identity linking is different from a legacy login being verified. Customer 360 must preserve that distinction.

### 8.4 Security & Audit

Existing AuditLog records actor, action, object type/object ID, metadata and creation time. SecurityEvent exists separately on the accounts side. Domain events are a separate event source.

The unified screen may combine these as a permission-scoped investigation view, but must retain source labels and event semantics:

- Audit log: who changed or acted on a record.
- Security event: security-related activity.
- Domain event: business lifecycle event.
- Operational log/job error: system processing evidence.

Avoid mixing these into an undifferentiated activity feed. Hide raw security identifiers and metadata fields that a staff member is not permitted to inspect. Provide links to the affected canonical record.

### 8.5 Policies & Readiness

This area connects legal policy versioning, business configuration and operational readiness.

Show:
- Active/missing/placeholder policy versions and checkout-readiness effect.
- Seller/invoice configuration.
- Database/HTTPS/email/payment provider configuration.
- Which checks are configuration-only and which have an actual test result.
- Date and evidence for completed operational tests, if such evidence is available.

Do not present a green “ready” state where the source has only checked whether environment variables or settings are populated.

### 8.6 Staff & Permissions

The design should make access understandable before it makes access changes possible.

First pass:
- Staff member identity and active status.
- Group/role membership.
- Relevant model/action permissions.
- Plan-specific reviewer scope for access tickets.
- Last relevant admin activity where the existing audit model supports it.

Proposed migration: begin with read-only permission explanation and links to Advanced Administration. Permission editing is high risk and should stay in the existing protected destination until the role matrix, server-side enforcement and audit workflow are designed and tested.

### 8.7 Advanced Administration

Keep a visible but secondary destination during the migration. It is the temporary home for Django Admin capabilities that have not yet been moved into a safe, reviewed Admin Desk workflow.

Maintain a feature migration register with:
- Current Django Admin model/view.
- User/persona and frequency.
- Risk level.
- Read/write actions and permissions.
- Dependencies and audit requirements.
- Replacement screen.
- Parity test and rollback plan.
- Migration status.

Do not remove an advanced feature simply because it is low-frequency. Retire it only after an equivalent destination is live, tested and approved.

### 8.8 Cross-domain connections

- Command Centre: timeline signals and global action queue.
- Customers: affected user, ticket and community-account status.
- Revenue: payment webhook and billing integration failures.
- Growth: email provider events, campaign jobs and referral jobs.
- Academy: content/media processing and publication operations where the actual source event exists.

**Existing foundations:** Job, PeriodicJob, ProvisioningOperation, operations timeline/detail routes, AuditLog, SecurityEvent, domain events, policy/business readiness and Django Admin.  
**Proposed experience:** cohesive Platform workspace with explicit separation between monitoring, investigation and permitted controls.

## 9. How the six domains connect: navigation contract

### 9.1 Canonical ownership matrix

| Record / concept | Canonical owner | Appears contextually in |
|---|---|---|
| User / learner account | Customers | Academy, Revenue, Growth, Platform, Command Centre |
| SupportTicket and TicketMessage | Customers | Command Centre, Customer 360, Operations Timeline |
| Course / Module / Lesson / CourseImport | Academy | Command Centre, Customers progress, Revenue offer link, Growth performance |
| CourseOffer | Academy | Revenue plan detail, Customer 360 purchase history |
| Plan / Product / PlanPrice / GeoPlanPrice | Revenue | Academy offer/membership context, Customers subscription/access context, Growth attribution |
| Subscription / SubscriptionHistory | Revenue | Customer 360, Academy membership access context, Growth gifts/rewards |
| PaymentIntent / Refund / Invoice / dispute | Revenue | Customer 360, Support ticket context, Command Centre |
| CourseEntitlement / CourseEntitlementEvent / LessonProgress | Academy | Customer 360, Revenue purchase context, Command Centre where exceptions exist |
| Referral / ReferralReward / reward ledger | Growth | Customers, Revenue transaction provenance |
| GiftInvite / PendingGiftClaim | Growth | Customers, Revenue gifted subscription |
| EmailLog / Suppression / MarketingPreference | Growth | Customer 360 safe summary, Platform provider health, Command Centre when action required |
| Job / PeriodicJob / ProvisioningOperation | Platform | Command Centre, Customer 360 safe status, Support ticket context |
| Notification | Recipient's notification feed | Command Centre entry point; links to owning domain |
| AuditLog / SecurityEvent / Domain Event | Platform | Command Centre timeline, relevant record activity sections |

### 9.2 Cross-link rules

- A cross-domain link must open the same canonical record, not a duplicate record page.
- Preserve search/filter/return context when moving from a queue to a detail page and back.
- Use a compact relationship panel rather than repeating entire foreign workspaces.
- Keep read-only context distinct from editable controls.
- If the current user cannot view a related record, show no data or a clear permission-limited state; do not leak its existence through counts, names or error text.
- Any global badge count must be computed from records the user is authorised to see.
- Activity timelines must identify whether an entry is a business event, notification, staff action, system operation or security event.

## 10. Priority end-to-end journeys the design must support

### Journey A — Create, review, publish and sell a course

1. Editor opens Academy → Course Builder and works in the currently supported authoring path.
2. Editor submits a draft; the submission becomes a CourseImport awaiting review.
3. Course Approvals queue surfaces the submission.
4. Reviewer opens the preview, checks content/assets and either returns it with mandatory feedback or approves it.
5. Approval goes through the canonical publisher and publishes the relevant course/content records.
6. Academy Course detail shows catalogue role, access type, publication and SEO state.
7. If individual purchase is intended, Academy configures a CourseOffer mapped to its dedicated hidden Plan; Revenue owns the linked Plan/price record.
8. The offer becomes saleable only after the existing course/plan/one-time-price conditions are met.
9. A successful payment creates/links the direct course entitlement.
10. Customer 360 displays the learner's entitlement and progress; the learner's progress is owned by Academy.

Design consequence: the course's editorial state, public catalogue/indexability, commercial offer and actual learner entitlement must be four clearly distinguishable facts.

### Journey B — Learner buys recurring membership

1. Revenue owns the public membership Product/Plan and its PlanPrice/GeoPlanPrice.
2. PaymentIntent captures the price/currency/provider/discount/tax snapshot.
3. The subscription service activates the Subscription on successful payment.
4. PlanCourseAccess defines which courses the plan unlocks.
5. Academy shows membership inclusion; Customer 360 shows the learner's subscription and resulting learning access.
6. Platform tracks asynchronous community provisioning/reconciliation if the plan is linked to an external channel.
7. Command Centre surfaces only a failed/unknown state that requires an operator.

Design consequence: do not turn membership access into a fake direct CourseEntitlement or assume a successful payment means Telegram/Discord provisioning has completed.

### Journey C — Review an access-request ticket

1. Customers → Support Tickets shows the ticket in the correct reviewer scope and SLA order.
2. Reviewer opens the ticket and sees the linked learner, referral/affiliate link and any default hidden plan.
3. Customer 360 context helps inspect the learner's current relationship.
4. Reviewer selects an eligible hidden Plan; plan-specific ticket_approvers controls must be respected.
5. Approval grants the hidden plan and enqueues reconciliation in the same transaction.
6. Ticket becomes approved; member notification is sent after commit using the plan's configured notice channel.
7. Platform shows external provisioning/reconciliation progress where a linked community operation exists.
8. Customer 360 shows subscription and community state; Command Centre removes the ticket from active work but may retain a separate failed-provisioning exception.

Design consequence: a ticket approval, plan grant, reconciliation job and external community membership are related stages, not one instant state change.

### Journey D — Investigate payment/access mismatch

1. Command Centre surfaces a real payment or entitlement exception using a defined source rule.
2. Operator opens Revenue → Payment detail.
3. Payment detail shows its immutable commercial snapshot, provider status, refund/dispute information and linked learner.
4. Operator opens Customer 360 to inspect existing subscription/direct course entitlement and progress.
5. If community access is expected, open the related Platform provisioning operation.
6. If member communication is needed, open or create the correct Support workflow.
7. Audit records who took each permitted action.

Design consequence: don't label a payment failure, an absent course entitlement and an external provisioning failure as the same problem. Each has a different owner and resolution path.

### Journey E — Investigate a billing support issue

1. Ticket originates in Customers and retains its SLA/assignment.
2. Ticket detail links to Customer 360 and the relevant payment/invoice.
3. Revenue is the owner of the financial transaction and refund/dispute workflow.
4. Support staff communicate with the member through public replies; internal review notes remain private.
5. The ticket is resolved/reopened using the existing service transitions.
6. The activity timeline records permitted public/status events without exposing internal notes.

Design consequence: a support ticket should not become a parallel financial ledger.

### Journey F — Trace referral or gift acquisition

1. Growth record identifies the referrer, referred learner or gift recipient.
2. Referral discount attribution links to PaymentIntent when applied.
3. ReferralReward and its ledger display reward state and any unlock delay.
4. GiftInvite/PendingGiftClaim leads to a claimed user and gifted Subscription.
5. Revenue owns the purchase/subscription record; Customers owns the learner relationship.
6. Growth analytics aggregates the appropriate recorded events.

Design consequence: reward, discount, gift claim, purchase and subscription are linked entities, not interchangeable statuses.

### Journey G — Trace an email or operational failure

1. Growth → Email Delivery shows the EmailLog and webhook/delivery status.
2. If provider/webhook processing has a durable job or system event, Platform provides the technical detail.
3. If a member is affected, Customers shows the relevant ticket/account.
4. Command Centre surfaces only the actionable exception, with a deep link to the right owner.
5. Audit/system events remain separately labelled.

Design consequence: email delivery, in-app notification, support ticket and worker job are separate sources.

## 11. Permissions and safety model across all domains

The interface must be permission-aware at every layer:

- Navigation destination.
- Domain-level counts.
- Search results.
- List rows.
- Detail sections.
- Cross-domain relationship panels.
- Actions and bulk actions.
- Export/download.
- Activity and audit visibility.

Important existing distinctions from the source baseline:

- Course content tools use course-content-admin permission checks.
- Support ticket visibility is filtered by reviewer and plan approver rules.
- Customer 360 applies separate view permissions for subscriptions, payments, invoices, Academy records and security events.
- Internal staff accounts receive a restricted Customer 360 view.
- Finance configuration and model views are gated by their respective permissions.
- Operations timeline event families are included only when the user has the corresponding model permission.

Do not infer a role matrix from menu labels. Complete the staff/group/permission audit before role-specific navigation and actions are frozen.

## 12. What is existing, proposed and not yet proven

### Existing and source-verified

- Six-domain Admin Desk concept has a shared shell prototype; the top-level grouping is owner-approved.
- Staff operational overview with permission-filtered support/operations/financial/course summaries.
- Course Builder legacy route and separate feature-flagged Tiptap development route.
- Course review queue/detail, canonical publish, feedback-required return, restricted test-import cleanup.
- SEO dashboard and indexability checks.
- Learner accounts, subscription list/actions, business/finance/invoice pages.
- Support queue/detail/actions with assignment, priority, SLA, public/internal message, access approval/rejection/reopen.
- Customer 360 with permission-scoped account, community, learning, subscription, finance, support and security context.
- Operations timeline, read-only job detail and read-only provisioning detail.
- Notification model/list/read API and staff support-ticket alert creation.
- Analytics read API for signups, email, campaigns, promotions and referrals.
- Growth data/admin configuration for gifts, referrals, rewards, preferences and suppression.
- Advanced Django Admin destination.

### Proposed Admin Desk experience

- A shared shell with six domain landing pages and nested destinations.
- One standard queue/table/detail visual system.
- Global search/quick switcher across authorised records.
- A Command Centre priority queue and consistent cross-domain deep links.
- A personal My Work view over true assignments.
- A more complete staff notification/operational alert experience, after event-source design.
- Cohesive Academy, Revenue, Growth and Platform workspaces.
- Contextual Customer 360 panel inside support ticket detail.
- A read-only staff permission explainer before any permission editing.
- A staged migration register for Django Admin capabilities.

### Needs verification before a detailed implementation specification

- Full current live/staging authenticated route visibility and role behaviour.
- Complete staff roles, groups and model/object permission matrix.
- Exact account and subscription action inventory and confirmation requirements.
- Full refund, invoice and dispute action rules and route inventory.
- Campaign/promotion data model and attribution semantics.
- Full notification event-source/recipient map beyond current support staff alerts.
- Complete list of Django Admin models/actions to migrate, retain or retire.
- Exact search scope, index fields, performance limits and pagination patterns.
- Which operations have safe supported retry/reconcile actions.
- Exact data refresh/polling requirements for each domain.

## 13. Recommended design order

Design the domains in this order, but test their cross-links from the beginning:

1. **Command Centre:** finalise queue semantics, priority rules, notification distinction and deep-link contract.
2. **Academy:** course lifecycle, review, Builder handoff, catalogue/SEO, course offer and learner access.
3. **Customers:** account list, SLA-driven support, Customer 360 and member context.
4. **Revenue:** payment/subscription/offer/invoice/dispute relationship and historical price snapshots.
5. **Growth:** acquisition/referral/gift/communications performance and its payment/customer connections.
6. **Platform:** job/provisioning/integration/security/readiness and the advanced-admin boundary.
7. **Holistic walkthrough:** complete journeys A–G with sample records through all six domains.
8. **Responsive/accessibility/edge-state review:** only after the information architecture and priority journeys are coherent.

## 14. Approval gates

Before this blueprint becomes an implementation specification:

- Review the child navigation and ownership of every destination.
- Confirm the Command Centre priority model and notification-vs-work distinction.
- Confirm Academy course lifecycle and offer/access model.
- Confirm ticket/customer context and role-specific visibility.
- Confirm Revenue's single source of truth for plans, prices, payments and refunds.
- Confirm Growth's attribution and reward semantics.
- Confirm Platform's safe operational actions and Django Admin migration boundary.
- Walk through every priority end-to-end journey.
- Validate against current live authenticated screens and staff roles.
- Record open issues and explicit owner approval.

This document is a design blueprint, not an implementation authorisation.


## 15. Workspace map and prototype artefacts

The first clickable six-domain navigation and relationship board is maintained as a standalone HTML planning artefact:

- `tradethesis_admin_six_domain_workspaces_v1.html`
- `ROUTE_TO_WORKSPACE_MAP_V1.md` — existing route and capability mapping, with proposed-vs-existing status.
- It uses the selected V2 visual template and provides a clickable overview and child destination for every proposed tab.
- Every page explains its workspace responsibility, records, lifecycle/hand-off, connected domains, source/proposal status and preservation rule.
- Records and activity are illustrative; it does not call live APIs or mutate records.
- This is an architecture review board, not the final visual design of every production screen.

The next screen-level design passes should turn each destination into a focused wireframe/prototype, beginning with Command Centre and Academy, then test the same fictional records through Customers and Revenue before extending the journeys into Growth and Platform.


## 16. Academy screen-level specification

The Academy workspace is now developed in a separate screen-level specification:

- `ACADEMY_WORKSPACE_SPEC_V1.md` — detailed fields, screen purpose, source-backed actions, route boundaries, permissions, status semantics, and edge cases for M03–M09 plus SEO and Builder hand-off.
- `tradethesis_admin_academy_workspace_v1.html` — clickable static prototype using the selected V2 shell.

The Academy screen proposal is still awaiting owner review. It does not authorise implementation and does not claim all proposed pages already exist as live Admin Desk routes.


## 17. Customers screen-level specification

The Customers domain has a first screen-level design proposal:

- `CUSTOMERS_WORKSPACE_SPEC_V1.md` — detailed source-backed account, ticket and Customer 360 semantics, proposed screen layouts, permission scope, actions and cross-domain links.
- `CUSTOMERS_REVIEW_NOTES_V1.md` — review boundary, validation and open owner decisions.
- `tradethesis_admin_customers_workspace_v1.html` — clickable static prototype using the approved V2 shell.

The proposal covers Customers Overview, Learners & Accounts, Learner Account Detail, Support Tickets, Ticket Detail and Customer 360. It remains pending owner review and does not authorise implementation.


## 18. Revenue screen-level specification

The Revenue domain has a first screen-level design proposal:

- `REVENUE_WORKSPACE_SPEC_V1.md` — detailed payment/refund/subscription/plan/price/invoice/dispute/business semantics, existing routes, permission boundaries and proposed screen layouts.
- `REVENUE_REVIEW_NOTES_V1.md` — source boundaries, browser smoke tests and open owner decisions.
- `tradethesis_admin_revenue_workspace_v1.html` — clickable static prototype using the approved V2 shell.

The proposal covers Revenue Overview, Payments & Refunds, Payment Detail, Subscriptions, Plans & Pricing, Invoices, Invoice Detail, Disputes, Dispute Detail, and Business & Finance.

Important newly confirmed migration boundary: the current Admin Desk finance page is read-only, but the Django Admin PaymentIntent action can record a full manual refund after a refund has already been processed in the provider dashboard. It records a ledger row, audit event and applies the existing full-refund access policy; it does not initiate a provider refund. This stays in Advanced Administration until a separately approved migration.

The Revenue screens remain pending owner review and do not authorise implementation.


## 19. Growth screen-level specification

The Growth domain has a first screen-level design proposal:

- `GROWTH_WORKSPACE_SPEC_V1.md` — detailed analytics/attribution, campaign, automation, coupon, referral/reward, gift, email delivery and advanced growth model semantics, route boundaries, execution caveats, permissions and cross-domain journeys.
- `GROWTH_REVIEW_NOTES_V1.md` — source boundaries, browser smoke tests and open owner decisions.
- `tradethesis_admin_growth_workspace_v1.html` — clickable static prototype using the approved V2 shell.

The proposal covers Growth Overview, Analytics & Attribution, Campaigns & Audiences, Journeys & Automation, Promotions & Coupons, Referrals & Rewards, Gifts, Email Delivery and Advanced Growth.

The source pass confirmed material caveats that must remain visible: the campaign send sweep uses a stub provider; additional campaign channels are staged; the analytics “signups” report counts purchase Events; promotion aggregate has an import defect; referral reward unlock logic has a PaymentIntent status mismatch; optional referee bonus credit currently logs only; reward balance helper mixes currencies; and the custom Referral Rewards Overview does not enforce staff-only access.

The Growth screens remain pending owner review and do not authorise implementation.


## 20. Platform screen-level specification

The Platform domain has a first screen-level design proposal:

- PLATFORM_WORKSPACE_SPEC_V1.md — detailed Job/PeriodicJob/worker lifecycle, provisioning state, integration/webhook evidence, audit/security, policies/readiness, staff authorization and migration boundaries.
- PLATFORM_REVIEW_NOTES_V1.md — source boundaries, browser smoke tests and open owner decisions.
- tradethesis_admin_platform_workspace_v1.html — clickable static prototype using the approved V2 shell.

The proposal covers Platform Overview, Jobs & Scheduler, Access & Provisioning, Integrations & Webhooks, Audit & Security, Policies & Readiness, Staff & Permissions and Migration Boundary.

The most important design constraint is that this extends the existing permission-filtered Operations Timeline and read-only Job/Provisioning detail routes. It does not create a second queue. Durable Jobs, PeriodicJob, ProvisioningOperation, UserChannelAssignment and ChannelMembershipSnapshot retain their distinct meanings. Unknown external state remains unknown and is not treated as failure.

The source pass also identified governance/verification gaps that must stay visible: /health/ is only a primary database SELECT 1 probe; configuration presence is not provider verification; AuditLog lacks an inspected append-only model guard; published PolicyVersion content immutability is not fully enforced; and the IsRoleAdmin API gate includes any is_staff user.

The Platform screens remain pending owner review and do not authorise implementation.


## 21. Holistic six-domain walkthrough (M50)

The six top-level workspaces now have an integrated clickable workflow board:

- `HOLISTIC_WALKTHROUGH_V1.md` — detailed seven-journey record graph, canonical ownership, lifecycle rules, permissions and source gaps.
- `HOLISTIC_REVIEW_NOTES_V1.md` — browser test record and owner decisions.
- `tradethesis_admin_holistic_workflow_v1.html` — M50 static prototype with 40 fictional linked records.

The shared sample follows Maya Chen through a course review/purchase, membership and community access, first/last-touch campaign and referral, a support billing issue/dispute, a gift invitation failure and email evidence. Dev Singh's access request connects Customers approval through Revenue subscription grant and Platform reconciliation. Rohan Patel is Maya's referrer.

The integrated source pass clarified two course-purchase details:
- CourseOffer activation uses Academy `activate_course_payment`, grants CourseEntitlement and records an `academy.entitlement_granted` (or simulation) Event. The inspected course branch does not write `purchase.completed`.
- Checkout can snapshot a coupon on the course PaymentIntent, but the CourseOffer activation branch returns before the ordinary membership CouponRedemption logic. The example keeps PI-7001 course purchase coupon-free and shows coupon/referral stacking on standard membership PaymentIntent PI-7002 instead. Course coupon policy needs explicit owner/engineering review.

The other critical invariant is that successful worker execution is not external provisioning completion: support ticket TCK-4402 can be Approved, Subscription SUB-8114 granted and reconciliation Job JOB-8432 Succeeded while external ProvisioningOperation PROV-8C14 is still Unknown. The UI must not collapse these states.

M50 passed 159/159 browser checks, including desktop shell geometry, all seven journeys, Inspect previews, 40-row register/search/owner filter, responsive mobile drawer and no-overflow checks at 390px. All records are fictional and no live APIs or mutations are connected.

This is the end-to-end architecture review artefact. All six domains and M50 remain pending owner review; implementation remains unauthorised.
