"""Admin-managed periodic scheduler: one cache-locked daemon thread.

Django-only scheduling (no Celery / no OS cron): started at app startup,
guards a cache lock so exactly one process (fleet-wide) checks due
PeriodicJobs and executes their handlers inline. Intended for LIGHT
housekeeping only (membership syncs, digests). Heavy work belongs in the
durable Job queue / workers.
"""
import importlib
import logging
import threading
import time

from django.core.cache import cache
from django.db import connections, transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

LOCK_KEY = "jobs:periodic_scheduler:lock"
LOCK_TTL_SECONDS = 180
POLL_SECONDS = 60

# periodic_job.name -> dotted path to a callable that accepts the PeriodicJob
PERIODIC_HANDLERS = {
    "sync_channel_memberships":
        "apps.bot_integration.services.channel_sync.sync_channel_memberships_window",
    "win_back_expired":
        "apps.growth.services.winback.run_win_back",
    "welcome_sequence":
        "apps.growth.services.welcomesequence.run_welcome_sequence",
}


def _claim_due_periodic_job(job_id):
    """Reserve a due periodic job in the database before running its handler.

    The scheduler starts in each Gunicorn worker. The default Django cache is
    process-local, so a cache lock alone cannot prevent duplicate runs across
    workers. The row lock and committed last_run_at reservation provide
    cross-worker exclusion without requiring a shared cache service.
    """
    from .models import PeriodicJob

    with transaction.atomic():
        try:
            job = PeriodicJob.objects.select_for_update().get(
                pk=job_id, enabled=True,
            )
        except PeriodicJob.DoesNotExist:
            return None
        if not job.is_due():
            return None
        job.last_run_at = timezone.now()
        job.save(update_fields=["last_run_at"])
        return job


def _run_due():
    from .models import PeriodicJob

    ran = 0
    job_ids = list(
        PeriodicJob.objects.filter(enabled=True).values_list("pk", flat=True)
    )
    for job_id in job_ids:
        # Save the claim before any external API call or outbound message.
        job = _claim_due_periodic_job(job_id)
        if job is None:
            continue
        path = PERIODIC_HANDLERS.get(job.name)
        if path is None:
            job.last_status = PeriodicJob.Status.ERROR
            job.last_error = "no handler registered for {!r}".format(job.name)
            job.save(update_fields=["last_status", "last_error"])
            continue
        try:
            module_path, attr = path.rsplit(".", 1)
            getattr(importlib.import_module(module_path), attr)(job)
            job.last_status = PeriodicJob.Status.OK
            job.last_error = ""
        except Exception as exc:
            logger.exception("periodic job %s failed", job.name)
            job.last_status = PeriodicJob.Status.ERROR
            job.last_error = str(exc)[:500]
        job.save(update_fields=["last_status", "last_error"])
        ran += 1
    return ran

_handlers_registered = False


def _drain_durable_queue(max_jobs=5):
    """Best-effort inline drain of the durable Job queue (Phase 0).

    Keeps webhooks/reconcile/reminders flowing even when no supervised
    `runjobs --loop` process runs. Bounded per tick; heavy or high-volume
    deployments should still run a dedicated worker.
    """
    global _handlers_registered
    try:
        from .worker import claim_next, process_job, reaper_reset
        from .handlers import register_builtin_handlers
        if not _handlers_registered:
            register_builtin_handlers()
            _handlers_registered = True
        reaper_reset()
        processed = 0
        while processed < max_jobs:
            job = claim_next()
            if job is None:
                break
            process_job(job)  # per-job failure handling is inside process_job
            processed += 1
        return processed
    except Exception:
        logger.exception("queue drain failed")
        return 0


def _loop():
    while True:
        try:
            if cache.add(LOCK_KEY, timezone.now().isoformat(), LOCK_TTL_SECONDS):
                try:
                    cache.set("jobs:scheduler:heartbeat",
                              timezone.now().isoformat(), LOCK_TTL_SECONDS)
                    _run_due()
                    _drain_durable_queue()
                finally:
                    cache.delete(LOCK_KEY)
                    connections.close_all()
        except Exception:
            logger.exception("periodic scheduler tick failed")
        time.sleep(POLL_SECONDS)


def start_scheduler():
    thread = threading.Thread(target=_loop, daemon=True, name="periodic-scheduler")
    thread.start()
    return thread
