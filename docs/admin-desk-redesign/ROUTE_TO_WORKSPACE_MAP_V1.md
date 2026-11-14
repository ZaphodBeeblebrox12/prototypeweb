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
| Offers & Access | `CourseOffer`, `Plan`, `PlanPrice`, `GeoPlanPrice`, `CourseEntitlement` and related models; some record management remains in Django Admin | Existing underlying models and validations; no dedicated unified Admin Desk page verified | Proposed Academy workspace owns the CourseOffer-to-Course relationship. Open canonical Plan/price details in Revenue. |
| Learner Access & Progress | Customer 360 exposes permission-scoped entitlements, progress and events at `/staff/admin-desk/customers/<uuid:user_id>/`; underlying model administration also exists | Existing data and Customer 360 context; no standalone Academy access workspace verified | Proposed standalone access/progress workspace with links to the canonical learner record. |
| SEO & Discoverability | `/staff/admin-desk/seo/` | Existing dedicated Admin Desk diagnostic | Keep in Academy and link each issue to Course detail/Builder. |

## 4. Customers

| Proposed tab | Current route/source | Current state | Design mapping |
|---|---|---|---|
| Overview | Accounts, support and Customer 360 links are embedded in `/staff/admin-desk/` | Existing summary links; no dedicated Customers landing page verified | Proposed Customers landing focused on tickets, learner lookup and member-impacting work. |
| Learners & Accounts | `/staff/admin-desk/accounts/`; detail `/staff/admin-desk/accounts/<uuid:user_id>/`; actions `.../action/` | Existing Admin Desk list/detail/action routes | Canonical owner of learner account operations. Staff/superuser accounts stay outside the normal learner list. |
| Support Tickets | `/staff/admin-desk/support/tickets/`; detail `.../support/tickets/<uuid:ticket_id>/`; actions `.../action/` | Existing Admin Desk queue/detail/actions | Canonical owner of ticket status, assignment, priority, public reply and internal note. Preserve reviewer scope and SLA. |
| Customer 360 | `/staff/admin-desk/customers/<uuid:user_id>/` | Existing read-oriented, permission-scoped cross-domain record | Retain as full-page relationship hub; add only a compact contextual preview within ticket detail. |

## 5. Revenue

| Proposed tab | Current route/source | Current state | Design mapping |
|---|---|---|---|
| Overview | Payment, subscription and invoice summaries are included in `/staff/admin-desk/` | Existing permission-filtered summaries | Proposed Revenue landing with exception-led work and commercial context. |
| Payments & Refunds | `/staff/admin-desk/finance/` (finance view includes payment/invoice sections); member/provider flows also use `/start/`, `/confirm/`, `/history/`, `/receipt/<uuid>/`; provider webhooks `/webhooks/stripe/` and `/webhooks/razorpay/` | Existing staff finance page and payment APIs/workflows | Proposed canonical staff transaction register/detail. Do not expose customer checkout routes as admin destinations. |
| Subscriptions & Plans | `/staff/admin-desk/subscriptions/`; plan configuration and prices are also in Django Admin; subscription APIs under `/api/subscriptions/` | Existing subscription staff workspace; plan/price configuration is not yet verified as a unified Admin Desk page | Proposed Revenue plan catalogue/detail and subscription register. Preserve price snapshots and product-scoped subscription behaviour. |
| Invoices | `/staff/admin-desk/finance/?tab=invoices`; detail `/staff/admin-desk/invoices/<uuid:invoice_id>/` | Existing finance section and invoice detail | Keep invoice detail linked to its source PaymentIntent and Customer 360. |
| Disputes | `/admin-disputes/`; detail `/admin-disputes/<uuid:pk>/` and actions under the same prefix | Existing separate dispute workflow | Map into Revenue navigation while retaining the existing dispute business process and permissions. |
| Business & Finance | `/staff/admin-desk/business/`; finance `/staff/admin-desk/finance/` | Existing staff-facing billing/business settings and readiness checks | Keep as controlled configuration/readiness destination; distinguish configured from tested. |

## 6. Growth

| Proposed tab | Current route/source | Current state | Design mapping |
|---|---|---|---|
| Overview | Admin-only analytics API and Django Admin growth models | Existing data sources; no full unified Growth landing page verified | Proposed Growth home connecting acquisition, referral, gift and delivery work. |
| Analytics | `/api/analytics/overview/` | Existing admin-only reporting API for signup, email, campaign, promotion and referral sections | Proposed human-readable Analytics UI over verified API output; keep definitions/time windows explicit. |
| Campaigns & Promotions | Campaign/promotion performance data appears in analytics; model/configuration details remain in Django Admin pending full inventory | Existing reporting/configuration fragments; unified management page not verified | Proposed workspace only after source model, attribution and action inventory is complete. |
| Referrals & Rewards | `/growth/referrals/` (member-facing referral dashboard); `/growth/admin/referral-rewards/` (admin reward view); growth models/settings also in Django Admin | Existing member and admin routes plus referral/reward models | Proposed Growth record views; do not confuse member referral dashboard with staff administration. |
| Gifts | `/admin/growth/send-gift/` and success route under same prefix; gift claim/customer state is recorded through Growth and Subscription models | Existing custom Django Admin gift-sending workflow | Proposed staff workspace in Growth; preserve claim, expiry and resulting gifted Subscription relationships. |
| Email Delivery | `EmailLog`, Resend delivery/bounce/complaint webhook at `/api/email/webhooks/resend/`, suppression and marketing preference models/admin | Existing delivery event and model/admin sources; no complete unified delivery console verified | Proposed read-first email operations view. The webhook is an inbound provider endpoint, not an operator UI. |

## 7. Platform

| Proposed tab | Current route/source | Current state | Design mapping |
|---|---|---|---|
| Overview | Operational signals are available in `/staff/admin-desk/` and `/staff/admin-desk/operations/` | Existing aggregated signal sources | Proposed Platform landing with job, provisioning, integration and readiness exceptions. |
| Background Jobs | Job detail `/staff/admin-desk/operations/jobs/<int:job_id>/`; job list/admin model in Django Admin; PeriodicJob is in Django Admin | Existing read-only detail and model administration | Proposed unified queue/register, but do not invent retry/cancel controls; current detail is read-only. |
| Provisioning & Integrations | `/staff/admin-desk/operations/provisioning/<int:operation_id>/`; timeline at `/staff/admin-desk/operations/`; related Telegram/Discord and bot admin routes | Existing read-only operation detail and related integration administration | Proposed Platform workspace; show safe external state without leaking invite links, payloads or raw provider IDs. |
| Security & Audit | AuditLog, SecurityEvent and domain Event models/admin; selected summaries in `/staff/admin-desk/operations/` | Existing model/event sources and timeline summary; separate detailed views live in admin/model tools | Proposed permission-scoped investigation destination with source type preserved. |
| Policies & Readiness | Business readiness at `/staff/admin-desk/business/`; policy versions through Django Admin and readiness summary in staff dashboard | Existing partial checks and configuration surfaces | Proposed Platform view; preserve configured-vs-tested distinction and link to Revenue business configuration where appropriate. |
| Staff & Permissions | Django Admin users/groups/permissions and object/plan-specific scopes | Existing administration in Django Admin; no unified permission explainer verified | Proposed initially read-only role/permission explainer; editing stays in Advanced Administration until safe parity exists. |
| Advanced Administration | `/admin/` (including custom `/admin/growth/...` destinations) | Existing Django Admin and custom admin destinations | Retain as visually secondary migration destination; do not remove capabilities until reviewed parity exists. |

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
3. Build missing unified workspaces over existing records: Academy Catalogue, Offers & Access, Learner Access, Revenue plan/pricing detail, Growth, Platform job/provisioning register, and role/permission explainer.
4. Move selected Django Admin model workflows only after parity and audit review.
5. Retain Advanced Administration for low-frequency or high-risk functions that have not earned a safe replacement.

This is a source-based route map for design planning. It does not authorise route/view or application-code changes.
