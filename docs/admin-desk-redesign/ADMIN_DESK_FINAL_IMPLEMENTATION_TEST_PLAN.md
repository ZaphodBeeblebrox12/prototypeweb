# TradeThesis Admin Desk — Final Implementation Test Plan

**Status:** Deferred — implementation first, consolidated testing afterwards  
**Planning branch:** `admin-desk-redesign-planning`  
**Application branch:** `my-new-branch`  
**Recorded:** 15 November 2026

## 1. Decision: finish implementation before the full test campaign

The owner wants the Admin Desk implementation completed before running the final manual, browser, role-based, workflow and acceptance test campaign.

**Do not start another round of incremental manual/browser/UAT testing while the Admin Desk is still being implemented.** Keep implementation and design work moving. Once the agreed final implementation is integrated and deployed to Academy staging, run one consolidated test campaign against that finished build and record the results here.

Previously completed tests remain useful baseline evidence; they are not final acceptance of the completed Admin Desk. The consolidated campaign must retest the relevant areas against the final integrated build.

Normal automated CI/build checks that are required to validate and merge code remain engineering gates; this deferral is about the full manual, role/persona, end-to-end and acceptance test pass.

## 2. Implementation scope to complete before final testing

The Admin Desk is planned as one V2 operating workspace with these six top-level destinations, in this order:

1. Command Centre
2. Academy
3. Customers
4. Revenue
5. Growth
6. Platform

Complete the agreed workflows and navigation across these destinations before the final acceptance campaign. Keep Advanced Administration available for high-risk legacy workflows until replacement parity is demonstrated. Do not globally lock ordinary staff out of Django Admin before that cutover decision. The legacy Course Builder remains the default; Tiptap is not to become the production/default editor until it is ready and explicitly integrated.

The supplied **Customers Workspace V1** HTML is a design/interaction reference, not a live implementation or evidence that these workflows already exist. Its illustrative people, amounts, ticket IDs, dates and counts must not be treated as real data. The final Customers implementation should be checked against the intended structure below.

## 3. Consolidated test campaign — execute after final implementation

### A. Deployment and release integrity

- Confirm the final Academy staging deployment is live and running the intended commit.
- Confirm migrations, static assets, templates and frontend assets load correctly.
- Verify the six destinations and their navigation work at desktop and mobile widths.
- Check that no production or public-static-staging service is changed as part of staging verification.
- Record the tested commit, deployment ID, date/time, browser and test personas.

### B. Authentication, role matrix and route/API permissions

Use distinct test personas: logged-out visitor, learner, generic Django staff with no domain grants, Academy specialist, Revenue specialist, Growth specialist, Platform specialist, and superuser.

For every persona, verify both page routes and the underlying APIs/actions:
- Expected allowed pages and data are accessible.
- Restricted pages, direct URLs, APIs and mutation endpoints return the correct denial rather than leaking content.
- A navigation item being hidden is not treated as security; direct URL and API access must also be checked.
- Permissions are least-privilege and do not spill across domains.
- Specialist roles can perform only the actions covered by their explicit group/model permissions.
- Superuser access remains functional.
- Generic `is_staff=true` alone does not grant protected business permissions.
- Verify object-level access and record ownership, not only route-level responses.

Include the previously audited protected routes:
- `/growth/admin/referral-rewards/`
- `/api/admin/staff-approvals/`
- `/api/analytics/overview/`
- `/admin/growth/send-gift/`
- `/admin-disputes/`

Also retest the generic-staff route matrix:
- Expected staff access: `/staff/admin-desk/`, `/staff/admin-desk/operations/`, `/staff/admin-desk/support/tickets/`, `/api/notifications/` (own notifications only).
- Expected denial without grants: Customers/Accounts, Academy review and SEO, both Course Builder routes, Finance, Subscriptions, Business settings, referral rewards, gift sending, disputes, staff approvals and Growth analytics.
- Test `/admin/` according to the final documented cutover policy. Until workflow parity and an explicit cutover, legacy generic-staff access may remain; do not silently change this expectation.

### C. Command Centre and shared workspace

- Verify landing/overview content, assigned work, notifications/alerts and operations timeline.
- Confirm counts and summary cards respect the current staff member's permissions and scope.
- Confirm notifications show only the signed-in user's permitted records.
- Verify links lead to the canonical destination and do not bypass permissions.

### D. Academy

- Verify catalogue and course approval/review flows for the intended Academy roles.
- Verify lesson/course content and authoring workflows, publishing and approval boundaries.
- Confirm the legacy Course Builder remains the default during this phase.
- Confirm Tiptap remains non-default until its integration is explicitly completed and approved.
- Verify SEO/discoverability permissions and direct API protection.
- Test learner entitlement and progress visibility only for roles with the relevant permissions.

### E. Customers — use the supplied Customers Workspace V1 as the design reference

**Customers overview and Learners & Accounts**
- Verify the overview links to Learners & Accounts, Support Tickets and Customer 360.
- Verify learner search by username, name and email; account-state filters for active, inactive and banned; newest-joined-first ordering; and 25-row pagination.
- Confirm internal staff and administrator accounts are excluded from the general learner register.
- Confirm subscription counts are hidden unless the reviewer has subscription-view permission.
- Confirm account details distinguish account state, last sign-in and managed community links.

**Account actions**
- Verify the required `accounts.change_user` permission for every mutation.
- Verify ban/deactivate require a reason of at least five characters.
- Verify activate/reactivate/unban and password-reset paths use the canonical account workflows.
- Confirm successful actions are audited and enqueue reconciliation.
- Confirm an account action does not mutate payments, invoices, subscriptions or course entitlements.
- Test denied roles and invalid/missing reasons without changing real customer accounts.

**Support queue and ticket lifecycle**
- Verify reviewer-scoped queue results, search, status/category/priority/assignment filters and ordering.
- Verify first-response SLA targets: urgent 2 hours, high 8 hours, normal 24 hours, low 72 hours.
- Verify deadline recalculation when priority changes before first response.
- Verify assignment is limited to eligible reviewers.
- Verify public replies, private internal notes, status transitions, start review, awaiting-member, approval and rejection.
- Verify rejection requires a reason.
- Verify public replies and internal notes remain distinct; internal notes never appear to the member.
- Verify access approval grants the selected eligible hidden plan and enqueues reconciliation transactionally; if enqueue fails, the grant and ticket update must roll back.
- Verify member notification is attempted after commit, not before.
- Verify ticket attachments are private and protected by the same reviewer/object scope.

**Support object-scope security — mandatory**
- Test a known in-scope ticket and a known out-of-scope ticket for the same generic staff persona.
- Test direct detail URLs and attachment URLs, not just queue visibility.
- Test plans with configured `ticket_approvers` and plans with an empty approver list.
- Resolve and explicitly approve the existing empty-approver fallback (currently described as allowing any active staff) before treating it as intended policy.
- Test assignment and every ticket action against the same scope rule.
- Five previously visible ticket detail pages returned 200; that was only a positive visibility check and did not prove out-of-scope denial.

**Customer 360**
- Verify the view is read-only and permission-scoped across Account, Academy, Revenue, Support, Community/Security and Activity.
- Verify Academy data requires the relevant course-entitlement and lesson-progress permissions.
- Verify Revenue sections are independently permission-gated and never expose provider tokens or raw payment identifiers.
- Verify Support history includes only reviewer-visible tickets.
- Verify managed Telegram/Discord account records are not confused with legacy login verification.
- Verify security summary shows only the approved event type/timestamp details, not raw IP addresses or user agents.
- Verify internal staff requester profiles are restricted to identity and reviewer-visible tickets; hide subscription, payment, invoice, course and security records as specified.
- Verify internal support notes are excluded from customer activity.
- Confirm each domain's canonical records remain owned by that domain; Customer 360 is a summary, not a second ledger or mutation surface.

### F. Revenue

- Verify payments, refunds, subscriptions/plans, invoices and disputes are accessible only to the intended Revenue roles.
- Verify read and mutation permissions separately.
- Verify financial summaries agree with canonical payment/invoice records.
- Verify no Customer 360 or Support action duplicates or changes the financial ledger.
- Verify dispute actions and refund actions are audited and cannot be reached by generic staff without explicit grants.

### G. Growth

- Verify analytics, referrals/rewards, coupons/gifts, campaigns and email delivery surfaces against the intended Growth role matrix.
- Verify sensitive aggregate and customer-level data is not exposed to learner or generic staff.
- Verify gift sending, reward changes and campaign actions require explicit permissions and are audited.
- Use safe staging fixtures for mutation tests; do not send real customer emails or issue live rewards.

### H. Platform

- Verify operations timeline, background jobs, provisioning/integrations, domain events, AuditLog and SecurityEvent views.
- Verify detail pages, retries and other actions require the corresponding explicit permissions.
- Verify job/provisioning object scope with known permitted and forbidden fixtures.
- Verify sensitive security data is not overexposed in customer-facing summaries.
- Verify operations failures are visible and do not silently create duplicate provisioning or side effects.

### I. End-to-end workflows

Run end-to-end scenarios with disposable staging fixtures:
1. Learner account lookup → Customer 360 → permitted cross-domain summaries.
2. Support ticket submission → reviewer queue → assignment → public reply/internal note → status transition → final resolution.
3. Referral/access request → reviewer-scope check → eligible plan grant → provisioning enqueue → post-commit notification; also test rollback when enqueue fails.
4. Account ban/deactivation with reason → audit event → reconciliation; verify no Revenue or Academy ledger mutation.
5. Payment/subscription/invoice context shown in Customer 360 while all financial mutation remains in Revenue.
6. Platform provisioning issue linked from a customer/ticket context and resolved through the canonical Platform workflow.

### J. Non-functional and regression checks

- Desktop and mobile responsive behavior, keyboard navigation, focus visibility and usable error/empty/loading states.
- Search, filtering, sorting, pagination and long-content handling.
- Performance for large lists and dashboards; no duplicate expensive queries or blocking work in shared operations pages.
- Audit trail completeness for every privileged mutation.
- CSRF/session behavior, expired session handling and safe error responses.
- No data leakage through HTML, JSON, browser-visible links, exports, attachments, notifications or logs.
- Confirm existing Academy learner/course workflows remain functional after Admin Desk integration.

### K. Final cleanup and sign-off

- Use only disposable staging test data/accounts for destructive workflow tests.
- Clean up only the disposable test accounts/fixtures created for the campaign, after evidence is recorded; never delete or alter the owner's main account.
- Revoke disposable test sessions.
- Record each test as PASS / FAIL / BLOCKED / NOT TESTED with persona, URL/workflow, expected result, observed result and evidence.
- Fix all critical/high severity failures and rerun affected tests.
- Obtain explicit owner review of the completed staging build and test report before any production deployment or global Django Admin cutover.

## 4. Baseline tests already completed — evidence only, not final sign-off

### Phase 0 three-persona protected-route matrix

On live Academy staging, the following five GET routes were checked using learner, generic staff and owner admin sessions:

| Route | Learner | Generic staff | Owner admin session |
|---|---:|---:|---:|
| Referral rewards | 403 | 403 | 200 |
| Staff approvals API | 403 | 403 | 200 |
| Growth analytics | 403 | 403 | 200 |
| Gift sending page | 403 | 403 | 200 |
| Disputes | 403 | 403 | 200 |

All 15 expected decisions matched. These were route-level GET checks only; no mutation was submitted.

### Generic-staff consolidated route smoke test

The generic staff session produced 17/17 expected decisions:
- 200: Command Centre, Operations, Support queue, own notifications.
- 403: Customers/Accounts, Academy review, Academy SEO, Course Builder, Tiptap Builder, Finance, Subscriptions, Business settings, referral rewards, gift sending, disputes, staff approvals API and Growth analytics.

Additional observations:
- Five ticket detail URLs discovered from the visible Support queue returned 200. This did not test an out-of-scope ticket.
- No Platform job/provisioning detail links were discovered; Platform details were not tested.
- Legacy `/admin/` returned 200, expected for now under the deferred global cutover.
- Requests were GET-only and no data was modified.

The detailed results are recorded in [PHASE_0_POST_DEPLOY_PERMISSION_VERIFICATION_2026-11-15.md](./PHASE_0_POST_DEPLOY_PERMISSION_VERIFICATION_2026-11-15.md).

## 5. Outstanding items to carry into the final campaign

- Support object-level boundary, especially direct access to an out-of-scope ticket and the empty-`ticket_approvers` fallback policy.
- Specialist permission matrix for Academy, Revenue, Growth and Platform.
- Platform job/provisioning detail access.
- Full workflow parity and final Django Admin cutover decision.
- Final cleanup of disposable staging accounts and fixtures.

**Release rule:** Admin Desk implementation first. One consolidated, evidence-backed test campaign after the final implementation is ready on Academy staging. No production deployment or global legacy-admin lockout is implied by this plan.
