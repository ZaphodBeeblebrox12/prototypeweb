"""Admin review queue for support tickets."""
import logging

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from .models import AffiliateLink, SupportTicket, TicketAttachment, TicketMessage
from .services import (
    add_ticket_message, approve_ticket, reject_ticket, reopen_ticket, set_ticket_status,
)

logger = logging.getLogger(__name__)


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    list_display = ["name", "referral_code", "plan", "is_active", "created_at"]
    list_filter = ["is_active", "plan"]
    search_fields = ["name", "referral_code", "url"]
    autocomplete_fields = ["plan"]


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    can_delete = False
    fields = ["file_link", "created_at"]
    readonly_fields = ["file_link", "created_at"]

    def file_link(self, obj):
        if obj.pk and obj.file:
            url = reverse("support:attachment_download", kwargs={"pk": obj.pk})
            return format_html('<a href="{}" target="_blank" rel="noopener">Open screenshot</a>', url)
        return "-"
    file_link.short_description = "Screenshot"

    def has_view_permission(self, request, obj=None):
        return bool(
            request.user.is_staff
            and (obj is None or obj.can_be_reviewed_by(request.user))
        )

    def has_add_permission(self, request, obj=None):
        return False


class TicketMessageInline(admin.TabularInline):
    """Read-only conversation trail; new entries use the explicit reply form."""
    model = TicketMessage
    extra = 0
    can_delete = False
    fields = ["author", "body", "is_internal", "created_at"]
    readonly_fields = ["author", "body", "is_internal", "created_at"]

    def has_view_permission(self, request, obj=None):
        return bool(
            request.user.is_staff
            and (obj is None or obj.can_be_reviewed_by(request.user))
        )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = [
        "short_id", "user", "category", "priority", "assigned_to", "plan",
        "status", "sla_state", "created_at", "reviewed_by",
    ]
    list_filter = ["category", "status", "priority", "assigned_to", "created_at", "affiliate_link"]
    search_fields = ["user__username", "user__email", "message", "admin_notes",
                     "assigned_to__username"]
    list_select_related = ["user", "plan", "affiliate_link", "reviewed_by", "assigned_to"]
    readonly_fields = [
        "user", "category", "affiliate_link", "message", "status", "created_at",
        "updated_at", "reviewed_by", "reviewed_at", "first_response_due_at",
        "first_response_at", "sla_state",
    ]
    inlines = [TicketAttachmentInline, TicketMessageInline]
    change_form_template = "admin/support/supportticket/change_form.html"

    fieldsets = (
        ("Ticket", {
            "fields": (("user", "created_at"), "category", "affiliate_link", "message"),
        }),
        ("Operations", {
            "fields": ("priority", "assigned_to", "first_response_due_at",
                       ("first_response_at", "sla_state")),
        }),
        ("Review", {
            "fields": ("plan", "status", "admin_notes",
                       ("reviewed_by", "reviewed_at")),
        }),
    )

    actions = ["approve_tickets", "reject_tickets"]

    def has_view_permission(self, request, obj=None):
        if not request.user.is_staff:
            return False
        return obj is None or obj.can_be_reviewed_by(request.user)

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        if not request.user.is_staff:
            return False
        if obj is None:
            return True
        return obj.can_be_reviewed_by(request.user)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "plan":
            from apps.subscriptions.models import Plan
            kwargs["queryset"] = Plan.objects.filter(is_hidden=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        ticket = self.get_object(request, object_id)
        if ticket and not ticket.can_be_reviewed_by(request.user):
            raise PermissionDenied
        if request.method == "POST" and ticket is not None:
            if "_send_reply" in request.POST:
                return self._send_reply(request, ticket)
            if "_start_review" in request.POST:
                return self._set_status(request, ticket, "in_progress")
            if "_reopen_ticket" in request.POST:
                return self._reopen_ticket(request, ticket)
            if "_approve_grant" in request.POST:
                return self._approve(request, ticket)
            if "_reject" in request.POST:
                return self._reject(request, ticket)
        return super().change_view(request, object_id, form_url, extra_context)

    def _approve(self, request, ticket):
        from apps.subscriptions.models import Plan

        raw_plan_id = (request.POST.get("plan") or "").strip()
        if raw_plan_id:
            plan = Plan.objects.filter(pk=raw_plan_id, is_hidden=True).first()
            if plan is None:
                messages.error(request, "Pick a valid hidden plan.")
                return HttpResponseRedirect(request.path)
        else:
            plan = ticket.plan or (
                ticket.affiliate_link.plan
                if ticket.affiliate_link_id and ticket.affiliate_link.plan_id else None
            )

        if ticket.is_access_request and plan is None:
            messages.error(request, "Assign a plan before approving an access request.")
            return HttpResponseRedirect(request.path)

        notes = request.POST.get("admin_notes", ticket.admin_notes)
        try:
            approve_ticket(ticket, plan, request.user, notes=notes)
            if ticket.is_access_request:
                messages.success(request, f"Approved - {ticket.user} granted {plan.name}.")
            else:
                messages.success(request, "Ticket marked resolved; user notified.")
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        except Exception:
            # Reconciliation-enqueue failures must roll back the approval and
            # grant. Show a safe, actionable error instead of a false success.
            logger.exception("ticket approval failed ticket=%s", ticket.pk)
            messages.error(
                request,
                "Approval failed and no changes were committed. Check the logs and retry.",
            )
        return HttpResponseRedirect(request.path)

    def _reject(self, request, ticket):
        notes = request.POST.get("admin_notes", ticket.admin_notes)
        try:
            reject_ticket(ticket, request.user, notes)
            messages.success(request, "Ticket closed; user notified.")
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        return HttpResponseRedirect(request.path)

    def _set_status(self, request, ticket, status):
        try:
            set_ticket_status(ticket, request.user, status)
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, f"Ticket moved to {ticket.get_status_display().lower()}.")
        return HttpResponseRedirect(request.path)

    def _reopen_ticket(self, request, ticket):
        try:
            reopen_ticket(ticket, request.user)
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Ticket reopened and returned to active work.")
        return HttpResponseRedirect(request.path)

    def sla_state(self, obj):
        if obj.is_sla_overdue:
            return format_html('<strong style="color:#b71c1c">Overdue</strong>')
        if obj.first_response_at:
            return "Responded"
        if obj.first_response_due_at:
            return f"Due {obj.first_response_due_at:%Y-%m-%d %H:%M}"
        return "No deadline"
    sla_state.short_description = "First-response SLA"

    def _send_reply(self, request, ticket):
        body = request.POST.get("staff_reply", "")
        is_internal = request.POST.get("staff_is_internal") == "on"
        try:
            add_ticket_message(ticket, request.user, body, is_internal=is_internal)
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        else:
            messages.success(
                request,
                "Internal note saved." if is_internal else "Reply sent to the member.",
            )
        return HttpResponseRedirect(request.path)

    @admin.action(description="Approve selected tickets (mapped plan or assigned plan required)")
    def approve_tickets(self, request, queryset):
        for ticket in queryset.select_related("plan", "affiliate_link", "affiliate_link__plan"):
            plan = ticket.plan or (
                ticket.affiliate_link.plan
                if ticket.affiliate_link_id and ticket.affiliate_link.plan_id else None
            )
            if ticket.is_access_request and plan is None:
                messages.warning(request, f"{ticket.short_id}: no plan assigned or mapped - skipped.")
                continue
            try:
                approve_ticket(ticket, plan, request.user, notes=ticket.admin_notes)
            except (ValueError, PermissionError) as exc:
                messages.warning(request, f"{ticket.short_id}: {exc}")
            except Exception:
                logger.exception("bulk support approval failed ticket=%s", ticket.pk)
                messages.error(request, f"{ticket.short_id}: approval failed; no changes were committed.")
        messages.success(request, "Approval pass complete.")

    @admin.action(description="Reject selected tickets (admin notes required)")
    def reject_tickets(self, request, queryset):
        for ticket in queryset.select_related("plan", "affiliate_link", "affiliate_link__plan"):
            try:
                reject_ticket(ticket, request.user, ticket.admin_notes)
            except (ValueError, PermissionError) as exc:
                messages.warning(request, f"{ticket.short_id}: {exc}")
        messages.success(request, "Rejection pass complete.")
