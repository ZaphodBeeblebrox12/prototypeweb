"""Copy and verify course media/source archives before a storage-provider cutover.

This command is read-only by default. It never changes the active provider or
rewrites database file references; cutover is a separate deployment operation.
"""
import base64
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from urllib.parse import quote

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.core.management.base import BaseCommand, CommandError

from apps.academy.google_drive_storage import DRIVE_API
from apps.academy.models import CourseImportAsset, CourseMediaAsset
from apps.academy.storage import GoogleDrivePrivateCourseAssetStorage, course_asset_storage

GITHUB_API = "https://api.github.com"


def _sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _safe_component(value):
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "file")).strip("._")
    return (value or "file")[:140]


def _read_storage(storage, name):
    with storage.open(name, "rb") as stream:
        return stream.read()


def _copy_to_target(target, target_name, raw, *, apply):
    """Copy idempotently. Never overwrite different bytes and verify every write."""
    expected = _sha256(raw)
    if target.exists(target_name):
        actual = _sha256(_read_storage(target, target_name))
        if actual != expected:
            raise ValueError(
                f"Target conflict at {target_name}: content hash differs; nothing was overwritten."
            )
        return {"status": "already_present", "sha256": expected, "size": len(raw)}
    if not apply:
        return {"status": "planned", "sha256": expected, "size": len(raw)}
    saved_name = target.save(
        target_name, ContentFile(raw, name=PurePosixPath(target_name).name)
    )
    if saved_name != target_name:
        raise ValueError(
            f"Target storage changed the logical path for {target_name}; returned {saved_name!r}."
        )
    if _sha256(_read_storage(target, target_name)) != expected:
        raise ValueError(f"Checksum verification failed after writing {target_name}.")
    return {"status": "copied_verified", "sha256": expected, "size": len(raw)}


def _github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "TradeThesis-course-storage-migration",
    }
    token = str(getattr(settings, "ACADEMY_GITHUB_ASSET_TOKEN", "") or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _github_tree_files():
    repository = str(getattr(settings, "ACADEMY_GITHUB_ASSET_REPOSITORY", "") or "").strip()
    branch = str(getattr(settings, "ACADEMY_GITHUB_ASSET_BRANCH", "my-new-branch") or "my-new-branch").strip()
    if not repository:
        raise RuntimeError("The legacy GitHub repository is not configured.")
    response = requests.get(
        f"{GITHUB_API}/repos/{repository}/branches/{quote(branch, safe='')}",
        headers=_github_headers(), timeout=20,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Could not inventory the legacy GitHub branch (HTTP {response.status_code}).")
    branch_data = response.json()
    tree_sha = branch_data.get("commit", {}).get("commit", {}).get("tree", {}).get("sha")
    if not tree_sha:
        raise RuntimeError("GitHub did not return the legacy branch tree SHA.")
    response = requests.get(
        f"{GITHUB_API}/repos/{repository}/git/trees/{tree_sha}",
        headers=_github_headers(), params={"recursive": "1"}, timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Could not inventory legacy GitHub assets (HTTP {response.status_code}).")
    payload = response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("tree"), list):
        raise RuntimeError("GitHub returned an unreadable repository tree.")
    if payload.get("truncated"):
        raise RuntimeError("GitHub truncated the repository tree; inventory completeness cannot be certified.")
    return repository, payload["tree"]


def _github_blob_bytes(repository, sha):
    response = requests.get(
        f"{GITHUB_API}/repos/{repository}/git/blobs/{sha}",
        headers=_github_headers(), timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Could not download a legacy GitHub blob (HTTP {response.status_code}).")
    payload = response.json()
    if payload.get("encoding") != "base64" or not payload.get("content"):
        raise RuntimeError("GitHub returned a blob with an unsupported encoding.")
    try:
        return base64.b64decode(payload["content"], validate=True)
    except (ValueError, TypeError) as exc:
        raise RuntimeError("GitHub returned invalid base64 for a legacy blob.") from exc


def _drive_files(storage, folder_id):
    page_token = None
    while True:
        params = {
            "q": f"'{folder_id}' in parents and trashed = false",
            "pageSize": 1000,
            "orderBy": "name",
            "fields": "nextPageToken,files(id,name,mimeType,size,md5Checksum,properties,modifiedTime)",
        }
        if page_token:
            params["pageToken"] = page_token
        response = storage._drive_request("GET", f"{DRIVE_API}/files", params=params)
        try:
            payload = response.json()
        except (ValueError, AttributeError, TypeError) as exc:
            raise RuntimeError("Google Drive returned an unreadable folder inventory.") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("files"), list):
            raise RuntimeError("Google Drive returned an unreadable folder inventory.")
        for item in payload["files"]:
            if isinstance(item, dict) and item.get("id"):
                yield item
        page_token = payload.get("nextPageToken")
        if not page_token:
            break


def _drive_blob_bytes(storage, file_id):
    response = storage._drive_request(
        "GET", f"{DRIVE_API}/files/{file_id}",
        params={"alt": "media"}, expected=(200,),
    )
    return response.content


class Command(BaseCommand):
    help = (
        "Inventory and checksum-copy course assets and source archives to another "
        "Django storage alias. Dry-run is the default and active provider is never switched."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--target-alias",
            default=str(getattr(settings, "ACADEMY_ASSET_MIGRATION_TARGET_ALIAS", "") or "").strip(),
            help="Django STORAGES alias for the new durable destination.",
        )
        parser.add_argument(
            "--apply", action="store_true",
            help="Write and verify copies. Without this flag the command is read-only.",
        )

    def handle(self, *args, **options):
        target_alias = str(options.get("target_alias") or "").strip()
        apply = bool(options.get("apply"))
        if not target_alias:
            raise CommandError("Set ACADEMY_ASSET_MIGRATION_TARGET_ALIAS or supply --target-alias.")
        if apply and not bool(getattr(settings, "ACADEMY_ASSET_MIGRATION_TARGET_DURABLE", False)):
            raise CommandError(
                "Refusing to write: confirm the destination is durable, then set "
                "ACADEMY_ASSET_MIGRATION_TARGET_DURABLE=True."
            )
        try:
            target = storages[target_alias]
        except Exception as exc:
            raise CommandError(f"Django storage alias {target_alias!r} is not configured.") from exc

        active = str(getattr(settings, "ACADEMY_ASSET_STORAGE_BACKEND", "google_drive")).strip().lower()
        report = {
            "schema_version": 1,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "target_alias": target_alias,
            "mode": "apply" if apply else "dry_run",
            "active_provider": active,
            "counts": {},
            "entries": [],
            "errors": [],
            "warnings": [],
        }
        assets_by_name = {}
        for model, kind in (
            (CourseImportAsset, "course_import_asset"),
            (CourseMediaAsset, "course_media_asset"),
        ):
            for record in model.objects.exclude(file="").iterator():
                name = str(record.file.name or "").strip()
                if name:
                    item = assets_by_name.setdefault(name, {"name": name, "records": []})
                    item["records"].append({"kind": kind, "id": str(record.pk)})

        counts = {
            "database_asset_keys": len(assets_by_name),
            "database_asset_references": sum(len(v["records"]) for v in assets_by_name.values()),
            "database_assets_copied_verified": 0,
            "database_assets_already_present": 0,
            "database_assets_planned": 0,
            "drive_source_snapshots_copied_verified": 0,
            "drive_source_snapshots_already_present": 0,
            "drive_source_snapshots_planned": 0,
            "drive_asset_archives_copied_verified": 0,
            "drive_asset_archives_already_present": 0,
            "drive_asset_archives_planned": 0,
            "github_source_snapshots_copied_verified": 0,
            "github_source_snapshots_already_present": 0,
            "github_source_snapshots_planned": 0,
            "github_asset_archives_copied_verified": 0,
            "github_asset_archives_already_present": 0,
            "github_asset_archives_planned": 0,
            "local_asset_archives_copied_verified": 0,
            "local_asset_archives_already_present": 0,
            "local_asset_archives_planned": 0,
            "records_without_stored_file": (
                CourseImportAsset.objects.filter(file="").count()
                + CourseMediaAsset.objects.filter(file="").count()
            ),
            "records_without_file_or_external_url": (
                CourseImportAsset.objects.filter(file="", original_url="").count()
                + CourseMediaAsset.objects.filter(file="", original_url="").count()
            ),
            "external_url_only_records": (
                CourseImportAsset.objects.filter(file="").exclude(original_url="").count()
                + CourseMediaAsset.objects.filter(file="").exclude(original_url="").count()
            ),
        }

        def copy_entry(target_name, raw, *, kind, source_id=None, records=None):
            try:
                result = _copy_to_target(target, target_name, raw, apply=apply)
                result.update({
                    "kind": kind, "target_name": target_name,
                    "source_id": source_id, "records": records or [],
                })
                report["entries"].append(result)
                suffix = {
                    "copied_verified": "_copied_verified",
                    "already_present": "_already_present",
                    "planned": "_planned",
                }.get(result["status"])
                if kind == "database_asset":
                    if result["status"] == "copied_verified":
                        counts["database_assets_copied_verified"] += 1
                    elif result["status"] == "already_present":
                        counts["database_assets_already_present"] += 1
                    elif result["status"] == "planned":
                        counts["database_assets_planned"] += 1
                elif suffix:
                    key = {
                        "drive_source_snapshot": "drive_source_snapshots",
                        "drive_asset_archive": "drive_asset_archives",
                        "github_source_snapshot": "github_source_snapshots",
                        "github_asset_archive": "github_asset_archives",
                        "local_asset_archive": "local_asset_archives",
                    }.get(kind)
                    if key:
                        counts[key + suffix] += 1
            except Exception as exc:
                report["errors"].append({
                    "kind": kind, "target_name": target_name,
                    "source_id": source_id, "error": str(exc),
                    "records": records or [],
                })

        # Copy all database-referenced draft/live images under their existing logical names.
        for name, item in assets_by_name.items():
            try:
                copy_entry(name, _read_storage(course_asset_storage, name),
                           kind="database_asset", records=item["records"])
            except Exception as exc:
                report["errors"].append({
                    "kind": "database_asset_source_read", "target_name": name,
                    "error": str(exc), "records": item["records"],
                })

        # Inventory any surviving private local fallback files as well. Do not treat a
        # missing local directory as durable storage, and never copy a tree into itself.
        local_root = Path(
            getattr(settings, "ACADEMY_PRIVATE_MEDIA_ROOT", "")
            or (settings.BASE_DIR / "private_course_media")
        ).resolve()
        if local_root.exists():
            target_location = getattr(target, "location", None)
            if target_location:
                target_root = Path(target_location).resolve()
                if target_root == local_root or local_root in target_root.parents:
                    raise CommandError(
                        "The target filesystem is the same as, or nested inside, the private local "
                        "source directory. Configure a separate target to avoid self-copying."
                    )
            for path in sorted(local_root.rglob("*")):
                if not path.is_file() or path.is_symlink():
                    continue
                relative = path.relative_to(local_root).as_posix()
                target_name = "course-assets/archive/local-filesystem/" + relative
                try:
                    copy_entry(target_name, path.read_bytes(), kind="local_asset_archive",
                               source_id=relative)
                except Exception as exc:
                    report["errors"].append({
                        "kind": "local_asset_archive_source_read",
                        "source_id": relative, "error": str(exc),
                    })
        elif active == "local_filesystem":
            report["errors"].append({
                "kind": "local_filesystem_inventory",
                "error": "The active local private-media directory does not exist; its inventory cannot be certified.",
            })
        else:
            report["warnings"].append(
                "The private local fallback directory is absent; no local-only objects were available to archive."
            )

        drive = GoogleDrivePrivateCourseAssetStorage()
        active = str(getattr(settings, "ACADEMY_ASSET_STORAGE_BACKEND", "google_drive")).strip().lower()
        drive_credentials_present = bool(
            getattr(settings, "ACADEMY_GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON", "")
            or getattr(settings, "ACADEMY_GOOGLE_DRIVE_REFRESH_TOKEN", "")
            or drive._refresh_token
        )
        drive_required = active == "google_drive" or drive_credentials_present
        if drive_required and not drive._drive_auth_configured:
            report["errors"].append({
                "kind": "google_drive_inventory",
                "error": "Drive access is not configured; complete Google Drive inventory cannot be certified.",
            })
        elif drive._drive_auth_configured:
            asset_folder, source_folder = drive._asset_folder_id, drive._source_folder_id
            if not asset_folder:
                report["errors"].append({
                    "kind": "google_drive_asset_inventory",
                    "error": "The Drive asset folder ID is missing; inventory cannot be certified.",
                })
            else:
                try:
                    # Archive every Drive object, including duplicate logical keys. Database-
                    # referenced objects are also copied under their canonical logical names above.
                    for item in _drive_files(drive, asset_folder):
                        file_id = str(item["id"])
                        target_name = "course-assets/archive/google-drive/{}-{}".format(
                            file_id, _safe_component(item.get("name"))
                        )
                        try:
                            copy_entry(target_name, _drive_blob_bytes(drive, file_id),
                                       kind="drive_asset_archive", source_id=file_id)
                        except Exception as exc:
                            report["errors"].append({
                                "kind": "drive_asset_archive_source_read",
                                "source_id": file_id, "error": str(exc),
                            })
                except Exception as exc:
                    report["errors"].append({"kind": "google_drive_asset_inventory", "error": str(exc)})

            if not source_folder:
                report["errors"].append({
                    "kind": "google_drive_source_inventory",
                    "error": "The Drive source snapshot folder ID is missing; source inventory cannot be certified.",
                })
            else:
                try:
                    for item in _drive_files(drive, source_folder):
                        file_id = str(item["id"])
                        target_name = "course-source/migrated-snapshots/google-drive/{}-{}".format(
                            file_id, _safe_component(item.get("name"))
                        )
                        try:
                            copy_entry(target_name, _drive_blob_bytes(drive, file_id),
                                       kind="drive_source_snapshot", source_id=file_id)
                        except Exception as exc:
                            report["errors"].append({
                                "kind": "drive_source_snapshot_source_read",
                                "source_id": file_id, "error": str(exc),
                            })
                except Exception as exc:
                    report["errors"].append({"kind": "google_drive_source_inventory", "error": str(exc)})
        elif not drive_required:
            report["warnings"].append("Google Drive is not configured; no Drive-only archive inventory was performed.")

        # Archive provider-only GitHub assets and builder source snapshots as a recovery layer.
        prefix = str(getattr(settings, "ACADEMY_GITHUB_ASSET_PATH_PREFIX", "course-assets") or "course-assets").strip("/")
        try:
            repository, tree = _github_tree_files()
            for item in tree:
                path = str(item.get("path") or "")
                if item.get("type") != "blob" or not item.get("sha"):
                    continue
                if path.startswith(prefix + "/"):
                    logical_name = path[len(prefix) + 1:]
                    target_name = "course-assets/archive/github/" + logical_name
                    try:
                        copy_entry(target_name, _github_blob_bytes(repository, item["sha"]),
                                   kind="github_asset_archive", source_id=path)
                    except Exception as exc:
                        report["errors"].append({
                            "kind": "github_asset_archive_source_read", "source_id": path,
                            "error": str(exc),
                        })
                elif path.startswith("course-source/builder-drafts/") and path.lower().endswith(".json"):
                    relative = path[len("course-source/builder-drafts/"):]
                    target_name = "course-source/migrated-snapshots/github/" + relative
                    try:
                        copy_entry(target_name, _github_blob_bytes(repository, item["sha"]),
                                   kind="github_source_snapshot", source_id=path)
                    except Exception as exc:
                        report["errors"].append({
                            "kind": "github_source_snapshot_source_read", "source_id": path,
                            "error": str(exc),
                        })
        except Exception as exc:
            report["errors"].append({"kind": "github_inventory", "error": str(exc)})

        report["counts"] = counts
        if counts["external_url_only_records"]:
            report["warnings"].append(
                f'{counts["external_url_only_records"]} asset records use external original URLs and have no stored file. '
                "Their URLs were not downloaded or rewritten."
            )
        if counts["records_without_file_or_external_url"]:
            report["warnings"].append(
                f'{counts["records_without_file_or_external_url"]} asset records have neither a stored file nor an external URL. '
                "Review these records and confirm they are intentional placeholders before cutover."
            )
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        report["complete"] = not report["errors"]

        manifest_path = None
        if apply:
            manifest_path = (
                "course-source/storage-migrations/migration-"
                + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                + ".json"
            )
            report["manifest_path"] = manifest_path
            try:
                manifest_raw = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
                saved = target.save(manifest_path, ContentFile(manifest_raw, name="migration-report.json"))
                if saved != manifest_path:
                    report["errors"].append({
                        "kind": "migration_manifest", "target_name": manifest_path,
                        "error": f"Target storage changed manifest path to {saved!r}.",
                    })
            except Exception as exc:
                report["errors"].append({
                    "kind": "migration_manifest", "target_name": manifest_path, "error": str(exc),
                })

        self.stdout.write(f"Target alias: {target_alias}")
        self.stdout.write(f"Mode: {'APPLY' if apply else 'DRY RUN (no writes)'}")
        self.stdout.write(f"Unique database asset keys: {counts['database_asset_keys']}")
        self.stdout.write(f"Database asset references: {counts['database_asset_references']}")
        self.stdout.write(f"External-URL-only records (not downloaded): {counts['external_url_only_records']}")
        self.stdout.write(f"Migration complete: {'YES' if not report['errors'] else 'NO'}")
        if manifest_path:
            self.stdout.write(f"Manifest: {manifest_path}")
        for warning in report["warnings"]:
            self.stdout.write(self.style.WARNING("Warning: " + warning))
        if report["errors"]:
            for error in report["errors"][:20]:
                self.stdout.write(self.style.ERROR(
                    "{}: {} {}".format(
                        error.get("kind"), error.get("target_name") or error.get("source_id") or "",
                        error.get("error"),
                    )
                ))
            if len(report["errors"]) > 20:
                self.stdout.write(self.style.ERROR(f"... plus {len(report['errors']) - 20} additional errors."))
            raise CommandError(
                f"Storage migration is incomplete ({len(report['errors'])} errors). "
                "Keep the old provider enabled and inspect the report before retrying."
            )
        self.stdout.write(self.style.SUCCESS(
            "Inventory/copy checks passed. The active provider was not changed; review the report before cutover."
        ))
