# Channel Mesh — Design Note

**Status:** Django control-plane models, plan configuration, signed inventory/assignment APIs, and assigned-spawn access reconciliation are committed on `my-new-branch`. A companion bot mirroring patch has passed offline tests but has not yet been integrated into the bot's tracked repository/runtime. The existing allocator call-site is still unresolved because it is not present in the bot source reviewed for this change. Do not treat the full Mesh feature as production-ready until that allocator integration and end-to-end staging tests pass.  
**Django integration branch:** `my-new-branch`  
**Companion bot patch:** supplied separately as `channel_mesh_bot_patch.zip`  
**Product scope:** Existing Telegram trading bot + Django access-control integration.

## Purpose

Channel Mesh is an opt-in publishing and destination-pool capability. Each course/plan must explicitly declare its delivery destinations. It may use **Direct Channel** delivery, **Channel Mesh** delivery, or **both** in combination. This is configured per course/plan, not as a global bot setting. The configuration must preserve the distinction between ordinary direct-channel memberships and Mesh spawn allocation; these are different destination types with different provisioning behaviour.

The existing trading bot remains the authoring/publishing bot. The rules that already filter and route content continue to decide what gets published to a configured Mesh Source. Anything published in that Mesh Source is then mirrored to every enabled spawn belonging to that Mesh.

The Mesh Source is the canonical publishing channel; it is not where Mesh-plan members are assigned to join. **Spawn Destinations are where members are assigned to live.** The existing member-allocation logic determines which spawn a member is assigned to and how many spawns are needed from the configured inventory/capacity. Do not replace it with a second allocation algorithm.

The source message and its copies have different Telegram message IDs. The system must persist a mapping between the canonical source message and every successfully created destination copy so it can mirror supported replies, edits, and controlled deletions.

This is a feature of the existing bot, not a second bot or a replacement for the current trade lifecycle, channel registry, message formatter, ledger, or membership-allocation logic.

## Course/plan delivery configuration

Every course/plan must explicitly list the delivery target types it uses. Valid configurations are:

- **Direct Channel only:** Keep the existing plan-to-channel provisioning behaviour.
- **Channel Mesh only:** Reference a Mesh/pool. Use the existing allocation logic to assign each entitled member to the appropriate spawn destination.
- **Direct Channel + Channel Mesh:** Provision the member to the configured direct channel(s) and also assign them to the appropriate spawn destination in the configured Mesh. The exact direct channels and Mesh association must be visible in the course/plan configuration.

This must be a composable destination configuration, not a mutually exclusive one-of-two mode. A course/plan can have multiple direct channels, one or more explicitly configured Mesh associations where the existing allocation policy supports it, or both destination types. Do not infer that every course needs Mesh, and do not enable Mesh globally.

For Mesh access, the member is granted access to the spawn selected for them by the existing allocation logic—not automatically to every spawn and not to the Mesh Source as their membership destination. A plan must not implement Mesh membership by attaching every spawn as an ordinary required channel; that would make all spawns mandatory and defeat the allocation logic. Plan-to-Mesh associations and member-to-spawn assignments must be represented separately from ordinary direct-channel mappings.

When both destination types are configured, successful entitlement provisioning must handle both sides and report partial failures clearly. For example, direct-channel access may succeed while spawn access fails; the system must not silently present the overall operation as fully successful. Expiry, renewal, and revocation must be applied to the relevant direct-channel grants and the member's recorded spawn assignment according to the configured plan.

The publishing and membership responsibilities are distinct:

1. The existing content-routing rules choose the destination route and send eligible content to the Mesh Source.
2. The Mesh publisher mirrors every supported source post to every enabled spawn in that Mesh, regardless of which spawn a particular member is assigned to.
3. The membership allocator chooses the appropriate spawn for each member according to the existing allocation policy and available registered inventory.
4. Entitlement expiry/revocation applies to the member's actual assigned spawn, as well as the configured direct-channel memberships where applicable. It must not revoke all spawn memberships unless the assignment records say the member was assigned to them.

## Core requirements

1. **Explicit destination configuration.** Every course/plan clearly declares whether it uses direct channels, Channel Mesh, or both. Existing plans default to their current direct-channel behaviour unless deliberately reconfigured. Mesh behaviour is enabled only when explicitly configured for the relevant course/plan and content route.
2. **One canonical source per Mesh.** A Mesh has one source channel and a registered pool of spawn destinations. The main bot publishes to the source, then copies source content to every enabled spawn in that Mesh. Administrator posts made directly in the source must also be observed and mirrored where Telegram supplies the relevant `channel_post` or `edited_channel_post` update. The system must not also send the same message directly to spawned destinations through ordinary routing.
3. **Content mirroring.** Preserve supported text, captions, formatting, photos and other supported media. Handle media albums deliberately rather than silently splitting or losing their grouping.
4. **Reply mapping.** Replies and trade updates must target the corresponding local message in each destination, not reuse the source channel's message ID.
5. **Edit/delete mapping.** Edits and bot-controlled deletion workflows must act on the source message and all known copies. Report partial failures and retry safely. Telegram's standard Bot API does not provide a general deletion event for arbitrary manual deletions of ordinary channel posts; therefore, guaranteed mirroring of deletion requires using the bot's managed deletion workflow.
6. **Durable message mappings.** Persist source chat/message IDs, destination chat/message IDs, operation status, timestamps, and retry state. Do not use the current seven-day message-mapping retention as the lifetime boundary for Mesh relationships; retention must be aligned with the managed message/trade lifecycle.
7. **Idempotency and recovery.** Retries must not create duplicate copies where the API outcome can be determined. Persist partial success and retry only unresolved operations. Distinguish failed from unknown/indeterminate outcomes.
8. **Allocation reuse.** Reuse the existing allocation policy to select a member's spawn and determine when additional spawns are needed. Store an auditable member-to-spawn assignment. Do not independently reimplement, bypass, or change the policy as part of Mesh publishing.
9. **No direct-route duplication.** Spawn destinations belong to the Mesh registry/router, not the ordinary direct-routing list. The same post must not be published once through direct routing and again through Mesh.
10. **Expiry and renewal.** Django remains the source of truth for plan entitlement and expiry. Grants, revocations, and renewal actions must apply to the assigned spawn and be durable, auditable, and retryable.
11. **Observability.** Show the course/plan's configured direct channels and Mesh associations, provisioning status for each destination type, the member-to-spawn assignment, per-destination verification, last sync, copy/edit/delete failures, retry state, and clear admin alerts. If both direct and Mesh access are configured, show the outcome for each side and the overall status.

## Telegram destination inventory — prepare now, integrate later

The empty destinations are created and owned in Telegram. Telegram does not provide a special folder/container where they must live. Create each as a **private Telegram channel** for broadcast-only trade content, or as a **private group/supergroup** if members are meant to converse. Keep the Mesh Source separate from spawned destinations.

For each source/destination:
- Add the existing trading bot as an administrator.
- Grant only the rights required for the configured behaviour: publish/copy, edit and delete bot-managed messages, manage invitation links, and ban/unban members for access control.
- Keep a written inventory of the friendly name, numeric Telegram chat ID (often shown as a `-100…` ID), chat type, intended Mesh/pool, role (`source` or `spawn`), and readiness/permission check.
- Do not put bot tokens, shared secrets, or other credentials in this inventory or commit them to Git.

**Important:** Do not register all spawned destinations through the existing `/add <KEY> <CHANNEL_ID> <NAME>` ordinary routing flow yet. The current registry is used for normal direct routing and feature/asset filters. Treating every spawn as a normal destination may cause duplicate direct posts in addition to Mesh copies.

Suggested inventory shape (conceptual, not yet an implemented config schema):

| Mesh | Key | Telegram chat ID | Type | Role | Enabled | Permissions verified |
|---|---|---|---|---|---|---|
| Example Mesh | MESH_MAIN | to be recorded | channel | source | no | no |
| Example Mesh | MESH_01 | to be recorded | channel/group | spawn | no | no |
| Example Mesh | MESH_02 | to be recorded | channel/group | spawn | no | no |

Use real numeric IDs during registration; friendly names are for display only. A future bot command or Admin Desk form should validate that the bot can access each destination before enabling it for live delivery.

## Membership, allocation, and seven-day access

Django remains the source of truth for entitlements and expiry. The existing allocation logic remains in place; Channel Mesh publishing must not select or grant every spawned destination to every member.

For a configured course/plan:
- Keep the existing plan-to-channel grant/revoke flow for every configured **Direct Channel** destination.
- For every configured **Channel Mesh** association, use the existing allocation logic to assign the member to the appropriate spawn. Do not represent every spawn as a separate required direct channel.
- If both destination types are configured, provision and track the direct-channel grants and assigned-spawn grant as distinct operations under the same entitlement. Make partial success/failure visible and safely retryable.
- Store each member's actual spawn assignment(s), along with confirmed entitlement start and expiry timestamps. The initial default proposal is seven days from confirmed payment/access approval, not from first join; this is a product rule to confirm before implementation.
- At expiry, enqueue durable revocations for the configured direct-channel memberships and the member's assigned spawn membership(s). The provisioning executor removes/bans the member from each applicable destination, records each outcome, and retries failures. A verified renewal can trigger the controlled unban/re-invite path.
- If a member is reassigned to another spawn, transfer access deliberately and record both the old and new assignment; do not leave an untracked membership behind.
- Use idempotent, auditable grants/revocations. An invite link expiry is not equivalent to entitlement expiry.
- Configure the bot as an administrator with the necessary membership-management rights in every managed destination.

## Deployment and Django bridge

The existing trading bot can run on the owner's computer while Django runs on a hosted server. The local machine must stay online for timely action. If it is offline, Django must retain due jobs and the executor must process them on reconnect; the UI must show overdue/unresolved revocations instead of reporting success.

The current Django branch contains a provisioning client and a signed bridge contract. Review/reuse that bridge rather than adding an unauthenticated public endpoint. Since a home computer normally cannot receive incoming HTTPS requests, prefer the local bot securely polling/claiming pending jobs from Django over HTTPS, or a suitably authenticated outbound connection. Preserve the current bot's single Telegram update receiver: do not start a second independent long-polling process with the same bot token.

Django exposes two signed POST endpoints for the existing allocator/integration process:

- `bot_integration:mesh_inventory` at `api/mesh/inventory/` returns only active Meshes and active spawn IDs (optionally filtered by `mesh_key`). It does not expose member data and does not allocate anyone.
- `bot_integration:mesh_assign` at `api/mesh/assign/` accepts `telegram_user_id`, `mesh_key`, and `spawn_chat_id` after the allocator has made its placement decision.

Both use the existing HMAC bridge headers and shared secret with timestamp/nonce replay protection. The assignment endpoint resolves a uniquely linked Telegram account and verifies active entitlement, Mesh, and spawn before recording the assignment. It **does not choose a spawn**. The existing allocator caller still has to be wired to fetch the inventory and invoke the assignment endpoint; do not mark Mesh allocation end-to-end until that is implemented and tested.

For dependable production enforcement, an always-on bot/provisioning host is preferable to a personal PC, but the two processes do not need to share a server.

## Implementation plan

1. Confirm which Telegram chat is the Mesh Source and decide whether each destination is a channel or group.
2. Add dedicated Mesh/pool and destination records without changing ordinary routing semantics.
3. Add explicit course/plan destination configuration that supports Direct Channel only, Channel Mesh only, or both. Preserve existing direct-channel mappings, add plan-to-Mesh associations, and keep those separate from member-to-spawn assignments.
4. Integrate Mesh-plan provisioning with the existing member-allocation logic so each member gets the correct spawn and the number of active/needed spawns follows the existing policy and registered inventory. When a plan has both destination types, provision each configured side and track partial failures independently.
5. Add a publisher/router that sends once to the source and mirrors into every enabled spawn, with durable source-to-copy mappings. Observe source channel posts and edits, including administrator-originated posts.
6. Integrate trade setups, updates, notes, replies, controlled deletion, and media handling with the publisher while preserving the current formatter, ledger, and trade ID workflow.
7. Add Admin Desk/bot admin controls to register, verify, enable, disable, and inspect Mesh sources/spawns and configure a plan's membership mode.
8. Integrate seven-day entitlements with durable grant/revoke jobs and the existing Django provisioning bridge.
9. Add tests for direct-channel non-regression, each destination configuration (direct only, Mesh only, both), allocation reuse, correct member-to-spawn assignment, provisioning partial failure when both are configured, no duplicate delivery, mirroring of all source posts, reply mapping, edit/delete propagation, retries, capacity/allocation integration, expiry, renewal, reassignment, and offline recovery.
10. Test on private staging channels first; do not turn on Mesh for live plans/routes until permission checks and end-to-end tests pass.

## Explicit non-goals

- Do not replace the existing trading bot or create a second publisher bot.
- Do not enable Mesh globally or change the behaviour of unrelated channels or existing direct-channel plans.
- Do not rewrite the existing member-allocation logic without a demonstrated gap.
- Do not treat spawn destinations as ordinary required plan channels for Mesh plans.
- Do not treat message-mapping retention as membership/access expiry.
- Do not promise propagation for manual Telegram deletions that the Bot API cannot notify the bot about.

## Initial preparation checklist

- [ ] Choose one existing or newly created private channel as the Mesh Source.
- [ ] Create the desired empty private spawn channels/groups in Telegram.
- [ ] Add the existing bot as administrator with the required permissions.
- [ ] Record each numeric chat ID and intended role in a private working inventory.
- [ ] Keep spawns out of normal `/add` routing until the dedicated Mesh registry/router exists.
- [ ] Explicitly configure each course/plan's destination(s): Direct Channel only, Channel Mesh only, or both.
- [ ] Confirm seven-day access starts at payment/approval confirmation unless a different policy is intentionally selected.
