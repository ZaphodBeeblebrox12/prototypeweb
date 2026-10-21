# Durable course storage: provider migration and rollback

## What is stored where

A provider switch must not be confused with moving the whole website or database.

- PostgreSQL remains the source of truth for course metadata, modules, lessons, builder drafts, review and publication state, asset references, permissions, entitlements, and learner progress. This media migration does not move the database.
- CourseImportAsset and CourseMediaAsset records hold logical file names. The router preserves those names across providers, so IDs and lesson content do not need to be rewritten.
- Course Builder source snapshots can exist in Google Drive and GitHub; both are inventoried and copied into the target's recovery archive.
- Static website code and checked-in course packages remain in Git and the website deployment workflow.
- Records with an original external URL but no stored file are reported separately. Records with neither a file nor an external URL also appear as warnings for manual review. This process does not fetch arbitrary third-party URLs or silently convert them into managed media.

## Configure a target provider

Keep the active provider on Google Drive until the copy and verification are complete.

Configure a dedicated Django STORAGES alias using these private hosting environment settings:

- ACADEMY_ASSET_STORAGE_BACKEND_CLASS: the target provider's Django Storage backend class.
- ACADEMY_ASSET_STORAGE_OPTIONS: a JSON object with backend options. Keep provider credentials in secret environment settings and do not commit them.
- ACADEMY_ASSET_STORAGE_ALIAS: the alias selected after cutover, normally academy_assets.
- ACADEMY_ASSET_STORAGE_DURABLE=True: explicit acknowledgement that this alias is backed by persistent durable storage.
- ACADEMY_ASSET_STORAGE_LABEL: a short label displayed in Course Builder status.
- ACADEMY_ASSET_MIGRATION_TARGET_ALIAS and ACADEMY_ASSET_MIGRATION_TARGET_DURABLE: configure the destination for migration while leaving Google Drive active.

Make sure the destination's private-access controls are suitable for instructional images. Images must still be delivered through the authenticated, entitlement-checked Django media route.

## Safe migration sequence

1. Configure the target alias only. Do not change ACADEMY_ASSET_STORAGE_BACKEND yet. Keep the Google Drive credentials/folders and GitHub branch/token available.
2. Run a read-only inventory. The command is dry-run by default:

   python manage.py migrate_course_storage --target-alias academy_assets

   It reads every stored image referenced by draft and published course records, hashes the bytes, inventories Google Drive's asset/source folders, inventories legacy GitHub images and Course Builder source JSON, and archives any surviving private local fallback files. An unreadable provider inventory or truncated GitHub tree is an error, not a pass.
3. Review all counts, errors, and warnings. Any error means the old provider must remain enabled. Review external-URL-only records separately because their bytes are not in managed storage, and investigate rows with neither a file nor a URL before cutover.
4. After confirming the destination is persistent, set ACADEMY_ASSET_MIGRATION_TARGET_DURABLE=True and run:

   python manage.py migrate_course_storage --target-alias academy_assets --apply

   This copies database-referenced assets under the same logical names, archives provider objects and historical source snapshots, verifies SHA-256 checksums, refuses to overwrite conflicting objects, and stores a timestamped JSON migration manifest in the destination. It does not change PostgreSQL references or select the new provider.
5. Run the dry-run inventory again. Identical copied objects should report as already present. Fix every error before cutover.
6. Briefly pause Course Builder image/source writes for a final copy and verification pass. This avoids a race in which an image is saved between inventory and cutover. Learner access can remain online if supported by the deployment arrangement.
7. Back up PostgreSQL separately. Then perform a deliberate deployment with ACADEMY_ASSET_STORAGE_BACKEND=django, ACADEMY_ASSET_STORAGE_ALIAS=academy_assets, ACADEMY_ASSET_STORAGE_DURABLE=True, and a meaningful ACADEMY_ASSET_STORAGE_LABEL. Do not change the old provider credentials yet.
8. Run staging smoke tests: upload, save, reload and preview a draft image; view a published lesson with multiple images; open a course containing legacy media; exercise course edit/review; check samples from every course and confirm that entitlement-controlled media delivery still works.
9. Keep the old provider data and credentials available through a rollback window. The router reads from the selected destination first, then uses retained providers/local private storage if an object is not there. The migration command never deletes the old copies.

## Completion criteria

Do not consider migration complete until the command reports zero errors, its manifest exists at the target, all database-referenced image keys have matching hashes, and both legacy provider inventories have been successfully read. The second dry run must show that the destination is consistent. A conflicting file at the same logical key stops the copy instead of overwriting it.

## Boundaries

This workflow migrates course images and source snapshots, not a PostgreSQL dump/restore, payment/user data, static-site deployment or third-party URLs. Database backups and database-provider migration are separate work. Do not remove a Google Drive folder or GitHub branch in the same operation as cutover, and do not combine storage migration with publishing a course. Validate with staging credentials and a non-production destination before using the same process on production.
