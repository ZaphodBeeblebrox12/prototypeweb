"""Durable jobs admin: operational / read-mostly."""
from django.contrib import admin

from .models import Job, PeriodicJob


class StalledJobFilter(admin.SimpleListFilter):
    """Show only pending/running jobs that have already retried three times."""

    title = "queue state"
    parameter_name = "queue_state"

    def lookups(self, request, model_admin):
        return (("stalled", "Stalled (3+ attempts)"),)

    def queryset(self, request, queryset):
        if self.value() == "stalled":
            return queryset.filter(
                attempts__gte=3,
                status__in=[Job.STATUS_RUNNING, Job.STATUS_PENDING],
            )
        return queryset


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Read-mostly view of the durable-jobs queue.  Do not hand-edit job
    state here (that would corrupt the queue); this is for inspection."""

    list_display = [
        "id", "kind", "status", "attempts", "max_attempts",
        "next_attempt_at", "locked_at", "created_at",
    ]
    list_filter = ["kind", "status", "created_at", "updated_at", StalledJobFilter]
    search_fields = ["kind", "idempotency_key", "payload"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    # Queue state is owned by the worker; admins inspect, not mutate.
    readonly_fields = [f.name for f in Job._meta.fields]

    def has_delete_permission(self, request, obj=None):
        # Deleting a job loses operational/audit trail of the queue.
        return False

    def has_add_permission(self, request):
        # Jobs are enqueued by code, not created by hand.
        return False


@admin.register(PeriodicJob)
class PeriodicJobAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled', 'interval_minutes', 'max_calls_per_run',
                    'last_run_at', 'last_status']
    list_filter = ['enabled', 'last_status']
    search_fields = ['name']
    readonly_fields = ['last_run_at', 'last_status', 'last_error', 'state', 'created_at']

