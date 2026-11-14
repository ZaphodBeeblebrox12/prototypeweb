# TradeThesis Admin Desk — Implementation Readiness & Sequence V1

**Date:** 14 November 2026  
**Repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Planning branch:** `admin-desk-redesign-planning`  
**Status:** Planning recommendation based on the source-level review and 60 approved owner decisions.  
**Implementation:** Not authorised. This document is not permission to modify application code or deploy.

## 1. Executive position

The product direction is now defined across 60 owner decisions. The six-domain V1 screen designs and the M50 seven-journey walkthrough exist. The work is **not yet implementation-ready**.

The next phase is a technical readiness and controlled migration exercise. The priority is to establish permission-safe shared foundations, prove workflow parity against the current source and authenticated staging environment, address known lifecycle/data-integrity gaps, and then migrate by workflow with departmental sign-off.

The owner-approved principles are:

- One unified Admin Desk with Command Centre, Academy, Customers, Revenue, Growth and Platform in that exact order.
- Action-first Command Centre; canonical actions happen in the owning workspace.
- V2 warm-light visual system.
- Department-based access, multiple department memberships, personal workspaces and cross-department visibility subject to permissions.
- Permission-checked individual actions, no mandatory second approver, low-risk-only bulk actions and auditable outcomes.
- Financial/provider state is never invented or manually overridden.
- Phased release, pilot testing and departmental-owner acceptance.
- Django Admin target access is superusers only; the timing of legacy workflow cutover must be resolved consistently with decisions 9 and 52.

See `OWNER_DECISION_REGISTER_V1.md` for the complete approved record.

## 2. Readiness status

| Area | Current evidence | Readiness |
|---|---|---|
| Product direction | 60 owner decisions recorded | Direction approved |
| Six-domain structure | V1 prototypes and domain specs exist | First pass; detailed owner review remains |
| End-to-end coverage | M50 seven journeys, 40 fictional linked records, 159/159 static browser checks | Prototype validated only |
| Current backend behaviour | Source-level inspection against `my-new-branch` | Baseline may be stale; refresh required |
| Authenticated staging | Not completed in the prior design audit | Blocker |
| Role/permission parity | Source-level caveats documented; actual role/account matrix not verified | Blocker |
| Workflow/service parity | Several proposed operations have no verified Admin Desk action path | Blocker |
| Accessibility | Keyboard, contrast and screen-reader audit incomplete | Blocker for workspace sign-off |
| Security/data governance | Several model/service enforcement gaps noted below | Blocker for affected controls |
| Deployment/rollback | Render settings/deployed SHA must be rechecked | Blocker before any rollout |
| Implementation authorisation | Not granted | Hard stop |

Static prototype checks prove navigation and local interactions only. They do not prove live API behaviour, permissions, provider completion, authenticated role visibility or production readiness.

## 3. Recommended implementation sequence

This is a dependency-based recommendation. It follows the owner-approved requirement to build shared foundations first and migrate gradually. Actual ordering may be adjusted after fresh source and staging verification.

### Phase 0 — Revalidate the operating baseline (no code changes)

**Purpose:** avoid building against stale source or an incorrect understanding of staging.

Tasks:
- Inspect current `my-new-branch` HEAD and compare it with `admin-desk-redesign-planning`.
- Inspect source-branch-only commits and deliberately reconcile relevant changes; do not blindly rebase or merge.
- Recheck Render service identity, branch, deployed SHA and auto-deploy state.
- Inspect authenticated staging pages with representative staff roles and a superuser.
- Verify actual route availability, HTTP behaviour, object-level visibility and API permissions.
- Build a route/action inventory showing: existing UI, existing service/API, permission, audit event, side effect, owner and parity status.
- Confirm which HTML mockup actions are only illustrative.

**Exit gate:** a signed-off current-state inventory and current deployed-source snapshot. No implementation begins in this phase.

### Phase 1 — Shared shell and operating foundations

**Purpose:** build the parts used by every domain before migrating business workflows.

Scope:
- Unified V2 shell and approved six-domain navigation.
- Staff identity/context, multiple department membership and permission-aware navigation.
- Permission model mapping actual roles, Django Groups, object scopes and approval state.
- Department owner and central system owner mapping.
- Personal workbench, assignment and reassignment model.
- Global and workspace-specific search with permission filtering.
- Shared record relationship/navigation pattern; canonical owner remains authoritative.
- Critical / Warning / Information alert taxonomy.
- Last-updated timestamps and stale-data indicators.
- Common activity history, actor/action evidence and confirmation patterns.
- Responsive navigation and accessibility foundations.

**Dependencies / cautions:**
- Do not infer the current permission model from role names alone. Existing source review found `IsRoleAdmin` accepts role=ADMIN **or** superuser **or any is_staff user**.
- Preserve action-specific reason constraints even though the owner rejected a universal reason requirement.
- Cross-domain history must independently permission-gate every connected record type.

**Exit gate:** shared shell passes role-based route, search, data visibility, audit, keyboard, contrast and responsive tests.

### Phase 2 — Platform governance and operational reliability

**Purpose:** provide safe, inspectable operational controls and make the Platform workspace trustworthy.

Scope:
- Extend the existing permission-filtered Operations Timeline; do not create a duplicate queue.
- Expose Job, PeriodicJob scheduler and worker lifecycle as distinct concepts.
- Show attempts, execution history, failures, stale states and related records according to permissions.
- Add retry actions only where the underlying job handler is safe/idempotent and a supported service route exists.
- Represent ProvisioningOperation, UserChannelAssignment and ChannelMembershipSnapshot separately.
- Show Unknown as **Needs verification**; provide a membership probe/verification path, not a blind resend.
- Integration monitor must distinguish configuration presence, last successful exchange, provider errors and downstream workflow failures.
- Show provider-specific webhook paths and their different evidence semantics.
- Add permission-safe emergency controls with confirmation and audit evidence.
- Include a simplified health summary for all staff and restricted diagnostics for authorised Platform staff.
- Establish security, policy and retention views.

**Known readiness blockers from the inspected source:**
- JobAdmin is read-only; no ordinary staff retry/replay/delete route was verified.
- Existing `/health/` only checks primary database connectivity (SELECT 1), not full service readiness.
- Configuration-presence checks are not provider test transactions.
- Telegram webhook durability was not verified.
- AuditLog lacks a model-level append-only guard in the inspected path; SecurityEvent has stronger append-only behaviour.
- Published PolicyVersion content immutability is not fully enforced in the inspected model/admin path.
- Raw IP and retention restrictions need enforcement review.
- Unknown membership probe must not cause a new invite; preserve existing invite reuse and resend-throttle safeguards.

**Exit gate:** safe job retry tests, provisioning-unknown tests, provider-health evidence tests, append-only/audit tests, permission tests and controlled emergency-action tests pass.

### Phase 3 — Customers, support and Customer 360

**Purpose:** establish the daily staff workflow around people, cases and cross-domain context.

Scope:
- Customers Overview, learner/account list and detail.
- Support ticket queue/detail, assignment, public reply vs private note, SLA tracking and escalation.
- Personal and departmental work queues.
- Customer 360 chronological journey with profile/commercial context.
- Read-only customer preview; no impersonation.
- Field-level and domain-level permission gating for contacts, payments, subscriptions, Academy records and security events.
- Customer exports only for specifically authorised roles, with scope limits and audit.
- Erasure request workflow with verification, retention review and eligible erasure/anonymisation.
- Contextual feedback and issue reporting with owner/status.

**Existing constraints to retain:**
- Reviewer scope and ticket visibility are permission-filtered.
- Existing public replies and internal notes are distinct; do not merge their visibility/semantics.
- Existing account ban/deactivation reason and audit rules remain mandatory.
- Customer 360 must not imply external Telegram/Discord membership from unrelated login-verification fields.

**Exit gate:** representative support cases pass across permissions, assignment, SLA/escalation, cross-domain history, restricted fields, export and erasure workflows.

### Phase 4 — Revenue and financial lifecycle

**Purpose:** provide reliable payment, subscription, refund and dispute workflows without altering financial truth.

Scope:
- Payment and refund register/detail.
- Subscription register/detail, immediate and end-of-period cancellation.
- Plans and pricing configuration only after the existing service/permission boundary is understood.
- Invoices and immutable invoice snapshots.
- Dispute lifecycle with final-outcome semantics.
- Finance/reporting views with currency-aware aggregation.
- Role-specific refund initiation/recording permissions for authorised Support and Revenue staff.
- Access changes only after provider-confirmed refund or final dispute outcome under the existing policy.
- Corrections as new ledger entries, never edits to completed financial records.

**Known readiness blockers from the inspected source:**
- Current finance page is read-only. The existing Django Admin manual full-refund action records a refund **after** provider-side processing; it does not initiate a PSP refund.
- No new refund button may claim to initiate a provider refund until a supported, permission-checked provider service is verified or separately implemented and approved.
- Verify that the current subscription service can safely express both immediate and end-of-period cancellation and returns the effective dates.
- PaymentIntent remains provider evidence and must not be manually marked Paid/Failed.
- Dispute “funds withdrawn” is not a final loss. Preserve access while the dispute remains open.

**Exit gate:** provider-confirmed payment/refund tests, idempotency, partial/full refund access policy, cancellation effective-date tests, immutable ledger tests, multi-currency reporting tests and dispute final-state tests pass.

### Phase 5 — Academy course lifecycle and access

**Purpose:** safely operate the course editorial/publishing lifecycle and tie purchase, entitlement and content operations together.

Scope:
- Course catalogue/detail, import review, course approvals and builder hand-off.
- Editor submit → approver review → publish workflow.
- Draft revisions for edits to published courses.
- SEO/indexability and saleability remain distinct from publication.
- Course offers and entitlements with Revenue-owned plan/price context.
- Explicit, permission-checked manual entitlement grant/revoke.
- Video job failure/retry visible in Academy without removing entitlement.
- Course purchase completion and entitlement reconciliation integrated with Revenue.

**Known readiness blockers from the inspected source/M50:**
- Course activation records `academy.entitlement_granted` (or simulation), not `purchase.completed` in the inspected function.
- Course activation exits before the ordinary membership coupon redemption path; a course PaymentIntent may hold a coupon snapshot without a matching CouponRedemption.
- Implement and test a dedicated course coupon redemption path before enabling course coupons.
- Standardise `purchase.completed` with purchase type for both course and membership transactions; ensure exactly-once event emission and reporting compatibility.
- Preserve canonical Course, CourseImport, CourseOffer, Plan and CourseEntitlement ownership; no duplicate editable copies.
- Tiptap remains outside the production/default authoring path until separately approved.

**Exit gate:** import review, revision approval, publish/return, coupon redemption, purchase event, entitlement grant, video retry and access-policy tests pass.

### Phase 6 — Growth, attribution and customer communication

**Purpose:** unify campaign, consent, promotion, referral, reward, gift and affiliate operations after financial and event contracts are stable.

Scope:
- Campaign creation and approval/publish controls.
- Frozen audience and immutable template-version visibility.
- Provider state labels that distinguish simulated, queued, accepted, delivered, bounced and failed where provider evidence supports them.
- Individual marketing sends subject to consent/suppression.
- Marketing opt-out propagation; keep transactional messages distinct.
- Promotion and coupon reporting with accurate redemption records.
- Referral reward eligibility and exception investigation.
- Gift invite lifecycle distinct from resulting Subscription.
- Affiliate commission states with external payout evidence.
- Outcome-based analytics with currency and attribution definitions.

**Known readiness blockers from the inspected source:**
- G2 send sweep uses `provider=stub` and marks Delivery SENT; display this as **Simulated — not sent to provider** and exclude it from real delivery claims.
- G1 Delivery and transactional EmailLog are separate ledgers; Resend webhook updates Delivery only.
- Referral reward unlock checks PaymentIntent status values not present in model choices; reward balance code mixes currencies; optional referee-bonus helper logs without persisting.
- Affiliate commission Paid is not proof of a payout.
- Custom Referral Rewards Overview route needs staff-only authorization review before use in staff navigation.
- Campaign recipient audience is frozen at schedule and TemplateVersion is immutable; keep those semantics visible.

**Exit gate:** real-vs-simulated delivery tests, consent/suppression tests, campaign approval tests, referral eligibility/currency/persistence tests, coupon redemption, gift invite failure and affiliate payout-evidence tests pass.

### Phase 7 — Command Centre completion and cross-domain rollout

**Purpose:** connect the shared action-first landing page to real, canonical work from each migrated workspace.

Scope:
- Aggregate Critical, Warning and Information items from verified event sources.
- Shared organisation overview plus staff-personalised work.
- Every item routes to its owning domain; Command Centre does not mutate canonical records.
- Assignment, response targets, escalation, last-updated/stale markers and safe bulk-action boundaries.
- Departmental outcome reporting without employee rankings.
- Simplified system-health view for all staff.
- Contextual feedback/reporting.

**Exit gate:** no duplicate ownership, no permission leakage, no stale/false alert claims, working canonical deep links, escalation and assignment tests across the migrated domains.

### Phase 8 — Pilot, parity sign-off and progressive cutover

For every workspace/workflow:
1. Run old and new paths in comparison where safe, without duplicating provider side effects.
2. Complete role-specific functional and negative-permission tests.
3. Verify audit evidence and state transitions.
4. Verify loading, empty, error, no-access, stale and success states.
5. Complete keyboard-only, contrast, screen-reader and mobile validation.
6. Pilot with representatives of affected departments.
7. Obtain written departmental-owner sign-off and central system-owner sign-off.
8. Define rollback trigger and exact rollback path.
9. Cut over the workflow and remove ordinary staff access to its legacy path only at the approved parity gate.
10. Retain superuser emergency access and record the final legacy boundary.

The Django Admin target policy is superusers only. The precise interpretation and timing of that policy must be settled against the workflow-by-workflow cutover rule in decision 52 before permissions change.

## 4. Cross-cutting acceptance requirements

Every action screen must support, where relevant:
- Server-side permission and object-scope enforcement.
- Confirmation for consequential actions.
- Actor, timestamp, action, target and outcome audit evidence.
- Idempotency and safe retry semantics.
- Previous-state preservation when operations fail.
- Current vs stale data indicators.
- Empty, loading, error, denied and success states.
- Mobile and keyboard usability.
- Canonical owner linking rather than duplicate editable copies.
- No inference of provider success from local queue completion or stub states.

Every domain must provide a migration inventory that maps each old workflow to a replacement, identifies users and permission scopes, lists dependencies, tests parity and states rollback conditions.

## 5. Decision-to-domain mapping

| Owner decision range | Main implementation areas |
|---|---|
| 1–5 | Revenue, Academy, Growth, Platform and shared event/state contracts |
| 6–15 | Shared access model, Command Centre, Customers, Platform and audit |
| 16–20 | Staff & Permissions, personal workbench, assignments and departmental queues |
| 21–25 | Command Centre, search, Customer 360 and freshness/event model |
| 26–30 | Revenue, provider services, immutable financial ledgers and access policy |
| 31–35 | Academy review, course revisions, imports, entitlements and video jobs |
| 36–40 | Growth campaigns, consent, referrals, rewards and affiliate payouts |
| 41–45 | Platform health, Jobs, provisioning, integrations and emergency controls |
| 46–50 | Customer privacy, export, erasure, security and retention |
| 51–55 | Release governance, pilot, parity testing and cutover |
| 56–60 | Workspace ownership, SLA, escalation, performance reporting and feedback |

## 6. Open blockers to resolve before affected work begins

- Current source/deployed state and authenticated role audit.
- Actual staff role and multi-department permission mapping.
- Decision 9 vs decision 52 Django Admin cutover interpretation.
- Refund provider initiation/service parity.
- Immediate vs end-of-period cancellation service support.
- Course coupon redemption and unified purchase event contract.
- Referral reward status/currency/referee-bonus correctness.
- Provider-backed campaign send and delivery evidence.
- Safe job retry API and idempotency contract.
- Integration health probes and Telegram webhook evidence path.
- AuditLog immutability, PolicyVersion content immutability and SecurityEvent privacy/retention enforcement.
- Jurisdiction-specific retention/deletion rules and export authorisation.
- Accessibility review and authenticated staging parity.

## 7. Hard stop and authorisation boundary

This plan does **not** authorise:
- application-code changes;
- database migrations;
- route/API/permission changes;
- test or production configuration changes;
- Render settings or deployment changes;
- branch merges or rebases.

Before implementation, the owner must review the final technical handoff, the refreshed source/deployment audit, the role/permission matrix, migration inventory, acceptance plan and rollback plan, then explicitly authorise implementation.
