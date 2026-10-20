"""Lifecycle helpers for persisted Course Builder drafts."""
from django.db import transaction

from .models import CourseImport


def mark_builder_draft_deleted(record):
    """Hide a builder draft permanently and remove its private staged media.

    Keep the CourseImport row as a tombstone so a stale browser tab cannot
    recreate the draft by autosaving an old serverDraftId.
    """
    if record.status != CourseImport.Status.DRAFT:
        return False

    for asset in record.assets.all():
        if asset.file:
            storage = asset.file.storage
            name = asset.file.name
            transaction.on_commit(
                lambda storage=storage, name=name: storage.delete(name),
                robust=True,
            )
    record.assets.all().delete()
    record.status = CourseImport.Status.DELETED
    record.save(update_fields=["status", "updated_at"])
    return True
