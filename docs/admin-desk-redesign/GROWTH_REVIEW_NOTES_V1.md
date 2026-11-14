# Growth Workspace — V1 Review Notes

**Date:** 14 November 2026  
**Status:** Draft for owner review; no implementation approval  
**Prototype:** `tradethesis_admin_growth_workspace_v1.html`

## Scope

- M18 Growth Overview.
- M41 Analytics & Attribution.
- M34 Campaigns & Audiences.
- M35 Journeys & Automation.
- M36 Promotions & Coupons.
- M37 Referrals & Rewards.
- M38 Gifts.
- M39 Email Delivery.
- M40 Advanced Growth (Affiliates, Experiments, Announcements and Channels).

## Source-derived boundaries preserved

- Analytics API is admin-only (`IsAdminUser`) and read-only.
- The response key/function labelled “signups” currently counts `purchase.completed` Events; prototype calls it Purchase Events and flags the mismatch.
- Promotion report currently references `Sum` without importing it in the inspected report; promotion aggregation is flagged as unverified.
- Email report does not include every supported Delivery state. CampaignMetrics bounce/complaint counters are not updated by the inspected Resend webhook.
- Campaign schedule freezes CampaignRecipient membership. Campaign and TemplateVersion are separate records; changing a template later does not rewrite its historical version.
- G2 campaign sweep creates Delivery rows using provider=stub and marks them SENT immediately. That is not live provider sending or delivery. Campaign extra Telegram/in-product actions are staged, not wired into the send sweep.
- AutomationRule/AutomationRun have event idempotency, delay and eligibility re-check semantics; runs are read-only. Rule editing remains in Django Admin.
- Coupon validation includes date window, plan tiers, campaign-scoped first-touch attribution, global/per-user usage caps, and referral stacking. CouponRedemption is created after successful activation and is read-only.
- Referral referee discount, referrer reward and optional referee bonus are separate. ReferralReward is a currency-bearing bucket with a triggering Subscription and delay.
- Current reward unlock service has a PaymentIntent status mismatch: it searches for refunded/canceled while PaymentIntent model choices are pending/success/failed. Missing triggering subscription leaves a reward pending.
- UserRewardBalance sums cents across currencies; prototype displays currency buckets separately and does not show one combined balance.
- Optional referee bonus credit helper logs only and does not persist a wallet/ledger balance; prototype shows it disabled/unavailable.
- The custom Referral Rewards Overview route currently uses LoginRequiredMixin rather than staff-only authorization; it is not linked as an Admin Desk screen.
- Gift creation can succeed while invitation email fails. GiftInvite and resulting Revenue Subscription are different records. Modern token flow and legacy gift_code flow remain separate. No staff resend UI was verified.
- MarketingPreference defaults opt-out. Global suppression (unsubscribe/bounce/complaint) overrides opt-in. Transactional email is separate from marketing eligibility.
- G1 Delivery and legacy transactional EmailLog are separate ledgers; Resend webhook updates Delivery only.
- TemplateVersion is an immutable snapshot referenced by campaigns/automations.
- Affiliate commission “Paid” is an internal state; no actual payout transfer was verified.
- Telegram marketing and in-product CampaignAction are distinct from Telegram membership/provisioning; their campaign actions are staged and delivery is stub/not wired.

## Design choices introduced for review

- A single Growth Overview routes to work rather than being a new source of KPIs.
- Analytics is presented as a read-only reporting and attribution workspace with visible source definitions and quality caveats.
- Campaigns/Audiences and event-triggered Journeys are separate destinations.
- Promotions and Referrals & Rewards are distinct to preserve coupon vs referral discount vs reward semantics.
- Gifts have a dedicated register; the row distinguishes invite state from email evidence and resulting Subscription.
- Email Delivery is split into G1 Delivery, transactional EmailLog, Consent & Suppression and Templates.
- Affiliates, Experiments and Announcements/Channels remain in Advanced Growth during staged migration.
- All preview actions are local-only; no model, job, provider, ledger or user record is changed.

## Browser validation

- All eight Growth destinations open.
- Campaign draft filter/search and campaign detail preview.
- Active coupon filter and coupon detail preview.
- Completed referral filter and settings preview.
- Pending gift filter and gift creation preview.
- Delivery bounced filter.
- Transactional EmailLog, consent/suppression and template tabs.
- Affiliate, experiment and announcement advanced tabs.
- Preview actions provide local-only feedback.
- Mobile drawer opens, navigates and closes.
- 390px viewport has no horizontal document overflow after CSS sizing correction.
- No JavaScript or console errors in exercised flows.

## Not tested / not claimed

- Authenticated live staging UI and all staff roles.
- Live campaign scheduling/send or real provider delivery.
- Campaign bounce/complaint metric reconciliation.
- Coupon/Referral/Gift/Reward writes.
- Reward unlock correctness or currency conversion.
- Actual referee bonus credit persistence.
- Staff-only authorization remediation for Referral Rewards Overview.
- Resend/repair actions or real provider webhook receipt.
- Affiliate payout execution.
- Keyboard-only, screen-reader, contrast and full responsive/accessibility audit.

## Review prompts

1. Does the Growth Overview surface the right work without becoming an analytics dashboard?
2. Is Analytics & Attribution a separate destination or should it be nested under Overview?
3. Are Campaigns and Journeys distinct in a useful way?
4. Are coupon discounts, referee discounts and referrer reward buckets clearly separated?
5. Should Gifts remain separate from Customers, or should Customer 360 surface a gift lifecycle panel?
6. Does the Email Delivery split prevent confusion between marketing Delivery and transactional EmailLog?
7. Is the Advanced Growth boundary appropriate?
8. Which source defects must be fixed before a first production migration?

## Next step

Revise Growth from owner feedback. Then design Platform, including durable jobs, scheduler health, webhook state, integration/provisioning operations, audit/security and safe operational actions. After Platform, run a holistic walkthrough of the same fictional learner/campaign/referral/coupon/payment/subscription/gift/ticket records through all six top-level domains.
