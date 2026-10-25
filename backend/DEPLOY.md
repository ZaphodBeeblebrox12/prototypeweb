# TradeThesis Academy — deployment and staging runbook

## Source-of-truth and safety boundaries

- Active website/backend integration target: `ZaphodBeeblebrox12/prototypeweb` on `my-new-branch`.
- Academy feature integration must target `my-new-branch` only. Do not merge or deploy this work to `main`.
- Do not modify the legacy `tradeadmin` service or its database. Academy staging must use its own dedicated PostgreSQL database and separate test-mode payment credentials.
- Do not assume a GitHub push deploys staging. The last confirmed Render checkpoint had automatic deploys disabled and a previously live staging instance. Verify the currently linked branch and latest deployment in Render before any manual deploy; this PR does not change Render services or environment variables.
- A `/health/` HTTP 200 is only a liveness check. It does not prove database connectivity, authentication, email, course access, checkout, or hosted persistence.

## Environment configuration

Keep local secrets in `backend/.env` (git-ignored) and hosted secrets in the Render Environment Group. Never commit provider credentials.

For local development and tests, the default console email backend is acceptable. For hosted signup verification and password-recovery acceptance testing, configure:

- `EMAIL_BACKEND=apps.core.email_backends.ResendEmailBackend`
- `RESEND_API_KEY` with the Resend API key stored in the hosting dashboard
- `RESEND_API_TIMEOUT=10` (or another deliberate timeout)
- `DEFAULT_FROM_EMAIL` using an address/domain verified with Resend

The backend sends over HTTPS; it does not require outbound SMTP. Do not count verification or recovery email as accepted until a real message is delivered and its link has been tested. Keep staging and production provider credentials separate.

The production configuration requires a PostgreSQL `DATABASE_URL`. Confirm that Academy points to its own dedicated database; never reuse the legacy TradeAdmin database. The application configuration alone does not provision a database or create a backup/restore policy.

## Validate and import the course catalogue

The catalogue command is create-only and draft-only. It imports Trading Path, Support & Resistance, and Volume Price Analysis from the repository's canonical source material, keeps instructor-only notes separate, creates no offers, and does not publish lessons.

First validate sources without writing to the database:

```bash
cd backend
python manage.py seed_academy_catalogue
```

Only after confirming that `DATABASE_URL` points to the intended dedicated staging database, and checking that none of the three course slugs already exists, run the import once:

```bash
python manage.py seed_academy_catalogue --apply
```

Expected import: 16 unpublished modules, 78 unpublished lessons, 78 instructor-material records, and no `CourseOffer` records. The command verifies the full batch and rolls back if the import fails validation. It refuses to overwrite existing course slugs, so inspect the catalogue before retrying after any previous or partial/manual import.

After import, inspect all three drafts in Django Admin: lesson order/count, learner-facing text, figure readability, and the separation of answers and instructor notes. Do not publish lessons or make a course saleable merely because import passed. Publishing and creating a hidden Plan/CourseOffer are separate, deliberate admin steps that require content, product terms, prices, access rules and payment routing to be reviewed first.

## Staging acceptance gates

Before considering the Academy release ready for learners, perform authenticated tests against the deployed candidate version:

1. Confirm the service is running the intended branch/commit and that the database connection reports PostgreSQL.
2. Test signup, verification email delivery, login/logout, password recovery and permission denial for non-staff accounts.
3. Review the imported draft catalogue, image/media loading, Markdown rendering, saved lesson progress, locked/preview/paid/expired access and desktop/mobile layout.
4. Use test-mode payment credentials to exercise successful and failed checkout, duplicate webhook delivery, idempotency, refund/revocation, and resulting course access.
5. Verify Telegram/Discord account linking, course-specific channel mappings, access grant/revocation, and reconciliation without changing real community access unexpectedly.
6. Confirm the public website's member links route to the intended Academy host.

Record any failed gate with the deployed commit and a reproducible example. CI and `/health/` alone do not pass these live acceptance gates.
