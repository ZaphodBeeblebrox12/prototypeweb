# Discord Community Access — Setup and Smoke Test

This integration uses the existing Django account, subscription, job queue, and
`PlanChannelMapping` records. It does not require a second bot service inside
Django.

## 1. Discord Developer Portal and bot

1. Create or choose the Discord Application used for TradeThesis OAuth.
2. Create its bot user and add that bot to the community guild.
3. Grant the bot `CREATE_INSTANT_INVITE` and `MANAGE_ROLES` in that guild.
4. Move the bot's highest role above every paid/product role it must grant or
   remove. Discord will reject role changes above the bot's highest role.
5. In the application's OAuth2 settings, register the exact callback URL:
   `https://<academy-host>/bot/discord/callback/`. Use the actual public Django
   host for each environment; the URL must match the value configured below.
6. Keep the OAuth client ID/secret and bot token from that same application.

The member-linking flow requests `identify` and `guilds.join`. The latter lets
the bot add the OAuth-authorized user to the configured guild. Discord documents
that this requires the bot to be in the guild, the `CREATE_INSTANT_INVITE`
permission, and an OAuth access token granted with `guilds.join`:

- [Discord Add Guild Member API](https://github.com/discord/discord-api-docs/blob/main/developers/resources/guild.mdx)
- [Discord OAuth2 scopes](https://github.com/discord/discord-api-docs/blob/main/developers/topics/oauth2.mdx)

## 2. Django configuration

In Django administration, open **Bot Configurations** and set:

- **Discord bot token** — bot token from the application above.
- **Discord guild ID** — the server/guild ID that hosts the community.
- **Discord client ID** — OAuth application client ID.
- **Discord client secret** — OAuth application client secret.
- **Discord redirect URI** — the exact public callback URL registered in the
  Developer Portal.

Do not put tokens or client secrets in the repository, screenshots, issue
reports, or logs.

## 3. Map paid plans to roles

In Django administration, open **Plan Channel Mappings**. Create one mapping
for each plan and managed Discord role:

- Platform: `discord`
- Plan: the subscription plan granting access
- External ID: the Discord role's numeric ID (enable Developer Mode in Discord
  to copy it)
- Name: optional human-readable role name

A role can be mapped to more than one plan. Access is calculated as the union
of mappings for **all active subscriptions** the member holds across products.
When a subscription activates, expires, is deleted, or its plan's role mappings
change, Django queues a reconciliation job. The job reads live Discord role
state, applies additions/removals, updates the local assignment record, and
retries platform failures using the existing durable job queue.

The site's long-lived Django process drains a small number of queued jobs on
each scheduler tick. Higher-volume deployments should keep the dedicated
`python manage.py runjobs --loop` worker running as well.

## 4. Staging smoke test

Use a test Discord account and test subscription; do not use a real customer or
a real charge.

1. Log in to TradeThesis and open Dashboard → Connections.
2. Select **Connect Discord**, authorize, and confirm the account returns to
   Connections with the linked account shown.
3. Confirm the account is present in the configured Discord guild.
4. Activate a test subscription with a Discord `PlanChannelMapping`. Confirm
   the mapped role appears after the reconciliation job runs.
5. Expire/cancel that subscription while leaving any other product subscription
   active. Confirm only roles no longer entitled are removed.
6. Repeat with two active product subscriptions. Confirm roles belonging to
   both remain present, then expire one and check the remaining product's role
   stays.
7. Disconnect Discord. Confirm all integration-managed roles are removed before
   the account link is deleted. If Discord refuses a role removal, the page
   must leave the link in place and report the failure rather than claim success.
8. In Django admin, review Bot Access Audits for successful/failed grant, revoke,
   link, and unlink actions.

The OAuth callback and reconciliation tests mock Discord API calls; passing
those tests proves application logic and failure handling, not the settings or
permissions of the live Discord application. Complete this smoke test against
the intended staging guild before offering Discord access to paying members.
