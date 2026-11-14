# Admin Desk V2 — Implementation Authorisation Addendum

**Date:** 15 November 2026  
**Owner direction:** Proceed with implementation; report back when the integrated implementation is ready.  
**Planning branch:** `admin-desk-redesign-planning`  
**Implementation branch:** `admin-desk-v2-implementation`  
**Source baseline:** `my-new-branch` at `294c173e8dd084c31595ac2d5aeab93d64f31481`

## 1. Authorisation and boundaries

The owner has directed the work to continue from planning into implementation. This supersedes the earlier planning-only status for the purpose of developing the Admin Desk V2 application changes on the dedicated implementation branch.

This is **not** approval to deploy to production, change the public static site, alter Render service settings, or perform the global Django Admin cutover. Academy staging remains the eventual integration/verification target, but no deployment is part of this authorisation.

The agreed six top-level destinations remain in their approved order: Command Centre, Academy, Customers, Revenue, Growth and Platform.

## 2. Test timing

The owner requested that the final test campaign be run after the final implementation is ready. The checklist is recorded in `ADMIN_DESK_FINAL_IMPLEMENTATION_TEST_PLAN.md`.

During implementation:
- Do not start another incremental manual/browser/UAT acceptance cycle.
- Add and maintain automated regression coverage with the code.
- Run the required engineering CI/build gates before integration/merge.
- After the complete implementation is deployed to Academy staging, run one consolidated evidence-backed campaign against that final build, covering the full role matrix, direct routes/APIs, object scope, domain workflows, responsive/accessibility and end-to-end scenarios.
- Prior successful staging tests remain baseline evidence, not final acceptance.

## 3. Initial implementation baseline

The first implementation branch was created from the verified Academy source branch, not from this planning branch. The first slice includes:
- Shared six-domain Admin Desk sidebar with server-permission-aware navigation.
- Desktop collapse and mobile drawer behavior.
- Shared base-template integration for Admin Desk and Course Builder paths while preserving the existing sitewide header.
- Action-first Command Centre signals based on existing operational data and canonical destination links.
- A server-rendered Customers overview using reviewer-scoped support records and independently permission-gated learner totals.

No application deployment or production change has been made.

## 4. Release/cutover guardrails

- Keep legacy Course Builder as the default. Tiptap remains non-default until its own authoring parity and integration gate is completed.
- Keep Django Admin workflows available until each corresponding replacement workflow is implemented and verified. Reconcile the target superuser-only policy with the staged workflow cutover decision before changing access.
- Preserve canonical domain ownership, existing action services, action-specific reason requirements, provider-truth semantics and server-side permission enforcement.
- Do not invent task ownership, provider success, alert states or customer data where the current source has no reliable signal.
- No production deployment without a separate explicit owner approval.

## 5. Implementation handoff

- **Implementation branch:** `admin-desk-v2-implementation`
- **Draft pull request:** [#68 — TradeThesis Admin Desk V2 unified workspace](https://github.com/ZaphodBeeblebrox12/prototypeweb/pull/68)
- **Latest implementation commit recorded:** `6fa58d256b359ce0eeb4a21ac272fc58b213c26b`
- **Status at this update:** all six domain overview routes, shared workspace navigation, Command Centre action queue, personal My Work/notifications and permission-aware reporting views have been added. The existing detailed account, support, course-review, finance, subscription and operations workflows remain the canonical action pages.
- **Automated CI:** running against the latest implementation head. Do not mark implementation ready until the latest CI matrix is green and any failures are resolved.
- **Manual/browser/UAT acceptance:** deliberately not started. Keep the single consolidated campaign deferred until implementation is final and a final Academy staging deployment is separately approved.

