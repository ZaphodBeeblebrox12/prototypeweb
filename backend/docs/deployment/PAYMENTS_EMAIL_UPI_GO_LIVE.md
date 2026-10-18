# Payments, UPI and email: go-live checklist

This is the small-creator go-live procedure for the Django payment flow. The application uses Razorpay Standard Checkout for India and Stripe Checkout for other pricing countries. Razorpay's hosted checkout is responsible for collecting the actual UPI/card/bank details; TradeThesis must never ask customers to enter a UPI PIN or banking password into its own pages.

## What the code does

- India pricing routes to a Razorpay order and opens Razorpay Standard Checkout.
- The checkout does not send a restrictive payment-method allow-list, so the methods enabled for your Razorpay merchant account can be offered. UPI availability and its available UPI apps/ID/QR presentation are governed by the Razorpay dashboard configuration and account eligibility.
- The Django app verifies the Razorpay order server-side before marking the payment successful and granting access. Webhooks also use the common idempotent payment-activation flow.
- A successful payment issues the saved invoice snapshot and sends the payment-success email via the existing notification service.
- Tax remains off by default. Do not enable a tax percentage until the applicable treatment is confirmed.
- Paid checkout is one-time only. Monthly, quarterly and yearly plans mean 30, 90 or 365 days of access bought once; they do not create a recurring provider subscription or charge the customer automatically again. Course offers are one-off purchases and may grant permanent or explicitly limited access.
- Paid trial plans that advertise a later automatic conversion are blocked from checkout while recurring billing is unsupported.
- Checkout consent is deliberately blocked if any required active policy still contains the seeded placeholder text. Publish the owner-approved versions before testing a real sale.

This is hosted UPI through Razorpay. A separate manual UPI QR/VPA transfer flow with proof uploads and manual reconciliation is not implemented or needed for this checkout path.

## Render environment variables

Add these in Render's **Environment** settings. Use Render's secret-entry UI for credentials; do not put production values in Git.

| Variable | Purpose |
|---|---|
| `SITE_BASE_URL` | Public HTTPS root URL of the deployed Django app, used by return links and invoice email links. |
| `RAZORPAY_KEY_ID` | Key ID for the selected Razorpay environment. |
| `RAZORPAY_KEY_SECRET` | Matching Razorpay API secret; keep private. |
| `RAZORPAY_WEBHOOK_SECRET` | Secret configured on the Razorpay webhook itself; it is not necessarily the API key secret. |
| `EMAIL_BACKEND` | Set to `django.core.mail.backends.smtp.EmailBackend` for SMTP delivery. |
| `EMAIL_HOST`, `EMAIL_PORT` | SMTP host and port from your email provider. |
| `EMAIL_USE_TLS` | Usually `True` for port 587 when your email provider specifies STARTTLS. Follow provider guidance. |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP credentials or app password. |
| `DEFAULT_FROM_EMAIL` | A sender address on a domain verified with your email provider. |

If using Stripe for non-India customers, also set `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, and `STRIPE_WEBHOOK_SECRET`.

## Razorpay: enable and verify UPI

1. In the Razorpay Dashboard, open **Account & Settings → Payment Methods** and verify UPI is enabled for your merchant account.
2. Open **Checkout / Payment Configuration** and inspect the configuration used by Standard Checkout. Make sure UPI and the UPI instruments you want to offer are visible. Do not configure a method list that hides UPI.
3. Use Razorpay test credentials in staging first. Open an India-priced course or membership checkout on a mobile device and a desktop browser. Confirm the Razorpay window visibly offers UPI as well as the other supported payment methods.
4. Complete a test payment using Razorpay's documented test UPI flow. Confirm Django only grants access after Razorpay verifies the order/payment, and confirm one invoice/receipt is produced.
5. Switch to live credentials only when the account's live payment methods are enabled and the test steps have passed.

Official guidance: [Razorpay UPI](https://razorpay.com/docs/payments/payment-methods/upi/) and [Razorpay Checkout payment-method configuration](https://razorpay.com/docs/payments/payment-gateway/web-integration/standard/configure-payment-methods/).

## Razorpay webhook

Configure a webhook in the Razorpay Dashboard pointing to:

`https://YOUR-PUBLIC-DOMAIN/webhooks/razorpay/`

Set its webhook secret to the value stored as `RAZORPAY_WEBHOOK_SECRET`. Subscribe to the events used by this code:

- `payment.captured`
- `order.paid`
- `refund.processed`

Use your actual public HTTPS host; do not use localhost. After test transactions, inspect Django Admin → Payment intents and Webhook events. A webhook that is absent, invalidly signed or not processed can delay invoice/access updates, so do not rely only on a successful browser redirect.

## Email smoke test

1. Verify that your email provider has authorised the sender domain/address.
2. Deploy with the SMTP values configured in Render.
3. Test a new signup/verification email and a password-reset email. Email verification is mandatory; do not open public registration if these messages do not arrive.
4. Complete a test purchase. Confirm the branded payment-success email arrives, the invoice link opens after login, and the invoice/receipt shows the correct price and transaction reference.
5. Test a failed payment and a refund using staging/test mode. Confirm notification failures are logged, and the payment state/access remains correct.

## Before public sales

- Confirm the current production plan prices and currencies in the production database.
- Verify that production uses a durable database, that records survive a restart/redeploy, and that a recent backup can be restored. Do not assume the separate legacy `tradeadmin` database is the Academy database.
- Replace and publish approved versions of all public policy pages (Terms, Refund & Cancellation, Cancellation, Risk Disclosure and Privacy). The policy admin flags placeholder or missing versions, and paid checkout refuses required placeholder consent documents.
- Confirm `SITE_BASE_URL` is the correct public HTTPS URL in the Academy Render environment; keep provider and email secrets in Render, never in Git.
- The public staging Trading Path buttons now lead to `/buy/course/trading-path/` on Academy staging. A matching active published `CourseOffer` with a dedicated hidden Plan and active `one_time` price must exist in the Academy database, otherwise the route deliberately shows “not available yet”.
- `site/assets/checkout-config.js` maps only the public staging hostname to the Academy staging service. Configure the production Academy URL for the production public hostname before launching the production marketing site; unknown hosts are not sent to staging.
- Populate Business and Tax Settings with your correct legal/seller details and support email.
- Leave tax disabled until your CA confirms whether and how to charge it. The current configurable rate is a single fixed percentage, not a GST place-of-supply engine.
- Keep invoice records and payment records intact; they are audit data and are intentionally read-only in Django Admin.
- Do not test live payments with real customer money. Complete a clearly identified low-value live smoke test only when you are ready and understand any transaction fees/refund steps.

## Scope boundary

This launch path supports UPI through Razorpay Checkout. It does not add automatic subscription renewals, direct manual UPI transfers, recurring UPI mandates, or a full accounting/tax engine. Those are separate features and should be added only if the business model requires them.
