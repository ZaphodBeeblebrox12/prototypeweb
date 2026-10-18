# Channel Mesh — Design Note

**Status:** Planning only — no runtime behaviour has been changed.  
**Working branch:** `feature/channel-mesh`  
**Branch base:** `my-new-branch`  
**Product scope:** Existing Telegram trading bot + Django access-control integration.

## Purpose

Channel Mesh is an opt-in publishing and destination-pool capability. The existing trading bot remains the authoring/publishing bot. For a channel route explicitly configured to use a Mesh, it publishes one canonical message to a designated **Mesh Source** and mirrors that content into the Mesh's registered **Spawn Destinations**.

The source message and its copies have different Telegram message IDs. The system must persist a mapping between the canonical source message and every successfully created destination copy so it can mirror supported replies, edits, and controlled deletions.

This is a feature of the existing bot, not a second bot or a replacement for the current trade lifecycle, channel registry, message formatter, ledger, or membership-allocation logic.

## Core requirements

1. **Opt-in only.** Existing channels continue using current direct routing. Mesh behaviour is enabled only for explicitly configured routes/plans.
2. **One canonical source.** A Mesh has one source channel. The main bot publishes to that source, then copies the source message to the configured spawned destinations. The system must not also send the same message directly to those spawned destinations through ordinary routing.
3. **Content mirroring.** Preserve supported text, captions, formatting, photos and other supported media. Handle media albums deliberately rather than silently splitting or losing their grouping.
4. **Reply mapping.** Replies and trade updates must target the corresponding local message in each destination, not reuse the source channel's message ID.
5. **Edit/delete mapping.** Edits and bot-controlled deletion workflows must act on the source message and all known copies. Report partial failures and retry safely. Telegram's standard Bot API does not provide a general deletion event for arbitrary manual deletions of ordinary channel posts; therefore, guaranteed mirroring of deletion requires using the bot's managed deletion workflow.
6. **Durable message mappings.** Persist source chat/message IDs, destination chat/message IDs, operation status, timestamps, and retry state. Do not use the current seven-day in-memory/message-mapping retention as the lifetime boundary for Mesh relationships; retention must be aligned with the managed message/trade lifecycle.
7. **Idempotency and recovery.** Retries must not create duplicate copies where the API outcome can be determined. Persist partial success and retry only unresolved operations. Distinguish failed from unknown/indeterminate outcomes.
8. **Observability.** Provide source/pool status, per-destination verification, last sync, copy/edit/delete failures, retry state, and clear admin alerts.

## Telegram destination inventory — prepare now, integrate later

The empty destinations are created and owned in Telegram. Telegram does not provide a special folder/container where they must live. Create each as a **private Telegram channel** for broadcast-only trade content, or as a **private group/supergroup** if members are meant to converse. Keep the Mesh Source separate from spawned destinations.

For each source/destination:
- Add the existing trading bot as an administrator.
- Grant only the rights required for the configured behaviour: publish/copy, edit and delete bot-managed messages, manage invitation links, and ban/unban members for access control.
- Keep a written inventory of the friendly name, numeric Telegram chat ID (often shown as a `-100…` ID), chat type, intended Mesh/pool, role (`source` or `spawn`), and readiness/permission check.
- Do not put bot tokens, shared secrets, or other credentials in this inventory or commit them to Git.

**Important:** Do not register all spawned destinations through the existing `/add <KEY> <CHANNEL_ID> <NAME>` ordinary routing flow yet. The current registry is used for normal direct routing and feature/asset filters. Treating every spawn as a normal destination may cause duplicate direct posts in addition to Mesh copies. A dedicated Mesh source/destination registry and router must be implemented first.

Suggested inventory shape (conceptual, not yet an implemented config schema):

| Mesh | Key | Telegram chat ID | Type | Role | Enabled | Permissions verified |
|---|---|---|---|---|---|---|
| Example Mesh | MESH_MAIN | to be recorded | channel | source | no | no |
| Example Mesh | MESH_01 | to be recorded | channel/group | spawn | no | no |
| Example Mesh | MESH_02 | to be recorded | channel/group | spawn | no | no |

Use real numeric IDs during registration; friendly names are for display only. A future bot command or Admin Desk form should validate the bot can access each destination before enabling it for live delivery.

## Membership and seven-day access

Django remains the source of truth for entitlements and expiry. The existing allocation logic remains in place; Channel Mesh publishing must not select or grant every spawned destination to every member.

For a configured plan/pool:
- Store a confirmed entitlement's start and expiry timestamps. The initial default proposal is seven days from confirmed payment/access approval, not from first join; this is a product rule to confirm before implementation.
- Keep each member assigned to the selected destination/pool result already determined by the access-allocation logic.
- At expiry, enqueue a durable revocation. The provisioning executor bans/removes the member from the actual assigned destination, records the outcome, and retries failures. A verified renewal can trigger the controlled unban/re-invite path.
- Use idempotent, auditable grants/revocations. An invite link expiry is not equivalent to entitlement expiry.
- Configure the bot as an administrator with the necessary membership-management rights in every managed destination.

## Deployment and Django bridge

The existing trading bot can run on the owner's computer while Django runs on a hosted server. The local machine must stay online for timely action. If it is offline, Django must retain due jobs and the executor must process them on reconnect; the UI must show overdue/unresolved revocations instead of reporting success.

The current Django branch contains a provisioning client and a signed bridge contract. Review/reuse that bridge rather than adding an unauthenticated public endpoint. Since a home computer normally cannot receive incoming HTTPS requests, prefer the local bot securely polling/claiming pending jobs from Django over HTTPS, or a suitably authenticated outbound connection. Preserve the current bot's single Telegram update receiver: do not start a second independent long-polling process with the same bot token.

For dependable production enforcement, an always-on bot/provisioning host is preferable to a personal PC, but the two processes do not need to share a server.

## Implementation plan

1. Confirm which Telegram chat is the Mesh Source and decide whether each destination is a channel or group.
2. Add dedicated Mesh/pool and destination records without changing ordinary routing semantics.
3. Add a publisher/router that sends once to the source and mirrors into spawns, with durable source-to-copy mappings.
4. Integrate trade setups, updates, notes, replies, controlled deletion, and media handling with the publisher while preserving the current formatter, ledger, and trade ID workflow.
5. Add per-route opt-in settings and an Admin Desk/bot admin workflow to register, verify, enable, disable, and inspect destinations.
6. Integrate seven-day entitlements with durable grant/revoke jobs and the existing Django provisioning bridge.
7. Add tests for ordinary-route non-regression, no duplicate delivery, reply mapping, edit/delete propagation, partial failures, retries, capacity/allocation integration, expiry, renewal, and offline recovery.
8. Test on private staging channels first; do not turn on the Mesh for live routes until permission checks and end-to-end tests pass.

## Explicit non-goals

- Do not replace the existing trading bot or create a second publisher bot.
- Do not enable Mesh globally or change the behaviour of unrelated channels.
- Do not rewrite the existing member-allocation logic without a demonstrated gap.
- Do not treat message-mapping retention as membership/access expiry.
- Do not promise propagation for manual Telegram deletions that the Bot API cannot notify the bot about.

## Initial preparation checklist

- [ ] Choose one existing or newly created private channel as the Mesh Source.
- [ ] Create the desired empty private spawn channels/groups in Telegram.
- [ ] Add the existing bot as administrator with the required permissions.
- [ ] Record each numeric chat ID and intended role in a private working inventory.
- [ ] Keep spawns out of normal `/add` routing until the dedicated Mesh registry/router exists.
- [ ] Confirm seven-day access starts at payment/approval confirmation unless a different policy is intentionally selected.
