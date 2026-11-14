# TradeThesis Admin Desk — Owner Decision Register V1

**Decision date:** 14 November 2026  
**Repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Planning branch:** `admin-desk-redesign-planning`  
**Approval status:** 60 owner decisions recorded across 12 rounds  
**Scope:** Product, operating-model, security, workflow and rollout direction. This is not implementation approval.

All entries below record the user's explicit selections or acceptance of the recommendations presented in the 12 decision rounds. Where a choice is a product direction, implementation must still preserve existing backend invariants and pass the readiness gates in `IMPLEMENTATION_READINESS_AND_SEQUENCE_V1.md`.

## Round 1 — Cross-domain workflow decisions

| # | Decision | Approved direction |
|---:|---|---|
| 1 | Course coupons | Support coupons on one-time course purchases through a dedicated, correctly recorded redemption path. |
| 2 | Purchase analytics | Use one standard `purchase.completed` event for course and membership purchases, with a purchase-type field. |
| 3 | Unknown provisioning | Display **Needs verification**, provide a manual verification action, and do not mislabel Unknown as Failed or Succeeded. |
| 4 | Open payment dispute | Keep access active while the dispute remains open, including while funds are withdrawn; change access only after a confirmed final loss or confirmed refund under the applicable policy. |
| 5 | Campaign stub delivery | Display **Simulated — not sent to provider** when the stub provider is used. |

## Round 2 — Staff access and control

| # | Decision | Approved direction |
|---:|---|---|
| 6 | Admin Desk access | Administrators and approved staff use role-specific permissions. |
| 7 | Support staff actions | Support staff may perform routine, reversible actions within their permissions. |
| 8 | Sensitive-action controls | Require permission checks and confirmation. A reason is not a universal mandatory field; preserve any existing action-specific reason requirements. |
| 9 | Django Admin access | Target access boundary is superusers only. The migration/cutover interpretation must be reconciled with decision 52 before access is changed. |
| 10 | Command Centre actions | Command Centre identifies and routes issues to the canonical owning workspace; actions are performed there. |

## Round 3 — Operational controls and accountability

| # | Decision | Approved direction |
|---:|---|---|
| 11 | Second-person approval | No mandatory second-person approval. An authorised staff member may complete an action independently. |
| 12 | Bulk operations | Permit bulk actions only for low-risk operations. |
| 13 | Failed actions | Preserve the previous state and show the failure; offer a safe retry only where the underlying operation supports it. |
| 14 | Audit/activity visibility | Show relevant history across connected records, subject to permissions. |
| 15 | Customer preview | Provide read-only customer preview; do not support acting as the customer. |

## Round 4 — Department structure and work ownership

| # | Decision | Approved direction |
|---:|---|---|
| 16 | Department membership | Staff may belong to multiple departments, with independently assigned permissions. |
| 17 | Department managers | Managers may manage staff access within their own department only. |
| 18 | Personal activity | Each staff member gets a personal activity workspace for assigned work, issues, attention items and relevant activity history. |
| 19 | Work assignment | Support automatic assignment and manual reassignment by managers. |
| 20 | Team visibility | Staff may see relevant departmental work, subject to permissions; private staff activity is not universally exposed. |

## Round 5 — Navigation, visibility and information

| # | Decision | Approved direction |
|---:|---|---|
| 21 | Command Centre personalisation | Show a shared organisation-wide overview plus a personalised section for each staff member. |
| 22 | Alert classification | Use three levels: Critical, Warning and Information. |
| 23 | Search | Provide both global and workspace-specific search; both are permission-filtered. |
| 24 | Customer 360 | Prioritise a unified chronological customer history, with profile and commercial information alongside it. |
| 25 | Freshness indicators | Show last-updated timestamps and flag potentially stale information. |

## Round 6 — Payments, refunds and financial integrity

| # | Decision | Approved direction |
|---:|---|---|
| 26 | Refund authority | Authorised Support and Revenue staff may issue refunds through specific permissions. |
| 27 | Refund/access relationship | Change access only after the payment provider confirms the refund. |
| 28 | Subscription cancellation | Support immediate and end-of-billing-period cancellation; end-of-period is the default. Show effective cancellation and access dates. |
| 29 | Payment status changes | Payment status must come from verified provider events or reconciliation; staff cannot manually override it. |
| 30 | Financial record integrity | Completed financial records are immutable. Corrections and adjustments are new entries, not edits to completed transactions. |

## Round 7 — Academy and course operations

| # | Decision | Approved direction |
|---:|---|---|
| 31 | Course publication | Editors submit; authorised Academy approvers review and publish. |
| 32 | Published-course edits | Changes create a draft revision. The published version remains live until the revision is approved. |
| 33 | Course imports | Successful import enters a review state; validate content and structure before an authorised person approves publication. |
| 34 | Manual entitlement management | Specifically authorised staff may grant or revoke learner entitlements with confirmation and an audit record. This must not alter or fabricate payment evidence. |
| 35 | Video-processing failures | Show failures in Academy and allow safe retry; a video job failure does not remove an existing learner entitlement. |

## Round 8 — Growth, campaigns and communication

| # | Decision | Approved direction |
|---:|---|---|
| 36 | Campaign launch | Growth staff create campaigns; authorised approvers approve before launch. |
| 37 | Individual marketing messages | Permitted staff may send individual marketing communications only when customer preferences and suppression rules allow it. |
| 38 | Referral rewards | Automatically unlock rewards when configured eligibility conditions are met; staff investigate exceptions. |
| 39 | Affiliate commissions | Distinguish calculated, approved, processing and actually paid; Paid requires verifiable payout evidence. |
| 40 | Marketing opt-out | Apply opt-out immediately across marketing channels. Keep separately authorised transactional communications distinct. |

## Round 9 — Platform, reliability and system health

| # | Decision | Approved direction |
|---:|---|---|
| 41 | Health visibility | All staff see a simplified system-health overview; technical details are permission-restricted. |
| 42 | Job retry authority | Authorised staff may retry specific safe jobs within their department; dangerous or unsupported retries remain restricted. |
| 43 | Technical job details | Execution history, errors, attempts and related records are visible according to permissions. |
| 44 | Integration monitoring | Show integration health, last successful activity, failures and affected workflows, with safe diagnostics. |
| 45 | Emergency controls | Specifically authorised Platform staff may use emergency controls with permission checks, confirmation and audit logging. |

## Round 10 — Privacy, security and data governance

| # | Decision | Approved direction |
|---:|---|---|
| 46 | Customer information | Staff see information needed for their work; sensitive fields require additional permissions. |
| 47 | Customer-data export | Specifically authorised roles may export customer data, with scope controls and audit logging. |
| 48 | Erasure requests | Verify the request, review applicable retention obligations, then erase or anonymise eligible data through a controlled workflow. |
| 49 | Security events | Relevant events are visible to authorised owners; detailed security information remains restricted. |
| 50 | Retention | Define retention periods by record category and apply controlled automated retention/deletion policies. |

## Round 11 — Implementation and migration

| # | Decision | Approved direction |
|---:|---|---|
| 51 | Release strategy | Roll out gradually, enabling workspaces and capabilities in stages. |
| 52 | Legacy-workflow cutover | Remove ordinary staff access to each corresponding legacy workflow as its replacement is successfully migrated and verified. Reconcile this staged cutover with the target superuser-only Django Admin policy in decision 9 before changing access. |
| 53 | Implementation sequence | Build shared foundations first: permissions, audit logging, navigation, global search and customer-record relationships. |
| 54 | Pilot | Test with a small pilot group representing the different departments. |
| 55 | Workspace readiness | Require working interface and workflows, permissions, audit history, error handling, mobile responsiveness and documented departmental-owner sign-off. |

## Round 12 — Accountability and daily operations

| # | Decision | Approved direction |
|---:|---|---|
| 56 | Workspace ownership | Each workspace has a departmental owner and a central system owner. |
| 57 | Response targets | Define response targets by severity and distinguish acknowledgement time from resolution time. |
| 58 | Escalation | Automatically escalate unresolved work using configurable severity, ownership and elapsed-time rules; managers can override. |
| 59 | Performance reporting | Measure outcomes and operational health: completion, unresolved work, age, failures, rework and bottlenecks. Do not rank individual employees. |
| 60 | Staff feedback | Allow contextual issue reports and improvement suggestions within the Admin Desk, with tracking and ownership. |

## Cross-cutting interpretation rules

1. **Permissions remain server-side.** Hiding a button is not authorization. Every action, API and record query must enforce the same policy.
2. **No dual approval does not mean broad access.** An authorised individual can act without a second approver, but must still hold the relevant capability and pass confirmation/audit requirements.
3. **No universal reason field does not erase existing rules.** Preserve action-specific mandatory reasons already required by current business services (for example, existing account or subscription controls).
4. **Provider truth is authoritative for money and external delivery.** An initiated action, local status or stub-provider status is not proof of provider completion.
5. **Canonical ownership remains unchanged.** Related context may be shown elsewhere, but a record is edited in its owning domain.
6. **Unknown remains distinct.** Unknown external state is not success or failure and cannot trigger unsafe assumptions or blind retries.
7. **Readiness decisions are not implementation approval.** The owner has approved product direction; application code, migration, permission changes, tests, hosting settings and deployment remain outside scope until explicit implementation approval.
8. **Existing business rules remain in force.** New UI behaviour must call existing audited services or a separately reviewed replacement service; mockup controls are not evidence of backend capability.

## Outstanding implementation clarifications (not further product rounds)

- Reconcile decisions 9 and 52 into a precise legacy staff-access cutover rule before changing Django Admin permissions.
- Map the approved department/persona model onto actual current account roles, Django Groups, object scopes and staff approval states.
- Confirm which existing services/APIs can initiate provider refunds and immediate/end-of-period cancellation; do not imply a new UI can do so until service parity exists.
- Confirm exact escalation/SLA targets, alert event sources and operating hours with the department owners during technical planning.
- Confirm applicable jurisdictional and contractual retention rules with the appropriate business/legal owner before configuring deletion.

## Change control

Future changes should be appended as new numbered decisions or explicit superseding decisions. Do not silently rewrite an approved choice. Record the reason, affected workflows, owner and date.
