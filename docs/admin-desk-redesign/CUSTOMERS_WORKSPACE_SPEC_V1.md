# TradeThesis Admin Desk — Customers Workspace Specification V1

**Status:** First screen-level design proposal; owner review pending  
**Date:** 2026-11-14  
**Planning branch:** `admin-desk-redesign-planning`  
**Source baseline:** `my-new-branch`  
**Visual template:** Selected V2 forest-green / warm-ivory shell, restrained terracotta and sage, editorial serif page headings and compact sans-serif controls.  
**Implementation status:** Planning and static mockup only. No application code, routes, permissions, APIs, database records or deployment settings have been changed.

## 1. Scope

The Customers domain owns learner identity, account operations and the support relationship. It contains five screen types in this first pass:

1. **M27 — Customers Overview:** attention-first entry point for member-impacting work.
2. **M12 — Learners & Accounts:** searchable non-staff learner register.
3. **M28 — Learner Account Detail:** canonical account record and controlled account actions.
4. **M10 — Support Tickets:** reviewer-scoped support queue.
5. **M11 — Ticket Detail:** conversation, reviewer actions and customer context.
6. **M13 — Customer 360:** read-only, permission-scoped cross-domain learner record.

The top-level six-domain navigation remains unchanged. Academy owns course content and direct course access; Revenue owns plans, payments, refunds and invoices; Platform owns provisioning and technical operations. Customers may show related context and link to those canonical records, but must not duplicate their data or action controls.

All names, usernames, emails, ticket IDs, messages, dates, amounts, counts and progress figures in the HTML are fictional illustrative data. The prototype does not call APIs, access live records, or mutate the application.

## 2. Source-verified customer and support model

### 2.1 Learner accounts

The existing Admin Desk account list is available at `/staff/admin-desk/accounts/`.

The current queryset:
- Includes non-staff, non-superuser accounts only.
- Searches username, email, first name, last name and nickname.
- Supports state filters:
  - Active = `is_active=True` and `is_banned=False`.
  - Inactive = `is_active=False`.
  - Banned = `is_banned=True`.
- Sorts by `-date_joined` (newest first).
- Paginates at 25 accounts per page.
- Annotates active subscription count only when the reviewer has `subscriptions.view_subscription`.
- Exposes account actions only when the reviewer has `accounts.change_user`.

Do not make the normal learner register a way to browse internal staff or superuser accounts. The separate Customer 360 exception for an internal staff requester is permission-scoped through a reviewer-visible ticket and described below.

### 2.2 Account detail and actions

The account detail route is `/staff/admin-desk/accounts/<uuid:user_id>/`; actions post to `/staff/admin-desk/accounts/<uuid:user_id>/action/`.

The current detail page can show:
- Account identity, email, joined date, last login, account state and ban reason.
- Legacy Telegram/Discord identity fields for the account list/detail view.
- Subscriptions and SubscriptionHistory when the reviewer has `subscriptions.view_subscription`.
- Direct course entitlements and lesson progress when the reviewer has both `academy.view_courseentitlement` and `academy.view_lessonprogress`.
- Payments when the reviewer has `payments.view_paymentintent`.
- Invoices when the reviewer has `payments.view_invoice`.

Supported account actions in the existing POST view:
- Ban (reason required, minimum five characters).
- Unban.
- Deactivate (reason required, minimum five characters).
- Activate.
- Send password-reset email, when an account email exists.

Ban, unban, activate and deactivate are audited. The account state transitions enqueue user reconciliation in the same transaction. The password-reset path uses the existing password-reset form/email process and writes an audit event when successfully submitted.

Important boundary:
- Account ban/activation is not a payment or invoice operation.
- These actions do not directly change payment, invoice or entitlement records.
- The UI must show a clear confirmation/reason requirement for high-impact account actions.
- The redesigned screen must not invent account deletion, email editing, impersonation, or role changes; these were not established by the inspected route.

### 2.3 SupportTicket model

The canonical support workflow is based on `SupportTicket`.

Categories:
- `access_request` — Access request (referral verification).
- `billing` — Billing / payment issue.
- `technical` — Technical issue (Telegram access, etc.).

Statuses:
- `pending` — Pending.
- `in_progress` — In progress.
- `awaiting_member` — Awaiting member.
- `approved` — Approved / Resolved.
- `rejected` — Rejected / Closed.
- `withdrawn` — Withdrawn by user.

Priorities and first-response SLA targets:
- Urgent — 2 hours.
- High — 8 hours.
- Normal — 24 hours.
- Low — 72 hours.

The model stores:
- User.
- Category.
- Optional AffiliateLink.
- Optional Plan.
- Member's original message.
- Status and priority.
- Assigned staff reviewer.
- `first_response_due_at` and `first_response_at`.
- Reviewer summary `admin_notes`.
- `reviewed_by` and `reviewed_at`.
- Created/updated timestamps.

A database constraint permits at most one active ticket per user/category across Pending, In Progress and Awaiting Member statuses.

Access requests require an AffiliateLink and may use only a hidden Plan. The optional plan can come from the referral link or the reviewer. Assignment must be to a reviewer who is authorised to access that ticket.

Attachments:
- Up to five images per ticket.
- Maximum 5 MB per file.
- Allowed extensions/formats: PNG, JPG, JPEG, GIF and WEBP.
- The model validates image content against its extension and stores files privately.

### 2.4 Reviewer visibility

The canonical visibility helper is `reviewable_ticket_queryset(user, queryset)`.

- Inactive users and non-staff users see no tickets.
- Superusers can see all tickets.
- For non-superuser staff, a populated `ticket_approvers` list on the relevant Plan restricts review to those approvers.
- An empty approver list retains the established any-staff behaviour.
- If the ticket has no direct Plan, the rule can be derived from the AffiliateLink's mapped Plan.
- The queryset is distinct to avoid duplicate ticket rows.

The model's `can_be_reviewed_by` is also used when validating assigned staff and when filtering eligible Plans/reviewers in the detail view.

This scope must govern:
- Queue rows and filters.
- Queue counts.
- Ticket detail access.
- Assignment choices.
- Approval/rejection plan choices.
- Customer 360 ticket history when opened from a ticket.
- Any proposed search, global search result and overview badge.

Hiding a menu item or record in the browser is not authorisation; server-side permission checks remain required.

### 2.5 Queue behaviour

Existing staff queue:
- Route: `/staff/admin-desk/support/tickets/`.
- Filters: search, status, category, priority and assignment.
- Search covers username, email, ticket message, admin notes and an exact UUID.
- Assignment filters include Assigned to me and Unassigned.
- Default queryset order is newest first (`-created_at`).
- Pagination is 25 rows.
- Summary counts are calculated from the reviewer-visible base queryset:
  - Pending.
  - Open (Pending, In Progress, Awaiting Member).
  - First response overdue.
  - Resolved/closed (Approved and Rejected; Withdrawn is not included).

The existing overdue predicate is specifically:
- Ticket is still in an active status.
- `first_response_at` is null.
- `first_response_due_at` exists and is before now.

A ticket that has received its first response is not first-response-overdue, even if the member has not replied yet.

The current query is newest-first. A proposed priority/SLA-first sort can be explored, but it is a behaviour change and must be separately approved; the prototype preserves the current newest-first default and shows SLA state clearly.

### 2.6 Ticket conversation and actions

Canonical detail route:
- `/staff/admin-desk/support/tickets/<uuid:ticket_id>/`.
- POST actions: `/staff/admin-desk/support/tickets/<uuid:ticket_id>/action/`.

Conversation:
- `TicketMessage` is append-only; existing messages cannot be edited in place.
- Public support replies are visible to the member.
- Internal notes are staff-only.
- The Customer 360 activity stream includes public messages only; internal notes are excluded.
- A staff public reply appends the message, moves an open ticket to Awaiting Member and sets `first_response_at` when not already set. The member is notified after commit.
- A staff internal note appends a private message and does not notify the member or change the ticket status.
- A member reply moves the ticket to In Progress and notifies staff.

Status transitions:
- Start Review → In Progress. If no reviewer is assigned, the transition assigns the current reviewer. It also appends a private status message.
- Awaiting Member → Awaiting Member via the status service, with an internal status message.
- Public reply → Awaiting Member.
- Member reply → In Progress.
- Reopen is permitted only from Approved or Rejected and is blocked if another active ticket exists for the same user/category. It returns the ticket to In Progress, clears review fields and reviewer summary, preserves the prior reviewer summary as an internal message, and notifies the member.

Assignment / priority:
- Only active staff who can review the ticket can be assigned.
- Priority must be one of Low, Normal, High or Urgent.
- If priority changes before first response, the model recalculates the first-response deadline.
- Assignment and priority changes write an audit event.

Approval:
- Only open tickets can be approved.
- For an access request, a hidden Plan is required. The eligible-plan list is filtered by reviewer scope.
- Approval uses `approve_ticket`, which grants a Subscription through `grant_subscription_by_admin` using the Plan's grant duration, then enqueues user reconciliation inside the same database transaction.
- If enqueue fails, the grant and ticket approval roll back.
- Ticket status/reviewer/timestamps are saved, then member notifications are attempted after commit using the Plan's configured notification channel (Telegram, email or both).
- For Billing and Technical categories, approval means resolving the ticket. It does not grant a subscription.

Rejection:
- Requires a non-empty reason.
- Uses the canonical `reject_ticket` service.
- Marks the ticket Rejected, records reviewer and review time, and notifies the member after commit.

Important wording distinction:
- `admin_notes` is the reviewer/resolution summary used in the approval/rejection process and member notification. The UI can show the last reviewer summary.
- An internal `TicketMessage` is a separate append-only staff-only conversation note.
- Do not label every field called “note” as private. Make member-visible resolution feedback and private internal notes unmistakably different.

### 2.7 Customer 360

Existing route: `/staff/admin-desk/customers/<uuid:user_id>/`.

Customer 360 is read-only. It opens from a support ticket and can also be reached through learner account access when the reviewer has the necessary account permission.

Resolution and visibility:
- The view first tries to resolve the profile through a reviewer-visible ticket for that user.
- This permits an internal staff account that raised a ticket to be reached through that visible ticket.
- If no visible ticket exists, the reviewer must have `accounts.view_user` to load a normal learner profile.
- Internal staff/superuser profiles are restricted to identity and reviewer-visible support history. They do not show subscription, payment, invoice, course, community identity or security records.

Separate permission gates:
- Account identity: resolved through ticket scope or `accounts.view_user`.
- Subscriptions: `subscriptions.view_subscription`.
- Payments/refunds/chargebacks: `payments.view_paymentintent`.
- Invoices: `payments.view_invoice`.
- Academy records: both `academy.view_courseentitlement` and `academy.view_lessonprogress`.
- Security events: `accounts.view_securityevent`.

Community account distinction:
- The managed Telegram/Discord state is read from `TelegramAccount` and `DiscordAccount` records in bot integration.
- If a managed account exists and is active, status is Linked.
- If it exists but is inactive, status is Disconnect pending.
- Legacy `telegram_verified` / `telegram_id` without a managed Telegram account is Login only.
- Legacy `discord_verified` / `discord_id` without a managed account is Legacy identity only.
- Do not equate legacy login identity with current managed community membership.
- Community identity details are not shown for internal staff profiles.

Customer 360 sections:
- Account identity and state.
- Community connections (learner profiles only).
- Reviewer-visible support tickets.
- Subscriptions and SubscriptionHistory.
- Payment snapshots, refund state/count and chargeback state.
- Invoice snapshots.
- Direct CourseEntitlement records and state.
- Learning progress calculated against published modules/lessons only.
- CourseEntitlementEvent history.
- A chronological activity view.
- Security events, if permitted, as event types and timestamps only.

Safety:
- Internal support notes are excluded from the customer activity timeline.
- Raw IP addresses, user agents and security event details are excluded.
- Raw provider payment IDs/tokens are not placed in the generic Customer 360 timeline.
- Each related section is independently permission-gated.
- A missing panel can mean no permission or no records; the interface should make that distinction clear where the source provides it.

The existing Customer 360 aggregates bounded result sets (for example, most recent subscriptions, payments, tickets and events). The detailed screen should preserve clear limits/pagination before any future expansion increases the query load.

## 3. M27 — Customers Overview

**Purpose:** Show work affecting learners and route the operator to the owning destination.

**Primary question:** Which customer-related issues need attention, and where do I resolve them?

Recommended hierarchy:
1. Small context indicators: open tickets, overdue first responses, unassigned tickets and recently resolved tickets. Each count must use the current staff member's reviewer-visible support scope.
2. Cross-customer attention queue, prioritised by:
   - First-response SLA overdue.
   - High/urgent unassigned work.
   - New member replies.
   - Issues with a linked external community/provisioning exception when a real source record supports it.
3. Customer destinations: Learners & Accounts, Support Tickets, Customer 360.
4. Cross-domain hand-offs to Academy, Revenue and Platform.

The overview is a router and a work summary, not the resolver. Ticket actions stay in Ticket Detail, account actions stay in Learner Account Detail, and payment or provisioning repair actions stay in Revenue or Platform.

The mockup counts and attention items are illustrative; the current overview does not yet provide a universal customer case-management queue. A role-aware cross-domain customer attention layer is proposed.

## 4. M12 — Learners & Accounts

**Purpose:** Search and manage the canonical User account without exposing internal staff accounts in the normal learner directory.

Recommended columns:
- Learner name / username / email.
- Account state: Active, Inactive or Banned.
- Active subscription count only if permitted.
- Joined date.
- Last login.
- Account Detail and Customer 360 links.

Filters:
- Search username, first/last name, nickname or email.
- Active.
- Inactive.
- Banned.

Preserve:
- Non-staff/non-superuser list scope.
- Newest-joined-first ordering.
- 25-row pagination.
- Subscription count permission gate.
- Clear no-results state distinct from a genuinely empty account list.

The Customer 360 entry should be a separate action from Account Detail. Account Detail contains the account-specific state and any permitted administrative actions; Customer 360 is the read-only cross-domain relationship record.

## 5. M28 — Learner Account Detail

**Purpose:** Provide one canonical account-management record.

Sections:
1. Identity, username, email, joined date, last login and account status.
2. Community summary; do not claim managed Telegram/Discord membership from legacy login verification alone.
3. Account actions, only when `accounts.change_user` is present.
4. Subscriptions and access history when permitted.
5. Direct course entitlements and learning progress when both Academy view permissions are present.
6. Recent payments when permitted.
7. Invoices when permitted.
8. Clear links to Customer 360, Support Tickets, Academy and Revenue.

Actions:
- Ban/unban.
- Activate/deactivate.
- Password-reset email.

For ban/deactivate, require a reason (minimum five characters) and show the audit/reconciliation consequence. Never imply that changing account status refunds or cancels a payment or automatically rewrites invoices.

## 6. M10 — Support Tickets Queue

**Purpose:** Process support work using existing reviewer scope, priority, response deadline and category.

Queue row fields:
- Ticket short ID.
- Learner name and email.
- Category.
- Concise request.
- Status.
- Priority.
- First-response state/deadline.
- Assigned reviewer or Unassigned.
- Submitted time.
- Open Ticket Detail.

Queue filters:
- Search member/email/ticket text/UUID.
- Status.
- Category.
- Priority.
- Assigned to me.
- Unassigned.

Summary indicators:
- Pending.
- Open.
- First response overdue.
- Approved/rejected.

The first version preserves newest-first ordering to match the current source. A priority/SLA-first ordering can be assessed later as an explicit behaviour decision. Colour is never the only way to communicate priority or overdue state; use labels and due times.

## 7. M11 — Ticket Detail

**Purpose:** Resolve or progress one support case without splitting the conversation from the review controls.

Recommended layout:
- Header: short ID, category, status, priority, created/updated times and queue return link.
- Request card: member, assignment, deadline, member's original request, referral link/Plan context for access requests, evidence attachments.
- Conversation: append-only chronology with visible Member, Support and Internal Staff Note styles.
- Compose area: one mode at a time — Public Reply or Internal Note.
- Reviewer rail: assignment, priority, status transitions and approval/rejection/reopen actions.
- Customer context panel: short account/community/access summary with link to Customer 360.
- Related domain links: Academy, Revenue, Platform only where the actual relation/source record exists.

Decision safeguards:
- An access request exposes only reviewer-eligible hidden Plans.
- Approval clearly says it grants a subscription and enqueues reconciliation; it is not a one-time course purchase.
- Billing/Technical approval is resolution only.
- Reject requires a reason.
- Reopen shows that another active ticket in the same user/category blocks reopening.
- Public and internal compose modes must not look interchangeable.
- Member-visible resolution summary is distinguished from private internal TicketMessage.

## 8. M13 — Customer 360

**Purpose:** Provide a single read-only learner relationship view, opened from Support, Accounts, Revenue or Academy.

Header:
- Name, username, email.
- Active / Inactive / Banned.
- Joined and last sign-in.
- Managed Telegram / Discord status for learner accounts only.

Summary indicators:
- Open support tickets in the current review scope.
- Active subscriptions when permitted.
- Successful payments when permitted.
- Active direct course entitlements when Academy records are permitted.

Internal tabs / sections:
- **Overview:** identity, current commercial and learning summaries, recent support history, community connection context.
- **Learning & Access:** direct entitlements, grant source, starts/expiry/state and published-lesson progress.
- **Revenue:** subscription/history, payment/refund/dispute state and invoices.
- **Support:** reviewer-visible ticket history and links.
- **Community & Security:** managed Telegram/Discord state; security event type/time only when permitted.
- **Activity:** chronological source-labelled activity, excluding internal support notes and sensitive provider/security details.

Account type / permission states:
- Normal learner account with the relevant permissions.
- Normal learner account with some permission-gated panels absent.
- Internal staff requester reached through a visible ticket: identity + reviewer-visible support only.

The mockup includes a local display-only selector to demonstrate the internal-account restriction. It is not a real role switch and does not change permissions.

Customer 360 remains read-only. It links to the canonical owner for account actions, ticket actions, course access, payments, invoices or provisioning.

## 9. Cross-domain ownership and hand-offs

| Customer screen context | Canonical owner | Destination |
|---|---|---|
| Account status, ban, activation, password reset | Customers | Learner Account Detail |
| Ticket status, assignment, public reply, internal note, approval/rejection | Customers | Ticket Detail |
| Direct CourseEntitlement and LessonProgress | Academy | Learner Access & Progress / canonical course-learner record |
| Subscription, plan, payment, refund, invoice or dispute | Revenue | Subscription / Payment / Invoice detail |
| Telegram/Discord provisioning operation | Platform | Provisioning & Integrations / operation detail |
| Referral record or reward | Growth | Referral / Reward detail |

Specific journeys to validate:
1. Access request → Support ticket → Customer 360 → hidden Plan → grant + reconciliation → Platform provisioning state.
2. Billing issue → Support ticket → Customer 360 → Revenue payment/invoice → support response.
3. Course access issue → Customer 360 → Academy entitlement and progress → linked Revenue payment or subscription.
4. Community access issue → Customer 360 managed Telegram/Discord state → Platform provisioning operation → Support communication.
5. Account restriction → Learner Account Detail → audited account state transition + reconciliation → member support context.

## 10. Prototype artefact

**HTML:** `tradethesis_admin_customers_workspace_v1.html`

Included:
- Customers Overview.
- Learners & Accounts.
- Learner Account Detail.
- Support Tickets queue with search and filters.
- Ticket Detail with simulated public reply/internal note modes and action rail.
- Customer 360 with Overview, Learning & Access, Revenue, Support, Community & Security and Activity sections.
- A display-only internal-staff requester restriction preview.
- V2 shell and cross-domain navigation entry points.

All sample data is fictional. Clicks are local prototype behaviour or explanatory messages only; no backend request or record mutation occurs.

## 11. Browser smoke-test record

Tested with a headless Chromium session:
- Initial Support Tickets page renders.
- Billing + learner search filters reduce the sample queue to the expected row.
- Resetting filters reveals the full sample queue.
- Ticket queue → Ticket Detail navigation.
- Public reply appends a local sample message.
- Internal note compose mode switches correctly.
- Ticket Detail → Customer 360 navigation.
- Customer 360 internal tabs switch correctly.
- Internal staff requester preview displays the restriction banner, hides cross-domain tabs and removes learner community identity.
- Learner account search filters the sample list.
- Learner list → Account Detail → back to list.
- Customers Overview navigation.
- Mobile drawer opens; selecting Customers Overview closes it.
- At 390px viewport, `document.documentElement.scrollWidth` equals `window.innerWidth` (390px).
- No JavaScript page errors in the exercised flows.

This is an interaction/layout smoke test only, not a full accessibility, security, authenticated staging or backend integration test.

## 12. Open review decisions

1. Is Customers Overview's action-first hierarchy useful, or should it be even more tightly centred on Support work?
2. Should Learners & Accounts expose account state and Customer 360 as two separate actions, as proposed?
3. Does the Account Detail page show the right administrative controls and history?
4. Is the Support Queue dense enough, and are its columns/filter set correct?
5. Should the source-preserving newest-first queue remain default, or should a separate priority/SLA-first option be introduced?
6. Does Ticket Detail make member-visible messages, internal notes and the member-facing resolution summary sufficiently distinct?
7. Is the Customer 360 internal navigation and permission-limited presentation correct?
8. Should Customer 360 be primarily a full page, with the compact context card inside Ticket Detail, as proposed?
9. Are the Academy, Revenue and Platform links positioned at the right points in the customer journey?
10. Which Customers screen needs a higher-fidelity pass before moving to Revenue?

This is a design specification for review, not implementation authorisation.
