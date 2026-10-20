# TradeThesis Academy — Google Drive durable storage

## Storage contract

- Django/PostgreSQL remains the source of truth for drafts, authors, review state, publication, and permissions.
- Google Drive is the preferred durable store for course images and JSON source snapshots.
- Existing GitHub-backed assets remain readable as a migration fallback.
- Google Drive failures must be reported as retryable; never claim a remote backup succeeded unless the API confirms it.
- Course media remains private and is delivered only through authenticated and entitlement-checked Django views.

## Google Cloud and staging setup

1. Enable the Google Drive API in the dedicated Google Cloud project.
2. In Google Auth Platform, use External audience for the personal Google account that will own the Drive files.
3. Create a Web application OAuth client. Use this exact Authorized redirect URI:

   https://tradethesis-academy-staging.onrender.com/staff/google-drive/oauth/callback/

   Leave Authorized JavaScript origins empty. Do not add a wildcard or production URL.
4. On the tradethesis-academy-staging Render service only, set:
   - ACADEMY_GOOGLE_DRIVE_CLIENT_ID — the OAuth client ID
   - ACADEMY_GOOGLE_DRIVE_CLIENT_SECRET — the OAuth client secret
   - ACADEMY_GOOGLE_DRIVE_REDIRECT_URI — the exact HTTPS URI above

   Do not put the client secret in GitHub, the Course Builder, or chat. The callback stores the refresh token encrypted in PostgreSQL; it is not displayed in the browser.
5. After the patch is reviewed, tested, and deployed to staging with explicit approval, sign in as an authorized course-content admin and open:

   https://tradethesis-academy-staging.onrender.com/staff/google-drive/connect/

   Approve Drive access. The callback creates two private folders in the authorized account's My Drive and stores their folder IDs.
6. Google states that external OAuth apps in Testing may issue refresh tokens that expire after seven days for Drive scopes. Keep Testing during validation. Before unattended backups are relied on, choose an appropriate publishing status and authorize Drive again after changing it.

## Validation before cutover

- Run the focused storage, OAuth, course builder, failure-path, and review tests with Google APIs mocked.
- In staging, save and reload a small image and a source snapshot; verify both are in the intended private folders and can be read back.
- Verify a Google Drive timeout or 403 is reported as retryable and does not falsely claim success.
- Confirm legacy GitHub-only assets remain readable before migrating old copies.
- Do not deploy, alter production credentials, or remove existing GitHub storage until staging verification and separate approval are complete.

## Boundaries

This patch does not automatically migrate every existing GitHub object to Drive. It does not replace PostgreSQL backups or durable database storage. Storage provider selection, folder permissions, credential validity, and token lifetime must be verified in staging before cutover.
