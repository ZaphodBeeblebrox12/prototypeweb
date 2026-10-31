# TradeThesis transactional email — Resend setup

The Django project includes a Resend HTTPS email backend. It is the hosted default
when `DEBUG=False`; local development keeps Django's console email backend.

## Sender-domain setup

1. Create a free Resend account.
2. Add `tradethesis.in` as a sending domain in Resend.
3. Copy the exact SPF, DKIM, and any recommended DMARC DNS records shown by Resend
   into the authoritative DNS provider for `tradethesis.in`. Do not reuse sample
   records or guess hostnames/values.
4. Wait until Resend shows the domain as verified.
5. Create an API key restricted to sending from the TradeThesis domain where the
   Resend account supports domain-scoped keys.

## Render Academy staging

Configure only the Academy staging web service initially:

- Service: `tradethesis-academy-staging`
- Service ID: `srv-db9ioke1egvs73feb8ag`
- Branch: `my-new-branch`
- URL: `https://tradethesis-academy-staging.onrender.com`

Set these environment variables in Render:

| Variable | Value |
| --- | --- |
| `EMAIL_BACKEND` | `apps.core.email_backends.ResendEmailBackend` |
| `RESEND_API_KEY` | API key created in Resend (secret) |
| `RESEND_API_TIMEOUT` | `10` |
| `DEFAULT_FROM_EMAIL` | `TradeThesis <noreply@tradethesis.in>` |
| `RESEND_WEBHOOK_SECRET` | Signing secret generated when the webhook is created (secret) |

Never put the API key or webhook signing secret in Git, a build command, or a
frontend environment variable.

## Delivery webhook

Create one webhook in Resend with this endpoint:

`https://tradethesis-academy-staging.onrender.com/api/email/webhooks/resend/`

Subscribe it to:

- `email.sent`
- `email.delivered`
- `email.delivery_delayed`
- `email.failed`
- `email.bounced`
- `email.complained`
- `email.suppressed`

Copy the webhook's signing secret into `RESEND_WEBHOOK_SECRET` in Render. The
endpoint verifies Svix signature headers against the raw request body and fails
closed when the secret is absent or invalid.

## Deployment and smoke test

The Academy staging Render service currently has automatic deploys disabled.
After setting the Resend variables, manually deploy the latest
`my-new-branch` commit. The build script runs migrations automatically.

Verify the following on staging:

1. Register a test account and confirm that the verification email arrives.
2. Open the confirmation link and verify the account can sign in.
3. Request a password reset and confirm that the reset email arrives.
4. Complete a test password reset.
5. Send a test email and check the Delivery admin list for its Resend message ID.
6. Check that the Resend webhook updates the matching Delivery state to Delivered.
7. Use a controlled invalid recipient only in a safe test; confirm the resulting
   bounce or suppression event updates the Delivery row.

The API response state `Sent` means Resend accepted the message. The webhook state
`Delivered` means Resend received confirmation from the recipient's mail server;
neither guarantees that the message is visible in the inbox rather than spam.

## Scope

Do not change the public static site or the separate course-template preview
service. Validate Academy staging first, then configure production separately
when its deployment branch and sender domain are ready.
