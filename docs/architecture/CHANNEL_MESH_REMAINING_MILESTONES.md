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

## Milestone B — bot runtime patch prepared (not installed)

- Updated artifact: `channel_mesh_bot_patch.zip`. It includes the companion `channel_mesh_bridge.py`, a snapshot-derived `main.py`, a reviewable `main_channel_mesh.patch`, an `.env.txt.example`, and offline tests.
- The patch uses the existing bot process and its single polling loop; it does not start a second process or change the reference `TelegramTwitterBot` repository.
- Python compilation passed; all 15 offline tests passed; the unified patch passed a dry-run and applied cleanly to the supplied `main(20261018-142924).py` snapshot; ZIP integrity check passed.
- Added deterministic relative-path handling for the SQLite mapping/retry store and graceful flushing of buffered source albums on shutdown.
- The user supplied `https://github.com/ZaphodBeeblebrox12/TelegramTwitterBot` as reference only and explicitly prohibited changes there. The connected GitHub access returned 404 for that repository, so its current HEAD could not be reviewed from this session. The downloadable patch is based on the uploaded source snapshot, not a verified checkout of current repository HEAD.
- Do not overwrite a possibly newer bot working tree blindly. Before installing, compare `main_channel_mesh.patch` with the actual local working copy and carry the hooks over any intervening changes. The package has not been installed, configured with real secrets, deployed, or tested against live Telegram staging.

### Still required when installation is authorized

- Configure `CHANNEL_MESH_DJANGO_BASE_URL` and the same `PROVISION_SHARED_SECRET` as Django through environment variables; never commit the real secret.
- Set `CHANNEL_MESH_MIRROR_DB` to an absolute path on persistent storage for any hosted/container runtime.
- Verify the bot administrator rights in the private source and spawn channels.
- Preserve normal direct signal routing; route into the Mesh Source only and do not also register spawn destinations as regular signal destinations.
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
- Original draft PR #5 targeted `my-new-branch` and is now closed (not merged).
- The remote `feature/channel-mesh` branch still exists as of this handoff. The connected GitHub actions in this session expose no branch-delete operation, and the local shell cannot reach GitHub. Delete the exact `feature/channel-mesh` ref in the repository's GitHub Branches UI; do not replace it with a fake-empty branch.
- `main` must remain untouched.
- Resume remaining work from `my-new-branch`, not the old feature branch.

No staging test or deployment has been performed as part of this handoff.
