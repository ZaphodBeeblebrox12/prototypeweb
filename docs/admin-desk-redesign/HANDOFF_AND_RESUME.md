# TradeThesis Admin Desk Redesign — Handoff & Resume

**Last updated:** 14 November 2026  
**Repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Planning branch:** `admin-desk-redesign-planning`  
**Source/code baseline:** `my-new-branch`  
**Current phase:** Phase 0 source/deployment baseline audit checkpoint; authenticated staging and role verification remain outstanding.  
**Implementation status:** Not authorised. Do not modify app code or deploy.

## 1. Resume instruction for a new chat

Start a new chat and say:

> Resume the TradeThesis Admin Desk redesign. Read `docs/admin-desk-redesign/HANDOFF_AND_RESUME.md` on branch `admin-desk-redesign-planning`, then inspect the latest Decision Log, Owner Decision Register, Implementation Readiness & Sequence, Mockup Register, Domain Workspace Blueprint and screen specifications. Continue from the next unreviewed design task. Keep all work on the planning branch and do not implement or deploy until I explicitly approve.

The resume document is intended to restore project context without depending on the previous chat transcript.

## 2. Approved decisions — do not reopen unless the owner asks

1. **One unified Admin Desk:** Academy, Customers, Revenue, Growth and Platform operations are accessible through one shared shell and sidebar.
2. **Action-first landing page:** Command Centre answers “What needs my attention now?” before presenting business metrics.
3. **Phased Django Admin migration:** everyday workflows move into the new Admin Desk gradually; Advanced Administration remains available for high-risk, low-frequency or not-yet-migrated capabilities until safe parity exists.
4. **Six top-level domains and exact order:**
   - Command Centre
   - Academy
   - Customers
   - Revenue
   - Growth
   - Platform
5. **Shared V2 visual template:** the supplied Customer 360 screenshot is the visual reference:
   - Deep forest-green sidebar.
   - Warm ivory workspace.
   - Warm-white surfaces.
   - Restrained terracotta emphasis.
   - Muted sage positive/selected states.
   - Editorial serif page headings.
   - Compact sans-serif interface text.
   - Fine borders, low shadow and restrained corners.
6. **Planning before implementation:** brainstorm, define workflows, create mockups, review end-to-end journeys and agree implementation handoff before any app-code changes.
7. **Existing rules are non-negotiable:** preserve server-side permissions, business services, transactional safety, audit events and canonical record ownership.
8. **Tiptap boundary:** do not treat Tiptap as the production/default Course Builder until separately approved; current supported legacy Builder remains the authoring baseline.

The exact decisions and their rationale are in `DECISION_LOG.md`.

## 3. Branch and change boundary

- Continue only on `admin-desk-redesign-planning`.
- The branch was created from `my-new-branch`.
- Current source inspections have used `my-new-branch` as the baseline.
- Compare against `my-new-branch` before handing over or merging.
- **Phase 0 comparison (14 November 2026):** at audit start, the planning branch was 82 commits ahead and 15 commits behind `my-new-branch`, with merge base `251260448c480ec5fbfec4f1966d9017fa0854ff`. All 21 planning-only changed files at that point were under `docs/admin-desk-redesign/`. The 15 source-only commits touched three Academy Course Builder files only. The Phase 0 audit and this handoff update add further documentation commits to the planning branch; re-run the comparison on resume rather than treating the planning-branch ahead count as fixed.
- Do not auto-merge or rebase the planning branch. Inspect/reconcile the 15 source-only commits deliberately. The current Academy Render deployment matches the source HEAD recorded in `PHASE_0_CURRENT_BASELINE_AUDIT_V1.md`.
- All changes so far are planning documentation. The HTML prototypes are standalone review artifacts supplied in conversation.
- No application code, migration, tests, settings, hosting configuration or Render deployment has been changed by this redesign work.
- Before any implementation, recheck the current branch HEAD, Render deployment SHA, auto-deploy setting, current authenticated staging pages and role-specific access. The old source baseline is not a substitute for a fresh implementation audit.

## 4. Documents to read first

Read these in order:

1. `OWNER_DECISION_REGISTER_V1.md` — all 60 owner-approved product and operating-model decisions.
2. `IMPLEMENTATION_READINESS_AND_SEQUENCE_V1.md` — readiness blockers, dependency-based phases, exit gates and hard-stop boundary.
3. `DECISION_LOG.md` — original design decisions and decision-control rules.
4. `REDESIGN_PLAN.md` — overall process, phases and guardrails.
5. `INFORMATION_ARCHITECTURE_V1.md` — approved six-domain model and proposed child navigation.
6. `DOMAIN_WORKSPACE_BLUEPRINT_V1.md` — responsibilities, workspaces, records and end-to-end journeys.
7. `CROSS_DOMAIN_CONNECTIONS_V1.md` — canonical ownership and hand-off contract.
8. `ROUTE_TO_WORKSPACE_MAP_V1.md` — current route, API and Django Admin boundaries.
9. `MOCKUP_REGISTER.md` — all mockups and their review state.

Screen-level specifications:
- `ACADEMY_WORKSPACE_SPEC_V1.md`
- `CUSTOMERS_WORKSPACE_SPEC_V1.md`
- `REVENUE_WORKSPACE_SPEC_V1.md`
- `GROWTH_WORKSPACE_SPEC_V1.md`
- `PLATFORM_WORKSPACE_SPEC_V1.md`
- `HOLISTIC_WALKTHROUGH_V1.md`

Review notes:
- `M01_M02_REVIEW_NOTES.md`
- `CUSTOMERS_REVIEW_NOTES_V1.md`
- `REVENUE_REVIEW_NOTES_V1.md`
- `GROWTH_REVIEW_NOTES_V1.md`
- `PLATFORM_REVIEW_NOTES_V1.md`
- `HOLISTIC_REVIEW_NOTES_V1.md`

## 5. Completed design work

### M01 / M02 — Shared shell and Command Centre concepts
- Shared V2 shell and six-domain order.
- Desktop/collapsed navigation and mobile drawer.
- Global search and notification entry points are design placeholders.
- Three Command Centre directions were explored: action queue first, operational cockpit and personal workbench.
- Action queue first is the recommended candidate; do not treat that specific screen composition as owner-approved unless later recorded.

Prototype artifact in the conversation:
- `tradethesis_admin_shell_command_centre_v2.html`

### M24 — Six-domain architecture board
- All six top-level domains and proposed child destinations represented.
- Canonical record ownership and cross-domain relationships documented.
- Seven end-to-end workflow tests included.
- Existing capabilities are separated from proposed unified views.

Prototype artifact:
- `tradethesis_admin_six_domain_workspaces_v1.html`

### Academy — M03–M09, M25 and M26
Screen types:
- Academy Overview.
- Course Catalogue.
- Course Detail.
- Course Approvals.
- Course Review Detail.
- Course Builder hand-off.
- Offers & Access.
- Learner Access & Progress.
- SEO & Discoverability.

Source boundaries preserved:
- CourseImport review and canonical publication.
- Return-to-editor requires mandatory feedback.
- Revision does not mutate the live Course until approved.
- Course role, publication state and access type remain separate.
- CourseOffer belongs to Academy; its linked Plan and prices belong to Revenue.
- Direct entitlement, free-course enrolment and the inspected TradeThesis Free membership mapping are distinct access paths.
- Tiptap remains a development/feature-gated path.

Specification:
- `ACADEMY_WORKSPACE_SPEC_V1.md`

Prototype artifact:
- `tradethesis_admin_academy_workspace_v1.html`

### Revenue — M14/M15 and M29–M33
Screen types:
- Revenue Overview.
- Payments & Refunds register and Payment Detail.
- Subscriptions.
- Plans & Pricing.
- Invoices and Invoice Detail.
- Disputes and Dispute Detail.
- Business & Finance.

Source boundaries preserved:
- PaymentIntent is read-only financial evidence; provider verification controls state.
- Refund is a separate append-only ledger. Partial refund leaves access unchanged; full refund cancels affected subscription or revokes course entitlement through the existing policy.
- Manual full refund record exists in Django Admin only and must be used after provider-side refund. It does not initiate a PSP refund.
- Subscription grants/extensions/cancellations use the current audited services and permission/reason constraints; price snapshots are immutable.
- Plan/base/geo pricing configuration remains Django Admin today; proposed unified Revenue editor is not live.
- Invoice snapshots are immutable and printable.
- Disputes remain on their existing staff route; funds withdrawn is not a final loss; Won keeps access, confirmed Lost/Accepted triggers exactly-once access action.
- Dispute evidence submit records external reference; does not upload evidence to PSP.
- Tax is a fixed percentage today, not a jurisdiction-aware GST engine; first enable requires accountant confirmation.

Specification:
- `REVENUE_WORKSPACE_SPEC_V1.md`

Review notes:
- `REVENUE_REVIEW_NOTES_V1.md`

Prototype artifact:
- `tradethesis_admin_revenue_workspace_v1.html`
- `tradethesis_admin_growth_workspace_v1.html`
- `tradethesis_admin_platform_workspace_v1.html`
- `tradethesis_admin_holistic_workflow_v1.html`
- `tradethesis_admin_growth_workspace_v1.html`

### Growth — M18 and M34–M41
Screen types:
- Growth Overview.
- Analytics & Attribution.
- Campaigns & Audiences.
- Journeys & Automation.
- Promotions & Coupons.
- Referrals & Rewards.
- Gifts.
- Email Delivery (G1 Delivery, transactional EmailLog, Consent/Suppression, Templates).
- Advanced Growth (Affiliates/Commissions, Experiments, Announcements/Channels).

Source boundaries preserved:
- Analytics response key/function "signups" currently counts purchase.completed Events; promotion report references Sum without import; email report omits delivered/delayed; CampaignMetrics bounce/complaint counters are not reconciled by the inspected webhook.
- Campaign audience membership is frozen at schedule; TemplateVersion is immutable. G2 send sweep uses provider=stub and marks Delivery SENT, not verified external delivery. Telegram/in-product campaign actions are staged and not wired into the send sweep.
- CouponRedemption is created after successful activation and is read-only; campaign scoping uses first-touch SignupAttribution; referral discount stacking is configurable.
- Referrer reward buckets are currency-bearing; UserRewardBalance currently sums across currencies. Reward unlock searches PaymentIntent statuses not in model choices; missing triggering Subscription stays pending; optional referee bonus helper logs only and does not persist.
- The custom Referral Rewards Overview route uses LoginRequiredMixin, not staff-only authorization; do not reuse in staff navigation without permission review.
- GiftInvite is separate from resulting Revenue Subscription; gift can be created while email fails; modern token and legacy gift-code flows remain distinct; no staff resend UI verified.
- G1 Delivery and transactional EmailLog are separate; Resend webhook updates Delivery only. Marketing opt-in defaults false; global suppression overrides it, while transactional email is separate.
- Affiliate commission Paid is an internal state, not proof of provider payout. Telegram marketing delivery is not membership provisioning.

Specification:
- `GROWTH_WORKSPACE_SPEC_V1.md`

Review notes:
- `GROWTH_REVIEW_NOTES_V1.md`

Prototype artifact:
- `tradethesis_admin_growth_workspace_v1.html`

### Platform — M42–M49
Screen types:
- Platform Overview.
- Jobs & Scheduler (durable Job, PeriodicJob and worker lifecycle).
- Access & Provisioning.
- Integrations & Webhooks.
- Audit & Security.
- Policies & Readiness.
- Staff & Permissions.
- Migration Boundary / Advanced Administration.

Source boundaries preserved:
- The existing Operations Timeline and read-only Job/Provisioning detail routes are the current operational foundation; Platform does not create a second queue.
- Durable Job, PeriodicJob scheduler and worker lifecycle are separate. JobAdmin is read-only; no ordinary staff retry/replay/delete action was verified.
- ProvisioningOperation, UserChannelAssignment and ChannelMembershipSnapshot remain separate. Unknown is not failure; unknown membership probe does not trigger resend; reuse stored invite and preserve six-hour resend throttle.
- Native Telegram Bot API is direct from Django; BotRuntimeState is legacy bridge diagnostic only. Superuser-only live grant/revoke test remains Advanced Administration.
- Stripe/Razorpay use durable WebhookEvent + queued worker processing; Resend updates G1 Delivery only; Telegram webhook ledger not verified. No unified integration monitor was found.
- /health/ only executes SELECT 1 on primary DB; runtime settings-presence checks are not provider test evidence.
- SecurityEvent is append-only; raw-IP/retention policy requires enforcement verification. AuditLog has no model append-only guard in the inspected source.
- PolicyAcceptance is write-once, but published PolicyVersion content immutability is not fully enforced by the inspected model/admin path.
- IsRoleAdmin allows role=ADMIN OR superuser OR any is_staff; Staff & Permissions cannot be migrated as an Admin-only permission matrix without further audit.

Specification:
- `PLATFORM_WORKSPACE_SPEC_V1.md`

Review notes:
- `PLATFORM_REVIEW_NOTES_V1.md`

Prototype artifact:
- `tradethesis_admin_platform_workspace_v1.html`

### Customers — M10–M13, M27 and M28
Screen types:
- Customers Overview.
- Learners & Accounts.
- Learner Account Detail.
- Support Tickets queue.
- Ticket Detail.
- Customer 360.

Source boundaries preserved:
- General learner list excludes staff and superusers.
- Account actions require `accounts.change_user`; ban/deactivate require a reason of at least five characters and are audited/reconciled.
- Ticket visibility follows plan/affiliate-plan approver scope.
- SLA targets: Urgent 2h, High 8h, Normal 24h, Low 72h.
- Public support replies and private internal notes are different append-only messages.
- Access-request approval grants a hidden Plan and enqueues reconciliation in the same transaction; billing/technical approval only resolves the ticket.
- Customer 360 is read-only and independently permission-gates subscriptions, payments, invoices, Academy records and security.
- Internal staff requester profiles remain identity + reviewer-visible support only.
- Managed Telegram/Discord membership is not inferred from legacy login verification.

Specification:
- `CUSTOMERS_WORKSPACE_SPEC_V1.md`

Review notes:
- `CUSTOMERS_REVIEW_NOTES_V1.md`

Prototype artifact:
- `tradethesis_admin_customers_workspace_v1.html`

## 6. Cross-domain operating model

Canonical ownership:
- **Command Centre:** aggregation and routing only; it does not own underlying business records.
- **Academy:** Course, curriculum, CourseImport, CourseOffer, direct CourseEntitlement and learning progress.
- **Customers:** User account, SupportTicket, TicketMessage and Customer 360 relationship view.
- **Revenue:** Product, Plan, prices, Subscription, PaymentIntent, Refund, Invoice and disputes.
- **Growth:** campaigns/promotions, referral/reward, gift and email-delivery records.
- **Platform:** Job, PeriodicJob, ProvisioningOperation, integration state, AuditLog and SecurityEvent.

Core hand-off rule: show related context in another domain, but resolve/edit the canonical record in its owning workspace. Do not create duplicate editable copies.

Critical lifecycle distinctions:
- Published course ≠ indexable page ≠ saleable offer ≠ learner entitlement.
- Individual course purchase ≠ recurring membership subscription ≠ access-request approval.
- Payment success ≠ course/subscription access completion ≠ external community provisioning success.
- Notification read state ≠ operational issue resolved.
- Email delivery ≠ in-app notification.
- Referral discount ≠ referral reward ≠ gift.

## 7. Current mockup review status

- M01/M02 V2: first visual pass exists; shell template selected. Remaining details and Command Centre action semantics need review.
- M24: first holistic navigation board exists; owner review still pending.
- Academy: detailed V1 prototype/spec exists; owner review pending.
- Customers: detailed V1 prototype/spec exists; owner review pending.
- Revenue: detailed V1 prototype/spec/review notes exist; owner review pending.
- Growth: detailed V1 prototype/spec/review notes exist; owner review pending.
- Platform: detailed V1 prototype/spec/review notes exist; owner review pending.
- M50 Holistic Workflow: integrated V1 board covers seven end-to-end journeys and a shared 40-record fictional dataset; owner review pending.
- Global accessibility, keyboard navigation, contrast and authenticated staging parity are not complete.

Do not mark a mockup as approved because it was created or smoke-tested. Record owner feedback and decision status.

## 8. Recommended next steps

1. Continue the unfinished Phase 0 work in `PHASE_0_CURRENT_BASELINE_AUDIT_V1.md`: complete authenticated staging and role-specific verification with authorised test accounts.
2. Reconcile the source-verified route/action/permission inventory in the Phase 0 audit with the live role and object-scope results. Do not treat source registration as live authenticated proof.
3. Reconcile the superuser-only Django Admin target with the workflow-by-workflow legacy cutover rule before changing access.
4. Close the source-contract gaps listed in the readiness document for refunds, subscription cancellation, course coupon redemption, unified purchase events, referral rewards, provider-backed campaign delivery, safe job retries, integration health, audit/policy immutability and privacy/retention.
5. Review and revise the six domain mockups and M50; finish accessibility and authenticated role review.
6. Complete the implementation handoff with parity tests, rollout stages and rollback boundaries.
7. Obtain explicit implementation approval before changing application code.

## 9. Prototype artifact availability

The current conversation includes downloadable HTML prototypes:
- `tradethesis_admin_shell_command_centre_v2.html`
- `tradethesis_admin_six_domain_workspaces_v1.html`
- `tradethesis_admin_academy_workspace_v1.html`
- `tradethesis_admin_customers_workspace_v1.html`
- `tradethesis_admin_revenue_workspace_v1.html`

The written specifications and design decisions are saved in this GitHub branch. The HTML files are standalone conversation artifacts; a portable archive named `tradethesis_admin_redesign_resume_bundle_v5.zip` contains the seven domain/shell prototypes, the M50 holistic walkthrough, domain and holistic preview images, Growth/Platform/Holistic build and test scripts, Revenue smoke tests and the V5 resume README. Retain/download that archive when carrying visual previews into another environment. If an artifact is not available in the next chat, rebuild its next revision from the saved screen-level specification rather than inferring live behaviour.

## 10. Safety and scope checklist for the next chat

- [ ] Start from `admin-desk-redesign-planning`.
- [ ] Read this handoff and the screen specifications.
- [ ] Do not ask again for approved six-domain grouping or selected visual template.
- [ ] Do not assume every proposed route already exists.
- [ ] Do not replace or bypass current business services.
- [ ] Do not expose data across reviewer/finance/Academy/security permission boundaries.
- [ ] Do not silently add new actions or state transitions.
- [ ] Do not change app code, merge, deploy or alter Render settings before explicit approval.
- [ ] Update `MOCKUP_REGISTER.md`, relevant specs and this handoff after each major design pass.


## 11. M50 holistic walkthrough checkpoint — 14 November 2026

- **Prototype:** `tradethesis_admin_holistic_workflow_v1.html`.
- **Specification:** `HOLISTIC_WALKTHROUGH_V1.md`.
- **Review notes:** `HOLISTIC_REVIEW_NOTES_V1.md`.
- **Dataset:** 40 fictional shared records; primary learner Maya Chen (USR-1042), referrer Rohan Patel (USR-1008), access requester Dev Singh (USR-1177).
- **Journeys:** mini-course publication/purchase; membership/community access; campaign/referral acquisition; support access request; billing/refund/dispute; gift invitation/email failure; email delivery/operational evidence.
- **Smoke test:** 159/159 browser checks passed. Desktop shell geometry, all seven journeys, every linked Inspect preview, 40-record register, search/owner filter, mobile drawer and 390px overflow checks passed. No JS/console errors.
- **Important source findings:** CourseOffer activation writes `academy.entitlement_granted` rather than `purchase.completed` and exits before the ordinary membership CouponRedemption block. The course sample is coupon-free; the membership sample carries COHORT20. Referral reward unlock status mismatch remains. A reconcile Job may be Succeeded while its ProvisioningOperation remains Unknown. Member Notification NOT-901 is not staff Command Centre work.
- **Review status:** M50 is draft for owner review. It is a static architecture test only, not implementation approval.


## 12. Owner decision and implementation-readiness checkpoint — 14 November 2026

### Owner decisions completed

- The owner completed 12 decision rounds and approved **60 decisions**.
- The full register is `OWNER_DECISION_REGISTER_V1.md`.
- The recommended migration order, dependencies, known source gaps, exit gates and hard-stop boundary are in `IMPLEMENTATION_READINESS_AND_SEQUENCE_V1.md`.
- Do not reopen these product decisions unless the owner asks or new source evidence demonstrates a material conflict.

### Decisions now fixed

- One unified V2 Admin Desk with the six approved domains in the established order.
- Shared foundations first, followed by phased workflow/domain rollout and a representative staff pilot.
- Department-scoped permissions, multiple department memberships, personal activity workspace, team visibility subject to permissions, assigned departmental and central owners.
- Sensitive actions require permission checks and confirmation; no universal second-person approval. Preserve current action-specific reason constraints.
- Low-risk-only bulk operations; safe retries only where supported and idempotent.
- Financial and provider truth must be evidenced externally; completed financial records remain immutable.
- Academy course approval/revision workflow, dedicated course-coupon redemption and a unified purchase event contract.
- Growth campaign approval, consent/suppression enforcement, automated referral eligibility and payout evidence.
- Platform health, job, provisioning, integration, security and emergency controls are role-gated.
- Customer privacy, export, erasure and retention are controlled and auditable.
- Department owners sign off before a workflow is cut over; do not rank employees.

### Reconciliation and blockers

- **Django Admin access:** decision 9 states the target boundary is superusers only; decision 52 says ordinary staff access is removed workflow by workflow after parity. Treat this as a cutover-policy clarification. Do not change permissions until the exact transition is reconciled against the live role model and actual staff workflows.
- **Refund initiation:** the inspected current manual-refund path records a refund after provider-side processing; it does not initiate a PSP refund. The approved staff refund capability requires a supported provider operation and permission-checked service path before the interface may claim to initiate a refund.
- **Source-contract gaps:** one-time course coupon redemption and `purchase.completed` emission, referral reward status/currency/persistence, campaign stub-vs-provider status, safe job retry service, provider health evidence, AuditLog/PolicyVersion immutability and privacy/retention enforcement remain readiness items for their respective phases.
- **Live verification:** the Phase 0 audit has now rechecked Academy service identity, branch, auto-deploy setting and deployed SHA. The Academy deployment is live and matches the current source HEAD captured in the audit. The public static staging deployment is older than the source HEAD. Authenticated staging role/permission review remains outstanding.

### Recommended immediate next step

Continue Phase 0 from `PHASE_0_CURRENT_BASELINE_AUDIT_V1.md`. The source/deployment baseline and source-level route/action/permission inventory have been refreshed. The remaining hard blocker is authenticated staging review with representative roles and a superuser, followed by a signed-off role/object-scope matrix and workflow parity/rollback checklist. This is still an audit/planning phase, not implementation.

### Scope boundary reaffirmed

No application code, migration, route, API contract, permission, test, Render setting, deployment, merge or rebase has been changed as part of the 60-decision consolidation. Explicit owner implementation approval remains required.


## 13. Phase 0 current baseline audit checkpoint — 14 November 2026

### Audit record

- **Full report:** `PHASE_0_CURRENT_BASELINE_AUDIT_V1.md`.
- **Audit state:** source and Render Academy baseline verified; authenticated staging and role verification remain incomplete.
- **Source HEAD:** `6cdb7b9e78306850902da9b95467e494066baa13` on `my-new-branch`.
- **Planning HEAD when Phase 0 began:** `69e3835eeb36fbe4d708fdbd3441f6c507e1e4a0`; the audit/report commits subsequently advance the planning branch.
- **Academy staging:** `tradethesis-academy-staging` is configured to `my-new-branch`, auto-deploy off, and latest live deployment SHA matches the source HEAD above.
- **Public staging:** static service is configured to `my-new-branch`, auto-deploy off, but its latest live deployment is `c5bdc0fb58be35122a41da3bc646a06c48dc162d` from 7 November 2026; assess separately.
- **Source-only delta:** 15 commits across the Course Builder API, preview template and Trading Path import JSON. No Admin Desk route/view/permission files changed in that delta. See the audit for the commit-by-commit content migration summary and required Builder regression tests.

### Material source findings

- Django Admin remains on the standard active-staff access boundary in the reviewed configuration; a superuser-only gate was not found. Reconcile owner decisions 9 and 52 before any permission change.
- The custom IsRoleAdmin API permission accepts role ADMIN, superuser **or any is_staff user**. It protects ban/unban and staff-approval actions.
- The Growth referral-rewards overview uses LoginRequiredMixin rather than a staff-only permission gate. Do not expose it in staff navigation until reviewed.
- Course review, Builder and SEO paths use the Academy content-admin helper (superuser or role ADMIN). Other operational routes use a mixture of model permissions, reviewer scope and broad staff-only guards.
- Current provider inspection found webhook-based recording of external refund events but no staff-initiated PSP refund operation. The manual Django Admin action records a refund after provider-side processing.
- Current subscription cancellation is immediate only; end-of-period cancellation was not found in the reviewed service.
- The health endpoint only probes the primary database with SELECT 1. It is not provider or full-service health.

### Phase 0 remaining work

- Complete the authenticated role matrix in the audit, including direct-route/API denial and object-level scope checks.
- Map current users, roles, Django Groups/model permissions and staff approval state to the approved departmental model.
- Resolve the Django Admin target/cutover policy.
- Confirm provider-backed refund capability and the intended cancellation contract.
- Run the source-only Academy Builder migration regression checks.
- Add workflow parity tests and rollback triggers before implementation approval.

**Do not restart the 60-decision process. Do not implement.** All work remains documentation-only until explicit implementation authorisation.


## 14. Phase 0 continuation — CI and regression-test evidence

The source/deployment commit `6cdb7b9e78306850902da9b95467e494066baa13` has successful GitHub Actions runs:

- **Verify Django Academy backend**, run [2048](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/43611322315): Python 3.11 and 3.12 jobs both passed; each reports 1,314 passed, 1 skipped, 512 warnings and 178 subtests passed.
- **Academy backend CI**, run [1888](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/43611322349): Python 3.11 and 3.12 backend jobs and the separate Tiptap bundle/DOM compatibility job all passed. The backend jobs each report 1,314 passed, 1 skipped and 178 subtests passed; Tiptap's focused Markdown suite reports 19 passed and 4 subtests passed.

These are isolated CI tests, not live staging role checks. Existing local tests cover course review, support reviewer scope, Customer 360 section permissions, operations timeline permissions/redaction, subscription lifecycle and job/provisioning idempotency. The account `IsRoleAdmin` test covers superuser, role ADMIN and plain user, but not an ordinary `is_staff=True` role=STAFF account; the implementation's predicate does accept any `is_staff` user. The current Growth referral rewards overview remains login-only.

An unauthenticated web retrieval attempt against six staging paths returned no HTTP statuses because the retrieval channel could not access the URLs. Do not infer a route failure or successful access-control response from that attempt.

Full test coverage and the explicit remaining limitations are in `PHASE_0_CURRENT_BASELINE_AUDIT_V1.md`.

### Remaining Phase 0 gate

- Obtain live authenticated staging results for the representative role matrix and superuser.
- Verify direct route/API denial and object-level scope using the actual deployed staff/group setup.
- Reconcile the Django Admin superuser-only target with workflow-by-workflow legacy cutover.
- Resolve the broad `IsRoleAdmin` boundary and the login-only Growth referral route before staff navigation/migration.
- Keep refund initiation and end-of-period cancellation classified as unsupported until a verified service contract exists.

**CI is green; Phase 0 is still incomplete. Implementation remains NOT AUTHORISED.**


## 15. Phase 0 continuation checkpoint — 14 November 2026 16:43 UTC

This checkpoint supersedes the older source SHA, Academy deployment SHA and 15-commit source-delta references in Sections 13–14 above. It does not supersede or reopen any of the 60 owner decisions.

### Current Git and deployment baseline

- Source branch `my-new-branch` is at `8832ecf9cc979747dc2715a39ecfeb7a292e55ee` (`Migrate Trading Path key takeaways into notebook prompts`, 2026-11-14 16:39:00 UTC).
- Planning branch was at `0f6e44a34c56cdccc17a3f717ee613b8b47081f1` before this report/handoff refresh. At that point it was 86 commits ahead and 18 behind source, merge base `251260448c480ec5fbfec4f1966d9017fa0854ff`. The documentation refresh adds planning-only commits; do not merge or rebase automatically.
- The 18 source-only commits modify exactly three files: `backend/apps/academy/course_builder_api.py`, `backend/apps/academy/course_builder_preview.html` and `backend/apps/academy/course_builder_trading_path_import.json`. No Admin Desk route/view/permission/test file changed in this source-only delta.
- Academy staging (`tradethesis-academy-staging`) is live on the exact current source SHA. Latest deployment `dep-dbs8tku7bikc73euh990` finished at 16:41:58 UTC on 14 November 2026. Auto-deploy remains disabled; the deployment was API-triggered. No Render setting was changed.
- Public static staging remains live on `c5bdc0fb58be35122a41da3bc646a06c48dc162d` from 7 November 2026 09:01:26 UTC. This remains a separate deployment-parity item.

### New Academy Builder migration in source

The newest three source commits move Trading Path **Key takeaways** into the lesson notebook prompts **Pause**, **Interpret** and **Apply**. The source API now includes notebook data in the migration payload; the Builder migration copies exactly three non-empty labelled prompts to the matching draft lesson, retains existing target notebook metadata/title where present, removes the Key takeaways section from the lesson body, and reports migration counts. The user-facing toast says Q&A is preserved and nothing is published.

Add explicit regression cases before relying on this transformation: repeated Builder loads must be idempotent; matching must be limited to intended Trading Path draft lessons; existing Q&A and notebook metadata/title must remain intact; only the Key takeaways section must be removed while surrounding content survives; published Course records must remain unchanged. The three changed source files contain no new dedicated test file for this migration.

A static scan of the current import data found five modules and 48 lessons; 27 contain exactly three non-empty notebook prompts in the order Pause, Interpret, Apply, and 21 have no populated prompt array. None of the source lesson bodies has a Markdown Key takeaways heading, so the actual removal must be verified against saved target drafts. The cleanup helper stops at the next Markdown heading regardless of heading level; nested headings inside a Key takeaways section may be left behind. Add a nested-heading fixture and inspect the real target-draft structure before sign-off.

### Latest CI evidence

GitHub Actions **Academy backend CI**, run [1891](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/43616758224), for the deployed SHA completed successfully:
- Python 3.11: 1,314 passed, 1 skipped, 178 subtests passed.
- Python 3.12: 1,314 passed, 1 skipped, 178 subtests passed.
- Tiptap bundle and DOM compatibility job: success. This does not make Tiptap the supported/default production Builder.

CI is isolated test evidence. It does not establish authenticated staging permissions or live record/object visibility.

### Remaining Phase 0 gate

- Authenticated staging checks for learner, ordinary staff, Support reviewer, Academy editor/approver, Revenue staff, Growth staff, Platform operator and superuser remain unperformed. No password or secret should be pasted into project docs or chat.
- For every authorised persona, test both allowed and denied direct routes/APIs and object-level visibility; record actual status codes and visible UI states.
- Map actual user roles, Django Groups, model permissions and staff-approval state to the approved multiple-department access model.
- Reconcile Django Admin superuser-only target against workflow-by-workflow cutover; resolve the broad `IsRoleAdmin` API boundary and login-only Growth referral overview before staff navigation migration.
- Keep PSP refund initiation and end-of-period cancellation unsupported until a verified service contract exists.
- Complete the Builder migration-specific idempotence/content-preservation tests and a staging draft-only verification.

**Phase 0 remains incomplete. Implementation remains NOT AUTHORISED.** No application code, test, permission, migration, deployment, Render setting, merge or rebase was changed in this continuation. Only the planning audit and handoff documents were updated.

## 16. First authenticated staging evidence — non-staff learner

On 14 November 2026 at 16:59:25 UTC, the operator ran the browser-console audit on `tradethesis-academy-staging.onrender.com` using a session labelled `Non-staff learner`.

Observed GET results from the supplied transcript:
- `/health/`: 200.
- 403 Forbidden: `/staff/admin-desk/`, `/staff/admin-desk/operations/`, `/staff/admin-desk/accounts/`, `/staff/admin-desk/support/tickets/`, `/staff/admin-desk/courses/review/`, `/staff/admin-desk/seo/`, `/staff/course-builder/`, `/staff/admin-desk/finance/`, `/staff/admin-desk/subscriptions/`, `/staff/admin-desk/business/`, `/api/admin/staff-approvals/` and `/api/analytics/overview/`.

This is encouraging direct-route denial evidence for the 12 reported staff/admin endpoints. The health 200 is expected because `/health/` is a public database readiness probe. Record persona as operator-labelled; the report did not include server-verified role metadata. The pasted JSON was truncated, so the Growth referral rewards, notifications, Django Admin, gift and disputes results are unknown, not passed.

### Consolidated access audit workflow

Use one read-only browser-console batch script for all GET route probes and any detail links discovered from visible list pages. Run the same script in each distinct authorised account session (learner, ordinary approved staff, Support reviewer, Academy editor/approver, Revenue, Growth, Platform and superuser). Browser session cookies belong to one signed-in account; one browser session cannot truthfully impersonate all role personas. Do not paste passwords, cookies or API tokens into chat.

For object scope, collect fixture IDs visible to the superuser or fixture owner, then probe those exact detail URLs in the other role sessions. The script should never guess IDs. Keep all action/POST verification separate and use designated disposable fixtures only after an explicit test plan.

**Phase 0 remains incomplete. Implementation remains NOT AUTHORISED.**