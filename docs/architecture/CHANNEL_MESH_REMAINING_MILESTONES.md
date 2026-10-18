# Channel Mesh — Remaining Milestones Handoff

Updated: 2026-10-19

## Current state

- Django integration work is on `my-new-branch`.
- Current baseline before this handoff: `648b21d53842168812b31ff35fa737d3ba733ecf`.
- Django models, plan-to-Mesh configuration, signed inventory/assignment APIs, access reconciliation, member display, and focused tests are in the branch.
- The API inventory includes the Mesh source chat ID/name and active spawn destinations.
- CI and the integration-target guard passed on commit `cc9e83612fd9082f14c21b266a39195806aa4b07`; the following edit to the design document only updates progress status and still needs its own workflow result reviewed.
- Bot-side patch exists separately as `channel_mesh_bot_patch.zip`. It passed offline compilation and 8 offline tests, but has not been installed in the running bot project or verified against Telegram staging.

## Milestone A — allocator-to-Django connection (not fully complete)

### Implemented
- Django exposes signed, replay-protected `POST /bot/api/mesh/inventory/` and `POST /bot/api/mesh/assign/`.
- Inventory returns only active Meshes and active spawns; it never includes members.
- Assignment validates a linked Telegram identity, active Mesh/spawn, plan entitlement, and writes the spawn chosen by the caller. Django does not choose the spawn.
- The bot patch has a client/helper for requesting inventory and reporting a chosen spawn.

### Blocker / next action
The supplied bot source (`main(20261018-142924).py`, `channel_registry.py`, `mapping_store.py`, `message_manager.py`, and `bot_integration(3).py`) is a signal broadcaster and message-mapping system. The reviewed sources do not contain the member-to-spawn allocation function or a membership-triggered allocation call-site. The connected GitHub account also exposed only `prototypeweb` and `test`, not a separate Telegram bot repository.

Do not invent a new allocation algorithm or hook allocation into the signal-routing registry. When work resumes, obtain the actual allocator source/repository, identify the existing placement decision and capacity/spawn lifecycle, then:
1. Fetch Django's active Mesh inventory through the signed client.
2. Keep the existing policy responsible for the member's spawn choice.
3. Immediately after the real allocation decision, report `telegram_user_id`, `mesh_key`, and the selected `spawn_chat_id` to Django.
4. Handle 4xx entitlement/configuration errors as non-retryable; handle timeouts/5xx as retryable without selecting a different spawn merely because the reporting call failed.
5. Test assignment idempotency, inactive inventory, expired entitlement, reassignment/revocation ordering, and the allocator's capacity accounting.

Milestone A is complete only when that real call-site is connected and tested.

## Milestone B — install bot-side publisher patch

- Apply the reviewed patch to the actual tracked bot repository (do not start a second polling process on the same bot token).
- Configure Django base URL and the shared HMAC secret through environment variables; never commit secrets.
- Persist the bot's SQLite message-map/retry database across restarts.
- Verify polling update types include `channel_post` and `edited_channel_post`.
- Preserve normal direct signal routing; Mesh spawn destinations must not also be ordinary signal destinations.
- Use existing/pre-created source and spawn channels for the first release.

## Milestone C — spawn provisioning approach

Current design supports registering pre-created spawn channels. Automatic Telegram channel creation is not part of the patch. Decide later whether channel creation remains manual or uses a separate, user-authenticated MTProto flow; do not assume the normal Bot API can create channels.

## Milestone D — private staging acceptance

Run with test accounts and private channels:
- inventory and assignment API with valid/invalid signatures;
- source post, media/caption/album, replies, supported edits and controlled deletions;
- partial copy failures, retries, process restart and mapping recovery;
- no duplicate direct + Mesh delivery;
- grant only the assigned spawn, optional direct-channel + Mesh plan, expiry/revoke, reassignment and retry behavior;
- admin/member UI shows the actual assignment and useful error state.

Telegram does not supply a general Bot API event for arbitrary manual deletion of ordinary channel posts. Guaranteed deletion mirroring must use the bot's managed deletion workflow.

## Branch cleanup performed/planned

- The changes from `feature/channel-mesh` were copied to `my-new-branch`.
- Original draft PR #5 targets `my-new-branch`; it is now obsolete and should be closed.
- `main` must remain untouched.
- Delete the remote `feature/channel-mesh` ref after closing the PR if the current GitHub connection supports branch deletion. If not, delete it in GitHub's Branches UI; do not replace it with a fake-empty branch.
- Resume remaining work from `my-new-branch`, not the old feature branch.

No staging test or deployment has been performed as part of this handoff.
