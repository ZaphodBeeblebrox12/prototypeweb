# TradeThesis Admin Desk — Growth Workspace Specification V1

**Status:** First screen-level design proposal; owner review pending  
**Date:** 14 November 2026  
**Planning branch:** `admin-desk-redesign-planning`  
**Source baseline:** `my-new-branch`  
**Visual template:** Approved V2 forest-green / warm-ivory shell with restrained terracotta and sage, editorial serif headings and compact sans-serif controls.  
**Implementation status:** Planning and static mockup only. No application code, routes, permissions, APIs, database records or deployment settings have been changed.

## 1. Scope and design intent

Growth owns acquisition, conversion assistance, referral/reward accounting, campaigns, lifecycle messaging, gift invitations and marketing communication evidence. It should connect the same canonical learner, course, payment and subscription records used by Customers, Academy and Revenue, not create parallel versions of those records.

The first screen-level pass contains eight workspace destinations:

1. **M18 — Growth Overview:** action-first work summary, capability status and cross-domain hand-offs.
2. **M41 — Analytics & Attribution:** read-only reports, first-touch and last-touch provenance, metric definitions and data-quality flags.
3. **M34 — Campaigns & Audiences:** frozen campaign audience, immutable template version, recipient snapshot and send state.
4. **M35 — Journeys & Automation:** event-triggered automation rules and durable run history.
5. **M36 — Promotions & Coupons:** coupon configuration view, checkout eligibility and immutable redemption provenance.
6. **M37 — Referrals & Rewards:** referral relationships, referee discount, referrer reward buckets and reward ledger.
7. **M38 — Gifts:** token-based gift invites, legacy gift-code distinction and resulting subscription.
8. **M39 — Email Delivery:** Growth Delivery ledger, transactional EmailLog, consent/suppression, templates and versions.
9. **M40 — Advanced Growth:** affiliates/commissions, experiments, in-product announcements and additional channels.

The HTML has eight navigation entries under Growth because Analytics is a destination and the final Advanced Growth view groups Affiliates, Experiments and Announcements/Channels. M18 is the Growth landing screen; M34–M40 are subworkspace mockup IDs.

All names, emails, campaign names, invite IDs, coupon codes, referral records, amounts, metrics, dates and delivery states in the prototype are fictional illustrative data. The prototype makes no live API calls and performs no actual campaigns, gift sends, email deliveries, coupon changes, reward credits or affiliate settlement actions.

## 2. Source-verified Growth model and system boundaries

### 2.1 Canonical record ownership

Growth records:
- Campaign and Audience.
- CampaignRecipient and CampaignMetrics.
- AutomationRule and AutomationRun.
- Coupon and CouponRedemption.
- ReferralCode and Referral.
- ReferralSettings, ReferralReward and ReferralRewardLedger.
- GiftInvite and PendingGiftClaim; gift subscription itself is owned by Subscriptions/Revenue.
- SignupAttribution.
- Email Template, TemplateVersion, VariableSpec, Delivery, Suppression and MarketingPreference.
- Affiliate, AffiliateAttribution, AffiliateCommission.
- Experiment, ExperimentVariant, ExperimentAssignment and ExperimentConversion.
- Announcement, AnnouncementExposure, Channel, CampaignAction and TelegramMarketingDelivery.

Cross-domain canonical owners:
- **Customers** owns User identity/account and the Customer 360 relationship view.
- **Revenue** owns PaymentIntent, Subscription, Plan, prices, refund and invoice records. Growth links to them.
- **Academy** owns Course and CourseOffer; Growth may report campaign/referral context but must not edit curriculum or course entitlement.
- **Platform** owns durable jobs, scheduler, provider connections, webhook health and technical reconciliation.
- **Growth** owns marketing/referral/reward intent and attribution, not payment capture or entitlement provisioning.

The Growth navigation may show links to the canonical Revenue payment or subscription, Customers learner record, Academy course/offer or Platform job, but it must never duplicate financial, subscription or account actions.

### 2.2 Attribution semantics

Two different attribution concepts exist and must stay separately labelled.

**First-touch signup attribution — SignupAttribution**
- One record per user.
- Captures UTM source, medium, campaign, term, content and optional referring Campaign.
- Capture is idempotent; first touch wins and existing attribution is preserved.
- Coupon campaign scoping uses this authoritative first-touch referring campaign rather than a client-supplied campaign ID.

**Last-touch purchase credit — email Delivery**
- The attribution service searches for the most recent marketing Delivery sent to the user before the purchase.
- It currently considers Delivery state SENT and sent_at at/before the purchase time.
- CampaignRecipient or AutomationRun foreign keys identify the originating campaign or automation.
- This is an attribution rule, not proof that the message was read or that it caused the purchase.

Affiliate attribution is a separate first-affiliate-wins relationship. It does not replace UTM SignupAttribution.

### 2.3 Analytics report and quality caveats

Current API:
- `GET /api/analytics/overview/`
- The view uses DRF `IsAdminUser`.
- Response keys are `signups`, `email`, `campaigns`, `promotions`, `referrals`.

The inspected source has several material limitations:

1. The response key/function `signups` calls `signup_analytics()`, but that function counts `purchase.completed` Events and returns purchases-per-day and total-purchases. It is not a signup count. The new UI labels the supported concept as Purchase Events and flags the API key/function mismatch for correction; it must not present the current figure as new user signups.
2. `promotion_performance()` calls `Sum("discount_cents")` but the inspected `report.py` imports `Count` only. Promotion aggregation is not verified until that source defect is corrected and tested.
3. `email_performance()` returns counts for sent, failed, bounced, complained and suppressed Delivery states; it does not include a delivered or delayed count even though the Delivery model and Resend webhook support those states.
4. `campaign_performance()` reads cached CampaignMetrics. The campaign send sweep updates sent/failed/suppressed counts; the inspected Resend webhook updates Delivery state but does not update CampaignMetrics bounced/complained. Those two counters must not be presented as authoritative without reconciliation.
5. `referral_performance()` returns global counts for completed referrals, pending rewards and credited rewards. The inspected implementation does not provide date or currency segmentation.
6. Purchase event payload amounts are in minor units and the report returns raw aggregates. The Growth dashboard must not add INR, USD and EUR values together without a documented conversion source, rate and timestamp.

The redesigned Analytics page is read-only and should put time window, source, definition, currency and caveat next to every KPI. Invalid/unverified metrics should be visibly marked as such, not hidden in a tooltip.

### 2.4 Campaigns and Audiences

Current models are in Campaigns:
- **Audience:** name, description, structured JSON rules evaluated against User. `members()` applies those rules to the User model.
- **Campaign:** name, immutable TemplateVersion foreign key, Audience foreign key, state, scheduled_at, subject_override and snapshot_at.
- Campaign states: Draft, Scheduled, Sending, Paused, Done.
- **CampaignRecipient:** one row per (Campaign, User), stores email, status and linked Delivery. Unique campaign+user constraint is the recipient idempotency guard.
- Recipient states: Queued, Sending, Sent, Failed, Suppressed, Skipped.
- **CampaignMetrics:** cached total/sent/failed/bounced/complained/suppressed counts.

Scheduling:
- `schedule_campaign` only accepts Draft.
- It evaluates the Audience and materializes CampaignRecipient rows.
- Marketing eligibility (opt-in plus no global suppression) is checked at snapshot time; ineligible rows are marked Skipped.
- Membership is frozen at schedule time; later audience changes do not rewrite the snapshot.
- Scheduling stores snapshot_at/scheduled_at and changes state to Scheduled.
- A retry of scheduling uses existing unique rows and ignores conflicts.

Execution caveat:
- `campaign_send_sweep` claims queued recipients in batches and creates an idempotent Delivery linked to CampaignRecipient.
- In the inspected code, the G2 send provider is a stub. The new Delivery is marked SENT immediately with provider=stub; this is not a real provider send/acceptance/delivery.
- Therefore Campaign Done/Sent counters in a sample screen are not evidence of external delivery.
- The inspected CampaignAdmin allows Schedule (freeze audience) and Send a batch now actions.
- Telegram and in-product CampaignAction records are configurable extra channels but the CampaignAdmin explicitly says their delivery automation is not wired into the campaign send sweep. They remain staged as queued.
- G6 Telegram marketing service itself creates a stub SENT delivery; it also respects marketing eligibility and is separate from provisioning or membership.
- Do not add a “send all channels” action or imply Telegram/in-product campaign delivery is live.

Template and audience snapshot:
- A Campaign references TemplateVersion and retains that historical version if the underlying Template is edited later.
- The campaign recipient list is a schedule-time snapshot; show the snapshot timestamp and the split between queued/sent/failed/skipped where source-backed.

Current management boundary:
- Campaign and Audience are in Django Admin via CampaignAdmin and AudienceAdmin.
- No dedicated Admin Desk Growth campaign route exists.
- The proposed Campaigns workspace is not an existing live route.

### 2.5 Journeys and Automation

Current models:
- **AutomationRule:** name, trigger_event_type, TemplateVersion, delay_minutes and enabled.
- **AutomationRun:** unique per (rule, Event), stores user, status, Delivery, error, scheduled_at, fired_at.
- Run statuses: Pending, Fired, Skipped, Failed.

The model documentation describes the lifecycle:
- A durable Event triggers an AutomationRun and delayed durable job.
- At fire time, the run re-checks marketing consent/suppression.
- It sends a frozen TemplateVersion through the idempotent Delivery layer.
- Unique (rule, triggering_event) prevents the same event from starting the same rule more than once.

The current AutomationRule editor and AutomationRun audit are in Django Admin. Runs are read-only in the admin; rules are editable. The redesigned Journeys screen is an inspection and design proposal until rule-management parity and permission mapping are reviewed. Do not invent retry, skip, replay or reschedule controls.

### 2.6 Promotions and Coupons

Current Coupon fields:
- Code, display name, discount type (Percent or Fixed), percent_off or amount_off_cents, currency.
- valid_from and valid_until.
- max_redemptions and max_per_user.
- Optional Campaign foreign key for campaign-scoped eligibility.
- plan_tiers JSON list (empty means all tiers).
- stackable_with_referral.
- active.

Validation:
- Coupon must exist and be active.
- Current time must be within its validity window.
- Plan tier must be eligible when plan_tiers is populated.
- If a referral discount is already present, the coupon must permit stacking; otherwise it is rejected.
- For campaign-scoped coupons, the user’s authoritative SignupAttribution.referring_campaign must match the Coupon’s Campaign. A client-supplied campaign ID is not trusted.
- Per-user and global redemption limits are enforced.
- Discount amount is capped at the post-referral base amount; final amount cannot be below zero.

Redemption:
- CouponRedemption is created only after successful activation, using an atomic limit re-check.
- It links Coupon, User, PaymentIntent and Subscription (as nullable references) and records base amount, discount, final amount, currency, finalized state/time.
- It is provenance, not a new payment. Revenue's PaymentIntent remains the canonical transaction.
- CouponRedemption is read-only in Django Admin; no add/delete.
- Coupon and redemptions currently live in Django Admin. No dedicated Admin Desk Coupon editor or redemption route exists.
- The new screen can inspect eligibility and redemption provenance but must not imply that prototype preview creates or edits a coupon.

### 2.7 Referrals and Rewards

Referral relationship:
- **ReferralCode:** one per user, unique code; generated for that user.
- **Referral:** referrer, one-to-one referred_user, Pending/Completed status, created/completed time, referee_reward_applied and discount_used flags.
- Database constraint prevents self-referrals.
- Referral code can be captured via `/growth/r/<code>/` and signup/member flows.
- A user cannot use a new referral if they already have a referral or have previous qualifying paid-subscription history, per the inspected service.
- Referral completes after successful paid subscription purchase (the inspected standard paid subscription activation path), then may create the referrer reward and referee discount benefit.
- Do not infer that a free membership join or every one-time Academy CourseOffer purchase necessarily triggers the same referral completion path; the inspected CourseOffer path dispatches into Academy course entitlement separately.

Referee checkout discount:
- The inspected canonical `ReferralService.get_checkout_discount` checks that the user has no active subscription, has a pending Referral, has not used its discount, and applies the configured `referee_discount_percent`.
- It returns a proposed discount calculation and Referral reference; it does not represent the referrer’s reward.
- Payment snapshot/checkout is the Revenue canonical record for the applied discount.

Referrer reward:
- **ReferralSettings** stores:
  - rewards_enabled (default true)
  - default_reward_percentage (default 20%)
  - minimum_purchase_amount_cents
  - reward_delay_hours (default 72)
  - referee_benefit_enabled (default false)
  - referee_bonus_cents (default zero)
  - referee_discount_percent (default 20)
- **ReferralReward:** one-to-one per Referral; referrer; currency-bearing amount; purchase amount snapshot; reward percentage; status Pending/Credited/Used/Expired; used_amount; unlocked_at; block_reason; optional triggering_subscription.
- Reward is created Pending after qualifying referral completion and minimum purchase check, using configured percentage and delay.
- Unlock service requires a triggering subscription; if absent, it skips the reward, leaving it pending.
- The inspected unlock service queries PaymentIntent status values `refunded` and `canceled`, while the PaymentIntent model choices are Pending, Success and Failed. This refund check is mismatched and requires code review. The Growth UI must not silently repair it or present automatic reward unlock as guaranteed.
- Eligible pending reward transitions to Credited through a conditional PENDING→CREDITED update; a ReferralRewardLedger Credit row is created on the winning transition.
- If the linked subscription is no longer valid or the service's refund test indicates refunded, the reward is expired with a ledger entry.
- **ReferralRewardLedger** has Credit, Debit, Expired, Reversal transaction types; amount, balance_after, optional description and Subscription link. It is the audit of reward consumption/expiry.

Reward consumption:
- Credited rewards are separate buckets and are consumed FIFO (oldest first) when applied to subscription time.
- SubscriptionCreditService converts credit to extra subscription days pro rata, creates debit ledger entries, then extends the linked Subscription through the existing path.
- Reward credits are denominated in currency. The current `UserRewardBalance` helper sums cent amounts across all credited buckets without grouping by currency. The new screen must show per-currency buckets and not display one combined multi-currency wallet total.
- Do not conflate:
  - Referee one-time checkout discount.
  - Referrer pending/credited reward bucket.
  - Referrer reward consumption into subscription extension.
  - Optional referee bonus credits.
  - Coupon discount.
- Important source caveat: `SubscriptionCreditService.add_credits()`, used by the optional referee bonus path, currently only logs the intent. It does not persist a credit balance or a ledger record. A Referral may set `referee_reward_applied` after calling it, so do not present the bonus as actually credited. Keep that feature disabled/unavailable until implemented.
- A member-facing custom Referral Rewards Overview route at `/growth/admin/referral-rewards/` uses LoginRequiredMixin rather than a staff-only gate in the inspected source. Do not embed it inside the staff Admin Desk without a separate authorization review.
- Referral models/settings/reward and reward ledger are managed through Django Admin today.

### 2.8 Gifts

Modern token invite:
- `GiftService.create_gift` creates a GiftSubscription plus one token-based GiftInvite.
- GiftInvite stores intended recipient email, email hash, raw claim_token, claim_token_hash, state, claimed_by/claimed_at, email sent timestamps/count and expiry.
- Default invite expiry is 30 days.
- Can resend at most five times, with a minimum one-hour gap, according to GiftInvite.can_resend_email.
- Claim is intended for the same email address as the invite; the service validates the signed-in recipient, blocks self-gift, row-locks the invitation and creates or extends the canonical Subscription.
- GiftInvite states: Pending, Claimed, Expired, Revoked.
- Claim invitation and active Subscription are distinct records.
- Do not show the raw claim_token or claim URL in broad registers or global search results. A success page may display the specific claim URL to the sending staff member under the existing flow.
- PendingGiftClaim stores anonymous claim attempts by session; stale after seven days and becomes Processed/Failed after authentication.

Legacy path:
- Legacy GiftSubscription gift_code claim flow still exists separately.
- Do not collapse its code/claim statuses into the modern token GiftInvite state machine without a migration strategy.

Existing staff send flow:
- Custom route `/admin/growth/send-gift/` and success route `/admin/growth/send-gift/success/<str:gift_invite_id>/`.
- View is decorated `staff_member_required`.
- It creates GiftSubscription + GiftInvite, sends invitation through GiftEmailService/NotificationService and gives a success/warning result.
- If email fails, gift creation still succeeded; the success page exposes the claim URL. The email result is not the same as gift creation outcome.
- AdminGiftSendForm restricts duration to 7, 30, 90 or 365 days, requires recipient email and a Plan, allows optional message up to 1000 characters and prevents sender email as recipient.
- The admin view currently queries active plans; no narrower grant-only/paid-only plan filter was verified.
- No distinct staff resend control was verified in the inspected route/template; the GiftInvite service has resend eligibility and send helpers, but do not add a live resend action to the prototype.

The modern GiftInviteAdmin and legacy GiftSubscription admin remain in Advanced Administration until parity is reviewed.

### 2.9 Email Delivery, Consent and Templates

Separate delivery ledgers:
1. **G1 Delivery** — provider-agnostic idempotent email delivery record, linked to TemplateVersion and User where available. Fields include recipient, kind, subject, state, provider, provider_message_id, error, created_at and sent_at.
2. **EmailLog** — legacy/transactional logging record created by NotificationService when sending template emails through Django's email backend. Fields include user, email, template, subject, state (queued/sent/failed/bounced), sent_at, error_message and metadata.

Do not collapse them:
- Their states differ.
- G1 Delivery is updated by the signed Resend webhook when provider=Resend and matching provider_message_id exists.
- The inspected Resend webhook updates Delivery only, not EmailLog.
- NotificationService transactional EmailLog is separate; its send_mail acceptance is recorded as Sent, not provider-confirmed delivered.

G1 Delivery states:
- Queued, Sending, Sent, Delivered, Delayed, Failed, Bounced, Complained, Suppressed.
- DeliveryAdmin is read-only; add/delete disabled.
- Webhook signature is verified from Svix-style headers; event updates match provider message id and recipient. State protection prevents late "sent"/"delayed" events downgrading stronger terminal outcomes.

Marketing consent:
- MarketingPreference.marketing_opt_in defaults false (default opt-out).
- Global Suppression overrides opt-in; any Unsubscribe, Bounce or Complaint suppression blocks marketing.
- `can_send_marketing(user,email)` is the shared eligibility gate.
- Transactional email is not gated by this marketing preference check.
- Suppression is compliance evidence and is read-only; add/delete disabled in Django Admin.
- Do not present marketing campaign eligibility as identical to transactional message eligibility.

Templates:
- Template kinds: Marketing and Transactional.
- TemplateVersion stores version number, editor mode (Visual/HTML), subject, preview text, canonical HTML/plain text, visual blocks and declared variables.
- TemplateVersion is an immutable version snapshot; campaigns and automation rules reference versions, not the mutable template identity.
- Only declared VariableSpec names are available for substitution.
- TemplateVersionAdmin is read-only; TemplateAdmin contains version inline management in Django Admin.
- No dedicated Growth Admin Desk Template Builder/Delivery screen exists today.

### 2.10 Advanced Growth

The inspected advanced_growth models/admin include:

**Affiliates**
- Affiliate: linked User, unique code, commission percent, status Pending/Active/Suspended, payout email.
- AffiliateAttribution: first-touch affiliate record, user, UTM source/campaign, click/signup/purchase times; self-referral blocked.
- AffiliateCommission: unique affiliate+PaymentIntent, user, amount/currency, status Pending/Approved/Payable/Paid/Reversed.
- Allowed state progression: Pending→Approved→Payable→Paid; Reversed can be used from any non-Paid status. Paid is terminal.
- No actual payout execution/provider transfer workflow was verified. “Paid” is an internal recorded state only.

**Experiments**
- Experiment: Draft/Running/Paused/Completed, unique key.
- ExperimentVariant: key/name/allocation percent and optional TemplateVersion.
- ExperimentAssignment: deterministic/stable per user and experiment; unique (experiment,user).
- ExperimentConversion: unique assignment+Event.

**Announcements / extra channels**
- Announcement: Banner/Modal/Notification, title/body, priority, audience_rules, starts_at/ends_at, max_shows_per_user default 3, active.
- AnnouncementExposure: unique by announcement/user/idempotency key; stores dismissed and exposure time.
- CampaignAction: Email is not configured through this table; Campaign's template_version is the only email source. Additional actions are Telegram or in-product.
- The CampaignAdmin explicitly notes Telegram and in-product CampaignAction rows are staged/queued and delivery automation is not wired into the campaign send sweep.
- TelegramMarketingDelivery is separate from community entitlement/provisioning; G6 sender uses a stub provider and state SENT, not confirmed real delivery.
- These advanced records are in Django Admin. Affiliate commissions have state-transition bulk actions; no actual payout system was verified.

## 3. M18 — Growth Overview

**Purpose:** Answer “Which acquisition, campaign, referral or delivery issue needs inspection, and which domain owns the next action?”

Recommended hierarchy:
1. Attention items with explicit source:
   - Referral reward missing its triggering subscription or approaching unlock validation.
   - Campaign in sending/done state while its Delivery provider is stub.
   - Marketing suppression or delivery exceptions.
   - Gift invite created but invitation email failed.
   - Analytics source metric marked unverified.
2. Compact operating indicators:
   - Pending/completed referrals.
   - Pending/credited reward buckets (currency-aware).
   - Campaign model states.
   - Pending/claimed gift invites.
3. Cross-domain hand-offs:
   - Customer 360 for learner and consent context.
   - Revenue for canonical PaymentIntent and Subscription.
   - Academy for course/offer conversion source.
   - Platform for durable jobs and provider/webhook state.

All counts in the mockup are illustrative. The Growth overview is a router/operating summary, not a new owner of campaign delivery, payments, subscriptions or provider infrastructure.

## 4. M41 — Analytics & Attribution

**Purpose:** Show source-backed acquisition/conversion evidence without mislabelling or overclaiming the current reports.

Proposed sections:
- Purchase Events (not Signups until the endpoint/source is corrected).
- Email Delivery outcomes (state definitions and provider source).
- Campaign snapshot/performance (distinguish CampaignMetrics cache from Delivery webhooks).
- CouponRedemption usage and discounts (mark unverified until Sum import defect corrected and endpoint tested).
- Referral status/reward counts with period and currency labels only where source supports them.
- First-touch SignupAttribution details.
- Last-touch email Delivery attribution to CampaignRecipient or AutomationRun.

Use explicit metric definitions:
- Purchase completed event count.
- Delivery Sent vs Delivered vs Bounced vs Complained vs Suppressed.
- CampaignRecipient status vs Delivery provider state.
- CouponRedemption finalized vs non-finalized.
- Referral Pending vs Completed.
- Reward Pending vs Credited vs Used vs Expired.
- Per-currency totals only.

No create/update action is required for the current read-only Analytics endpoint. Proposed charts/tables should use the same query definitions and show “unverified” when the current response cannot support a reliable claim.

## 5. M34 — Campaigns & Audiences

**Purpose:** Inspect campaign lifecycle, frozen audience membership, email version and downstream delivery evidence.

Recommended register:
- Campaign name.
- Model state.
- Audience name and estimated count.
- Snapshot timestamp and frozen recipient count.
- Skipped/suppressed recipient count.
- TemplateVersion and subject override.
- Scheduled time.
- Delivery provider / execution warning.
- Open campaign detail.

Campaign detail sections:
1. Campaign identity and state.
2. Audience rules and live estimate; mark clearly as a live estimate until scheduled.
3. Frozen CampaignRecipient snapshot, including Queued/Sending/Sent/Failed/Suppressed/Skipped counts.
4. Linked immutable TemplateVersion.
5. Delivery records and provider state.
6. Additional CampaignAction rows (Telegram/in-product) clearly marked Staged / not wired.
7. CampaignMetrics cache shown as a separate derived counter, not substituted for Delivery state.

The prototype includes campaign filter and detail preview only. It does not schedule, pause, send, enqueue or mutate a campaign.

## 6. M35 — Journeys & Automation

**Purpose:** Inspect event-triggered automation rules and their individual execution histories.

Rule fields:
- Name.
- Trigger Event type.
- Frozen TemplateVersion.
- Delay minutes.
- Enabled/disabled.
- Rule age.

AutomationRun fields:
- Source Event.
- Rule.
- User.
- Status Pending/Fired/Skipped/Failed.
- Scheduled/fired timestamps.
- Linked Delivery.
- Error message.

Rules remain editable through Django Admin, runs are audit/read-only. The prototype provides status and provenance views only. It does not enable/disable rules, requeue failed runs or retry sends.

## 7. M36 — Promotions & Coupons

**Purpose:** Explain the offer a learner used and trace it to the payment snapshot.

Register fields:
- Code/name.
- Percent or fixed discount.
- Currency.
- Active/valid window.
- Campaign scope.
- Plan tier scope.
- Per-user/global redemption limits and current use.
- Referral stacking rule.
- CouponRedemption count/discount amount where source is verified.

Detail:
- Coupon eligibility configuration.
- Campaign and SignupAttribution requirement where scoped.
- Plan tier and validity.
- Referral discount stacking.
- Redemption ledger with canonical PaymentIntent and Subscription links.
- Base/discount/final/currency snapshots.

Coupon management currently remains in Django Admin. Redemption rows are read-only; no edit/delete. The prototype's “New coupon” is a display-only preview, not a functional editor.

## 8. M37 — Referrals & Rewards

**Purpose:** Trace one referral from code/share through qualifying purchase, discount, reward bucket and subscription extension.

Recommended sub-sections:
- Referral relationship register (Referrer, Referred User, Code, Pending/Completed, discount_used).
- ReferralSettings summary (with Django Admin boundary).
- Referrer reward buckets grouped by currency.
- ReferralRewardLedger entries and links to triggering Subscription.
- Reward lifecycle: Pending→Credited→Used/Expired.
- Reward logic caveat and referee bonus unavailable state.

Do not expose a combined global cent balance across mixed currencies.
Do not provide a manual “credit reward” button or “apply reward” action.
Do not claim optional referee bonus credits exist as a persisted balance.
Do not expose the current LoginRequired-only Referral Rewards overview within staff navigation without fixing its staff permission boundary.
The Settings preview is read-only and local-only.

## 9. M38 — Gifts

**Purpose:** Inspect a GiftInvite separately from its underlying GiftSubscription and resulting Revenue Subscription.

Register fields:
- Intended recipient email (no raw token).
- Plan and gift duration.
- Sender.
- Invite state.
- Email evidence (separate state/record).
- Expiry.
- Claimed user/time if applicable.

Detail:
- Modern token invite vs legacy gift code flow.
- Underlying GiftSubscription.
- Claim conditions (email match, not self, pending/not expired).
- Resulting canonical Subscription once claimed.
- Email invite evidence and failure handling.
- Invite expiry and resend service constraints.

Existing staff send route is staff_member_required and offers durations 7/30/90/365 days. Gift may exist even when email send fails. No staff resend control was verified; the prototype has no resend action and does not show raw claim token or URL.

## 10. M39 — Email Delivery

Use four subtabs:

**Growth Delivery ledger**
- G1 Delivery register and filters by recipient, subject, state and kind.
- Provider, message ID (may be masked or restricted), error and sent time.
- Resend webhook lifecycle for provider=Resend only.
- Clearly distinguish Sent (provider accepted/recorded send) from Delivered (provider-confirmed event).

**Transactional EmailLog**
- Separate legacy ledger created by NotificationService.
- Queued/Sent/Failed/Bounced states.
- Do not imply the Resend webhook updates this ledger.
- The service's Sent is the Django mail backend send result, not provider-confirmed Delivered.

**Consent & Suppression**
- Marketing opt-in default false.
- Global suppression on unsubscribe/bounce/complaint overrides opt-in.
- Transactional emails are not gated by marketing preference.
- Suppression is read-only compliance evidence; no casually editable/delete control.
- Do not add bulk unsubscribe, suppression deletion, or forced opt-in actions.

**Templates**
- Template identity and immutable TemplateVersion.
- Marketing vs Transactional kind.
- Visual builder vs HTML editor.
- Declared variables only.
- Version referenced by Campaign/Automation; edits create new version.
- Current Template/TemplateVersion administration remains Django Admin until editor/migration parity is reviewed.

The email screen does not retry/resend delivery, change recipient consent, or edit immutable Delivery records.

## 11. M40 — Advanced Growth

Keep lower-frequency/high-risk features visible but secondary while the migration is staged.

Subsections:
- **Affiliates & Commissions:** affiliate identity/status, first-touch attribution and commission state progression. “Paid” is not proof of external payout.
- **Experiments:** stable per-user assignment, variant allocation and Event-linked conversions.
- **Announcements & Channels:** in-product announcement targeting/time window/frequency cap/exposures; CampaignAction extra channels; TelegramMarketingDelivery separate from provisioning and stub delivery.
- All records remain in Advanced Administration until route/role/action parity is defined.
- No experiment allocation mutation, commission state change, payout, announcement broadcast or Telegram send from the prototype.

## 12. Cross-domain hand-offs and lifecycle contracts

| Growth context | Canonical owner | Linked domains |
|---|---|---|
| SignupAttribution / Referral / ReferralCode | Growth | Customers, Command Centre |
| Campaign / Audience / CampaignRecipient / CampaignMetrics | Growth | Customers, Platform, Command Centre |
| Coupon / CouponRedemption | Growth | Revenue, Customers |
| ReferralReward / Ledger | Growth | Revenue Subscription, Customers |
| GiftInvite / PendingGiftClaim | Growth (invite); Subscription is Revenue | Customers, Revenue |
| Template / TemplateVersion / Delivery / Suppression | Growth | Customers, Platform |
| PaymentIntent / Subscription | Revenue | Growth, Customers, Academy |
| Course / CourseOffer | Academy | Growth, Revenue |
| Durable jobs / provider / webhook health | Platform | Growth, Command Centre |
| User identity / Customer 360 | Customers | Growth, Revenue, Academy |

Priority journeys:
1. Campaign conversion: Campaign/TemplateVersion → frozen Audience/CampaignRecipient → Delivery (provider state) → last-touch attribution → purchase.completed Event → Revenue PaymentIntent/Subscription → Academy entitlement if the purchase is a course offer.
2. Referral: referral code → Referral pending → eligible paid membership subscription purchase → Referral completed → referee checkout discount snapshot and referrer reward Pending → unlock eligibility → Credited reward bucket → FIFO subscription extension ledger.
3. Coupon: SignupAttribution campaign scope → Coupon eligibility and stacking → PaymentIntent discount snapshot → CouponRedemption on successful activation → Revenue payment/subscription.
4. Gift: staff creates GiftSubscription + GiftInvite → transactional EmailLog evidence → recipient email-matched claim → Revenue Subscription created/extended → Customer 360.
5. Suppression: unsubscribe/bounce/complaint → global Suppression → marketing eligibility false even if user remains opted in → transactional sends remain distinct.
6. Automation: durable Event → AutomationRun pending → delayed execution re-checks consent/suppression → frozen TemplateVersion → idempotent Delivery → last-touch attribution if eligible before purchase.
7. Affiliate: affiliate first-touch signup attribution → attributed PaymentIntent purchase → unique AffiliateCommission → state transitions → external payout remains unverified/not available.

Critical distinctions:
- Referral discount ≠ referrer reward ≠ coupon ≠ referee bonus credit ≠ gift.
- Campaign model state ≠ provider send ≠ provider delivery.
- CampaignRecipient SENT with provider=stub ≠ real email delivered.
- EmailLog SENT ≠ G1 Delivery DELIVERED.
- Telegram marketing ≠ Telegram membership provisioning.
- GiftInvite Pending ≠ active Subscription.
- CouponRedemption ≠ a second payment record.
- AffiliateCommission PAID state ≠ proof of a provider/bank payout.
- First-touch attribution ≠ last-touch email credit.

## 13. Prototype and browser smoke-test record

**HTML:** `tradethesis_admin_growth_workspace_v1.html`

Included:
- Growth Overview.
- Analytics & Attribution.
- Campaigns & Audiences.
- Journeys & Automation.
- Promotions & Coupons.
- Referrals & Rewards.
- Gifts.
- Email Delivery (Growth Delivery, transactional EmailLog, Consent & Suppression, Templates).
- Advanced Growth (Affiliates & Commissions, Experiments, Announcements & Channels).
- V2 shell, six-domain navigation and mobile drawer.

Browser checks passed:
- All eight Growth destinations open.
- Campaign status filter and search, campaign detail preview.
- Coupon active filter and detail preview.
- Referral completed filter and settings preview.
- Pending gift filter, gift detail and send preview.
- Growth Delivery bounced filter.
- Transactional EmailLog, Consent & Suppression and Templates subtabs.
- Advanced Growth affiliate, experiment and announcements subtabs.
- Campaign, coupon, referral settings and gift preview actions display preview-only confirmations.
- Mobile drawer opens, navigates and closes.
- 390px viewport has no horizontal page overflow after the responsive sizing adjustment.
- No JavaScript page errors or console errors in exercised paths.

Not tested/claimed:
- Authenticated staging route/role parity.
- Live Campaign or provider delivery.
- Actual provider webhook outcomes or retry.
- Live gift send/claim or resend.
- Real coupon, referral setting or reward mutation.
- Reward unlock correctness, currency conversion or referee bonus persistence.
- Actual affiliate payouts.
- Full keyboard-only, screen-reader, contrast certification and cross-browser accessibility.

## 14. Owner review decisions requested

1. Is the Growth Overview appropriately attention-first, or should it be narrower and centre only on campaign/delivery and reward exceptions?
2. Should Analytics & Attribution be a full Growth destination, or a sub-tab of Overview?
3. Are Campaigns and Journeys separate enough, given that campaigns use frozen audiences while automation is event-triggered?
4. Should Promotions remain a separate destination from Referrals & Rewards, as proposed?
5. Does the distinction between Referral Code, Referral, referee discount, referrer reward and reward ledger read clearly?
6. Should Gifts be directly inside Growth or be linked from Customers as well?
7. Is separating G1 Delivery, transactional EmailLog, Consent/Suppression and Template Versions the right Email Delivery organisation?
8. Should Affiliates, Experiments and Announcements remain under Advanced Growth until permissions and execution services are reviewed?
9. Which source caveats should block a first implementation slice: analytics import/key mismatch, stub campaign provider, referral reward unlock mismatch, currency aggregation or referee bonus persistence?
10. Which Growth page needs a higher-fidelity pass before moving to Platform?

This is a design specification for review, not implementation authorisation.
