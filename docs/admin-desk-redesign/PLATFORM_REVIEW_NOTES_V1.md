# Platform Workspace — V1 Review Notes

**Date:** 14 November 2026  
**Status:** Draft for owner review; no implementation approval  
**Prototype:** `tradethesis_admin_platform_workspace_v1.html`

## Screens

- M42 Platform Overview.
- M43 Jobs & Scheduler.
- M44 Access & Provisioning.
- M45 Integrations & Webhooks.
- M46 Audit & Security.
- M47 Policies & Readiness.
- M48 Staff & Permissions.
- M49 Migration Boundary.

## Source-derived boundaries preserved

- The existing Operations Timeline at `/staff/admin-desk/operations/` is the current operational foundation. It supports 24h and 7d windows and permission-filters optional job, provisioning, PeriodicJob, Event, AuditLog and SecurityEvent summaries.
- Existing job detail and provisioning detail routes are read-only. Job detail requires `jobs.view_job`; provisioning detail requires `jobs.view_provisioningoperation`.
- JobAdmin disables add/delete and makes all Job fields readonly. Jobs are claimed, retried, closed and reaped by workers. The “stalled” value is a list filter (open jobs with 3+ attempts), not a stored Job state.
- Durable Job queue is different from the lightweight PeriodicJob scheduler. The scheduler starts in long-lived server processes, polls every minute, executes registered light handlers inline and drains up to five durable Jobs as a best-effort fallback. A dedicated runjobs worker remains a separate process path.
- Generic worker recovery includes a 300-second stale lock reaper and backoff on failure. Long-running video job kinds receive a 45-second lease heartbeat.
- ProvisioningOperation, UserChannelAssignment and ChannelMembershipSnapshot remain three different records. An active assignment denotes the managed entitlement mapping, not proof of live membership.
- Provisioning unknown state is not failure. Membership must be probed; unknown probe results do not trigger a resend. A persisted invite link is reused; a six-hour resend throttle is enforced. Control channel cannot be a subscriber target.
- Current direct Telegram provisioning uses BotConfig credentials from the database. BotRuntimeState is legacy bridge diagnostic evidence, not current native Telegram Bot API health.
- The live manual grant/revoke test route under `/bot-admin/` is superuser-only; it remains Advanced Administration and is not a normal operator action.
- Telegram verification pages are staff-only; no unified integration health monitor was verified. Google Drive OAuth is Academy course-admin-only and should remain in Academy context.
- Stripe/Razorpay webhooks create durable idempotent WebhookEvent rows and enqueue a processing Job. The WebhookEvent admin is read-only. Raw payloads are sensitive.
- Resend webhook updates G1 Delivery only, not transactional EmailLog; no separate webhook ledger is created by the inspected Resend handler. Telegram webhook history also has no durable event ledger verified. Discord OAuth callback is not a webhook.
- `/health/` only verifies a primary database SELECT 1; it is not a worker, scheduler, provider, storage or integration health check.
- Existing runtime readiness indicators are configuration-presence checks. They do not prove provider authentication, webhook receipt, successful test transaction, email delivery or backup/restore.
- SecurityEvent is append-only at model level; the source comment describes raw IP restrictions and a 13-month retention plan. This pass does not prove every read/export enforces the policy.
- AuditLog has no append-only save guard in the inspected model and the admin fields are not all readonly.
- PolicyAcceptance is write-once. PolicyVersion publication service archives the prior active version, but the inspected PolicyVersion.save() recalculates content hash and the Django Admin does not make published content fields read-only. Published-content immutability is not fully enforced.
- The staff approval API exists at `/api/admin/staff-approvals/` and `/api/admin/staff-approvals/action/`, but no Admin Desk UI was verified.
- The class permission named IsRoleAdmin permits role=ADMIN OR is_superuser OR any is_staff. Do not describe it as Admin-only.
- Application role, is_staff, is_staff_approved, is_active, superuser and Django Group/model permissions are separate dimensions. The prototype permission matrix is proposed, not an existing role assignment list.

## Design choices introduced for review

- Platform Overview is a thin operational router over the existing Operations Timeline, not a replacement queue.
- Durable Jobs, PeriodicJob scheduler and worker lifecycle remain separated.
- Access and provisioning distinguish desired entitlement, persisted external operation and observed membership.
- Integrations & Webhooks distinguishes Telegram native direct API, Discord OAuth/role sync, Academy-owned Google Drive, Payment WebhookEvent, Resend Delivery update and legacy bridge diagnostics.
- Audit & Security preserves source-specific evidence rather than creating a generic mutable activity record.
- Policies & Readiness separates legal policy state, configuration-presence and real verification evidence.
- Staff & Permissions explains access dimensions; the displayed matrix is a proposed design, not a claim about current staff Groups.
- Migration Boundary keeps live grant/revoke, credentials, policy publishing, staff/group permissions and high-risk edits in Advanced Administration until service/permission parity and hardening are reviewed.
- All preview interactions are local-only. No job, operation, audit row, webhook, policy, permission or provider state is changed.

## Browser validation

- All eight Platform destinations open.
- Durable queue / Periodic scheduler tabs switch.
- Staff access model / proposed permission matrix tabs switch.
- Job search and status filter work.
- Audit event source filter works.
- Job, provisioning, webhook and security detail previews open/close.
- Mobile drawer opens, navigates to Provisioning and closes after selection.
- 390px viewport has no horizontal overflow.
- No JavaScript page errors or browser console errors in exercised paths.
- Desktop previews: Overview, Jobs, Provisioning, Integrations, Audit, Readiness and Staff; mobile preview captured.

## Not tested / not claimed

- Authenticated staging UI or real staff role/per-object permission matrix.
- Worker or scheduler liveness from staging.
- Provider credentials, integration probes, real webhooks or test transactions.
- External Telegram/Discord grant/revoke and Google Drive operations.
- Security evidence privacy enforcement, data retention, policy immutability or AuditLog mutation prevention.
- Staff approval authorization hardening, maker/checker and real action permissioning.
- Keyboard-only, screen-reader, contrast and full cross-browser review.

## Review prompts

1. Is Platform Overview appropriately thin over the existing Operations Timeline?
2. Are durable jobs, PeriodicJob and worker lifecycle separated clearly?
3. Which read-only detail routes should migrate first?
4. Should PeriodicJob configuration stay in Advanced Administration until handler validation and permission controls are defined?
5. Should Google Drive remain Academy-owned?
6. Is the unknown provisioning recovery contract clear?
7. Which audit/security evidence needs a distinct permission and redaction policy?
8. Should Staff Approvals become a Platform workspace, and what authorization/maker-checker boundary is required?
9. Which immutability/auth gaps must block migration?
10. Is the Advanced Administration boundary appropriate?

## Next step

After Platform owner review, perform a six-domain holistic walkthrough using the same fictional learner, course, payment, subscription, support ticket, campaign, referral, gift, job and provisioning records. Recheck every hand-off and permissions assumption. Then update the full migration inventory and obtain explicit owner approval before implementation planning.
