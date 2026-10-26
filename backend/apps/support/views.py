"""Member-facing support ticket views, protected attachment delivery, and replies."""
import logging
import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View
from django.db import IntegrityError, transaction

from .forms import SupportTicketForm, TicketReplyForm
from .models import MAX_ATTACHMENTS_PER_TICKET, SupportTicket, TicketAttachment
from .services import (
    add_ticket_message,
    notify_staff_about_ticket,
    send_ticket_confirmation,
)

logger = logging.getLogger(__name__)

_IMAGE_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


class RequestTicketView(LoginRequiredMixin, CreateView):
    """Raise a support ticket (access request / billing / technical)."""
    model = SupportTicket
    form_class = SupportTicketForm
    template_name = "support/request_ticket.html"
    success_url = reverse_lazy("support:my_tickets")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # One open ticket per category. Do not block a separate billing issue
        # merely because the member also has an access request in progress.
        category = (request.POST.get("category") or "").strip()
        if request.method == "POST" and category in SupportTicket.Category.values:
            existing = SupportTicket.objects.filter(
                user=request.user,
                category=category,
                status__in=SupportTicket.ACTIVE_STATUSES,
            ).first()
            if existing:
                messages.info(
                    request,
                    "You already have an open ticket in this category. Continue the existing conversation.",
                )
                return HttpResponseRedirect(
                    reverse_lazy("support:ticket_detail", kwargs={"pk": existing.pk})
                )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        stored_attachments = []
        try:
            with transaction.atomic():
                form.instance.user = self.request.user
                link = form.cleaned_data.get("affiliate_link")
                if (form.cleaned_data.get("category") == SupportTicket.Category.ACCESS
                        and link and link.plan_id and link.plan.is_hidden):
                    # The referral-link mapping is the default plan. Reviewers
                    # may explicitly override it later, subject to that plan's ACL.
                    form.instance.plan = link.plan
                self.object = form.save()
                uploads = (form.cleaned_data.get("attachments") or [])[
                    :MAX_ATTACHMENTS_PER_TICKET
                ]
                for upload in uploads:
                    attachment = TicketAttachment(ticket=self.object, file=upload)
                    attachment.save()
                    stored_attachments.append(attachment)
        except OSError:
            # Drive writes are outside the database transaction. Remove any
            # earlier successful uploads if a later upload in this batch fails.
            for attachment in reversed(stored_attachments):
                try:
                    attachment.file.storage.delete(attachment.file.name)
                except Exception:
                    logger.exception(
                        "support upload cleanup failed ticket=%s attachment=%s",
                        getattr(self.object, "pk", None),
                        attachment.pk,
                    )
            logger.exception(
                "support attachment storage failed for user=%s",
                self.request.user.pk,
            )
            form.add_error(
                "attachments",
                "We couldn't securely store the screenshots just now. "
                "Please try again in a moment; your ticket has not been submitted.",
            )
            return self.form_invalid(form)
        except IntegrityError:
            category = form.cleaned_data.get("category")
            existing = SupportTicket.objects.filter(
                user=self.request.user,
                category=category,
                status__in=SupportTicket.ACTIVE_STATUSES,
            ).first()
            if existing:
                messages.info(
                    self.request,
                    "You already have an open ticket in this category. Continue the existing conversation.",
                )
                return HttpResponseRedirect(
                    reverse_lazy("support:ticket_detail", kwargs={"pk": existing.pk})
                )
            form.add_error(None, "This ticket could not be created because a conflicting open ticket exists.")
            return self.form_invalid(form)
        except ValidationError as exc:
            form.add_error("attachments", "; ".join(exc.messages))
            return self.form_invalid(form)

        # Send notifications after the transaction commits; an email provider
        # failure must not turn a successfully created ticket into a 500.
        try:
            send_ticket_confirmation(self.object)
        except Exception:
            logger.exception("ticket confirmation processing failed ticket=%s", self.object.pk)
        try:
            notify_staff_about_ticket(self.object)
        except Exception:
            logger.exception("staff alert processing failed ticket=%s", self.object.pk)
        messages.success(self.request,
                         "Ticket submitted. We'll review it and get back to you.")
        return HttpResponseRedirect(self.get_success_url())


class MyTicketsView(LoginRequiredMixin, ListView):
    model = SupportTicket
    template_name = "support/my_tickets.html"
    context_object_name = "tickets"
    paginate_by = 20

    def get_queryset(self):
        return (SupportTicket.objects
                .filter(user=self.request.user)
                .select_related("affiliate_link", "plan")
                .prefetch_related("attachments", "messages"))


class TicketDetailView(LoginRequiredMixin, DetailView):
    CONVERSATION_PAGE_SIZE = 8

    model = SupportTicket
    template_name = "support/ticket_detail.html"
    context_object_name = "ticket"

    def get_queryset(self):
        return (SupportTicket.objects
                .select_related("affiliate_link", "plan", "reviewed_by")
                .prefetch_related("attachments"))

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        obj = self.get_object()
        is_owner = obj.user_id == request.user.id
        is_authorized_staff = request.user.is_staff and obj.can_be_reviewed_by(request.user)
        if not (is_owner or is_authorized_staff):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_review"] = (
            self.request.user.is_staff
            and self.object.can_be_reviewed_by(self.request.user)
        )
        # Keep long ticket histories compact by default. Load older items in
        # deliberate batches rather than rendering every message on each request.
        message_queryset = self.object.messages.select_related("author")
        if not context["can_review"]:
            message_queryset = message_queryset.filter(is_internal=False)

        total_message_count = message_queryset.count()
        try:
            requested_count = int(
                self.request.GET.get("show_messages", self.CONVERSATION_PAGE_SIZE)
            )
        except (TypeError, ValueError):
            requested_count = self.CONVERSATION_PAGE_SIZE
        visible_count = min(
            total_message_count,
            max(self.CONVERSATION_PAGE_SIZE, requested_count),
        )
        latest_messages = list(
            message_queryset.order_by("-created_at", "-pk")[:visible_count]
        )
        latest_messages.reverse()

        context["conversation_messages"] = latest_messages
        context["total_message_count"] = total_message_count
        context["has_earlier_messages"] = total_message_count > visible_count
        context["next_message_limit"] = min(
            total_message_count, visible_count + self.CONVERSATION_PAGE_SIZE
        )
        context["messages_to_load"] = min(
            self.CONVERSATION_PAGE_SIZE, total_message_count - visible_count
        )
        context["earlier_message_count"] = total_message_count - visible_count
        context["reply_form"] = TicketReplyForm()
        return context


class TicketReplyView(LoginRequiredMixin, View):
    """Allow the ticket owner to add a public follow-up while review is pending."""
    http_method_names = ["post"]

    def post(self, request, pk):
        ticket = get_object_or_404(SupportTicket, pk=pk)
        if ticket.user_id != request.user.pk:
            raise PermissionDenied
        form = TicketReplyForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Enter a reply of 10,000 characters or fewer.")
            return redirect("support:ticket_detail", pk=pk)
        try:
            add_ticket_message(ticket, request.user, form.cleaned_data["body"])
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Reply added to your ticket.")
        return redirect("support:ticket_detail", pk=pk)


class TicketAttachmentDownloadView(LoginRequiredMixin, View):
    """Serve attachments only to the ticket owner or an authorized reviewer."""

    def get(self, request, pk):
        attachment = get_object_or_404(
            TicketAttachment.objects.select_related("ticket", "ticket__user", "ticket__plan"),
            pk=pk,
        )
        ticket = attachment.ticket
        is_owner = ticket.user_id == request.user.pk
        is_authorized_staff = request.user.is_staff and ticket.can_be_reviewed_by(request.user)
        if not (is_owner or is_authorized_staff):
            raise PermissionDenied

        extension = os.path.splitext(attachment.file.name)[1].lower()
        content_type = _IMAGE_CONTENT_TYPES.get(extension)
        if not content_type:
            raise Http404("Unsupported attachment type.")
        try:
            stream = attachment.file.open("rb")
        except (FileNotFoundError, OSError):
            logger.exception("support attachment unavailable attachment=%s", attachment.pk)
            raise Http404("This attachment is unavailable. Please contact support.")

        filename = f"support-{ticket.short_id}-{str(attachment.pk)[:8]}{extension}"
        response = FileResponse(stream, content_type=content_type)
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class WithdrawTicketView(LoginRequiredMixin, View):
    """Let a user close (withdraw) their own pending ticket."""
    http_method_names = ["post"]

    def post(self, request, pk):
        ticket = get_object_or_404(SupportTicket, pk=pk)
        if ticket.user_id != request.user.id:
            raise PermissionDenied
        if not ticket.is_open:
            messages.error(request, "Only open tickets can be withdrawn.")
            return redirect("support:ticket_detail", pk=pk)
        ticket.status = SupportTicket.Status.WITHDRAWN
        ticket.save(update_fields=["status", "updated_at"])
        messages.success(request, "Ticket withdrawn.")
        return redirect("support:ticket_detail", pk=pk)
