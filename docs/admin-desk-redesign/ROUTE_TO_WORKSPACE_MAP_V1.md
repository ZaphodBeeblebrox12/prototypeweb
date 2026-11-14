# TradeThesis Admin Desk — Route-to-Workspace Map v1

**Status:** Source-level route inventory for design planning  
**Baseline branch:** `my-new-branch`  
**Planning branch:** `admin-desk-redesign-planning`  
**Important:** This is not a live authenticated route/role audit. A route may exist without being linked from the current Admin Desk or accessible to every staff role. Recheck deployed HEAD and role-specific access before implementation.

## 1. Route status vocabulary

- **Existing Admin Desk page:** a dedicated staff-facing page already mounted under `/staff/admin-desk/`.
- **Existing non-Desk route/API:** a page or API exists elsewhere but is not yet a unified Admin Desk workspace.
- **Django Admin destination:** capability is present through `/admin/` model administration or custom admin URL.
- **Proposed unified destination:** a new shell page/route proposed by the redesign; no equivalent route was found in the inspected source map.
- **Development-only path:** explicitly feature-flagged/staff development route; must not be represented as the default production path.

## 2. Command Centre

| Proposed tab | Current route/source | Current state | Design mapping |
|---|---|---|---|
| Overview | `/staff/admin-desk/` | Existing Admin Desk page; permission-filtered summaries and links | Retain as the Command Centre landing destination and redesign around the agreed action-first queue. |
| My Work | Support queue supports `/staff/admin-desk/support/tickets/?assignment=mine` | Existing support-only assignment filter; no universal task engine verified | Proposed personal workbench over genuinely assigned records. Start with assigned support tickets; do not invent assignment for course reviews/jobs. |
| Notifications & Alerts | `/notifications/`; `/api/notifications/`; `/api/notifications/unread-count/`; `/api/notifications/<uuid>/read/`; `/api/notifications/read-all/` | Existing per-user notification list/read API. Support workflow creates staff notifications for new tickets. | Shared-shell entry to personal notification feed. Broader operational alert routing, severity, deduplication and acknowledgement remain proposed. |
| Operations Timeline | `/staff/admin-desk/operations/` | Existing Admin Desk page with 24h/7d window, support clusters, jobs, provisioning, periodic errors, domain events, audit and security summaries | Keep as Command Centre's cross-domain observation view; detailed operational record management belongs in Platform. |

## 3. Academy

| Proposed tab | Current route/source | Current state | Design mapping |
|---|---|---|---|
| Overview | Course metrics and review links are embedded in `/staff/admin-desk/` | Existing overview data, no separate Academy landing page found | Proposed Academy landing with review, catalogue, offer and SEO attention. |
| Course Catalogue | Course records and related models are available through Django Admin; public catalogue API is `/api/academy/catalogue/` | Existing model/admin and public API; no dedicated staff-facing Admin Desk catalogue page verified | Proposed compact Course table/detail. Keep public API separate from staff administration. |
| Course Approvals | `/staff/admin-desk/courses/review/` | Existing Admin Desk queue | Keep the canonical queue and redesign it inside Academy. |
| Review detail | `/staff/admin-desk/courses/review/<uuid:import_id>/`; assets under `.../assets/<uuid:asset_id>/`; actions under `.../approve/` and `.../return/` | Existing preview, asset, approve and return workflow | Preserve canonical publisher, feedback-required return and reviewer permissions. |
| Course Builder | `/staff/course-builder/`; API under `/staff/course-builder/api/`; video/assets and Google Drive OAuth routes under `/staff/course-builder/...` and `/staff/google-drive/...` | Existing supported legacy authoring route | Keep as a separate authoring workspace launched from Academy; preserve the selected course and return context. |
| Tiptap preview | `/staff/course-builder/tiptap/` and `/staff/course-builder/tiptap/api/...` | Development-only / feature-flagged staff path | Do not label as the live default editor until separately approved and integrated. |
| Offers & Access | `CourseOffer`, `Plan`, `PlanPrice`, `GeoPlanPrice`, `CourseEntitlement` and related models; some record management remains in Django Admin | Existing underlying models and validations; no dedicated unified Admin Desk page verified | Proposed Academy workspace owns the CourseOffer-to-Course relationship. Preserve validation: Published Paid/Mixed course, dedicated hidden Plan and active one-time base/geo price. Link to canonical Revenue Plan/price details. |
| Learner Access & Progress | Customer 360 exposes permission-scoped CourseEntitlement, LessonProgress and entitlement events at `/staff/admin-desk/customers/<uuid:user_id>/`; underlying model administration also exists | Existing data and Customer 360 context; no standalone Academy access workspace verified. Direct paid/free-course access uses CourseEntitlement; the inspected membership-access helper specifically checks the dedicated TradeThesis Free plan/product and PlanCourseAccess mapping. | Proposed standalone access/progress workspace with direct entitlements, the source-verified Free membership path and progress shown separately; link to Customer 360. Do not imply every subscription tier unlocks mapped courses without further source verification. |
| SEO & Discoverability | `/staff/admin-desk/seo/` | Existing dedicated Admin Desk diagnostic | Keep in Academy and link each issue to Course detail/Builder. |

## 4. Customers

| Proposed tab | Current route/source | Current state | Design mapping |
|---|---|---|---|
| Overview | `/staff/admin-desk/` has cross-domain operational summaries; no dedicated Customers landing route exists | Existing account/support summaries; no dedicated Customers home verified | Proposed action-first Customers landing focused on reviewer-visible tickets, account lookup and member-impacting work. Counts must be reviewer-scoped. |
| Learners & Accounts | `/staff/admin-desk/accounts/`; detail `/staff/admin-desk/accounts/<uuid:user_id>/`; actions `/staff/admin-desk/accounts/<uuid:user_id>/action/` | Existing Admin Desk list/detail/action routes. List searches username/email/first/last name/nickname, filters active/inactive/banned, orders newest joined first and paginates 25. | Canonical owner of learner account operations. Staff/superuser accounts stay outside the normal learner list. Subscription count is permission-gated. Account actions require `accounts.change_user`; ban/deactivate require a reason and write audit/reconciliation evidence. |
| Support Tickets | `/staff/admin-desk/support/tickets/`; detail `/staff/admin-desk/support/tickets/<uuid:ticket_id>/`; actions `/staff/admin-desk/support/tickets/<uuid:ticket_id>/action/` | Existing Admin Desk queue/detail/actions. Queue supports search, status, category, priority, mine/unassigned filters; newest-first ordering; 25/page. Reviewer scope uses active staff and plan/affiliate-plan ticket_approvers. | Canonical owner of ticket status, assignment, priority, public reply, internal note and access-request decisions. Preserve 2h/8h/24h/72h SLA targets, reviewer scope and transactional grant/reconciliation workflow. |
| Customer 360 | `/staff/admin-desk/customers/<uuid:user_id>/` | Existing read-only, permission-scoped cross-domain record. Can resolve through a reviewer-visible ticket or `accounts.view_user`. Independent section permissions for subscriptions, payments, invoices, Academy and security; internal requester profiles are restricted to identity + reviewer-visible support. | Retain as full-page relationship hub; add only a compact contextual preview within ticket detail. Keep internal notes, raw security details and raw payment-provider identifiers out of the activity stream. |

## 5. Revenue

| Proposed tab | Current route/source | Current state | Design mapping |
|---|---|---|---|
| Overview | Payment, subscription and invoice summaries are included in `/staff/admin-desk/` | Existing permission-filtered summaries | Proposed Revenue landing with exception-led work and commercial context. |
| Payments & Refunds | `/staff/admin-desk/finance/` (Payments tab); CSV export via existing finance link to `ops-payments-csv`; provider webhooks `/webhooks/stripe/` and `/webhooks/razorpay/`. PaymentIntent and Refund models/services own the ledger. | Existing staff payment register is read-only, 30/page, searchable/filterable and permission-gated. PaymentIntent Django Admin is read-only for financial fields and cannot delete; Refund inline/admin are read-only/no add/delete. Django Admin PaymentIntent has a “Record FULL manual refund” bulk action that must be used only AFTER refunding in the provider dashboard; it records the full remaining amount in the Refund ledger, audits, applies full-refund access policy and notifies. It does not initiate a provider refund. | Proposed canonical Revenue payment register/detail. Keep provider refund actions out of the current read-only finance UI until a separately approved migration. Preserve the current manual full-refund action in Advanced Administration in the meantime. Do not expose customer checkout routes as admin destinations. |
| Subscriptions | `/staff/admin-desk/subscriptions/`; detail lifecycle actions `/staff/admin-desk/subscriptions/<uuid:subscription_id>/action/` | Existing staff workspace supports search, status, expiring/recent filters, 30/page, permission-gated audited hidden-plan grant (1–365 days + reason), extend (1–365 days + reason) and cancel (reason; active only; queues reconciliation). | Redesign the existing subscription register/actions; preserve all service and permission rules. Do not edit Subscription price snapshots or raw lifecycle fields. |
| Plans & Pricing | Product/Plan/PlanPrice/GeoPlanPrice/PlanFeature/PlanChannelMapping through `/admin/` and Django Admin inline configuration; subscription API under `/api/subscriptions/` is member-facing | No unified staff Admin Desk Plan/price editor route verified. PlanAdmin manages Plan plus inline global base prices, geo overrides, features and channel mappings. | Proposed Revenue plan catalogue/detail. Keep editing in Advanced Administration until a permission-safe editor preserves uniqueness, country/region validation, product/tier/trial rules, base-vs-geo price resolution and audit. Member APIs are not admin destinations. |
| Invoices | `/staff/admin-desk/finance/?tab=invoices`; detail `/staff/admin-desk/invoices/<uuid:invoice_id>/`; model is read-only in Django Admin | Existing invoice register and detail with print/save-as-PDF; Invoice snapshot is not ordinarily addable/editable/deletable. BillingSettings changes affect future invoices only. | Keep immutable invoice detail linked to source PaymentIntent and Customer 360; no issue/edit/delete/refund controls. |
| Disputes | `/admin-disputes/`; detail `/admin-disputes/<uuid:pk>/`; actions `/admin-disputes/<uuid:pk>/note/`, `/generate/`, `/submit/`, `/resolve/` | Existing staff dispute dashboard/detail. Read uses staff_member_required; note/generate/submit/resolve require disputes.change_dispute. Evidence packages are content-hashed/immutable after submission. The app records external submission reference; it does not upload the package to the PSP. | Map into Revenue navigation while retaining the separate Dispute model, services, permissions and state machine. Keep opened/funds-withdrawn distinct from final outcome. |
| Business & Finance | `/staff/admin-desk/business/` (BillingSettings form/save path/audit); finance `/staff/admin-desk/finance/` | Existing seller/invoice/tax settings form requires add/change BillingSettings permission. Tax is disabled by default; first enable requires accountant confirmation. Current tax calculation is one fixed percentage, not a jurisdiction-aware tax engine. | Keep as controlled configuration destination. Clearly state fixed-rate tax limitation; distinguish configured from end-to-end tested. |

## 6. Growth

| Proposed tab | Current route/source | Current state | Design mapping |
|---|---|---|---|
| Overview | Growth models/admin and `/api/analytics/overview/`; gift custom view and existing Delivery/webhook sources | Existing data sources; no unified Growth Admin Desk landing route verified. API uses `IsAdminUser`. | Proposed action-first Growth home. Show source-quality/execution gaps and route to canonical Growth, Customers, Revenue and Platform records. Do not present sample counts as live alerts. |
| Analytics & Attribution | `/api/analytics/overview/`; `SignupAttribution`; durable `events.Event`; `Delivery`; `CampaignMetrics`; `CouponRedemption`; `Referral` and `ReferralReward` | Existing admin-only read-only API. Source caveats: `signups` function counts `purchase.completed` Events; `promotion_performance` references `Sum` without importing it; email response omits delivered/delayed; CampaignMetrics bounce/complaint counts are not reconciled by inspected webhook; referrals are global counts without date/currency segmentation. | Proposed read-only Analytics UI. Rename or repair the mislabeled purchase event metric; show source, definition, period and currency; mark promotion aggregate unverified until tested; keep first-touch and last-touch attribution distinct. |
| Campaigns & Audiences | `Campaign`, `Audience`, `CampaignRecipient`, `CampaignMetrics` in Django Admin (`CampaignAdmin`, `AudienceAdmin`) | Existing Django Admin campaign workspace supports scheduling/frozen audience snapshot and batch-send job. No Admin Desk campaign route. G2 send sweep uses provider=stub and marks Delivery SENT; additional Telegram/in-product CampaignAction rows are staged and not wired into campaign send sweep. | Proposed Growth campaign workspace. Preserve immutable TemplateVersion, schedule-time recipient snapshot and consent/suppression rules. Do not imply stub SENT equals provider-delivered; mark extra channels staged. |
| Journeys & Automation | `AutomationRule`, `AutomationRun` in Django Admin | Existing rule configuration and read-only run audit; no Admin Desk route. Model documentation describes event idempotency, delay and consent/suppression re-check at fire time. | Proposed read/inspect workspace first. Keep editing in Advanced Administration until rule permission and parity are reviewed; do not invent retry/replay controls. |
| Promotions & Coupons | `Coupon`, `CouponRedemption` under Django Admin; checkout validation in promotions service; redemptions created during successful Revenue activation | Existing configuration/ledger models; no Admin Desk route. CouponRedemption is read-only with no add/delete. | Proposed Growth coupon register/detail. Preserve validity, plan tier, campaign first-touch attribution, usage caps, referral stacking and Revenue snapshot links. Keep redemptions read-only. |
| Referrals & Rewards | `/growth/r/<code>/` (capture); `/growth/referrals/` and `/growth/referrals/api/rewards/` (member-facing); `/growth/admin/referral-rewards/` (custom page); referral/reward models/admin | Existing member views/API and Django Admin models. The custom “admin” reward page uses LoginRequiredMixin, not staff-only authorization. Reward unlock PaymentIntent status check mismatches the model; UserRewardBalance sums cents across currencies; optional referee bonus helper logs only. | Proposed staff-only Growth register only after permission review. Do not link/embed the current login-only overview in staff navigation. Show reward buckets per currency; keep referee discount/referrer reward/bonus/coupon separate; flag current unlock and bonus gaps. |
| Gifts | `/admin/growth/send-gift/`; success at `/admin/growth/send-gift/success/<str:gift_invite_id>/`; `GiftInvite`, `PendingGiftClaim`, legacy `GiftSubscription.gift_code` claim | Existing custom view is `staff_member_required`; sends invite via NotificationService. Gift can exist when email fails. Modern token invite and legacy code flow coexist; invite claims and resulting Subscription are separate. No staff resend page verified. | Proposed Gifts register/detail. Never expose raw claim token broadly. Preserve recipient email match, 30-day invite expiry, resend guard (five sends, one-hour interval), and resulting Revenue Subscription link. Keep legacy path distinguishable. |
| Email Delivery | `Delivery`, `Template`, `TemplateVersion`, `VariableSpec`, `Suppression`, `MarketingPreference`, `EmailLog`; signed Resend webhook at `/api/email/webhooks/resend/` | Existing G1 Delivery ledger is read-only; transactional EmailLog is separate and written by NotificationService. Resend webhook updates Delivery, not EmailLog. TemplateVersion is immutable/read-only as a version record. Suppression is read-only/no add/delete. MarketingPreference defaults opt-out; global suppression overrides it; transactional mail is not gated by marketing opt-in. | Proposed read-first Email Delivery console with separate G1 Delivery and transactional EmailLog tabs, consent/suppression, and immutable templates. No resend, edit or suppression-deletion control without a separate audited design. |
| Advanced Growth | `Affiliate`, `AffiliateAttribution`, `AffiliateCommission`, `Experiment`, `ExperimentVariant`, `ExperimentAssignment`, `ExperimentConversion`, `Announcement`, `AnnouncementExposure`, `CampaignAction`, `TelegramMarketingDelivery` in Django Admin | Existing advanced records/admin. Affiliate commission has Pending→Approved→Payable→Paid/Reversed transitions, but no payout execution system was verified. Experiment assignments are stable/unique per user. CampaignAction Telegram/in-product actions are staged; G6 Telegram delivery uses a stub and is not membership provisioning. | Keep as Advanced Growth during staged migration. Display “Paid” as an internal commission state only, not proof of transfer. Keep marketing Telegram separate from community provisioning. |

Current route and ownership notes:
- `/growth/referrals/` is member-facing; not a staff Admin Desk route.
- `/growth/admin/referral-rewards/` is not safe to embed as a staff surface until the missing staff-only permission gate is reviewed.
- `/admin/growth/send-gift/` is a custom staff-only workflow and may be launched from a proposed Growth Gifts screen while preserving its existing service/route until parity is designed.
- `/api/analytics/overview/` is a read-only admin API, not a page.
- `/api/email/webhooks/resend/` is an inbound signed provider callback, not an operator page.
- Campaigns, Audience, coupons, automation, templates, referrals/rewards, affiliate/experiment/announcement and most delivery records currently remain in Django Admin.

## 7. Platform

| Proposed tab | Current route/source | Current state | Design mapping |
|---|---|---|---|
| Overview | /staff/admin-desk/operations/; /staff/admin-desk/; Job, Provisioning, PeriodicJob, support, Event, AuditLog and SecurityEvent sources | Existing permission-filtered operational timeline and overview. No separate unified Platform landing page. | Proposed Platform router over existing Operations Timeline; do not create a second queue or unpermissioned cross-domain incident feed. |
| Jobs & Scheduler | /staff/admin-desk/operations/jobs/<int:job_id>/; Job and PeriodicJob in Django Admin; runjobs management command | Existing read-only Job detail and Django Admin queue; JobAdmin disables add/delete and makes all fields readonly. PeriodicJob configuration is editable while last-run/status/error/cursor are readonly. | Proposed unified inspection view. Keep durable Job, PeriodicJob and worker lifecycle as separate concepts. No manual status changes, retry/replay/delete in V1. |
| Access & Provisioning | /staff/admin-desk/operations/provisioning/<int:operation_id>/; /staff/admin-desk/operations/; ProvisioningOperation, UserChannelAssignment, ChannelMembershipSnapshot, BotAccessAudit | Existing read-only operation detail and timeline signals; underlying integration records are in Django Admin. Membership snapshots are display-only; operation has an explicit unknown state. | Proposed unified inspection view. Keep intent, entitlement assignment and observed membership separate. Unknown state must not become failure; no direct grant/revoke control. |
| Integrations & Webhooks | /bot-admin/verify-bot/, /bot-admin/verify-control-channel/, /bot-admin/verify-target-channel/<int:mapping_id>/; superuser-only /bot-admin/test-grant-revoke/; /bot/telegram/webhook/; /bot/api/register/, /bot/api/heartbeat/; /webhooks/stripe/, /webhooks/razorpay/; /api/email/webhooks/resend/; Academy Drive route /staff/google-drive/connect/ | Existing provider endpoints and admin fragments. Telegram native Bot API is called by Django via BotConfig. BotRuntimeState is legacy bridge diagnostic. Stripe/Razorpay use durable WebhookEvent; Resend updates Delivery only; Telegram has no durable webhook ledger verified. Google Drive is course-admin-only and Academy-owned. | Proposed integration inspection page with distinct evidence models. Keep secrets and raw payloads restricted. Do not claim a single unified health signal. Do not move Google Drive ownership out of Academy or expose the live grant/revoke test as an ordinary action. |
| Audit & Security | /staff/admin-desk/operations/ summaries; AuditLog, SecurityEvent, BotAccessAudit, Event, PolicyAcceptance and WebhookEvent model/admin sources | Existing event and audit sources; Ops Timeline permission-filters summary sections. SecurityEvent is append-only at model level; AuditLog has no append-only model guard verified. | Proposed source-specific evidence workspace. Preserve event/audit/security/webhook distinctions; redact raw IP, user-agent, provider payload and sensitive identifiers. |
| Policies & Readiness | sales_policy_readiness() from staff dashboard; PolicyVersion and PolicyAcceptance in Django Admin; Revenue business settings/readiness via /staff/admin-desk/business/; /health/ | Existing partial readiness checks and policy publication/admin surface. /health/ only probes the primary database with SELECT 1. PolicyVersion published-content immutability is not fully enforced by inspected save/admin path. | Proposed view separating policy active/placeholder state, configuration presence and actual end-to-end test evidence. Revenue remains owner of business settings. Do not present DB health or credential presence as full service health. |
| Staff & Permissions | /api/admin/staff-approvals/; /api/admin/staff-approvals/action/; /api/admin/ban/; /api/admin/unban/; Django Admin User, Group and permission models | Existing staff approval/ban API and Django Admin access control; no unified Admin Desk staff approval screen or complete assigned-role matrix verified. IsRoleAdmin allows role=ADMIN OR superuser OR any is_staff. | Proposed initially read-only access explainer and permission matrix. Ban/unban remains in Customers. Staff approval migration requires a corrected authorization gate, maker/checker policy and explicit action permission. |
| Migration Boundary / Advanced Administration | /admin/ and custom /bot-admin/ | Existing Django Admin/custom staff surfaces remain authoritative for un-migrated operational configuration and privileged actions. | Proposed inventory of read-first vs controlled-action vs keep-advanced. Retain superuser-only Telegram grant/revoke test, credentials, role/group assignment and high-risk publication/configuration until safe parity and source hardening exist. |

Existing Admin Desk operational routes:
- /staff/admin-desk/operations/ — permission-aware 24h/7d timeline; includes ticket clusters and, according to model permissions, job, provisioning, PeriodicJob, domain Event, AuditLog and SecurityEvent summaries.
- /staff/admin-desk/operations/jobs/<int:job_id>/ — read-only Job detail; requires jobs.view_job.
- /staff/admin-desk/operations/provisioning/<int:operation_id>/ — read-only ProvisioningOperation detail; requires jobs.view_provisioningoperation.
- /health/ — database SELECT 1 probe only.

Important migration caveats:
- Durable Job queue is worker-owned and read-only. A “stalled” filter is not a Job status.
- PeriodicJob is a separate lightweight inline scheduler; do not combine its last result with durable worker status.
- ProvisioningOperation state, UserChannelAssignment entitlement and ChannelMembershipSnapshot observation are three separate records.
- Native Telegram Bot API is the current direct Django path; BotRuntimeState is legacy bridge diagnostic only.
- Stripe/Razorpay WebhookEvent is durable and idempotent; Resend updates G1 Delivery only; Telegram webhook persistence was not verified.
- Runtime readiness checks infer configuration presence, not successful provider auth, payment, webhook, email, backup or restore.
- PolicyVersion published content and AuditLog immutability require hardening review before migration.
- Staff/application roles, is_staff, is_staff_approved, active, superuser and Django Groups/model permissions must not be collapsed into one role badge.

## 8. Routes that are not Admin Desk destinations

These routes exist for public/member/API/provider flows and should not appear as staff workspace pages merely because they share models:

- `/api/academy/catalogue/` — public course catalogue API.
- `/learn/...` — learner-facing Academy pages, progress and protected media.
- `/buy/course/<slug>/`, `/start/`, `/confirm/`, `/checkout/...` — learner checkout/payment journeys.
- `/api/subscriptions/...` — member/subscription APIs and actions.
- `/growth/referrals/` — member-facing referral dashboard (not the staff Growth Console).
- `/api/notifications/...` — authenticated user's notification API.
- `/api/email/webhooks/resend/`, `/webhooks/stripe/`, `/webhooks/razorpay/` — provider callbacks, not UI destinations.
- `/support/...` — member support-ticket interface, distinct from staff ticket queue.
- `/bot-admin/...` — integration administration; exact migration scope requires role and route audit.

## 9. First-release migration principle

The redesigned shell can link to an existing destination before that destination is visually migrated, provided the hand-off is clear and permissions remain intact. Do not create a fake new page solely to make the sidebar look complete.

Suggested migration sequence by workflow:

1. Shared shell + Command Centre action-first home.
2. Move existing Course Approvals, SEO, Support, Customer 360, Accounts, Subscriptions, Finance, Business and Operations destinations into consistent shell presentation, retaining their established services and permissions.
3. Build missing unified workspaces over existing records: Academy Catalogue, Course Detail, Offers & Access, standalone Learner Access, Revenue plan/pricing detail, Growth, Platform job/provisioning register, and role/permission explainer.
4. Move selected Django Admin model workflows only after parity and audit review.
5. Retain Advanced Administration for low-frequency or high-risk functions that have not earned a safe replacement.

This is a source-based route map for design planning. It does not authorise route/view or application-code changes.


## Academy screen-design follow-up — 14 November 2026

The detailed Academy prototype and specification are recorded in:

- `ACADEMY_WORKSPACE_SPEC_V1.md`
- `tradethesis_admin_academy_workspace_v1.html`

The screen-level proposal covers Academy Overview, Course Catalogue, Course Detail, Approvals Queue, Review Detail, Course Builder hand-off, Offers & Access, Learner Access & Progress and SEO & Discoverability. All sample data is illustrative; proposed screens do not imply that a dedicated production route already exists.


## Customers screen-design follow-up — 14 November 2026

The detailed Customers prototype and specification are recorded in:

- `CUSTOMERS_WORKSPACE_SPEC_V1.md`
- `CUSTOMERS_REVIEW_NOTES_V1.md`
- `tradethesis_admin_customers_workspace_v1.html` (standalone HTML artifact supplied in the design review conversation)

M27 Customers Overview and M28 Learner Account Detail are proposed page structures. M12, M10, M11 and M13 redesign current source-backed account/support/customer workflows while preserving their permission, SLA and lifecycle rules. The sample data remains illustrative.


## Revenue screen-design follow-up — 14 November 2026

The Revenue prototype and specification are recorded in:

- `REVENUE_WORKSPACE_SPEC_V1.md`
- `REVENUE_REVIEW_NOTES_V1.md`
- `tradethesis_admin_revenue_workspace_v1.html`

The current Admin Desk finance register is read-only. Manual FULL refund recording remains an Advanced Administration action after provider-side refund. Product/Plan/pricing editing remains Django Admin. Disputes have a separate staff route and are proposed to be surfaced under Revenue navigation while preserving their existing case model/service/permissions. All prototype records are illustrative.


## Growth screen-design follow-up — 14 November 2026

The Growth prototype and specification are recorded in:

- `GROWTH_WORKSPACE_SPEC_V1.md`
- `GROWTH_REVIEW_NOTES_V1.md`
- `tradethesis_admin_growth_workspace_v1.html`

The current pages are proposed unified workspaces over existing models/admin routes; only the Analytics API, staff gift-send route, member referral routes and delivery/webhook foundations were source-backed. Campaign send provider remains stub, extra campaign channels remain staged, and the referral reward/analytics integrity caveats are documented in the specification.


## Platform screen-design follow-up — 14 November 2026

The Platform prototype and specification are recorded in:

- PLATFORM_WORKSPACE_SPEC_V1.md
- PLATFORM_REVIEW_NOTES_V1.md
- tradethesis_admin_platform_workspace_v1.html

The proposal extends the existing permission-filtered Operations Timeline and read-only job/provisioning detail routes. It does not introduce queue mutation or direct external-access actions. Source gaps and Advanced Administration boundaries are documented in the Platform specification.
