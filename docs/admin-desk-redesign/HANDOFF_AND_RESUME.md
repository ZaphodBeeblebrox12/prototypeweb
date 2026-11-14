# TradeThesis Admin Desk Redesign — Handoff & Resume

**Last updated:** 14 November 2026  
**Repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Planning branch:** `admin-desk-redesign-planning`  
**Source/code baseline:** `my-new-branch`  
**Current phase:** Information architecture, workflow design and clickable mockups.  
**Implementation status:** Not authorised. Do not modify app code or deploy.

## 1. Resume instruction for a new chat

Start a new chat and say:

> Resume the TradeThesis Admin Desk redesign. Read `docs/admin-desk-redesign/HANDOFF_AND_RESUME.md` on branch `admin-desk-redesign-planning`, then inspect the latest Decision Log, Mockup Register, Domain Workspace Blueprint and screen specifications. Continue from the next unreviewed design task. Keep all work on the planning branch and do not implement or deploy until I explicitly approve.

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
- **Current comparison (14 November 2026):** the planning branch is 2 commits behind `my-new-branch`; all 14 files changed on the planning branch are exclusively under `docs/admin-desk-redesign/`. The ahead count continues to increase as each planning document is updated, so it is not a stable handoff value. The source branch has advanced independently since the planning branch was created.
- Do not auto-merge or rebase the planning branch. Before implementation, inspect the two source-branch-only commits, re-verify the deployed source/route state, and reconcile any relevant changes deliberately.
- All changes so far are planning documentation. The HTML prototypes are standalone review artifacts supplied in conversation.
- No application code, migration, tests, settings, hosting configuration or Render deployment has been changed by this redesign work.
- Before any implementation, recheck the current branch HEAD, Render deployment SHA, auto-deploy setting, current authenticated staging pages and role-specific access. The old source baseline is not a substitute for a fresh implementation audit.

## 4. Documents to read first

Read these in order:

1. `DECISION_LOG.md` — approved decisions and remaining owner choices.
2. `REDESIGN_PLAN.md` — overall process, phases and guardrails.
3. `INFORMATION_ARCHITECTURE_V1.md` — approved six-domain model and proposed child navigation.
4. `DOMAIN_WORKSPACE_BLUEPRINT_V1.md` — responsibilities, workspaces, records and end-to-end journeys.
5. `CROSS_DOMAIN_CONNECTIONS_V1.md` — canonical ownership and hand-off contract.
6. `ROUTE_TO_WORKSPACE_MAP_V1.md` — current route, API and Django Admin boundaries.
7. `MOCKUP_REGISTER.md` — all mockups and their review state.

Screen-level specifications:
- `ACADEMY_WORKSPACE_SPEC_V1.md`
- `CUSTOMERS_WORKSPACE_SPEC_V1.md`
- `REVENUE_WORKSPACE_SPEC_V1.md`

Review notes:
- `M01_M02_REVIEW_NOTES.md`
- `CUSTOMERS_REVIEW_NOTES_V1.md`
- `REVENUE_REVIEW_NOTES_V1.md`

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
- Growth: not yet designed at screen level.
- Platform: not yet designed at screen level.
- Global accessibility, keyboard navigation, contrast and authenticated staging parity are not complete.

Do not mark a mockup as approved because it was created or smoke-tested. Record owner feedback and decision status.

## 8. Recommended next steps

1. Review the Customers prototype/specification with the owner; record requested changes and decisions.
2. Revise M10/M11/M12/M13/M27/M28 where necessary.
3. Review the Revenue prototype/specification; revise the action hierarchy and record relationships from owner feedback.
4. Design Growth next, then Platform, using the same fictional learner/payment/course/subscription/ticket records.
5. Walk through cross-domain journeys again using the same stable fictional record set.
6. Complete role/permission matrix and Django Admin migration inventory, including the PaymentIntent manual full-refund and Plan/price configuration actions.
7. Perform authenticated staging visual/role audit before producing an implementation handoff.
8. Obtain explicit implementation approval before changing application code.

## 9. Prototype artifact availability

The current conversation includes downloadable HTML prototypes:
- `tradethesis_admin_shell_command_centre_v2.html`
- `tradethesis_admin_six_domain_workspaces_v1.html`
- `tradethesis_admin_academy_workspace_v1.html`
- `tradethesis_admin_customers_workspace_v1.html`
- `tradethesis_admin_revenue_workspace_v1.html`

The written specifications and design decisions are saved in this GitHub branch. The HTML files are standalone conversation artifacts; a portable archive named `tradethesis_admin_redesign_resume_bundle_v2.zip` was also created in the design review conversation with the four current prototypes and PNG previews. Retain/download that archive when carrying visual previews into another environment. If an artifact is not available in the next chat, rebuild its next revision from the saved screen-level specification rather than inferring live behaviour.

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
