# Revenue Workspace — V1 Review Notes

**Date:** 14 November 2026  
**Status:** Draft for owner review; no implementation approval  
**Prototype:** tradethesis_admin_revenue_workspace_v1.html

## Scope

- M14 Revenue Overview.
- M29 Payments & Refunds.
- M30 Subscriptions.
- M31 Plans & Pricing.
- M32 Invoices.
- M33 Disputes.
- M15 Business & Finance.

## Source-derived boundaries preserved

- Admin Desk payment and invoice registers are read-only. PaymentIntent status and historical financial snapshots are provider/service-owned.
- Refund is a unified append-only ledger. Partial refund leaves access unchanged; full refund cancels the affected subscription or revokes a course entitlement through the current policy.
- PaymentIntent Django Admin has a full manual refund recording action, but it is to be used after the refund is already processed in the provider dashboard. The current staff finance page does not expose it; prototype does not invent it.
- PaymentIntent simulator success is not cash collected.
- Subscriptions are access records distinct from payments and CourseEntitlements.
- Existing staff grant/extend/cancel flows are permission-gated, reasoned and audited. Grant requires active learner, active hidden non-trial plan, 1–365 days and reason; extend is 1–365 days; cancel is active-only and queues reconciliation.
- Plan and base/geo pricing configuration remains Django Admin today; M31 is proposed.
- Geo price resolution order is country → region → global base; geo price is override-only; one active base price per Plan+interval.
- Invoice snapshots are immutable and only have view/print behaviour in Admin Desk.
- Disputes are a separate staff workflow. Funds withdrawn does not mean loss; the app's “submit” action only records external submission details and does not upload to provider.
- Confirmed Lost/Accepted uses the exactly-once chargeback access policy; Won keeps access; opening/funds-withdrawn does not revoke access.
- Business tax currently uses one fixed percentage, disabled by default, with explicit accountant confirmation before first enabling; not a jurisdiction-aware GST engine.
- Configuration present and end-to-end tested are separate readiness states.

## Design decisions introduced for review

- A single Revenue Overview with action-first exceptions and secondary financial context.
- Payments and Refunds share a workspace but maintain separate PaymentIntent and Refund records.
- Payment detail shows immutable transaction facts and links to Customer 360, Academy access, invoice and dispute.
- Subscriptions have a distinct workspace with audited grant/extend/cancel affordances and explicit permissions/reason rules.
- Plans & Pricing is proposed as a unified catalogue, but the editing boundary remains Django Admin until migration parity.
- Invoices are a register plus printable detail.
- Disputes are moved into Revenue navigation while preserving the current case app and service. The UI explicitly distinguishes provider funds withdrawal from a final outcome and labels external submission recording.
- Business & Finance has seller/invoice fields and tax confirmation, but no live save or readiness checks.

## Browser validation

- All six Revenue destinations visible through navigation.
- Payment search/filter and payment detail.
- Subscription search/filter and inspection modal.
- Hidden-plan + plan text filter.
- Invoice register to printable invoice detail.
- Dispute filter and detail.
- External evidence submission reference preview.
- Tax enable reveals accountant confirmation.
- Mobile drawer opens and closes after navigation.
- 390px width has no horizontal overflow.
- No page errors or console errors during exercised interactions.

## Not tested / not claimed

- Current authenticated staging route/role parity.
- Permission matrix for all finance, subscription, plans and dispute roles.
- Real payment/refund/provider actions or webhooks.
- Actual PSP dispute evidence upload.
- Tax/legal/compliance readiness.
- Accessibility, keyboard-only, screen-reader and contrast certification.
- Production query performance and currency reporting definitions.

## Review prompts

1. Is the Revenue landing page's attention-first hierarchy right?
2. Does the payment register expose the right transaction facts without looking editable?
3. Does the refund ledger and Advanced Administration note make the manual full-refund boundary clear?
4. Are subscriptions separate enough from payments and plan configuration?
5. Does the Plans & Pricing workspace show enough product/geo logic while preserving the current Django Admin boundary?
6. Does the dispute detail make the funds-withdrawn and final chargeback distinctions unmistakable?
7. Does the invoice page provide the correct snapshot/print experience?
8. Is the tax and business settings warning clear?
9. Which Revenue screen should receive a higher-fidelity pass before moving to Growth?

## Next step

Revise Revenue from owner feedback. Then design Growth, keeping the same fictional learner/payment/course/subscription links and testing referral discount, reward, gift and email delivery relationships without creating duplicate commerce records.
