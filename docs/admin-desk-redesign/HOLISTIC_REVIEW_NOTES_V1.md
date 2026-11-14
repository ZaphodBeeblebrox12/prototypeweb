# Holistic Workflow Walkthrough — V1 Review Notes

**Date:** 14 November 2026  
**Status:** Draft for owner review; no implementation approval  
**Prototype:** `tradethesis_admin_holistic_workflow_v1.html`  
**Specification:** `HOLISTIC_WALKTHROUGH_V1.md`

## What the board tests

One fictional primary learner (Maya Chen / USR-1042), two secondary actors (Rohan Patel / USR-1008 and Dev Singh / USR-1177), seven complete workflows and 40 cross-linked sample records.

Seven journeys:
1. Publish and sell a mini-course.
2. Membership purchase and community access.
3. Campaign and referral-driven acquisition.
4. Support access request and reviewer approval.
5. Billing issue, refund and dispute.
6. Gift invitation and email failure.
7. Email delivery and operational evidence.

The board includes a shared record register, canonical owner label, sample status, linked record IDs and local-only inspect previews.

## Key cross-domain rules validated

- A record has one canonical owner; other domains link to it.
- Course publication, discoverability, saleability, entitlement, personalized-video work and lesson progress are different states.
- Course purchase and membership purchase use different fulfilment paths.
- Membership subscription, Academy PlanCourseAccess and community provisioning are distinct.
- A failed personalized-video Job does not revoke a verified course entitlement.
- A successful reconcile Job does not prove external membership; ProvisioningOperation may remain Unknown.
- Access-request approval grants a hidden Plan and enqueues reconciliation transactionally; it is not a purchase.
- Coupon, referral discount, referrer reward and gift are separate concepts.
- Course PaymentIntent coupon snapshot and CouponRedemption need separate analysis.
- First-touch SignupAttribution and last-touch marketing Delivery attribution are separate.
- Stub Campaign Delivery Sent is not real provider delivery.
- PaymentIntent, Refund and Dispute are separate; funds withdrawn is not final dispute loss.
- GiftInvite creation, email send result, successful recipient claim and resulting Subscription are separate.
- Member Notification is not a staff Command Centre work item.
- Growth G1 Delivery and transactional EmailLog are separate; Resend updates Delivery only.
- Business Event, AuditLog, SecurityEvent, WebhookEvent and provisioning evidence retain separate source identity.

## New source-level gaps surfaced

1. CourseOffer PaymentIntent checkout may snapshot a coupon code/amount, but the CourseOffer branch exits through `activate_course_payment` before the ordinary subscription code's `redeem_coupon` / CouponRedemption block. The course example therefore deliberately does not use a coupon. Decide whether course coupons are disallowed or require a course-redemption path.
2. `activate_course_payment` records `academy.entitlement_granted` (or `academy.entitlement_simulated`) but does not write `purchase.completed` in the inspected function. The ordinary membership activation path does. Growth purchase analytics/attribution should not assume course purchases are currently counted by that report.
3. Referral reward unlock checks PaymentIntent states that are not present in model choices; currency aggregation and referee bonus persistence gaps remain.
4. Campaign provider is stub and CampaignMetrics does not yet prove provider delivery; Resend updates Delivery but no CampaignMetrics reconciliation was verified.
5. An access approval's reconciliation Job can complete its handler while external ProvisioningOperation remains Unknown. This is not contradictory: worker execution is not external membership.
6. NOT-901 is a member Notification, not a staff attention/Command Centre item.

## Browser smoke-test record

- **159/159 checks passed.**
- Desktop shell: 250px sidebar, main starts after sidebar, no accidental content-width collapse.
- Seven journey pages open; every step with a real linked record opens and closes its sample detail modal.
- 40 sample records render in the register.
- Search PI-7001 returns a matching row and detail preview.
- Revenue owner filter returns a subset and retains PI-7001.
- Mobile drawer opens, navigates and closes.
- Every destination tested at 390px with no horizontal document overflow.
- No JavaScript page errors or console errors.

The HTML and scripts use local fictional data only. Tests do not exercise authenticated staging, live provider/API operations or server-side permission enforcement.

## Decisions requested

1. Confirm whether course coupon redemptions should be allowed and, if so, what canonical redemption record path is required.
2. Confirm how one-time course purchases should feed Growth purchase analytics/attribution.
3. Confirm which seven journeys are release-critical and should become acceptance tests.
4. Confirm which sample Customer 360 context panels are genuinely valuable versus distracting/duplicative.
5. Confirm where Command Centre should show a staff work item and where a member Notification should remain a separate record.
6. Decide which source gaps are hard implementation blockers.

## Next step

Collect owner feedback on the six domains and this integrated board. Record decisions in DECISION_LOG.md, revise the relevant screen specification(s), and then prepare an implementation readiness matrix. Do not begin app-code changes until the owner explicitly approves the implementation handoff.
