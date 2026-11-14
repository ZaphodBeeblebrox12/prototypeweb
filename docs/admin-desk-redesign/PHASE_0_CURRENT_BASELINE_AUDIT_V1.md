# TradeThesis Admin Desk — Phase 0 Current Baseline Audit V1

**Audit date:** 14 November 2026  
**Repository:** ZaphodBeeblebrox12/prototypeweb  
**Planning branch:** admin-desk-redesign-planning  
**Application source branch:** my-new-branch  
**Phase:** 0 — Revalidate the operating baseline  
**Implementation status:** NOT AUTHORISED  
**Audit status:** Source and Render baseline verified; authenticated staging/role verification remains outstanding.

## 1. Executive finding

The Admin Desk redesign is **not yet implementation-ready**. The current source and Render Academy deployment can now be tied to the same commit, and the source-level route/action inventory has been refreshed against that deployed SHA. However, the required authenticated staging review with representative staff roles and a superuser could not be performed in this audit environment. No live permission matrix, real account-role sample or object-level negative test is therefore signed off.

The current application is a collection of existing staff routes, permission-gated views, Django Admin model surfaces and custom staff endpoints. It is not yet the approved unified six-domain operating shell. Some proposed workspace screens are new presentation layers over existing models; others would require new staff pages or service capabilities.

The biggest immediate governance risks are:
1. Django Admin still follows the active-staff access boundary in the current configuration; no superuser-only override was found.
2. The account administration API's IsRoleAdmin permission accepts any is_staff user as well as role ADMIN and superusers.
3. The growth referral-rewards overview is login-only, not staff-only.
4. The current refund action records a refund after the operator has refunded through the provider dashboard; no staff-initiated provider refund operation was found in the reviewed payment provider module.
5. Subscription cancellation in the current service is immediate only; end-of-period cancellation is not implemented in the reviewed service.
6. The approved multiple-department staff model is not represented by the User model's single Role field; the actual mapping through Groups or other records still needs verification.

These findings do not authorise any application change. Keep the implementation hard stop in place.

## 2. Scope and evidence standard

This pass:
- Read the current planning-branch handoff, 60-decision register, implementation-readiness sequence, decision log, information architecture and route-to-workspace map.
- Confirmed the current Git branch heads and compared both directions.
- Inspected source files on my-new-branch, which is also the source SHA deployed to Academy staging.
- Read the current Render service configuration and latest deployment record for Academy and public staging.
- Inspected current URL registrations, staff/admin views, permission helpers, selected business services and source-side effects.

Evidence labels used below:
- **Verified — source:** directly supported by files on the current source branch.
- **Verified — Render:** returned by the Render service/deployment configuration.
- **Not verified — staging:** requires a live authenticated browser/session or test account and was not performed.
- **Proposed:** design or implementation target, not a current capability.

This audit is not a penetration test, full code review, data inspection, production access review or authenticated staging sign-off.

## 3. Current Git baseline

| Item | Verified value |
|---|---|
| Repository | ZaphodBeeblebrox12/prototypeweb |
| Source branch | my-new-branch |
| Source HEAD | 8832ecf9cc979747dc2715a39ecfeb7a292e55ee |
| Source HEAD subject | Migrate Trading Path key takeaways into notebook prompts |
| Source commit time | 2026-11-14 16:39:00 UTC |
| Planning branch | admin-desk-redesign-planning |
| Planning HEAD before this document refresh | 0f6e44a34c56cdccc17a3f717ee613b8b47081f1 |
| Planning HEAD subject before this document refresh | docs(admin-desk): add Phase 0 CI evidence to handoff |
| Merge base | 251260448c480ec5fbfec4f1966d9017fa0854ff |
| Planning-only commits relative to source (before this refresh) | 86 |
| Source-only commits relative to planning | 18 |
| Planning-only changed files | 23; all are under docs/admin-desk-redesign/ |

The branches are diverged. Do not merge or rebase automatically. The current comparison is 86 planning-only commits and 18 source-only commits before this documentation refresh. The comparison uses merge base `251260448c480ec5fbfec4f1966d9017fa0854ff`; this planning-only branch should not be merged or rebased automatically.

### 3.1 Source-only changes since the planning branch baseline

The 18 source-only commits modify exactly three files:
- backend/apps/academy/course_builder_api.py
- backend/apps/academy/course_builder_preview.html
- backend/apps/academy/course_builder_trading_path_import.json

They cover three related Course Builder content migrations:

**Trading Path Quick Check / Q&A migration**
- Move bundled Quick Check questions into Practice & Q&A.
- Preserve already-saved Q&A using stable question IDs.
- Remove duplicate inline Quick Check content and answer blocks from affected lesson bodies.
- Normalize lesson-title matching and limit the migration to intended daily Quick Check lessons, not unrelated checkpoint quizzes.
- Correct the Day 4 Nifty lot-size example to 65 units: 80 points × 65 units × 2 lots = ₹10,400 gross before costs.

**Learning outcomes / lesson summary migration**
- Move “What you'll learn” content from lesson bodies into the short lesson summary.
- Reconcile the intended Trading Path draft(s) on Builder load and save them as drafts.
- Refresh the selected lesson editor after the migration.
- The migration toast states that Q&A is preserved and nothing is published.

**Notebook / Key takeaways migration**
- Add the source lesson's notebook data to the draft migration payload.
- When the source notebook contains exactly three non-empty prompts labelled `Pause`, `Interpret` and `Apply` in that order, copy those prompts into the matching target lesson notebook.
- Preserve the target notebook object and its other metadata; retain its existing title, otherwise use the source title or the fallback `Before you make the call`.
- Remove the `Key takeaways` section from the matching target lesson body and report notebook/section migration counts in the Builder response and toast.
- The toast states that inline sections were removed, Q&A was preserved and nothing was published.

No Admin Desk route, Admin Desk view or permission file appears in the source-only comparison. However, the Course Builder changes are material to Academy workflow parity and must be included in regression tests. Confirm on authenticated staging that every migration is idempotent, scoped only to the intended Trading Path draft(s), preserves Q&A and notebook metadata, removes only the intended Key takeaways section and does not mutate published Course content.

The 18 source-only commits are:
1. 8124dc4 — Move Trading Path Quick Checks into Course Builder Q&A
2. fddfbfa — Merge Trading Path Quick Checks into saved Q&A drafts
3. 9da97e9 — Expose Trading Path Quick Check source for saved drafts
4. 14d7a04 — Reconcile Trading Path Quick Checks on every Builder load
5. 265c594 — Remove complete Quick Check blocks from Trading Path lesson bodies
6. fbae6f8 — Remove full Trading Path Quick Checks from saved lesson bodies
7. 8bab988 — Correct Trading Path Day 4 Q&A for 65-unit Nifty lot
8. 6081288 — Match Trading Path Q&A cleanup across legacy and imported drafts
9. 6945e10 — Limit Trading Path migration to daily Quick Check lessons
10. 77a68c6 — Fix Quick Check detector regex for legacy lessons
11. 99be31e — Move Trading Path learning outcomes into lesson summaries
12. 98220da — Expose Trading Path learning outcomes for saved-draft migration
13. ef01f2f — Migrate learning outcomes into Trading Path lesson summaries
14. c738c27 — Scope summary migration to Trading Path drafts
15. 6cdb7b9 — Refresh the selected Builder lesson after summary migration
16. a7738ea — Move Trading Path key takeaways into notebook prompts
17. 192646d — Expose Trading Path notebook prompts to draft migration
18. 8832ecf — Migrate Trading Path key takeaways into notebook prompts

The changed-file comparison from the merge base confirms that all 18 source-only commits touch only the three Academy Course Builder files listed above. No Admin Desk URL, view, permission or test file is present in that source-only delta. The latest three commits do not add a dedicated regression test for the notebook/Key takeaways migration; the green full-suite CI result below is therefore not a substitute for the specific idempotence/content-preservation checks.

## 4. Current Render baseline

### 4.1 Academy staging — backend source verified

| Item | Verified value |
|---|---|
| Service | tradethesis-academy-staging |
| URL | https://tradethesis-academy-staging.onrender.com |
| Service ID | srv-db9ioke1egvs73feb8ag |
| Repository | ZaphodBeeblebrox12/prototypeweb |
| Configured branch | my-new-branch |
| Auto-deploy | Disabled |
| Auto-deploy trigger | Off |
| Region | Oregon |
| Health-check path | /health/ |
| Latest deploy ID | dep-dbs8tku7bikc73euh990 |
| Latest deployed commit | 8832ecf9cc979747dc2715a39ecfeb7a292e55ee |
| Latest deployment status | live |
| Latest deployment trigger | api |
| Deployment finished | 2026-11-14 16:41:58 UTC |

The deployed commit exactly matches the current `my-new-branch` HEAD. This is a verified source/deployment match for this Render service. The deployment was API-triggered because auto-deploy is disabled; no Render setting was changed.

The deployment trigger is recorded as api, not an automatic commit deployment. Auto-deploy is currently disabled. No Render setting was changed.

### 4.2 Public staging — separate static service

| Item | Verified value |
|---|---|
| Service | tradethesis-public-staging |
| URL | https://tradethesis-public-staging.onrender.com |
| Service ID | srv-db9j72m1egvs73ffpfkg |
| Configured branch | my-new-branch |
| Auto-deploy | Disabled |
| Latest deployed commit | c5bdc0fb58be35122a41da3bc646a06c48dc162d |
| Latest deployment subject | Refresh Courses modal stylesheet version |
| Latest deployment finished | 2026-11-07 09:01:26 UTC |
| Latest deployment status | live |

The public static service's latest live deploy is older than the current source branch HEAD. Treat this as a separate deployment-parity item; it is not evidence that the Academy Django service is stale.

### 4.3 Other Render service

A separate tradethesis-course-template-preview service points to course-template-parity-fixes with auto-deploy enabled. It is not the Academy staging service and should not be treated as the Admin Desk deployment target.

## 5. Authenticated staging and role verification

**Status: NOT VERIFIED — Phase 0 exit blocker.**

The audit environment did not have an authenticated browser session for Academy staging or the user's representative staff accounts. The browser retrieval attempt could not open the staging paths; that is a limitation of this audit channel, not proof that the Render service is down or that the routes return an error.

No claim is made that the following have been tested live:
- staff sign-in and superuser sign-in;
- representative Support, Academy, Revenue, Growth and Platform role access;
- Django Group/model permission assignment on actual staff accounts;
- route-level 401/403/404 behaviour by role;
- object-level visibility across plan approver scopes, customer records, disputes or finance;
- no-access/empty/error/stale states in the deployed UI;
- current deployed page navigation and action submission.

### Required authenticated test matrix

Use existing authorised test accounts; do not share passwords in project documents or chat.

| Persona/account | Required checks |
|---|---|
| Non-staff learner | Denied staff routes, Django Admin and staff APIs; can only see own member notifications/account data |
| Ordinary approved staff | Staff shell/overview entry; only assigned model permissions; cannot enter Academy authoring/review unless role ADMIN or superuser under current helper |
| Support reviewer | Ticket list/detail only within reviewer scope; public reply/internal note; assignment, status, approve/reject/reopen; customer 360 section visibility |
| Academy editor | Builder, assets, video and Google Drive paths; confirm role boundary currently enforced by is_course_content_admin |
| Academy approver | Course review queue, private assets, publish and return-with-feedback; cannot access unrelated domains without permissions |
| Revenue staff | Finance read-only views, invoices, subscriptions, business settings and available Django Admin finance surfaces according to actual model permissions |
| Growth staff | Gift send route; verify referral overview is not exposed as staff data without an explicit staff gate; inspect campaign/email surfaces only where authorised |
| Platform operator | Operations timeline, job/provisioning detail and integration/security details individually gated by model permissions |
| Superuser | Full intended access, with explicit verification of sensitive actions and audit evidence |

For every persona, verify both positive and negative cases. A menu item being hidden is not sufficient; call the direct route/API and inspect the server response. Include object-level denial tests, not just route-level access.

## 6. Source-verified route, action and permission inventory

The routes below are registered in backend/config/urls.py on the deployed source commit. Their live authenticated availability still requires the tests in Section 5.

### 6.1 Command Centre and shared operations

| Current surface | Source-backed access | Actions / side effects | Canonical owner and migration state |
|---|---|---|---|
| /staff/admin-desk/ | Login required; active is_staff gate. Overview sections are separately populated by model permissions and Academy content-admin helper. | Overview and links; no verified universal task queue. | Command Centre aggregation only. Existing staff landing page, not the approved six-domain shell. |
| /staff/admin-desk/operations/ | Active staff gate. Ticket summaries use reviewer scope. Jobs, provisioning, periodic jobs, domain events, AuditLog and SecurityEvent sections each require their relevant view permission. | Read-only cross-domain observation and issue grouping. | Command Centre observation view; detailed operations belong to Platform. |
| /staff/admin-desk/operations/jobs/<id>/ | jobs.view_job plus active staff. | Read-only Job detail. No retry/replay/delete action in the reviewed route. | Platform; existing read-only destination. |
| /staff/admin-desk/operations/provisioning/<id>/ | jobs.view_provisioningoperation plus active staff. | Read-only ProvisioningOperation detail. | Platform; existing read-only destination. |
| /notifications/ and /api/notifications/ | Login or IsAuthenticated. Query and read/write operations are scoped to request.user. | User marks own notifications read or read-all; unread count. | Personal notification system. It is not a staff alert centre or assigned work queue. |
| Support queue assignment=mine | Same reviewer-scoped SupportTicket queue; filter selects assigned_to=request.user. | View tickets assigned to self. | Limited existing personal-work filter, not a universal My Work engine. |

### 6.2 Academy

| Current surface | Source-backed access | Actions / side effects | Canonical owner and migration state |
|---|---|---|---|
| /staff/admin-desk/courses/review/ and review detail/assets | Active staff plus is_course_content_admin: superuser or user.role=ADMIN. | Read review submission and protected assets. | Academy; existing review UI. |
| Review approve | Same Academy content-admin gate; POST only. | Calls canonical publish_course_import service; successful approval publishes the reviewed submission. | Academy; retain canonical publisher and its validations. |
| Review return | Same gate; POST only. | Requires non-empty reviewer feedback; atomic locked update to rejected/returned state and AuditLog entry. | Academy; existing action. |
| Import cleanup/delete | Same gate; cleanup is GET; delete is POST and requires typed DELETE. | Only unlinked unpublished imports in permitted statuses may be removed; row lock, staged file deletion after commit, AuditLog. | Academy; destructive capability must remain narrowly guarded and be parity-tested. |
| /staff/course-builder/ and /staff/course-builder/api/ | Login required; active user and is_course_content_admin. | Draft create/save/submit/delete, content and asset handling. Builder API DELETE is restricted to DRAFT/REJECTED builder records and cannot delete live Course rows. | Academy; existing supported legacy Builder. |
| Builder video/assets and Google Drive routes | Login-required staff/Academy helper gates in reviewed Builder/API path. Exact per-operation checks must be covered by authenticated tests. | Protected asset/video upload and Drive OAuth/storage. | Academy; existing operations. |
| /staff/course-builder/tiptap/ and Tiptap API | Development/feature-gated path per current route map; not the default supported production authoring path. | Preview and feature-specific draft API. | Academy; do not promote to default without separate approval. |
| /staff/admin-desk/seo/ | Login required; active user and is_course_content_admin. | Read-only course indexability diagnostics and Builder links. | Academy; existing Admin Desk diagnostic. |
| Catalogue / offers / plan-price setup | Public catalogue API exists; course and offer/plan records are administered through existing Django Admin/model surfaces. No unified staff catalogue or offers editor route verified. | Model administration; no new Admin Desk editor. | Academy owns Course/CourseOffer; Revenue owns Plan/pricing. |

Important Academy boundaries:
- Course publication, indexability, saleability and learner entitlement are separate states.
- Published-course edits must remain draft revisions until approved.
- Course Builder current default is the legacy supported path; Tiptap is not the production/default path.
- Current source-only commits add draft reconciliation/migration for Trading Path Quick Checks and summaries. Regression-test that only intended drafts change, existing Q&A remains, repeated loads are idempotent and live published Course records remain unchanged.

### 6.3 Customers and Support

| Current surface | Source-backed access | Actions / side effects | Canonical owner and migration state |
|---|---|---|---|
| /staff/admin-desk/accounts/ and detail | Active staff plus accounts.view_user. Learner list/detail excludes staff and superuser accounts. | Read learner profile and permitted cross-domain sections. | Customers; existing account list/detail. |
| Account actions | accounts.change_user. | Password reset dispatch; ban/unban; activate/deactivate. Ban and deactivate require reason length >=5. State changes enqueue reconciliation and write AuditLog with before/after/reason metadata. | Customers; existing audited action. |
| /staff/admin-desk/support/tickets/ and detail | Active staff plus reviewable_ticket_queryset. Superuser sees all. Other staff visibility follows plan/affiliate-plan ticket_approvers; an empty approver list keeps the established any-staff scope. | Queue filters, reviewer-limited ticket detail, assignment context and conversation. | Customers; existing support queue. |
| Support ticket actions | Same reviewer scope and ticket.can_be_reviewed_by checks; POST. | Public reply, internal note, start review, awaiting member, reopen, approve, reject, priority/assignee update. Most state changes append messages or notifications and write AuditLog. | Customers; existing service path. |
| Access-request approval | Same reviewer scope; approved hidden Plan required. | grant_subscription_by_admin plus reconciliation enqueue and ticket update in the same atomic service transaction. Enqueue failure should roll back grant/ticket state. | Customers executes the support decision; Revenue owns Subscription; Platform owns reconciliation job. |
| Customer 360 | Active staff; access via a visible reviewable ticket or accounts.view_user. Internal staff requester profiles are restricted. Subscription, payment, invoice, Academy and security sections each have independent permission checks. | Read-only relationship view; no impersonation. | Customers; existing read-only view. |

Support and account workflows need negative tests for a staff member outside the ticket's plan approver set, an internal staff requester, a learner account, and a staff/superuser account. Preserve public-reply versus private-note visibility and existing reason requirements.

### 6.4 Revenue

| Current surface | Source-backed access | Actions / side effects | Canonical owner and migration state |
|---|---|---|---|
| /staff/admin-desk/finance/ | Active staff plus payments.view_paymentintent and/or payments.view_invoice; payments and invoices are independently gated. | Read-only registers and CSV link for authorised payment viewers. No refund initiation action in this page. | Revenue; existing read-only Finance view. |
| PaymentIntent / Refund Django Admin | Model-level permissions; PaymentIntent fields are read-only; Refund records are read-only and cannot be added/deleted through standard admin. | Financial state is provider-backed. Manual refund action records a refund after provider-side processing. | Revenue / Advanced Administration until a safe staff workflow exists. |
| /staff/admin-desk/invoices/<id>/ | payments.view_invoice. | Read-only immutable invoice snapshot. | Revenue; existing detail. |
| /staff/admin-desk/subscriptions/ | subscriptions.view_subscription. Grant requires subscriptions.add_subscription; change actions require subscriptions.change_subscription. | Grant hidden-plan access (1–365 days and reason); extend access (1–365 days and reason); cancel. Actions use existing services and audit records. | Revenue; existing workspace. |
| Subscription cancellation | subscriptions.change_subscription. | Current cancel_subscription service sets CANCELED and is_active=False immediately, writes history/event and queues reconciliation. | End-of-period cancellation is not supported by the reviewed service. |
| /staff/admin-desk/business/ | payments.add_billingsettings or payments.change_billingsettings, depending on whether settings exist. | Controlled BillingSettings form save and AuditLog. Tax behaviour remains fixed-rate and first enable requires accountant confirmation. | Revenue; existing settings form. |
| /admin-disputes/ | Dashboard/detail use staff_member_required; action POSTs require disputes.change_dispute. No narrower object-level dispute scope was found in the reviewed view. | Notes, evidence package generation, submission reference recording and resolution. Submission view instructs staff to submit the same evidence through PSP dashboard/API; it does not itself upload the package to PSP. | Revenue; separate current staff route proposed to be surfaced in unified workspace. |

**Refund capability verification**

- The reviewed providers.py exposes Stripe checkout creation and hosted checkout, not an operator-facing refund request method.
- The webhook processor records provider-generated Stripe/Razorpay refund events, deduplicates by provider refund ID and applies the existing access policy.
- The Django Admin “Record FULL manual refund” action is explicitly described as “use after refunding in the provider dashboard”. It creates a manual Refund ledger row, audits it, applies refund policy and notifies. It does not initiate the PSP refund.
- No staff-initiated provider refund service was found in the reviewed provider/service path.

Therefore, do not show or label a new Admin Desk action as “Issue refund” until an approved provider-backed refund capability, permissions, idempotency, provider-confirmation handling and recovery path exist and are tested.

**Cancellation capability verification**

The reviewed cancel_subscription implementation is explicitly immediate: it sets CANCELED, is_active=False and canceled_at=now, records history/event and enqueues reconciliation. No end-of-period option or provider subscription cancellation path was verified. The approved end-of-period product direction is not yet supported by this service.

### 6.5 Growth

| Current surface | Source-backed access | Actions / side effects | Canonical owner and migration state |
|---|---|---|---|
| /api/analytics/overview/ | Current route map/source audit identifies an admin-only read API; live role behaviour still needs API tests. | Read analytics payload with known metric/aggregation caveats. | Growth; no unified Analytics page. |
| Campaigns/Audiences/Automation/Coupons/Email templates | Mainly Django Admin/model surfaces; no unified staff Admin Desk pages verified. | Campaign audience frozen at scheduling; TemplateVersion immutable. Current G2 stub send path can mark Delivery SENT without external provider delivery. | Growth; migration proposed, source contracts need fixing. |
| /admin/growth/send-gift/ | staff_member_required; active staff gate. | Creates GiftInvite/GiftSubscription, then attempts email. Gift may exist even if email delivery fails. | Growth; existing staff action, not yet a unified Gifts workspace. |
| /growth/admin/referral-rewards/ | LoginRequiredMixin only in reviewed AdminReferralRewardsView; no staff-only gate. | Aggregates referral reward totals and recent rewards. | Unsafe as a staff Admin Desk destination until access is corrected and verified. |
| Referral reward service | Member referral/reward routes and service/model logic. | Currency-bearing reward buckets are aggregated by UserRewardBalance.total_cents without separating currencies; reward unlock/persistence caveats remain in the readiness record. | Growth; known data-integrity blocker. |
| Affiliate commissions | Django Admin/model surface. | Internal Paid state is not proof of external payout. | Growth; no verified payout execution. |
| Email delivery | G1 Delivery and transactional EmailLog are separate records; Resend webhook updates Delivery. | Marketing opt-out/suppression must remain separate from transactional communication. | Growth; preserve ledger separation. |

### 6.6 Platform, integrations and security

| Current surface | Source-backed access | Actions / side effects | Canonical owner and migration state |
|---|---|---|---|
| Operations Timeline | Active staff; each technical section independently requires its view permission. | Read-only observation; not a second queue. | Platform; foundation already exists. |
| Job detail and JobAdmin | jobs.view_job for Admin Desk detail. JobAdmin is read-only; add/delete disabled. | No ordinary staff retry/replay/delete action was verified. | Platform; safe retry capability is not present in the reviewed UI/service route. |
| PeriodicJob | Django Admin model surface; configuration fields remain editable; run result fields are read-only. | Separate lightweight scheduler from durable Job/worker lifecycle. | Platform; do not merge concepts or invent retry. |
| Provisioning | jobs.view_provisioningoperation for detail; model state is distinct from entitlement assignment and observed membership snapshot. | Read-only detail. Unknown external membership state is not success or failure and must not trigger blind resend. | Platform; preserve Unknown and existing resend safeguards. |
| Integration callbacks | Stripe/Razorpay, Resend and Telegram callback routes exist; callbacks are not operator consoles. | Stripe/Razorpay use durable WebhookEvent processing; Resend updates G1 Delivery; Telegram webhook durability was not verified in the prior source audit. | Platform observes provider evidence; domain owner remains responsible for business record. |
| /health/ | Public health endpoint. | Performs database SELECT 1 only. | Not a full service/provider/integration health signal. |
| Audit/Security/Policies | AuditLog, SecurityEvent, PolicyVersion and PolicyAcceptance sources exist; detailed access is model-permission dependent in the timeline. | SecurityEvent is append-only at model level; AuditLog append-only enforcement and published PolicyVersion immutability need further hardening/verification. | Platform; source/governance blockers. |
| Staff approval APIs | /api/admin/staff-approvals/ and /action/ use IsRoleAdmin. | Approve/reject changes role, is_staff and is_staff_approved; writes AuditLog. | Platform / central ownership; no unified Staff & Permissions UI. |

## 7. Access-model findings and policy reconciliation

### 7.1 Django Admin target versus staged workflow cutover

The current Django app configuration installs DashboardAdminConfig, which customises the admin index/dashboard and mounts a dashboard through admin.site.admin_view. No override of the default AdminSite has_permission gate was found in the reviewed configuration. The current practical Django Admin access boundary therefore remains the standard active + is_staff gate, not superuser-only.

The owner-approved product decisions must still be reconciled:
- Decision 9: target Django Admin access is superusers only.
- Decision 52: remove ordinary staff access to each legacy workflow after its replacement is migrated and verified.

Do not choose one interpretation silently. A workable technical policy needs a workflow-by-workflow access map plus a final cutover gate. Until that owner-approved policy is expressed precisely, do not change Django Admin permissions.

### 7.2 Account API role bypass

The custom IsRoleAdmin class claims to require role ADMIN, but its actual predicate also accepts any active authenticated is_staff user and any superuser. The same class gates ban, unban and staff-approval API actions. The class is therefore broader than its name/comment implies.

This is a current source-level access boundary that must be explicitly tested and resolved in the technical readiness plan before building Staff & Permissions.

### 7.3 User/department model mapping

The User model has one role choice (ADMIN, STAFF, USER), plus is_staff, is_staff_approved, is_active and Django permission/group support through PermissionsMixin. The reviewed User model does not contain a department-membership field. No verified model-to-department assignment contract was established in this audit. The approved multi-department model therefore remains a target requiring a mapping design against actual users, groups and permissions.

### 7.4 Login-only referral overview

AdminReferralRewardsView uses LoginRequiredMixin without a staff-only or model-permission check. Do not embed or link this route from the staff Admin Desk until its authorization boundary is repaired and verified.

### 7.5 Other mixed staff gates

Some custom gift/dispute routes use staff_member_required, which is broader than a domain-specific permission. Other workflows use model permissions, the Academy content-admin helper or explicit reviewer scope. The new shell must not assume a single shared “staff” badge grants all domain access.

## 8. Readiness blockers carried forward

| Blocker | Evidence / consequence | Required closure |
|---|---|---|
| Authenticated staging role checks | Not performed in this audit | Run Section 5 test matrix against current deployed SHA. |
| Django Admin cutover policy | Decision 9 and 52 require precise reconciliation; current gate is active staff | Approved workflow-to-legacy access map and staged transition tests. |
| Account admin API scope | IsRoleAdmin allows any is_staff | Define intended role/capability gate and positive/negative API tests. |
| Department permissions | User model has single role; actual department/group mapping not verified | Map actual users, Groups, object scopes, managers and central owner. |
| Refund initiation | No provider refund initiation found in reviewed path | Design/approve provider service, idempotency and confirmation semantics; otherwise keep record-only. |
| End-of-period cancellation | Current service is immediate-only | Implement/approve supported state/effective-date contract before exposing that option. |
| Academy course purchase events/coupons | Prior source audit found course activation diverges from membership purchase event/redemption path | Dedicated course coupon redemption and common purchase.completed event with purchase type and exactly-once semantics. |
| Growth campaign delivery truth | Stub provider can mark Delivery SENT | Explicitly label simulated/not sent to provider and test real provider evidence separately. |
| Referral reward integrity | Currency aggregation and reward-unlock/persistence caveats | Currency-safe buckets/ledger and eligibility/persistence regression tests. |
| Staff referral route | Login-only overview | Staff-only authorization and negative tests before reuse. |
| Job recovery | JobAdmin read-only; no ordinary staff retry route | Only build retries for proven idempotent job kinds and a supported service path. |
| Integration health | /health/ checks DB only; config presence is not provider health | Provider-specific last-success/failure evidence and synthetic/end-to-end tests. |
| Provisioning unknown state | Job and external membership state are separate | Keep unknown distinct; no automatic resend based only on a successful Job. |
| Audit and policy immutability | AuditLog and PolicyVersion enforcement gaps | Enforcement review, tamper/immutability tests, retention and privacy tests. |
| Accessibility | Keyboard, contrast and screen-reader validation incomplete | Complete per-workspace accessibility and mobile checks before sign-off. |
| Public static deployment parity | Public staging live deploy is from 7 Nov, behind source HEAD | Confirm whether a deliberate static-site release is needed; do not alter Render until separately authorised. |
| Rollback and parity | No signed-off current-state inventory/test evidence yet | Workflow-specific parity and rollback plan before any migration. |

## 9. Required parity tests and rollback criteria

These are test requirements, not claims that tests have been run.

### Shared access and navigation
- Test each route/API directly as non-staff, ordinary staff, role ADMIN, superuser and inactive account.
- Verify navigation visibility and backend denial independently.
- Verify each sensitive section is independently permission-gated.
- Verify reviewer/object scope across plan/affiliate ticket approvers, customers, disputes, payment records, security events and Academy content.
- Verify search does not disclose records outside the caller's scope.
- Roll back the affected migration slice if any unauthorised role can read or mutate a record, if data appears outside its owner scope, or if audit evidence is missing.

### Academy
- Course submit → review → approve/publish, and return with mandatory feedback.
- Published-course edit creates a draft revision and does not mutate the live version before approval.
- Private asset and video access checks for allowed/denied staff.
- Builder auto-migration is idempotent, intended-draft-only, Q&A-preserving and draft-only.
- Course coupon redemption creates exactly one correct redemption record; duplicate webhook/retry cannot double redeem.
- Course and membership emit the standard purchase event exactly once with an explicit purchase type.
- Roll back the Academy migration if any published content is changed unexpectedly, an entitlement is granted without canonical evidence, Q&A is lost/duplicated, or access becomes inconsistent.

### Customers and Support
- Ticket read/write tests for plan approver, non-approver, unassigned staff, superuser and inactive staff.
- Public reply is visible to customer; internal note is not.
- Assignment/priority changes enforce reviewer scope.
- Access approval grants the intended hidden plan and enqueues reconciliation atomically.
- Enqueue failure leaves both ticket and entitlement unchanged.
- Reject requires reason; reopen enforces existing duplicate-open-ticket rule.
- Account ban/deactivate requires reason; state, audit and reconciliation evidence agree.
- Roll back if access changes without a matching successful canonical action, a private note leaks, or a state transition occurs without audit/evidence.

### Revenue
- Payment status follows verified provider evidence; staff cannot directly mark Paid/Failed.
- Provider refund request (once implemented) has role permission, idempotency, provider event confirmation, partial/full handling and safe timeout/retry semantics.
- Partial refund leaves access unchanged; full refund follows existing access policy only after confirmed provider refund.
- Manual record-only path must be clearly distinguished from initiating a PSP refund.
- Subscription cancellation tests current immediate semantics; any future end-of-period option must prove effective dates and access period.
- Invoice snapshots and completed financial ledger rows remain immutable.
- Disputes test non-final states vs Won/Lost/Accepted final outcome and PSP submission evidence.
- Roll back if any access revocation precedes provider confirmation, duplicate refunds are recorded, ledger evidence is mutated, or cancellation timing differs from the approved contract.

### Growth
- Campaign approval and frozen audience/version semantics.
- Stub delivery never appears as externally sent or delivered.
- Resend evidence updates Delivery without falsely merging into transactional EmailLog.
- Opt-out and global suppression immediately block marketing; transactional communications remain separate.
- Coupon, referral and reward eligibility tests include delayed unlock, refund, missing subscription, multi-currency balance and optional referee bonus persistence.
- Affiliate Paid cannot be shown as payout-confirmed without external payout evidence.
- Gift creation/email-failure path retains a clear “created, email failed” state.
- Roll back if any suppressed marketing message sends, simulated delivery is represented as real, reward currency is mixed, duplicate reward is credited or payout status is fabricated.

### Platform
- Durable Job, PeriodicJob scheduler and worker lifecycle tested separately.
- Retry available only for allowlisted idempotent jobs through an approved service.
- Unknown provisioning state never becomes success/failure and never causes blind resend.
- A successful Job cannot be used as proof that Telegram/Discord membership changed.
- Provider health reports last successful exchange and relevant failures, not just config presence or database connectivity.
- Webhook idempotency, invalid signature, duplicate event and replay tests.
- AuditLog append-only, PolicyVersion immutability and SecurityEvent privacy/retention tests.
- Roll back if an unsafe retry duplicates an external action, unknown state triggers revoke/resend, audit/security evidence is editable, or health labels claim unverified provider success.

### Common rollback triggers
- Any permission leak or unauthorised write.
- Canonical data mutation without a corresponding approved service/action.
- Missing, duplicate or incorrect audit/event record.
- Provider-confirmed state being inferred from local initiation or a background Job alone.
- External duplicate side effect after retry.
- Data loss, destructive cleanup outside the allowed scope, or mutation of immutable financial/published records.
- Error path that does not preserve the previous state or cannot be safely retried.
- Failure of critical mobile, keyboard or screen-reader workflow gates.

For each workflow, rollback should restore the previous route/service as the canonical operational path; keep data written through the canonical service; disable the new entry point rather than deleting business records; reconcile any in-flight jobs/provider effects explicitly before retry.

## 10. Recommended next steps

1. Complete authenticated staging checks from Section 5 using existing authorised test accounts. Do not send credentials in chat or store them in this document.
2. Record the actual staff-role, Django Group/model permission and object-scope matrix. Include negative tests for the broad IsRoleAdmin and login-only referral route.
3. Resolve the Django Admin decision 9/52 cutover policy in a written workflow map before any permission change.
4. Confirm refund provider capability with the payment owner/provider sandbox. Do not describe the current manual ledger action as refund initiation.
5. Confirm the commercial policy and technical contract for immediate vs end-of-period cancellation.
6. Run targeted regression tests for the 15 source-only Academy changes on the current deployed SHA.
7. Update the route/workspace map with verified current gates and annotate every proposed route/action as existing, proposed, read-only, action-backed or blocked.
8. Produce a per-workflow parity checklist and rollback runbook with departmental owner and central system owner.
9. Revisit the public static staging deployment only after confirming whether its older deployed SHA is intentionally pinned.

**Phase 0 exit gate is not yet met.** The source and Render backend baseline are verified, but authenticated staging/role verification and the complete live route/action matrix remain open. Do not seek implementation approval yet.

## 11. Change boundary confirmation

This audit created/updated planning documentation only. It did not:
- modify application code;
- create/apply migrations;
- change API contracts, routes, permissions or user roles;
- modify tests or application settings;
- change Render configuration;
- deploy, merge or rebase any branch.

Implementation remains NOT AUTHORISED.


## 12. Test-suite evidence and unauthenticated staging probe — continuation pass

### 12.1 CI status on the deployed source SHA

GitHub Actions was queried for commit `6cdb7b9e78306850902da9b95467e494066baa13`, which is the source SHA currently deployed to Academy staging.

<https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/43611322315> — **Verify Django Academy backend**, run 2048:
- Python 3.11 job: success.
- Python 3.12 job: success.
- Both jobs ran Django configuration and Python syntax checks, isolated database migration, sitewide navbar role tests, source-course catalogue validation, draft-import smoke test, Ruff, formatting check, mypy, and the full backend regression suite.
- Both full-suite results: **1,314 passed, 1 skipped, 512 warnings, 178 subtests passed**.

<https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/43611322349> — **Academy backend CI**, run 1888:
- Python 3.11 backend job: success.
- Python 3.12 backend job: success.
- Tiptap bundle and DOM compatibility job: success.
- Backend jobs ran Render build-script syntax validation, migration-state check, Ruff, Black check, mypy, static collection, focused micro-course image-slot regressions and the full backend suite.
- Both full-suite results: **1,314 passed, 1 skipped, 178 subtests passed**. The log summary for this workflow did not report a warning count.
- Tiptap job completed its bundle build and the sidecar/privacy, Markdown, reference, image-extension, sidecar-block, code-marker and full Bollinger Bands course round-trip checks. Its focused Markdown suite reported **19 passed, 4 subtests passed**.

These are CI checks against an isolated test database and test accounts. They do not establish authenticated access or live object visibility in Render staging. A successful Tiptap compatibility job does not make Tiptap the supported/default production Course Builder.

### 12.2 What existing tests cover for Admin Desk access

The reviewed source tests provide meaningful local regression evidence:

| Area | Existing test evidence | Remaining limitation |
|---|---|---|
| Account admin API | `apps/accounts/tests/test_admin_auth.py` tests role ADMIN, superuser and plain-user access. | It does not include an explicit ordinary `is_staff=True`, non-superuser, role=STAFF positive/negative case. The production IsRoleAdmin predicate nevertheless explicitly accepts any authenticated `is_staff` user. |
| Academy review | `apps/academy/test_admin_desk_course_reviews.py` tests review, canonical publish, feedback-required return, constrained cleanup and a staff learner-role account denied with 403. | It does not cover the complete live staff roster or every Builder/Drive/video permission combination. |
| Support | `apps/support/test_admin_desk.py` tests reviewer-scoped ticket visibility, restricted-plan 404, ticket actions, assignment, public replies and internal notes. | Tests use fixture accounts, not the actual deployed staff role/group matrix. |
| Customer 360 | `apps/support/test_customer_360.py` tests independent section permissions, profile access denial without a visible ticket/global account permission, plan-scope denial, and hiding internal notes/provider identifiers/security details. | The real staging account/object combinations remain unverified. |
| Operations Timeline | `apps/support/test_operations_timeline.py` tests non-staff denial, independent technical-feed permissions, plan reviewer scope, PII/payload redaction and job/provisioning detail denial. | Live role assignment and staff-specific route visibility remain unverified. |
| Subscription lifecycle | `apps/subscriptions/tests/test_admin_actions.py` and `test_lifecycle.py` test idempotent cancellation/extension and reconciliation behaviour; a permission test checks a model-admin change gate. | These tests do not establish a new unified Admin Desk role-to-department matrix or end-of-period cancellation. |
| Durable jobs/provisioning | `apps/jobs/tests/test_jobs_system.py` covers coalescing, stale-job recovery, invite-link reuse, membership check without resend and idempotent revoke. | It does not expose a new staff retry UI; no such route was verified. |
| Growth referral overview | The inspected `AdminReferralRewardsView` is still a `LoginRequiredMixin` view. | No staff-only permission gate was found in that view; no corresponding staff authorization regression test was identified in the reviewed test inventory. |

### 12.3 Ordinary-staff API boundary is now confirmed as a test-coverage issue

The current `IsRoleAdmin` implementation accepts any authenticated user where at least one of these is true:
- `role == ADMIN`
- `is_superuser`
- `is_staff`

The existing test docstring itself describes the intended test condition as role ADMIN “AND superuser/staff”. The tests cover superuser and role ADMIN as allowed, and plain user as denied, but not an ordinary approved staff account. Therefore:
- The implementation's broad staff acceptance is source-verified.
- The available test suite does not explicitly pin the intended ordinary-staff policy.
- Do not silently reinterpret the existing behaviour. Resolve the approved capability boundary and add explicit STAFF-only tests before the Staff & Permissions workflow is migrated.

### 12.4 Direct unauthenticated staging probes

An unauthenticated retrieval attempt was made against the following public Academy staging paths:
- `/health/`
- `/staff/admin-desk/`
- `/admin/login/`
- `/api/admin/staff-approvals/`
- `/growth/admin/referral-rewards/`
- `/admin-disputes/`

The available retrieval channel reported each URL as inaccessible and did not return an HTTP response/status. This is **inconclusive**: it does not establish a route failure, authentication redirect, 403, 404 or service outage. No credentials were supplied and no authenticated staging action was attempted.

### 12.5 Updated Phase 0 position

The source/deployment baseline and CI state are now verified, and the source route/action inventory is supplemented by a review of the existing regression tests. This materially reduces uncertainty around code-level behaviour.

**Phase 0 still does not pass its exit gate.** Live authenticated staging checks with representative staff accounts and a superuser, plus the actual staff/group/object-scope matrix, remain outstanding. The web retrieval failure is not a substitute for those checks.

No application code or tests were changed in this continuation. Only this planning audit document was extended.


## 13. Latest source, deployment and CI checkpoint — 14 November 2026

### 13.1 Branch and deployment refresh

- Current application source branch: `my-new-branch`.
- Current source HEAD: `8832ecf9cc979747dc2715a39ecfeb7a292e55ee` — `Migrate Trading Path key takeaways into notebook prompts` (2026-11-14 16:39:00 UTC).
- Current Academy staging deployment: `dep-dbs8tku7bikc73euh990`, status `live`, finished at `2026-11-14 16:41:58 UTC`; deployed SHA matches the source HEAD above.
- Academy staging remains configured to `my-new-branch` with auto-deploy disabled and API-triggered deployments.
- Planning branch at the start of this refresh: `0f6e44a34c56cdccc17a3f717ee613b8b47081f1`. Before the two audit/handoff document updates, it was 86 commits ahead and 18 behind the source branch, with the same merge base recorded in Section 3. The document updates themselves add planning-only commits.
- Public static staging remains on `c5bdc0fb58be35122a41da3bc646a06c48dc162d` (7 November 2026 09:01:26 UTC), older than the current application source. This is a separate frontend deployment-parity item, not a stale Academy backend deployment.

### 13.2 Latest source-only Academy changes

The 18 source-only commits since the planning branch merge base still touch only:
- `backend/apps/academy/course_builder_api.py`
- `backend/apps/academy/course_builder_preview.html`
- `backend/apps/academy/course_builder_trading_path_import.json`

The newest three commits add the `Pause`, `Interpret` and `Apply` notebook migration described in Section 3.1. No Admin Desk route, view, permission or test file changed in this source-only delta. Add explicit checks for: repeated Builder load idempotence; exact Trading Path lesson matching; preserving target notebook title/metadata and saved Q&A; removing only the Key takeaways section while retaining surrounding lesson content; and no mutation of published Course records.

A static scan of the current import JSON found five modules and 48 lessons. Twenty-seven lessons have exactly three non-empty notebook prompts labelled `Pause`, `Interpret` and `Apply` in that order; the other 21 have no populated prompt array. None of the 48 source lesson bodies currently contains a Markdown `Key takeaways` heading. Thus, the source JSON demonstrates the 27 available notebook payloads but does not exercise removal of a legacy Key takeaways section from a saved target draft.

**Conditional cleanup edge case:** `stripKeyTakeawaysContent()` stops at the next Markdown heading of any level, not the next heading at the same or a higher level. If a saved target's Key takeaways section contains nested subheadings, the helper may remove the section title and preceding text but leave the nested subsection content behind. Whether any actual target draft has that structure is not verified. Add fixtures for nested headings and compare the result against saved draft content before signing off this migration.

### 13.3 CI on the current deployed source SHA

GitHub Actions **Academy backend CI**, run [1891](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/43616758224), for commit `8832ecf9cc979747dc2715a39ecfeb7a292e55ee`, completed with conclusion **success**:
- Python 3.11: success; full suite **1,314 passed, 1 skipped, 178 subtests passed**.
- Python 3.12: success; full suite **1,314 passed, 1 skipped, 178 subtests passed**.
- Tiptap bundle and DOM compatibility tests: success.

These results validate the committed code against isolated CI databases. They do not test authenticated staging role assignments, actual staff-group mappings or live object-level access. The notebook migration itself has no dedicated test file in the source-only delta; add explicit migration-focused tests before treating its exact content transformation as independently regression-covered.

### 13.4 Phase 0 status after refresh

The current Academy source/deployment SHA and CI are now aligned and green. The Admin Desk source-level authorization findings from the earlier inventory remain in force because no Admin Desk route/view/permission files changed in the 18-commit source-only delta.

**Phase 0 remains open.** The outstanding exit blocker is live authenticated staging review with representative staff roles and a superuser, including direct-route/API denial, object-level scope and the actual User/Group/model-permission mapping. The Django Admin cutover policy, broad `IsRoleAdmin` boundary, login-only Growth referral view, refund-initiation capability and cancellation contract remain unresolved. **Implementation remains NOT AUTHORISED.**


## 14. First live authenticated staging result — non-staff learner

**Test timestamp:** 2026-11-14 16:59:25 UTC  
**Target:** `https://tradethesis-academy-staging.onrender.com`  
**Persona label supplied by operator:** Non-staff learner  
**Method:** Browser console batch, same-origin `fetch`, GET only, redirects followed, no state-changing request.

### Observed results in the supplied report

| Route | HTTP | Observed interpretation |
|---|---:|---|
| `/health/` | 200 | Public health endpoint reachable; source contract says primary database `SELECT 1` only. |
| `/staff/admin-desk/` | 403 | Forbidden |
| `/staff/admin-desk/operations/` | 403 | Forbidden |
| `/staff/admin-desk/accounts/` | 403 | Forbidden |
| `/staff/admin-desk/support/tickets/` | 403 | Forbidden |
| `/staff/admin-desk/courses/review/` | 403 | Forbidden |
| `/staff/admin-desk/seo/` | 403 | Forbidden |
| `/staff/course-builder/` | 403 | Forbidden |
| `/staff/admin-desk/finance/` | 403 | Forbidden |
| `/staff/admin-desk/subscriptions/` | 403 | Forbidden |
| `/staff/admin-desk/business/` | 403 | Forbidden |
| `/api/admin/staff-approvals/` | 403 | Forbidden |
| `/api/analytics/overview/` | 403 | Forbidden |

The JSON report marked the 403 pages with title `403 Forbidden`, `denialText=true`, and no redirect. The browser Network console independently displayed HTTP/3 403 for the listed staff routes.

### Assessment and evidence limits

- **Positive evidence:** all 12 listed staff/admin route/API checks denied access from the session labelled Non-staff learner; no login redirect was followed and no successful staff data response was reported for those paths.
- **Health check:** `/health/` returns 200. This is expected and does not expose staff workspace access; the endpoint is a DB readiness probe, not a staff page.
- **Identity confidence:** the persona is the operator-supplied label. The browser report did not include a server-verified user ID/role/`is_staff` value, so the test is recorded as a session labelled Non-staff learner rather than independently verified account metadata.
- **Partial transcript:** the pasted JSON was truncated after the start of the checks array. Results for `/growth/admin/referral-rewards/`, `/api/notifications/`, `/admin/`, `/admin/growth/send-gift/`, `/admin-disputes/` and any discovered detail links were not available for review and are not recorded as pass or fail.
- **Method scope:** this was a read-only GET test. It did not exercise POST actions, record mutation, staff approval, or object-scope restrictions across two different personas.

### Updated status

This is the first observed live authenticated staging evidence and supports the non-staff denial boundary for the 12 listed routes. It does not close Phase 0. Run the consolidated batch against each authorised test-account session and capture the full compact JSON summary. Then perform cross-persona object-scope checks using known test fixture IDs for tickets, learners, invoices, Academy imports and disputes.

**Phase 0 remains open. Implementation remains NOT AUTHORISED.**

## 15. Confirmed learner-visible Growth referral rewards exposure

**Priority:** High — authenticated non-staff data exposure in Academy staging.  
**Observed:** 2026-11-14 16:59:25 UTC, on a browser session labelled `Non-staff learner`.  
**Request:** `GET /growth/admin/referral-rewards/`.  
**Observed response:** HTTP 200, no redirect, final path unchanged, title `Referral Rewards Overview | Django site admin`, `denialText=false`.

### Source and rendered data scope

The deployed source view `AdminReferralRewardsView` in `backend/apps/growth/views.py` inherits from `LoginRequiredMixin` and `TemplateView`; no staff-only or model-permission gate appears in the class. Its context includes:
- ReferralSettings values: default reward percentage, minimum purchase amount and rewards-enabled state.
- Global reward aggregates: total reward count, total issued amount, total used amount and computed outstanding amount.
- The 20 most recent ReferralReward objects, with `referrer` and `referral.referred_user` selected.

The corresponding `backend/apps/growth/templates/growth/admin/referral_rewards_overview.html` renders the settings values; reward counts and financial totals; and a recent-rewards table containing referrer username, referred-user username, amount, status, available amount and creation date. It also renders links to edit referral settings and open all rewards, reward ledger and referrals in Django Admin.

This source/template evidence establishes what the 200 response is designed to render. The supplied console script did not retain or print the response body, so this audit does not reproduce or assert the actual individual values shown in the browser.

### Finding

The learner-labelled session was able to retrieve the referral rewards overview, although the same report returned 403 for the other listed staff/Admin Desk routes. This is a confirmed authenticated access-control failure for a staff-oriented Growth page. Aggregate reward values and referral-linked usernames are in scope for exposure. The availability of Django Admin links does not itself prove that the linked model pages can be opened by the learner; those links still need separate direct-route checks.

**Immediate handling:** do not link or embed this view in the new Admin Desk. Treat the current staging response as exposed to ordinary authenticated members until the route's server-side authorization is restricted and retested. No code or permission change is made by this audit. Remediation should use an explicit staff/domain permission, not rely only on hiding the link or changing navigation.

### Related results from the same learner-labelled report

| Route | Result | Notes |
|---|---|---|
| `/api/notifications/` | 200 | Expected for a signed-in member; source scopes notifications to the current user. |
| `/admin/` | Redirected to `/admin/login/` | Learner did not enter Django Admin. |
| `/admin/growth/send-gift/` | Redirected to `/admin/login/` | Learner did not enter the staff gift form. |
| `/admin-disputes/` | Redirected to `/admin/login/` | Learner did not enter the dispute dashboard. |

The second consolidated report used the manually entered persona label `Superuser`, but it returned 403 for all staff Admin Desk pages and redirected `/admin/`, the gift route and disputes to `/admin/login/`. This is not a successful superuser test. The report does not provide server-verified identity metadata; either the account was not actually switched or it is not configured as a Django staff/superuser account. Do not count this run as a superuser result.

### Corrective test instrumentation

The next consolidated read-only batch should call `/api/auth/me/` and emit only the server-returned `role`, `is_staff` and `is_admin` flags, omitting user ID, email and names. The serializer does not expose `is_superuser`; verify the superuser session separately by successful entry into `/admin/` and its visible superuser-only capabilities. The manually entered persona label must remain descriptive metadata, not identity proof.

**Phase 0 remains open.** This finding must be closed with a route-level permission fix, learner denial (403 or login redirect), and positive access for the explicitly authorised staff persona, before implementation migration or sign-off. Implementation remains NOT AUTHORISED.

## 16. Repeated consolidated test — server identity contradicts manual label

**Timestamp:** 2026-11-14 17:05:19 UTC  
**Operator-entered label:** `Superuser`  
**Server identity endpoint:** `GET /api/auth/me/` returned HTTP 200.

The response flags were:
- `role`: `user`
- `is_staff`: `false`
- `is_admin`: `false`

This proves the browser session used for this run was still a normal non-staff member account. The manually entered `Superuser` label is not evidence of the signed-in identity. The following 403 responses from staff routes are therefore expected for this session and must not be counted as a superuser permission failure or success:
- `/staff/admin-desk/`, `/staff/admin-desk/operations/`, `/staff/admin-desk/accounts/`, `/staff/admin-desk/support/tickets/`;
- `/staff/admin-desk/courses/review/`, `/staff/admin-desk/seo/`, `/staff/course-builder/`, `/staff/course-builder/tiptap/`;
- `/staff/admin-desk/finance/`, `/staff/admin-desk/subscriptions/`, `/staff/admin-desk/business/`;
- `/api/admin/staff-approvals/`, `/api/analytics/overview/`.

`/admin/`, `/admin/growth/send-gift/` and `/admin-disputes/` followed a redirect to `/admin/login/`; this is also consistent with a non-staff/non-admin session.

### Reproducibility of the Growth referral access failure

The same run returned HTTP 200 for `/growth/admin/referral-rewards/`, with title `Referral Rewards Overview | Django site admin`. This is the second supplied browser run showing this route available from a session whose server identity is `role=user`, `is_staff=false`, `is_admin=false`. The access-control finding is therefore reproducible and now has server-verified non-staff identity evidence.

The other successful member route `/api/notifications/` remains expected; source code scopes notifications to the current user. `/health/` returns 200 as a public database readiness endpoint.

### Required next account-switch step

Before the superuser run, explicitly sign out of Academy staging using the site's own sign-out control, then sign in using the authorised superuser account. In the same tab, check `/api/auth/me/` through the batch. Do not proceed until the server flags are consistent with an elevated account (`is_staff=true`, `is_admin=true` and role appropriate for the account). Then confirm `/admin/` reaches the admin index rather than redirecting to `/admin/login/`. The serializer does not expose `is_superuser`; use Django Admin access and an authorised superuser-only page/capability for final confirmation.

**Phase 0 remains open.** The learner access failure on Growth referral rewards is reproducible. No code or permissions were changed. Implementation remains NOT AUTHORISED.