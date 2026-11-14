# TradeThesis Admin Desk — Platform Workspace Specification V1

**Status:** First screen-level design proposal; owner review pending  
**Date:** 14 November 2026  
**Planning branch:** `admin-desk-redesign-planning`  
**Source baseline:** `my-new-branch`  
**Visual template:** Approved V2 forest-green / warm-ivory shell with restrained terracotta and sage, editorial serif headings and compact sans-serif controls.  
**Implementation status:** Planning and static mockup only. No application code, routes, permissions, APIs, database records, credentials, jobs, provider calls or deployment settings have been changed.

## 1. Purpose and design intent

Platform owns the operational infrastructure and governance records that support the other five domains. It should answer:

- Is the application process responding?
- Are durable background jobs moving through their worker lifecycle?
- Are lightweight periodic tasks running within their schedule and API budget?
- Is community access converging toward the entitlement the learner currently owns?
- Are external providers and webhook event paths observable without exposing secrets?
- Can staff inspect audit/security evidence within their actual permissions?
- Are business, payment and legal readiness checks configured, tested and evidenced?
- Who can see or operate each capability?

Platform must not become a second Command Centre, a duplicate job queue or a replacement for the canonical Revenue, Customers, Academy or Growth records.

The existing Operations Timeline at `/staff/admin-desk/operations/` is the operational foundation. Platform should organise and extend that existing read surface, not create a competing event timeline.

## 2. Screen inventory

The clickable prototype contains eight destinations:

| ID | Screen | Purpose | Source status |
|---|---|---|---|
| M42 | Platform Overview | Permission-aware operations and service-health summary; route to canonical incident detail | Proposed landing over existing operational sources |
| M43 | Jobs & Scheduler | Separate durable Job queue, PeriodicJob scheduler and worker lifecycle | Existing Django Admin models; proposed unified read view |
| M44 | Access & Provisioning | Separate provisioning intent, entitlement assignment and observed membership | Existing read-only Admin Desk detail and Django Admin records |
| M45 | Integrations & Webhooks | Provider configuration status, webhook receipt/processing evidence and integration ownership | Existing endpoints/admin fragments; no unified integration monitor verified |
| M46 | Audit & Security | Domain activity, staff audit records, bot-access audit and restricted SecurityEvent evidence | Existing Ops Timeline summaries and model/admin sources |
| M47 | Policies & Readiness | Policy version/readiness and operational configuration-vs-test evidence | Existing readiness helper and Django Admin publication surface |
| M48 | Staff & Permissions | Explain current staff dimensions, approval API and proposed permission matrix | Existing User/Group/model permission system and API; no unified matrix verified |
| M49 | Migration Boundary | Catalogue what can migrate, what needs parity and what must remain Advanced Administration | New planning artefact over existing source capability |

All names, IDs, timestamps, incidents, counts, job states, integration states, policy versions, staff candidates and configuration status displayed in the mockup are fictional illustrative data. The prototype is static, makes no live API calls, reads no credentials, and does not enqueue, retry, replay, cancel, reassign or mutate operational work.

## 3. Canonical ownership and non-goals

Platform owns:
- `Job`, `PeriodicJob`, `ReconcileState` and `ProvisioningOperation`.
- Integration runtime status models such as `BotRuntimeState` (legacy bridge diagnostic only).
- Integration configuration/evidence models such as `BotConfig`, `PlanChannelMapping`, `UserChannelAssignment`, `CommunityChannel`, `ChannelMembershipSnapshot` and `BotAccessAudit`.
- `WebhookEvent` for Stripe/Razorpay provider events.
- `AuditLog` and `SecurityEvent`.
- `PolicyVersion` and `PolicyAcceptance`.
- User role/group/model-permission governance as a cross-cutting access-control concern.

Canonical owners remain:
- **Customers:** User identity, staff/customer account context and support ticket records.
- **Revenue:** PaymentIntent, Refund, Subscription, Plan, BillingSettings, Invoice and disputes.
- **Academy:** Courses, CourseOffer, learning progress and Google Drive course-asset workflow.
- **Growth:** Campaigns, marketing/referral/reward, coupons, gifts and email Delivery/consent records.
- **Command Centre:** cross-domain work aggregation, notification/attention state and routing only.
- **Platform:** operational job/provisioning/configuration/evidence records, not customer commercial entitlement.

The Platform interface may show a related Customer, PaymentIntent, Subscription, Course, campaign or support ticket only when the viewer has the relevant owning-domain permission. Cross-links should open canonical records; they should never create a second editable copy.

Non-goals:
- No hand-editing or deletion of durable Job rows.
- No generic retry/replay/re-enqueue button.
- No direct manual grant/revoke of external membership from the ordinary Operations UI.
- No raw provider secret, invite URL, full webhook payload, raw IP or full user-agent in global search or broad tables.
- No replacement of the existing worker/scheduler or provisioning services.
- No claim that a configuration-presence check proves a real provider round-trip.
- No staff role/group/permission editing in the prototype.
- No legal-policy publication action without explicit accountable approval and enforcement review.

## 4. Source-verified operational model

### 4.1 Durable Job queue

Source: `backend/apps/jobs/models.py`, `worker.py`, `enqueue.py`, `handlers.py`, `admin.py`.

Job fields include kind, JSON payload, status, requested reconciliation version, attempts, max_attempts (default five), next_attempt_at, lock timestamp, creation/update timestamps and a conditional unique idempotency key for open jobs.

Current state machine:
- Pending: waiting for due execution / retry.
- Running: claimed by a worker.
- Succeeded: handler completed and the open idempotency key was released.
- Failed: terminal failure after max attempts.

Worker semantics:
- `claim_next` claims a due pending job, sets Running, records lock time and increments attempts.
- Generic failure returns the job to Pending with exponential-ish linear backoff `30 seconds × attempts`; at max attempts it becomes Failed.
- A reaper resets Running jobs with `locked_at` older than 300 seconds to Pending.
- Two long-running video job kinds have lease heartbeat every 45 seconds.
- Reconciliation jobs use a desired-state version and bounded convergence (maximum ten iterations in the inspected enqueue/worker code); if state moves forward during work, the worker adopts the latest version rather than claiming success on stale work.
- Built-in handlers cover reconcile, video processing/cleanup, sweep, subscription expiry/reminders, payment webhook processing, campaign sends, automation, referral unlock and MaxMind updates.
- Management command is `python manage.py runjobs [--loop] [--sleep N] [--once] [--kind]`.

Admin boundary:
- `JobAdmin` is read-only, disables add and delete, and has a filter for open jobs with three or more attempts.
- Existing Admin Desk job detail is read-only and uses only a restricted field set.
- No staff retry/cancel/replay operation was verified in the inspected Admin Desk route.
- Do not present the “stalled” filter as a Job status. It is a filter over Pending/Running jobs with attempts >= 3.
- A Failed row is evidence of the worker's final state, not permission to manually change the Job.

Proposed UI:
- Show status, kind, attempts/max attempts, due time, lock age, created/updated and safe detail.
- Label a stalled filter separately from the status field.
- Show expected next step as “inspect owner record / worker logs” unless a safe existing action is verified.
- Link to the canonical business object only if its owner-domain permission is present.
- Keep payload and idempotency keys restricted or masked.
- No retry, replay, delete or state-change control in V1.

Existing routes:
- Timeline: `/staff/admin-desk/operations/`.
- Job detail: `/staff/admin-desk/operations/jobs/<int:job_id>/` (requires `jobs.view_job`).
- Job model list and diagnostics: Django Admin `/admin/` (read-only).

### 4.2 Periodic scheduler

Source: `backend/apps/jobs/models.py`, `scheduler.py`, `apps.py`, `handlers.py`, `admin.py`.

`PeriodicJob` is separate from durable `Job`. It stores a handler name, enabled flag, interval_minutes, last_run_at, last_status (OK/Error), last_error, max_calls_per_run API budget and a JSON scheduler cursor.

Current scheduler:
- Started from `JobsConfig.ready()` in long-lived server processes; one-shot commands/tests are skipped.
- A Django daemon thread polls every 60 seconds and uses a cache lock plus a database row-lock/reservation of last_run_at to avoid duplicate cross-worker execution.
- Periodic tasks run inline and are intended only for light housekeeping such as membership syncs/digests, not heavy processing.
- A registry maps supported names to handler functions: `sync_channel_memberships`, `win_back_expired`, `welcome_sequence`.
- An unsupported handler name becomes an error (“no handler registered for ...”).
- Scheduler also performs a best-effort bounded inline drain of up to five durable Jobs per tick. A dedicated supervised `runjobs --loop` worker remains the separate durable worker process.
- `PeriodicJobAdmin` keeps last_run_at, last_status, last_error, state cursor and created_at read-only; operational configuration such as enabled, interval and max_calls_per_run is editable in Django Admin.

Proposed UI:
- Dedicated Periodic scheduler sub-section; do not combine rows/statuses with durable Jobs.
- Show enabled state, interval, handler registration, API budget, last run and last result.
- Clearly label last_run_at as a reservation/start reference (the scheduler stamps it before the handler call), not proof of successful completion.
- Explain inline scheduler drain vs dedicated worker.
- Preserve a fixed supported-handler list until code-backed handler registration is available.
- Schedule edits are a later permissioned migration candidate; no direct editing in the prototype.

### 4.3 Access and provisioning

Sources: `backend/apps/jobs/models.py`, `operations.py`, `apps/bot_integration/models.py`, `reconcile.py`, `reconcile_jobs.py`, `admin_desk_views.py`.

These three records must remain separate:

1. **ProvisioningOperation** — one persisted external side-effect lifecycle (grant/revoke) with a unique operation id, user/channel identifiers, operation state, invite link, attempts and last error.
2. **UserChannelAssignment** — integration-managed entitlement mapping. Its `is_active` flag represents an active provisioned entitlement assignment; it does not prove live external membership.
3. **ChannelMembershipSnapshot** — observed membership at a checked_at time. It is explicitly display-only and must never drive access control.

Provisioning operation states:
- Pending → Creating → Created → Sending → Sent → Completed.
- Unknown external state is a separate state when a provider response cannot determine whether the action occurred.
- Failed is a separate state, with next recovery governed by the existing reconciliation path.
- Grant and revoke are distinct operations; a grant after completed revoke starts a new lifecycle.

Grant recovery safeguards:
- A persisted invitation link is saved before the DM attempt and reused on retries.
- For SENDING, SENT or UNKNOWN recovery, a read-only membership probe occurs first.
- If member=true, operation can complete; if result is unknown/None, no invite is re-sent.
- Only a definite non-member result permits invite recovery.
- An atomic six-hour resend claim prevents concurrent duplicate recovery sends.
- The narrow crash window in which the invite may have been created but the URL was not persisted is documented; recovery can create one replacement link and still checks membership first.

Revoke:
- Revoke request is followed by a read-only membership probe.
- A successful provider response alone is not enough; completion requires the user to be verified absent.
- Discord reconciliation changes only roles mapped by this integration and preserves unrelated server roles.

Safety:
- The configured control/admin Telegram channel cannot be mapped as a subscriber target.
- Current Admin Desk provisioning detail intentionally omits external IDs and raw payloads.
- Do not show invite URLs, tokens or raw identifiers in broad UI.
- Do not provide an ordinary staff “grant” or “revoke” button. Existing live manual `test_grant_revoke` is superuser-only and should remain in Advanced Administration.
- Failed/unknown operation is not permission to hand-edit UserChannelAssignment.
- Existing Admin Desk timeline is read-only; detail route is `/staff/admin-desk/operations/provisioning/<int:operation_id>/` and requires `jobs.view_provisioningoperation`.

### 4.4 Integrations and runtime state

**Telegram**
- Current main path calls Telegram Bot API directly from Django using the singleton `BotConfig` token.
- Staff verification page calls `getMe` and records latency; control channel and target channel have separate verification routes.
- Native webhook route is `/bot/telegram/webhook/`, authenticated by `X-Telegram-Bot-Api-Secret-Token`; a signed legacy bridge fallback remains for controlled rollback.
- Custom staff-only tools are mounted under `/bot-admin/`: verify bot, verify control channel, verify target channel and superuser-only live grant/revoke test.
- No separate durable Telegram webhook event ledger was verified.

**Discord**
- OAuth callback and role sync are separate from Telegram.
- Reconciliation uses live member-role reads and only changes managed PlanChannelMapping roles.
- Account linking/role context is a different concept from community provisioning outcome.
- Do not infer actual guild role state from an old cached roles list without a live read.

**Legacy bot bridge runtime**
- `BotRuntimeState` records a self-registered bridge instance, base URL, provision contract/version, advertised operations and last_seen.
- It can be marked Online/Offline/Incompatible based on heartbeat freshness and compatibility.
- Inspected integration admin explicitly describes it as legacy bridge diagnostic history; current native provisioning calls Telegram Bot API directly from Django.
- Do not label the legacy bridge heartbeat as current native Telegram Bot API health.

**Google Drive**
- Google Drive OAuth and encrypted refresh token belong to Academy course-content administration.
- It creates private asset/source/support folders, and does not grant public or anyone-with-link access.
- OAuth route is `/staff/google-drive/connect/`; access is course-admin-restricted.
- Keep its configuration/action in Academy context, not as a general Platform credential editor.

No unified integration health monitor or universal “test all providers” operation was verified.

### 4.5 Webhook evidence

**Stripe and Razorpay**
- Routes: `/webhooks/stripe/` and `/webhooks/razorpay/`.
- Receive code verifies signature, obtains provider event ID/type, creates one durable `WebhookEvent` per (provider, provider_event_id), and enqueues a `process_webhook_event` durable Job only when the event row is newly created.
- `WebhookEvent` statuses: Received, Processed, Failed, Ignored.
- The processor handles business mutations through canonical payment/refund/dispute/subscription services; terminal Processed/Ignored events are not reprocessed. Job retries wrap processor execution.
- `WebhookEventAdmin` is read-only with add/delete disabled.
- Raw payload may contain payment/customer data. Do not expose raw payload in broad tables, global search or normal detail preview.

**Resend**
- Route: `/api/email/webhooks/resend/`.
- Signed Svix-style callback updates G1 `Delivery` state by provider message ID and recipient.
- It does not create a separate durable webhook ledger and does not update legacy transactional `EmailLog`.
- EmailLog and Delivery remain distinct.

**Telegram**
- Native Telegram webhook is secret-header authenticated; no durable webhook event ledger was verified in the inspected app.

**Discord**
- OAuth callback is a session-state validated login/connection callback, not a provider webhook inbox.

Do not display one combined “webhooks healthy” badge from these different evidence models.

### 4.6 Operations Timeline and health endpoint

Existing Admin Desk route `/staff/admin-desk/operations/` supports 24h and 7d windows (default 7d), with permission-filtered sections:
- Support issue clusters / recent reviewer-visible tickets.
- Job incidents: recent Failed, open Pending/Running with attempts >=3, Running with lock age >15 minutes.
- Provisioning incidents: Failed and Unknown external state.
- PeriodicJob errors.
- Domain Event rows.
- AuditLog activity.
- SecurityEvent aggregate counts.

It bounds ticket clustering/feed data, sorts the activity timeline and only includes optional sections when the user has the relevant model permission:
- `jobs.view_job`
- `jobs.view_provisioningoperation`
- `jobs.view_periodicjob`
- `events.view_event`
- `audit.view_auditlog`
- `accounts.view_securityevent`

The job/provisioning detail URLs are existing read-only Admin Desk routes. Preserve the independent section-permission checks in lists, counts, search and cross-links.

The public `/health/` endpoint is only a primary database readiness probe: executes `SELECT 1`, returns status ok or unavailable. It does not test worker, scheduler, providers, webhooks, email delivery, storage/Drive, backup/restore or community provisioning. Do not display it as a complete Platform health score.

### 4.7 Audit and security evidence

**AuditLog**
- Stores actor (nullable), action, object_type, object_id, metadata and timestamp.
- It has a model helper to create audit records.
- The inspected model does not enforce append-only in its `save()`; Django Admin exposes some editable fields (ID/created_at readonly, but other values not all readonly). This is an integrity hardening question, not an assumption that the record is immutable.

**SecurityEvent**
- Records login success/failure, password changed, email verified, MFA enabled and account-takeover flag.
- Model prevents updating an existing record (append-only).
- Source comment describes raw IP restriction and 13-month retention evidence plan, but this pass does not prove that every query/export enforces the stated restriction or that deletion/retention jobs are implemented.
- Broad lists should mask IP, full user-agent and detail metadata.

**BotAccessAudit**
- Records grant/revoke/link/unlink/sync action, platform, outcome and error.
- Django Admin view is read-only, with add/change/delete disabled.

**PolicyAcceptance**
- Write-once record tied to exact immutable-by-intent PolicyVersion, context, timestamp, IP/user-agent, session hash and optional checkout evidence.
- It is used as evidentiary context for accepted policy version, not a mutable preference.

**Events**
- Domain Event store is business-transition evidence and distinct from AuditLog staff activity and SecurityEvent authentication signals.

Recommended event screen:
- Source-specific filters: domain event / audit / security / bot-access / provider webhook.
- Preserve exact event type/action and source table.
- Distinguish user-facing actor, staff actor and system actor.
- Show redacted detail by default, with permission-specific access to deeper evidence.
- No edit/delete/replay/acknowledgement controls in V1 unless source contract and permission audit explicitly support them.

### 4.8 Policies and readiness

**PolicyVersion**
- Types: Terms, Refund, Cancellation, Risk, Privacy.
- States: Draft, Active, Archived; database constraint allows one active version per policy type and one version identifier per type.
- Publishing a version atomically archives previous Active version and activates the selected version.
- **Important enforcement gap:** the inspected `PolicyVersion.save()` recalculates content hash every save, but does not refuse content changes after publication; Django Admin does not make published content fields read-only. The model/design comments describe published versions as immutable, but the inspected enforcement does not fully guarantee that property. Do not migrate a published-policy editor until this is addressed.
- `PolicyAcceptance` is write-once at model level and records exact version.
- `sales_policy_readiness()` checks whether each expected launch policy has an Active version and whether known placeholder text markers remain. It does not establish legal sign-off.

**Runtime configuration readiness**
- Existing Admin dashboard checks presence of database engine, public HTTPS base URL, SMTP settings, Razorpay credentials/webhook secret and optional Stripe settings.
- These are configuration-presence checks only. For example, configured credentials do not prove provider authentication, webhook receipt, real payment, backup/restore or email delivery.
- Current DB engine warning differentiates SQLite from server database; it explicitly says backup/restore requires separate proof.

Proposed UI:
- Split “Configured” from “Verified” and “Evidence missing”.
- Keep policy publication separate from technical integration readiness.
- Preserve Revenue as canonical owner of seller/billing configuration; Platform can show readiness status and cross-link to Revenue.
- No legal publish action or credential editor in the Platform prototype.

### 4.9 Staff and permissions

Current user access dimensions are not interchangeable:
- `is_active` (account can authenticate).
- `is_staff` (staff-gated Admin Desk / Django Admin entry).
- application `role`: Admin, Staff, User.
- `is_staff_approved` flag.
- Django `PermissionsMixin`: groups and per-model permissions.
- Superuser bypasses model permissions in certain guards.
- Academy course-content permission helper and reviewer/finance/plan-specific scope are additional constraints.

Existing API:
- `/api/admin/staff-approvals/` lists users where role=STAFF and is_staff_approved=False.
- `/api/admin/staff-approvals/action/` approves (sets role STAFF, is_staff True, is_staff_approved True) or rejects (sets role USER, is_staff False, is_staff_approved False).
- The API class permission named `IsRoleAdmin` allows an authenticated role=ADMIN **or any is_superuser or any is_staff**. This is broader than a strict Admin-only permission name/comment; do not assume only role=ADMIN can access these endpoints.
- Ban/unban APIs are in the same class-level permission; they create AuditLog and are a Customers-owned account action.
- No Admin Desk staff approval screen or complete role/group permission matrix was verified. The mockup's staff matrix is a proposal and must not be represented as existing assignments.
- The proposed matrix should be based on a full staff-user / Django Group / model permission inventory before implementation.
- Actual sensitive security, integration, policy and external access controls must remain server-side; hiding a button is never authorization.

The prototype has no staff approve/reject, ban/unban, grant/revoke or group/permission mutation action.

## 5. M42 — Platform Overview

Purpose: answer “Which system is showing a source-backed operational issue and where is its canonical owner?”

Recommended hierarchy:
1. Existing Operations Timeline deep-link and high-signal exceptions: failed/stalled worker work, unknown provisioning state, periodic handler errors, payment webhook processing errors and permission-safe security signals.
2. Separate compact indicators for durable Jobs, PeriodicJob errors, unknown/failed ProvisioningOperation, provider webhook states and readiness gaps.
3. Domain ownership hand-offs: Customers for user/ticket, Revenue for payment/subscription, Academy for course/video/Drive, Growth for campaigns/email, Platform for worker/configuration/evidence.
4. Clearly separate the existing source state from proposed alert/aggregation.

All counts in prototype are illustrative. The Platform Overview is an operational router and status context, not a second source of truth.

## 6. M43 — Jobs & Scheduler

Subsections:
- Durable queue.
- Periodic scheduler.
- Worker lifecycle.

The queue filter/search and job detail are local preview only. No live retry, replay, create, cancel, delete or state-edit action. A “stalled” filter is not a model status. PeriodicJob management is a separate later migration candidate with supported handler validation and explicit interval/API-budget permission.

## 7. M44 — Access & Provisioning

Show:
- ProvisioningOperation state, attempts, age and safe explanatory detail.
- UserChannelAssignment as entitlement-managed mapping.
- ChannelMembershipSnapshot as observed membership, timestamp and display-only context.
- Reconciliation lifecycle and recovery boundaries.

Never treat Unknown as Failed, Assignment Active as verified membership, or membership snapshot as entitlement. Never expose invitation links or raw external IDs in broad lists. No live grant/revoke button.

## 8. M45 — Integrations & Webhooks

Show separate cards/sections for:
- Telegram native Bot API.
- Discord OAuth and role sync.
- Academy-owned Google Drive.
- Stripe/Razorpay WebhookEvent inbox.
- Resend delivery callback.
- Telegram native webhook authentication.
- Legacy bridge BotRuntimeState diagnostics.

No universal integration health badge. Use “configured”, “probe available”, “heartbeat diagnostic”, “event received”, “processed”, “delivery updated”, and “not verified” precisely. Redact secrets and payload.

## 9. M46 — Audit & Security

Show separate sources:
- Operations Timeline.
- domain Events.
- AuditLog.
- BotAccessAudit.
- SecurityEvent.
- PolicyAcceptance and provider WebhookEvent links.

Keep raw IP, full user-agent, metadata/payload, identity and payment references permission-gated. Preserve append-only/immutable source distinctions. Highlight the current AuditLog and published PolicyVersion enforcement questions; do not imply they have been fixed.

## 10. M47 — Policies & Readiness

Separate:
- PolicyVersion types and Active/Draft/Archived lifecycle.
- PolicyAcceptance evidence.
- Launch policy readiness.
- Runtime configuration-presence checks.
- Real verification/evidence still needed.
- Primary DB `/health/` probe.

Show configured vs verified. No publication action, no credentials UI and no “all systems healthy” claim.

## 11. M48 — Staff & Permissions

Present the current dimensions separately: active status, staff flag, app role, staff approval flag, groups/model permissions, superuser and domain-specific scopes.

Show current staff-approval API and its source-level permission gate caveat. Keep proposed domain permission matrix clearly marked as not an existing assigned role set. Do not add controls to edit staff/role/group/permission or ban/unban records here.

## 12. M49 — Migration Boundary

For every record/control, classify:
- Migrate as read-only inspection.
- Migrate only after permission/service parity.
- Keep in Advanced Administration.
- Keep in owning domain or member-facing app.

Initial recommendations:
- **Read-only migration candidate:** current Operations Timeline, Job detail, Provisioning detail, WebhookEvent summary with redaction, BotAccessAudit and limited security summaries under existing permission gates.
- **Later after parity:** PeriodicJob configuration, bot configuration, channel mappings, policy draft editing/publication, staff-approval surface.
- **Keep in Advanced Administration / superuser-only:** live Telegram grant/revoke test, direct secret changes, manual provider test and highly privileged group/superuser editing.
- **Keep in owner domain:** Account ban/unban in Customers, billing/seller settings in Revenue, Google Drive asset/OAuth in Academy, campaign/email/marketing config in Growth.
- **Engineering hardening before migration:** published PolicyVersion content immutability; AuditLog append-only controls and privacy/retention enforcement; overbroad `IsRoleAdmin` class permission; staff approval maker/checker/audit contract; complete permission matrix; provider webhook payload masking.

This classification is a recommendation for owner review, not approval to implement or remove an existing admin feature.

## 13. Cross-domain operational journeys

1. Revenue payment captured → WebhookEvent durably stored → `process_webhook_event` Job → canonical PaymentIntent verification/activation → Subscription/CourseEntitlement → ProvisioningOperation if the current entitlement maps to community access.
2. Subscription entitlement changes → ReconcileState version increments → durable reconcile Job → diff-based desired access → Telegram/Discord operations → safe operation state → observed membership snapshot (display-only).
3. Learner disconnects/loses entitlement → Customers/Revenue canonical state changes → reconciliation job → managed channel/role revoke → provider membership probe → BotAccessAudit + AuditLog/related Event.
4. Periodic scheduler reserves a due PeriodicJob → light housekeeping handler runs and records last result → error appears in existing Operations Timeline; heavy work stays in durable Job worker.
5. PolicyVersion draft is approved and published → previous Active version archives → new acceptance records exact version → Revenue checkout/dispute evidence links that acceptance.
6. SecurityEvent login/ATO evidence → permission-scoped Audit & Security screen → Customers/Revenue only if separate owner-domain permission also exists.
7. Stripe/Razorpay webhook receive → signature verify → idempotent WebhookEvent store → durable Job → processor uses existing service → terminal event status and business record.
8. Resend signed webhook → G1 Delivery state update; no EmailLog or generic WebhookEvent row is created by the inspected handler.
9. Operations Timeline detects job/provisioning/periodic error → read-only Platform detail → canonical source owner determines remediation; no duplicate ad hoc recovery action.

## 14. Browser validation

**HTML:** `tradethesis_admin_platform_workspace_v1.html`

Browser smoke-test record (14 November 2026):
- All eight Platform destinations open.
- Durable queue and PeriodicJob subtabs switch.
- Staff role model and proposed permission matrix tabs switch.
- Job search and status filter work.
- Audit event source filter works.
- Job, provisioning, webhook and security preview modals open and close.
- Mobile drawer opens, navigates to Provisioning and closes after selection.
- 390px viewport has no horizontal document overflow.
- No JavaScript page errors or browser console errors in exercised flows.
- Screenshot set includes overview, jobs, provisioning, integrations, audit, readiness, staff and mobile.

Not tested/claimed:
- Authenticated staging UI, actual staff roles or model-permission scope.
- Worker runjobs health, real scheduler thread liveness or provider credentials.
- Live webhook receipt/processing, email send/delivery, Telegram, Discord or Google Drive.
- Real provisioning grant/revoke or manual superuser test.
- Security data access/retention enforcement; published PolicyVersion immutability; AuditLog mutation protection.
- Full keyboard-only, screen-reader, contrast certification or broad browser compatibility.

## 15. Owner review decisions

1. Should Platform Overview remain a thin view over the current Operations Timeline, or have a separate set of system-specific panels?
2. Is the split between Durable Jobs, Periodic Scheduler and Worker Lifecycle clear?
3. Should the read-only Job/Provisioning details move into the same visual shell in the first migration slice, leaving all mutation in the worker/service?
4. Which PeriodicJob configuration controls, if any, should be exposed after permission review?
5. Should Integrations & Webhooks remain a consolidated inspection page, or split bot connections from payment/email webhook evidence?
6. Is Google Drive best kept as Academy-owned configuration with only a cross-link from Platform?
7. Does the unknown provisioning state and six-hour recovery boundary read clearly enough for support operators?
8. Should SecurityEvent detail use a separate security-only permission beyond `accounts.view_securityevent`?
9. Which evidence fields (IP, User-Agent, provider payload, bot target) should be hidden in all ordinary staff roles?
10. Should Staff Approvals become a Platform screen, and what maker/checker and specific permission gate should apply?
11. Which engineering hardening items must block the first Platform migration: AuditLog immutability, published PolicyVersion immutability, `IsRoleAdmin` scope, or retention/privacy controls?
12. Is the proposed migration boundary between Admin Desk, owner domains and Advanced Administration correct?

The Platform screens are a design proposal for review and do not authorise implementation.
