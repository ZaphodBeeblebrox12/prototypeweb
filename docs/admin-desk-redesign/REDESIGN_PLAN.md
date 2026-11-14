# TradeThesis Admin Desk Redesign — Planning Brief

**Status:** Discovery and design planning only  
**Branch:** `admin-desk-redesign-planning`  
**Planning baseline:** `my-new-branch` (Academy staging source branch)  
**Implementation status:** Not started. No application code, templates, models, APIs, migrations, permissions, or deployment configuration should be changed during this phase.

## 1. Purpose

Redesign the TradeThesis Admin Desk as a coherent operational workspace, rather than replacing the current system with a generic SaaS dashboard.

The redesign must make existing capabilities easier to discover and use while preserving the permissions, business rules, data relationships, and safety checks that already exist. It should also make gaps visible instead of presenting proposed features as though they are already implemented.

The desired outcome is a reviewed set of information architecture, user journeys, screen specifications, responsive wireframes, visual mockups, interaction prototypes, and an implementation handoff. Only after those artefacts are reviewed and approved should implementation begin on a separate implementation branch.

## 2. Non-goals and hard boundary

During this planning branch:

- Do not edit Django views, URL configuration, models, serializers, forms, templates, static assets, JavaScript, CSS, migrations, or settings.
- Do not change permissions, role assignments, approval rules, support SLAs, billing behaviour, publication behaviour, notification delivery, or access provisioning.
- Do not deploy to Render or modify the live/staging service configuration.
- Do not remove or replace Django Admin workflows until an equivalent Admin Desk workflow has been designed, implemented, tested, and approved.
- Do not treat the previous standalone HTML dashboard as an implementation specification. It is an exploratory visual direction only.
- Do not assume the Tiptap editor is ready to replace the existing Course Builder. Its feature-flagged state and current integration boundary must be respected.
- Do not invent data, metrics, or operational states in a future connected UI. Mockup data must be clearly marked as illustrative.

This branch is for research, planning, discussion, design and static mockups only.

## 3. Design intent

The Admin Desk should feel like the control room for running TradeThesis Academy and its related services: calm, compact, trustworthy, quick to scan, and designed around work that needs to be done.

Provisional visual direction (to be debated, not assumed final):

- Warm light surfaces, restrained ink/charcoal typography and a controlled accent palette.
- Compact density without making tables, controls or text difficult to read.
- Clear hierarchy between urgent exceptions, daily work and low-frequency configuration.
- Strong status and priority language; colour must never be the only status indicator.
- Avoid oversized decorative KPI cards, excessive rounded containers, generic gradient-heavy SaaS styling and unnecessary whitespace.
- Reuse the site's shared navigation and established visual language where it helps continuity.
- Responsive behaviour should be designed intentionally, not achieved by merely stacking desktop cards.

## 4. Verified baseline: what exists today

The baseline was inspected from the deployed Academy staging service configuration and source on `my-new-branch`. The staging service is `tradethesis-academy-staging`, backed by the `prototypeweb` repository. The service was reported as deployed from commit `36fd220950005ef3577e00285ad30221b3d29570` on 13 November 2026. The planning branch itself is based on the source branch `my-new-branch`; confirm its current HEAD again before implementation.

### 4.1 Admin Desk and route inventory

The main Admin Desk route is `/staff/admin-desk/`.

Existing route families declared in `backend/config/urls.py` include:

| Area | Existing route family / destination | Current source-level understanding |
|---|---|---|
| Admin overview | `/staff/admin-desk/` | Permission-aware operational overview and links |
| Course Builder | `/staff/course-builder/` | Existing creator-facing authoring surface |
| Tiptap preview/API | `/staff/course-builder/tiptap/` and `/api/` endpoints | Staff-only development path; do not assume default production authoring path |
| Course approvals | `/staff/admin-desk/courses/review/` | Course submission queue and individual review |
| Approve / return | `.../approve/`, `.../return/` | Approval publishes via canonical publisher; return requires reviewer feedback |
| Import cleanup | `/staff/admin-desk/courses/import-cleanup/` | Restricted permanent cleanup for eligible test imports |
| SEO | `/staff/admin-desk/seo/` | Course overview indexability, metadata, topic overlap and content checks |
| Support queue | `/staff/admin-desk/support/tickets/` | Searchable/filterable support queue |
| Ticket detail/actions | `.../support/tickets/<id>/` | Conversation, public response, internal note, assignment, priority and review actions |
| Customer 360 | `/staff/admin-desk/customers/<user_id>/` | Permission-scoped customer history and relationship view |
| Operations | `/staff/admin-desk/operations/` | Operational timeline, support clusters and incident signals |
| Jobs / provisioning | `.../operations/jobs/`, `.../operations/provisioning/` | Detail screens for durable jobs and provisioning operations |
| Accounts | `/staff/admin-desk/accounts/` | Learner account operations |
| Subscriptions | `/staff/admin-desk/subscriptions/` | Subscription management |
| Business / finance | `/staff/admin-desk/business/`, `/staff/admin-desk/finance/` | Business setup, payments and invoice register |
| Invoices | `/staff/admin-desk/invoices/<id>/` | Invoice detail |
| Notifications | `/notifications/`, `/api/notifications/` | Existing user notification page/API, not yet confirmed as an admin-specific alert centre |
| Analytics API | `/api/analytics/overview/` | Admin-only overview data for signups, email, campaigns, promotions and referrals |
| Growth admin | `/admin/growth/...` | Gift sending and related growth administration |
| Django Admin | `/admin/` | Advanced model administration and several low-frequency/configuration workflows |
| Disputes | `/admin-disputes/` | Separate dispute workflows; exact screen inventory needs a focused audit |

Route existence does not automatically mean a route is linked from the main Admin Desk, available to every staff member, or implemented with a dedicated Admin Desk screen. Permission checks and current navigation must be confirmed route by route during discovery.

### 4.2 Academy and course operations

The current course model already distinguishes:

- Catalogue role: Flagship programme, Supporting programme, Mini-course, Hidden.
- Course access type: Free, Membership, Paid individual purchase, Mixed.
- Publication status: Draft, Published, Archived.

The current Academy data model also includes modules, lessons, release days, lesson formats, instructor-only lesson materials, offers, course entitlements, entitlement events and learner progress.

Important commerce rules to preserve in design:

- A course offer maps to a dedicated commerce Plan.
- Active individual-purchase offers require a published paid/mixed course and an active one-time price.
- Course-offer plans are hidden from the general subscription catalogue.
- Existing payment history can constrain changes to course, plan and access duration.
- Course access may be permanent or time-limited.
- Subscription-plan course access and individual course offers are different access relationships and should not be collapsed into one ambiguous “price” field.

The Admin Desk currently exposes course metrics, approval queue links, Course Builder access, course/module/lesson/offer/import/entitlement links (subject to permissions), and an SEO audit.

### 4.3 Course review workflow

The existing review queue handles submissions with status `REVIEW`. Reviewers can open a course submission preview, inspect imported content/assets, approve and publish through the canonical publisher, or return the submission to the editor.

Returning a course requires feedback. The feedback is stored with the import and the reviewer is recorded. This is an important workflow and should be represented explicitly in future queue and review mockups.

### 4.4 Support workflow

Support tickets currently cover:

- Access requests (including referral verification).
- Billing/payment issues.
- Technical issues (including community access).

The model supports Pending, In Progress, Awaiting Member, Approved/Resolved, Rejected/Closed and Withdrawn states. Priorities have first-response targets: Urgent 2h, High 8h, Normal 24h, Low 72h.

The ticket queue supports search, status, category, priority and assignment filters, including “mine” and “unassigned”. Ticket detail supports:

- Conversation history and attachments.
- Public reply to the member.
- Private internal staff note.
- Reviewer assignment and priority changes.
- Start review / awaiting member actions.
- Access-plan selection for access-request approval.
- Resolution and rejection notes.
- Reopening a resolved/closed ticket.
- Customer 360 navigation.
- Plan-specific reviewer permissions where configured.

Do not reduce this to a basic four-column ticket table. SLA state, assignee, category, priority, next action and permission-scoped access are core parts of the workflow.

### 4.5 Customer 360

The existing Customer 360 view can combine, subject to permissions and account type:

- Account identity and account status.
- Telegram/Discord community connection status.
- Subscriptions and subscription history.
- Payments, refunds, chargebacks and invoices.
- Course entitlements, entitlement events and lesson progress.
- Support tickets and public conversation activity.
- Security event history.

Internal staff profiles are deliberately more restricted than learner profiles. Future designs must communicate this permission boundary and avoid implying that every administrator can see every customer field.

### 4.6 Operations and platform signals

The existing operations timeline can bring together support issue clusters, failed/retried/stalled jobs, provisioning failures/unknown states, periodic-job errors, domain events, audit events and security summaries, within a selected time window.

The Admin Desk overview separately surfaces operational signals such as:

- Pending, failed and stalled jobs.
- Failed Telegram/community access operations.
- Pending and failed payments.
- Subscription expiry/cancellation signals.
- Overdue first-response support SLAs.

The design should prioritise actionability and explain what is affected, what happened, how severe it is, whether it is still active, and where the operator can safely investigate.

### 4.7 Revenue, business and legal readiness

Existing areas include learner accounts, subscriptions, products/plans/prices, payment intents, refunds/disputes, invoices, business details and tax settings, billing settings, sales policy readiness, runtime configuration checks and payment-provider readiness.

Some checks report configuration presence only; they do not prove a successful payment, email delivery, backup restore or end-to-end operational readiness. The UI must preserve that distinction.

### 4.8 Notifications, email and growth

The notifications app already has a per-user Notification model, unread-count context/API, list API, mark-read and mark-all-read actions, and a notifications page. This confirms member notification infrastructure; it does not establish a complete staff/admin notification centre with staff event routing, subscriptions, escalation, ownership or a global navigation bell.

EmailLog tracks queued/sent/failed/bounced status and is available through Django Admin. Analytics exposes an admin-only endpoint for signups, email performance, campaign performance, promotion performance and referral performance. Growth models/admin include gifts, referrals, referral rewards/ledger, marketing preference and suppression records. Gift sending has a dedicated admin route.

These should be considered in the information architecture even if some remain advanced/secondary destinations in Django Admin during the first release.

### 4.9 Shared navigation and editor integration

The shared sitewide navigation is included by the common authenticated base template and the Django Admin base-site override. The Admin Desk should not introduce a disconnected second global header without a deliberate reason.

The current Admin Desk itself has a compact light visual treatment and a set of functional sections, but its links are grouped within a single long page rather than a unified persistent operational navigation model.

The Course Builder has a legacy authoring path. Tiptap work exists behind a feature-flagged staff-only development path and must not be presented as the live/default editor until the separate integration decision and release gates are complete.

## 5. Design principles and product rules

1. **Work before metrics.** The home screen should answer: what needs action, what is at risk, and where do I go next?
2. **Preserve workflows.** Do not remove capability to gain visual simplicity.
3. **Permission-aware by design.** Navigation, counts, links, record details and actions must follow server-side permission rules. Hiding a button is not authorization.
4. **Separate content from commerce.** Catalogue role, access type, offer, price, billing interval, currency, access duration and actual entitlement are distinct concepts.
5. **Separate notification from work queue.** Notifications inform an operator; the destination workspace is where the task is resolved.
6. **Make ownership explicit.** Queues should expose assignee, unassigned state, due time/SLA, priority and next action where applicable.
7. **Make risk visible.** Failed payment, overdue ticket, stuck provisioning and security signals should be distinguishable from normal activity.
8. **Explain readiness accurately.** “Configured” is not the same as “tested and working”.
9. **Maintain auditability.** Sensitive actions should show who performed them, what changed, when and why, consistent with existing audit trails.
10. **Respect data scope.** Customer 360 and ticket views must not expose internal notes, secrets or restricted security identifiers to unauthorised users.
11. **Avoid duplicate sources of truth.** A redesigned screen should consume existing domain data and services instead of creating new parallel records.
12. **Progressive complexity.** Daily tasks belong in the Admin Desk; rare advanced record/configuration work may remain in Django Admin until deliberately migrated.

## 6. Information architecture — approved top-level domains, child structure in review

On 14 November 2026, the owner approved one unified Admin Desk with six top-level domains in this exact order: Command Centre, Academy, Customers, Revenue, Growth and Platform. The V2 forest-green / warm-ivory editorial shell is the selected shared visual template. The child destinations below remain a first-pass proposal for screen-by-screen review; they are not yet an implementation specification.

### 6.1 Command Centre
- Overview
- Notifications & attention (proposed admin experience; existing member notification infrastructure is not sufficient on its own)
- Operations timeline

### 6.2 Academy
- Course Builder
- Course catalogue
- Course approvals
- Course offers & pricing
- Learner access & releases
- SEO & discoverability

### 6.3 Customers
- Learners & accounts
- Customer 360
- Support tickets

### 6.4 Revenue
- Payments
- Subscriptions & plans
- Invoices, refunds and disputes
- Business & tax settings

### 6.5 Growth
- Analytics
- Campaigns and promotions
- Referrals and rewards
- Gifts
- Email delivery and suppression

### 6.6 Platform
- Background jobs
- Provisioning and community integrations
- Security events
- Audit trail
- Policies and readiness
- Staff roles and permissions (destination/workflow needs further verification)

A persistent sidebar, compact top bar, global search/quick switcher and contextual breadcrumbs should be evaluated in mockups. The sitewide navigation should remain consistent with the rest of the authenticated experience.

## 7. Work plan and decision gates

### Phase 0 — Baseline capture and route audit
**Purpose:** establish exactly what is live, linked, permission-gated, duplicated or Django-only.

Tasks:
- Record current staging service, branch and deployed commit.
- Capture desktop and mobile screenshots of the Admin Desk and each reachable admin route.
- Build a route-to-screen inventory with template, view, permission condition, primary user, data source and actions.
- Confirm which screens are linked from the Admin Desk and which are reachable only through Django Admin or direct URL.
- Audit all staff roles/groups and model permissions; identify superuser-only and plan-approver-specific actions.
- Trace the Course Builder legacy/Tiptap boundary and current feature flag.
- Identify existing search, filtering, pagination, bulk actions, export, confirmation and audit behaviours.
- Record technical and operational constraints, including slow/expensive aggregate views and high-volume tables.

**Deliverables:** route inventory, capability matrix, role-permission matrix, current-state screenshots, known-gaps register.

**Exit gate:** no critical admin workflow is omitted from the inventory; uncertain behaviour is explicitly marked for verification.

### Phase 1 — User jobs, roles and task prioritisation
**Purpose:** design around the people operating the system, not around app labels.

Tasks:
- Define administrator personas and real access levels (owner/superuser, course content admin, support reviewer, finance operator, operations reviewer, limited staff).
- List daily, weekly and exceptional tasks for each persona.
- Map task frequency, urgency, business impact, reversibility and risk.
- Identify actions requiring a reason, second review, confirmation or audit evidence.
- Decide which tasks need a dashboard shortcut versus a dedicated workspace.

**Deliverables:** persona/task matrix, top-task ranking, risk/action matrix.

**Exit gate:** agreed top workflows for the first design scope and a clear understanding of who may perform each action.

### Phase 2 — Information architecture and navigation
**Purpose:** agree the structure before drawing detailed screens.

Tasks:
- Test the proposed child destinations in Section 6 against the role/task matrix.
- Decide which items are nested, contextual, or left in Advanced Administration.
- Finalise child labels, order, grouping and role-based visibility under the six approved top-level domains.
- Define navigation badge rules: what counts as unread, pending, overdue, failed, or requiring action.
- Design empty, loading, error, permission-denied and no-access states.
- Define global search scope, quick actions and cross-links between course, learner, ticket and payment records.

**Deliverables:** approved sitemap, navigation model, permission-aware navigation rules, global search specification.

**Exit gate:** navigation reviewed against real top tasks; no duplicate or dead-end destinations.

### Phase 3 — Command Centre concepts
**Purpose:** decide what the admin sees first and how work is prioritised.

Explore at least three distinct layout concepts:
- **Action queue first:** overdue tickets, approvals, failures and business blockers dominate.
- **Operational cockpit:** split view of Academy health, customer support, revenue and platform health.
- **Personal workbench:** assigned work, recent activity, shortcuts and team-wide exceptions.

For each concept, mock:
- At-a-glance counts with explicit time windows.
- High-priority attention queue.
- Pending course approvals.
- Support SLA and ownership summary.
- Payment/entitlement/provisioning exceptions.
- Recent audit/activity timeline.
- Business and launch readiness (only where the operator has permission).

**Deliverables:** three overview directions, side-by-side comparison, chosen overview concept.

**Exit gate:** user approves the hierarchy and what belongs above the fold. Avoid committing to a metric or chart without defining its question, source and refresh expectations.

### Phase 4 — Detailed screen mockups
Design each screen at desktop and mobile/tablet breakpoints. All mockup records are illustrative until connected.

#### 4A. Shared application shell
- Sitewide header continuity.
- Sidebar expanded/collapsed behaviour.
- Active item and count badges.
- Breadcrumbs and page titles.
- Global search / quick switcher.
- Notification centre entry point.
- Account menu and role context.
- Mobile navigation and narrow-screen handling.

#### 4B. Course catalogue and course detail
- Search, filters, sorting and table density.
- Flagship / Supporting / Mini-course / Hidden distinction.
- Draft / Published / Archived lifecycle.
- Free / Membership / Paid / Mixed access model.
- Course health/readiness, published modules/lessons, preview availability and content format.
- Detail overview, editorial metadata and links to Builder/review.
- Actions consistent with existing permissions.

#### 4C. Course approvals queue and review detail
- New submission vs revision.
- Author, submitted time, course identity and status.
- Content completeness and missing assets.
- Lesson/module outline and content preview.
- Asset preview and protected asset access.
- Approve/publish validation.
- Return-to-editor feedback form.
- Test-import cleanup separated from normal rejection/return actions.
- Reviewer identity and audit history.

#### 4D. Course Builder handoff
- Clarify Admin Desk vs Course Builder responsibilities.
- Course-level links into a selected draft.
- Show video/asset presence and content readiness where reliable.
- Preserve current legacy editor path.
- Treat Tiptap as a separate prototype/integration decision until its feature flag, save behaviour, learner preview, validation and migration parity are approved.
- Do not redesign the editor itself as part of the first Admin Desk shell unless explicitly added to scope.

#### 4E. Offers, pricing and learner access
- Course ↔ offer ↔ Plan relationships.
- One-time and applicable plan price information.
- Currency and geographic pricing display.
- Active/inactive offer state.
- Access duration (permanent or time-limited).
- Membership inclusion vs individual purchase distinction.
- Current entitlements, scheduled/expired/revoked access and history.
- Safe access grant/revoke/extend actions with reasons and audit trail.
- Validation warnings for existing payment history or incompatible plan configuration.

#### 4F. Support queue and ticket detail
- Queue filters: status, category, priority, assignee, unassigned, mine, overdue.
- SLA countdown/overdue treatment.
- Ticket identity, category, summary, member and age.
- Detail view: public conversation, internal note, attachments, assignment and priority.
- Access request plan selection and approver scope.
- Resolve/reject/reopen and mandatory reason/feedback fields.
- Customer 360 side panel or contextual link.
- Mobile support workflow that keeps reply/actions usable.

#### 4G. Learner accounts and Customer 360
- Account search, status and safe account actions.
- Profile identity and status.
- Course access/progress.
- Subscription and payment history.
- Support history.
- Community connection status.
- Security events only where permitted.
- Internal-staff profile restrictions.
- Timeline filters and data provenance.

#### 4H. Revenue workspaces
- Pending/failed/successful payments.
- Refunds and disputes/chargebacks.
- Subscription status, expiry and cancellation.
- Plan/product management.
- Invoice register and invoice detail.
- Business/tax and billing settings.
- Distinguish course commerce from recurring membership commerce.
- Sensitive-action confirmation and audit display.

#### 4I. Operations and incidents
- Operational timeline with 24h / 7d windows.
- Issue clusters and affected customers.
- Job status, retries, lock age and next attempt.
- Provisioning operation state including unknown external state.
- Periodic job health and last error.
- Community integration failures.
- Domain events, audit and security summaries.
- Incident detail, safe retry/reconcile actions only where currently supported.
- Clear separation between observation and operator actions.

#### 4J. Growth, analytics and messaging
- Signups and attribution.
- Email performance and delivery status.
- Campaign/promotion performance.
- Referral performance/rewards.
- Gift sending and gift lifecycle.
- Marketing preferences and suppression handling.
- Identify which actions stay in Django Admin initially.
- Do not imply that email delivery events are the same as in-app notifications.

#### 4K. Notifications and attention centre
First decide whether this is:
- a global notification inbox,
- a live operational alert centre,
- personal task assignments,
- or a deliberate combination with distinct tabs/types.

Specify event sources, recipient rules, unread semantics, deduplication, severity, retention, deep links, escalation, polling/refresh, read/acknowledged/snoozed states and whether notifications can be assigned. Avoid building a decorative bell that is disconnected from real event sources.

#### 4L. Policies, readiness, staff and settings
- Legal policy readiness.
- Business and invoice readiness.
- Runtime/payment/email readiness with accurate “configuration present vs tested” language.
- Staff roles and permission visibility.
- Audit trail.
- Integration status and safe configuration entry points.
- Define the boundary with Django Admin.

**Deliverables:** screen-by-screen wireframes, interaction maps, responsive variants, edge-state mockups.

**Exit gate:** every high-priority admin job has a complete proposed path from entry point to completion, including permission and error states.

### Phase 5 — Visual design system
Tasks:
- Explore at least two visual directions, retaining the current warm-light direction as one candidate.
- Define typography scale, spacing, table density, layout grid, surfaces, borders, focus states and responsive breakpoints.
- Define semantic status palette for success, warning, danger, neutral and informational states.
- Define buttons, menus, filters, search, tabs, tables, empty states, banners, drawers, dialogs and toasts.
- Test long course names, long learner emails, multi-currency amounts, long ticket summaries, dense timelines and narrow screens.
- Check keyboard focus, accessible names, contrast and reduced-motion behaviour.

**Deliverables:** design tokens, component board, visual direction comparison, approved visual language.

**Exit gate:** a consistent set of components can represent every mocked screen without inventing one-off visual patterns.

### Phase 6 — Clickable HTML mockups
Purpose: test navigation and interaction before implementation.

Build standalone HTML prototypes, not connected to production data. Use seeded illustrative records and label them clearly. Include:
- Working navigation between agreed screens.
- Search/filter/sort interactions where they affect the mock data.
- Notification open/read states using clearly simulated events.
- Course review and return-feedback interaction.
- Ticket assignment/reply/status interaction.
- Customer 360 navigation.
- Offer/access detail interaction.
- Operations filters and incident drill-down.
- Responsive menu and table behaviour.

Do not call live APIs, submit actual support replies, publish courses, modify prices, grant access or change customer records from a mockup.

**Deliverables:** versioned HTML prototypes, interaction checklist, feedback notes.

**Exit gate:** the user can complete the priority journeys in the prototype without facilitator explanation; unresolved interaction choices are recorded.

### Phase 7 — Review and validation
Tasks:
- Run design reviews with the owner and relevant operational users.
- Walk through at least one happy path and one failure/edge path for every priority workflow.
- Test role-specific visibility and restricted record states.
- Test keyboard-only navigation and representative mobile widths.
- Confirm terminology is understood and consistent with existing backend language.
- Review visual hierarchy and density at actual target screen sizes.
- Record decisions, unresolved questions, rejected variants and reasons.

**Deliverables:** review log, issue list, signed-off screen designs, final sitemap and acceptance criteria.

**Exit gate:** no open high-severity design issue; owner explicitly approves the design handoff.

### Phase 8 — Implementation handoff (still not implementation)
Prepare a separate technical plan after mockups are approved:
- Route/template/view inventory mapped to proposed screens.
- Reuse vs redesign decision for each existing view.
- Required API/data changes (if any), clearly separated from presentation-only work.
- Permission matrix and server-side authorization requirements.
- Audit requirements for sensitive actions.
- Performance constraints and query budgets.
- Test plan and regression suite.
- Rollout plan, staging verification and rollback approach.
- Ordered implementation slices with dependencies and acceptance criteria.

**Deliverable:** implementation-ready technical specification and proposed implementation branch name.

**Exit gate:** owner approves the technical plan and explicitly authorizes implementation.

## 8. First-pass decisions to brainstorm

These questions should be answered in discussion, not silently decided by the prototype:

1. **Child navigation:** finalise submenu labels, destination order and role-based visibility under the six approved top-level domains.
2. **Overview:** action queue first, operational cockpit, or personal workbench?
3. **Notification model:** notification inbox, operational alerts, personal assignments, or separate surfaces?
4. **Customer 360:** full page, side drawer from tickets, or both?
5. **Course catalogue:** table-first, compact list, or hybrid cards/list?
6. **Course detail:** should the Admin Desk offer a unified course control page, or act as a well-designed launch point into existing Builder/record screens?
7. **Pricing:** should course offers and subscription plans be shown in one commerce area with clear separation, or in distinct workspaces?
8. **Django Admin boundary:** which low-frequency actions can remain there for the first redesign release?
9. **Staff permissions:** should staff-role visibility be read-only in the first pass, or is management itself in scope?
10. **Density:** how much information should be visible above the fold on the main desktop view?

## 9. Acceptance criteria for the design phase

The design is not ready for implementation until:

- Every existing high-value route and capability is accounted for in the sitemap.
- All current workflow rules and permission boundaries are documented.
- The top admin jobs have complete click-through prototypes.
- Course publishing, return-to-editor, offers, entitlements and access changes are represented accurately.
- Ticket SLA, assignment, internal/public communications and access-request decisions are represented.
- Customer 360 respects field-level/role-level restrictions.
- Operations views distinguish signals from safe actions.
- Notifications are designed from real event sources and recipient rules, not sample badge counts.
- Existing member-facing sitewide navigation remains consistent.
- Desktop, tablet and mobile states have been reviewed.
- Empty, loading, error, no-permission and success states have been considered.
- The implementation boundary with Django Admin and the Course Builder is explicit.
- The user has approved the final mockups and the implementation handoff.

## 10. Initial deliverable sequence

1. Complete and validate the current-state route/capability matrix.
2. Agree personas and top tasks.
3. Refine and approve the child-level sitemap, route-to-workspace map and permission-aware navigation.
4. Create three Command Centre concepts.
5. Select and refine the overview.
6. Create Academy, Support and Customer 360 wireframes.
7. Create Revenue and Platform Operations wireframes.
8. Create Growth, Notifications and Settings wireframes.
9. Establish visual design system.
10. Build clickable HTML prototypes.
11. Review, revise and sign off.
12. Produce implementation handoff.
13. Only then create a separate implementation branch and begin code changes.

---

## 11. Source files reviewed for this baseline

The following source files informed this planning brief:

- `backend/config/urls.py`
- `backend/apps/admin_dashboard.py`
- `backend/apps/admin_desk_views.py`
- `backend/templates/admin/desk.html`
- `backend/templates/admin/desk_support_tickets.html`
- `backend/templates/admin/desk_support_ticket.html`
- `backend/templates/admin/desk_customer_360.html`
- `backend/apps/academy/models.py`
- `backend/apps/academy/seo_admin.py`
- `backend/apps/support/models.py`
- `backend/apps/subscriptions/models.py`
- `backend/apps/notifications/models.py`
- `backend/apps/notifications/views.py`
- `backend/apps/jobs/models.py`
- `backend/apps/audit/models.py`
- `backend/apps/analytics/views.py`
- `backend/apps/growth/admin.py`
- `backend/templates/partials/sitewide_nav.html`
- `backend/templates/base.html`

This is a source-level baseline. Before finalising screen specifications, verify the current deployed HEAD, inspect the live authenticated UI, confirm staff roles/permissions and test the relevant routes with appropriately authorised accounts.


## 12. Progress snapshot — 14 November 2026

This is a planning-only progress record. It does not alter the original approval gates.

| Workstream | Current progress | Remaining |
|---|---|---|
| Unified operating workspace | Top-level six-domain model approved | Child destinations and role visibility still under review |
| Command Centre | V2 shell and three overview concepts prototyped | Confirm queue composition, priority logic, notifications vs work |
| Visual direction | V2 forest-green / warm-ivory template selected | Finish tokens, accessible contrast, keyboard and screen-reader review |
| Domain architecture | Six-domain blueprint and cross-domain ownership model documented | Owner review of detailed child structure and journeys |
| Route map | Source-level route-to-workspace inventory created | Recheck deployed HEAD and inspect authenticated live pages / role-specific access |
| Academy | Detailed screen specification and clickable V1 prototype created | Owner review and revisions |
| Customers | Detailed screen specification and clickable V1 prototype created | Owner review and revisions |
| Revenue | Detailed screen specification, clickable V1 prototype and review notes created | Owner review and revisions |
| Growth | Detailed screen specification, clickable V1 prototype and review notes created | Owner review and revisions |
| Platform | Detailed screen specification, clickable V1 prototype and review notes created | Owner review and revisions; holistic six-domain walkthrough follows |
| Handoff and resumption | Dedicated `HANDOFF_AND_RESUME.md` created | Update it after each major design pass |

### Phase status

- **Phase 0 — Baseline capture and route audit:** source-level inventory is substantially documented; authenticated live visual and role audit remains outstanding.
- **Phase 1 — User jobs, roles and task prioritisation:** initial operating model recorded; complete staff/persona and permission matrix remains open.
- **Phase 2 — Information architecture:** six top-level domains and order approved; child navigation is proposed and remains reviewable.
- **Phase 3 — Command Centre concepts:** three concepts prototyped; final composition and prioritisation rules remain open.
- **Phase 4 — Screen-level wireframes:** Academy, Customers, Revenue, Growth and Platform V1 screens/specs drafted; owner review and holistic walkthrough remain.
- **Phase 5 — Visual design system:** common V2 visual direction selected; complete component tokens and accessibility validation remain.
- **Phase 6 — Clickable HTML mockups:** shell, six-domain architecture, Academy, Customers, Revenue, Growth and Platform static prototypes created and smoke-tested; end-to-end holistic prototype remains.
- **Phase 7 — Review and validation:** owner review is pending for the domain mockups; accessibility and authenticated staging parity remain.
- **Phase 8 — Implementation handoff:** not started; only begins after the user approves the design and technical plan.

### Current implementation boundary

No application code, migrations, routes, permissions, API contracts, tests, Render settings or deployments have been changed by this planning branch. Do not begin implementation until the owner explicitly approves the design handoff.


### Revenue source files added to the design audit

The Revenue workspace pass also inspected these source files on `my-new-branch`:

- `backend/apps/payments/models.py`
- `backend/apps/payments/services.py`
- `backend/apps/payments/views.py`
- `backend/apps/payments/admin.py`
- `backend/apps/subscriptions/models.py`
- `backend/apps/subscriptions/services.py`
- `backend/apps/subscriptions/admin.py`
- `backend/apps/disputes/models.py`
- `backend/apps/disputes/services.py`
- `backend/apps/disputes/views.py`
- `backend/apps/disputes/urls.py`
- `backend/templates/admin/desk_finance.html`
- `backend/templates/admin/desk_subscriptions.html`
- `backend/templates/admin/desk_invoice_detail.html`
- `backend/templates/disputes/dashboard.html`
- `backend/templates/disputes/detail.html`

Revenue-specific source boundaries confirmed include the read-only PaymentIntent finance view, Django Admin's full manual refund recording action (after provider-side refund), audited Subscription grant/extend/cancel paths, Django Admin Plan/base/geo price configuration, immutable Invoice snapshots and the separate Dispute state machine.

### Revenue screen-design pass — 14 November 2026

- **Prototype:** `tradethesis_admin_revenue_workspace_v1.html`.
- **Specification:** `REVENUE_WORKSPACE_SPEC_V1.md`.
- **Review notes:** `REVENUE_REVIEW_NOTES_V1.md`.
- **Smoke test:** All Revenue navigation destinations, payment/subscription/plan/invoice/dispute filters, payment/invoice/dispute detail views, modal and external-submission preview, tax confirmation and mobile navigation passed. No JavaScript or console errors; 390px viewport had no horizontal overflow.
- **Data safety:** all sample amounts, records, IDs and names are illustrative; no live API/provider/database action is connected.
- **Review state:** V1 is draft for owner review; no implementation is approved.


### Growth source files added to the design audit

The Growth workspace pass also inspected these source files on `my-new-branch`:

- `backend/apps/growth/models.py`
- `backend/apps/growth/admin.py`
- `backend/apps/growth/admin_views.py`
- `backend/apps/growth/admin_urls.py`
- `backend/apps/growth/forms.py`
- `backend/apps/growth/services/gifts.py`
- `backend/apps/growth/services/referrals.py`
- `backend/apps/growth/services/rewards.py`
- `backend/apps/campaigns/models.py`
- `backend/apps/campaigns/admin.py`
- `backend/apps/promotions/models.py`
- `backend/apps/promotions/services/coupons.py`
- `backend/apps/advanced_growth/models.py`
- `backend/apps/advanced_growth/admin.py`
- `backend/apps/automation/models.py`
- `backend/apps/automation/admin.py`
- `backend/apps/analytics/views.py`
- `backend/apps/analytics/models.py`
- `backend/apps/analytics/services/report.py`
- `backend/apps/analytics/services/attribution.py`
- `backend/apps/emailing/models.py`
- `backend/apps/emailing/admin.py`
- `backend/apps/emailing/webhooks.py`
- `backend/apps/notifications/models.py`
- `backend/apps/notifications/services.py`
- `backend/apps/payments/views.py`
- `backend/apps/payments/services.py`
- `backend/apps/subscriptions/services.py`

Growth-specific source boundaries confirmed include the admin-only Analytics API and report-data issues, Campaign's frozen recipient snapshot and stub provider send sweep, staged Telegram/in-product campaign actions, coupon eligibility and immutable redemption, referral/reward currency and unlock defects, modern gift invite vs legacy gift-code paths, separate G1 Delivery and transactional EmailLog ledgers, opt-out/suppression rules and Advanced Growth commission/experiment/announcement records.

### Growth screen-design pass — 14 November 2026

- **Prototype:** `tradethesis_admin_growth_workspace_v1.html`.
- **Specification:** `GROWTH_WORKSPACE_SPEC_V1.md`.
- **Review notes:** `GROWTH_REVIEW_NOTES_V1.md`.
- **Smoke test:** All Growth destinations, campaign/coupon/referral/gift/Delivery filters, preview modals, Email Delivery subtabs, Advanced Growth subtabs and mobile drawer passed. No JavaScript or console errors; 390px viewport had no horizontal overflow after a responsive sizing correction.
- **Data safety:** all sample people, campaigns, amounts, codes and delivery states are illustrative; no API, mail provider, job or database writes are connected.
- **Review state:** V1 is draft for owner review; no implementation is approved.


### Platform source files added to the design audit

The Platform workspace pass also inspected these source files on my-new-branch:

- backend/apps/jobs/models.py
- backend/apps/jobs/admin.py
- backend/apps/jobs/worker.py
- backend/apps/jobs/scheduler.py
- backend/apps/jobs/operations.py
- backend/apps/jobs/handlers.py
- backend/apps/jobs/enqueue.py
- backend/apps/jobs/apps.py
- backend/apps/audit/models.py
- backend/apps/audit/admin.py
- backend/apps/bot_integration/models.py
- backend/apps/bot_integration/runtime_models.py
- backend/apps/bot_integration/reconcile.py
- backend/apps/bot_integration/reconcile_jobs.py
- backend/apps/bot_integration/sync.py
- backend/apps/bot_integration/views.py
- backend/apps/bot_integration/urls.py
- backend/apps/bot_integration/integration_admin.py
- backend/apps/bot_integration/services/telegram.py
- backend/apps/accounts/models.py
- backend/apps/accounts/admin.py
- backend/apps/accounts/admin_views.py
- backend/apps/admin_dashboard.py
- backend/apps/admin_desk_views.py
- backend/apps/payments/models.py
- backend/apps/payments/webhook_views.py
- backend/apps/payments/webhook_processor.py
- backend/apps/payments/admin.py
- backend/apps/emailing/webhooks.py
- backend/apps/policies/models.py
- backend/apps/policies/services.py
- backend/apps/policies/admin.py
- backend/apps/policies/views.py
- backend/apps/core/views.py
- backend/config/urls.py

Platform-specific source boundaries confirmed include the existing permission-filtered Operations Timeline and read-only Job/Provisioning details, a separate durable worker and PeriodicJob scheduler, persisted Telegram external provisioning operations and unknown-state recovery safeguards, direct native Telegram API vs legacy bridge runtime diagnostics, distinct provider webhook evidence paths, append-only SecurityEvent vs less-constrained AuditLog, partial policy-content immutability enforcement, and a staff API permission class broader than its Admin-only name suggests.

### Platform screen-design pass — 14 November 2026

- **Prototype:** tradethesis_admin_platform_workspace_v1.html.
- **Specification:** PLATFORM_WORKSPACE_SPEC_V1.md.
- **Review notes:** PLATFORM_REVIEW_NOTES_V1.md.
- **Screens:** Platform Overview, Jobs & Scheduler, Access & Provisioning, Integrations & Webhooks, Audit & Security, Policies & Readiness, Staff & Permissions, Migration Boundary.
- **Smoke test:** 30/30 browser checks passed. All Platform destinations, tabs, job filters, event-source filter, detail previews and mobile drawer passed. No JavaScript or console errors; 390px viewport had no horizontal overflow.
- **Data safety:** names, IDs, states, incidents and counts are fictional. Prototype does not read secrets, query live APIs, enqueue jobs or perform provider actions.
- **Review state:** V1 is draft for owner review; no implementation is approved.
