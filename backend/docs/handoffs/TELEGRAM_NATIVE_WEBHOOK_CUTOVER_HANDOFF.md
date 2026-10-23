# TradeThesis Telegram Native Webhook Cutover — Handoff

**Updated:** 2026-10-23  
**Repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Working branch:** `my-new-branch`  
**Implementation commit:** `e3f568fd21b8f1fa850f01988f6efe0bfca02348`  
**Current state:** Source commit is on the approved branch. CI status still needs to be confirmed. Render staging has not been deployed or modified.

## Goal and non-negotiables

Move Titan Pip Bot's account-linking updates and Telegram channel provisioning into the Django Academy service, using the canonical bot token stored in Django Admin `BotConfig`. Keep the separate publisher script and its bot configuration untouched. Work only on `my-new-branch`. Do not merge or deploy without explicit approval.

## Implemented in the source commit

- The Telegram webhook accepts the native `X-Telegram-Bot-Api-Secret-Token` header, compared in constant time against `TELEGRAM_WEBHOOK_SECRET`.
- Signed HMAC requests are still accepted as a temporary rollback path; bridge registration/heartbeat endpoints remain, but normal account linking and channel provisioning no longer require the bridge.
- The webhook handles `/start`, verification deep links, and simple greetings such as `Hi` and `Hello`. It restricts account linking to private messages from human users.
- Linking detects a Telegram identity already owned by another TradeThesis account and does not consume the token or overwrite the existing link. Duplicate delivery after a successful link returns an already-linked response.
- `TelegramBotService` now provides conservative direct membership checks and native `setWebhook` configuration with Telegram's secret token. API transport errors no longer log token-bearing request URLs.
- The durable `ProvisionTransport`, older synchronous reconciliation entry point, and admin verification/test-grant tools now call Telegram directly rather than relying on `ProvisionClient`.
- Invite flow persists the one-use URL before DM delivery; a retry reuses the saved URL. Unknown membership is not treated as non-membership and does not trigger another invitation.
- The admin Set Webhook action opens a confirmation page; the state-changing request is a CSRF-protected POST and uses `SITE_BASE_URL` as the fallback URL.
- Added direct transport and native webhook regression tests; updated the existing account-linking, grant-notification, and reconcile tests to reflect Django-side delivery.

## Before enabling the webhook on staging

1. Wait for CI to pass and review any failure before deploying.
2. In the Render environment group used by `tradethesis-academy-staging`, add `TELEGRAM_WEBHOOK_SECRET` with a unique Telegram-valid random string (1–256 characters, only letters, digits, underscore, and hyphen). Keep it out of Git and chat logs.
3. Confirm `SITE_BASE_URL` points to the Academy staging HTTPS URL and that Bot Configuration contains Titan Pip Bot's correct token and bare username.
4. Only after a separately approved deployment, use Bot Configuration → Set Telegram Webhook, review the confirmation page, and explicitly confirm the action.
5. Test an actual account link, greeting, invite delivery, membership check, and revoke on a controlled test account/channel before removing or stopping Trade Admin/legacy bridge services.

**No Render environment variables, services, webhooks, bot tokens, or channel memberships were changed by this source commit.** The Academy Render service's auto-deploy setting was observed as disabled, so the branch commit did not itself deploy that service.

## Verification still required

- Confirm GitHub Actions for the implementation commit are present and green, including both backend workflows.
- Review any test failure and patch it on this same branch.
- After approval to deploy, perform a controlled staging smoke test and verify the configured webhook status.
- Keep legacy bridge settings and Trade Admin intact until the native flow is demonstrated working. The publisher script was not edited.

## Rollback principles

Do not remove the legacy service or shared-secret configuration before the direct flow passes staging checks. If rollback is needed, restore the known bridge path deliberately and reset Telegram webhook/polling configuration for Titan Pip Bot so the same bot is not operated through both webhook and polling at once.
