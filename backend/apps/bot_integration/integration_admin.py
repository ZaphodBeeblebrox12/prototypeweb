"""
Django admin tools for the native Telegram Bot API integration.

All Telegram operations use BotConfig's configured bot token directly.
BotRuntimeState remains visible only as legacy-bridge diagnostic history.
"""
from __future__ import annotations

import time

from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import path

from .models import BotAccessAudit, PlanChannelMapping, TelegramAccount
from .runtime_models import BotRuntimeState
from .reconcile_jobs import ProvisionTransport
from .services.telegram import TelegramBotService


@admin.register(BotRuntimeState)
class BotRuntimeStateAdmin(admin.ModelAdmin):
    list_display = ("instance_id", "status", "contract", "contract_version",
                    "base_url", "bot_username", "last_seen")
    list_filter = ("status", "contract", "contract_version")
    readonly_fields = ("instance_id", "base_url", "contract", "contract_version",
                       "operations", "status", "bot_telegram_id", "bot_username",
                       "last_seen", "created_at", "updated_at")
    search_fields = ("instance_id", "base_url", "bot_username")

    def has_add_permission(self, request):
        return False


def _control_channel_id() -> str:
    from django.conf import settings
    return str(getattr(settings, "PROVISION_CONTROL_CHANNEL_ID", "") or "").strip()


def _is_control_channel(channel_id: str) -> bool:
    return bool(_control_channel_id()) and str(channel_id).strip() == _control_channel_id()


def _assert_not_control(channel_id: str) -> str | None:
    if _is_control_channel(channel_id):
        return "This is the CONTROL channel — subscriber provisioning targets it is refused."
    return None


@staff_member_required
def verify_bot(request):
    started = time.monotonic()
    raw = TelegramBotService.get_bot_info()
    latency_ms = round((time.monotonic() - started) * 1000, 1)
    bot = raw.get("result") if raw.get("ok") else {}
    info = {
        "ok": bool(raw.get("ok")),
        "error": raw.get("description") or raw.get("error") or "Telegram did not accept getMe",
        "base_url": "Telegram Bot API (called directly by Django)",
        "source": "BotConfig database token",
        "contract": "Native Bot API",
        "version": "direct",
        "operations": [
            "webhook verification", "create invite", "send invite",
            "membership check", "ban / unban",
        ],
        "bot": bot or {},
        "latency_ms": latency_ms,
        "compatible": bool(raw.get("ok")),
    }
    return render(request, "bot_integration/verify_bot.html", {"info": info})


@staff_member_required
def verify_control_channel(request):
    channel_id = _control_channel_id()
    error = None
    result = None
    if not channel_id:
        error = "TELEGRAM_CONTROL_CHANNEL_ID / PROVISION_CONTROL_CHANNEL_ID is not configured."
    else:
        result = TelegramBotService.verify_channel(channel_id)
    return render(request, "bot_integration/verify_channel.html", {
        "title": "Verify Control Channel", "channel_id": channel_id,
        "result": result, "error": error, "is_control": True,
    })


@staff_member_required
def verify_target_channel(request, mapping_id: int):
    mapping = get_object_or_404(PlanChannelMapping, pk=mapping_id)
    if mapping.platform != "telegram":
        return HttpResponseForbidden("Only Telegram mappings can be verified by Titan Pip Bot.")
    result = TelegramBotService.verify_channel(mapping.external_id)
    return render(request, "bot_integration/verify_channel.html", {
        "title": f"Verify Target Channel ({mapping})", "channel_id": mapping.external_id,
        "result": result, "is_control": _is_control_channel(mapping.external_id),
    })


@user_passes_test(lambda u: u.is_active and u.is_superuser)
def test_grant_revoke(request):
    """Explicit superuser-only live operation using the exact direct transport."""
    accounts = TelegramAccount.objects.select_related("user").filter(
        telegram_user_id__isnull=False
    )
    mappings = PlanChannelMapping.objects.filter(platform="telegram")
    result = None

    if request.method == "POST":
        account = get_object_or_404(TelegramAccount, pk=request.POST.get("account_id"))
        mapping = get_object_or_404(PlanChannelMapping, pk=request.POST.get("mapping_id"))
        operation = request.POST.get("operation")
        if operation not in ("grant", "revoke") or mapping.platform != "telegram":
            return HttpResponseForbidden("Invalid operation or platform")
        guard = _assert_not_control(mapping.external_id)
        if guard:
            messages.error(request, guard)
        else:
            transport = ProvisionTransport()
            if operation == "grant":
                invite_link = transport.create_invite_link(
                    account.telegram_user_id, mapping.external_id,
                    idempotency_key=f"admin-test:grant:{account.pk}:{mapping.pk}",
                )
                if not invite_link:
                    result = {
                        "ok": False, "status": "failed",
                        "error": "Could not unban the user or create an invite link.",
                    }
                else:
                    delivered = transport.send_invite_dm(
                        account.telegram_user_id, mapping.external_id, invite_link
                    )
                    result = {
                        "ok": delivered is True,
                        "status": ("applied" if delivered is True else
                                   "unknown" if delivered is None else "failed"),
                        "detail": {"invite_link": invite_link},
                        "error": ("" if delivered is True else
                                  "Telegram DM delivery outcome is unknown." if delivered is None
                                  else "Telegram rejected the invite DM."),
                    }
            else:
                mutation = transport.revoke(
                    account.telegram_user_id, mapping.external_id,
                    idempotency_key=f"admin-test:revoke:{account.pk}:{mapping.pk}",
                )
                member = transport.is_member(
                    account.telegram_user_id, mapping.external_id
                ) if mutation.ok else None
                success = mutation.ok and member is False
                result = {
                    "ok": success,
                    "status": "applied" if success else "failed",
                    "error": ("" if success else mutation.error_message or
                              "Telegram accepted the ban, but membership could not be verified."),
                }
            BotAccessAudit.objects.create(
                user=account.user,
                action=f"admin_test_{operation}",
                platform="telegram",
                target=mapping.external_id,
                status="success" if result["ok"] else "failed",
                error_message=str(result.get("error", ""))[:500],
            )
            if result["ok"]:
                messages.success(request, f"{operation.title()} -> {result['status']}")
            else:
                messages.error(request, f"{operation.title()} failed: {result.get('error', 'unknown error')}")

    return render(request, "bot_integration/test_grant_revoke.html", {
        "accounts": accounts, "mappings": mappings, "result": result,
        "control_channel_id": _control_channel_id(),
    })


urlpatterns = [
    path("verify-bot/", verify_bot, name="bi_verify_bot"),
    path("verify-control-channel/", verify_control_channel, name="bi_verify_control"),
    path("verify-target-channel/<int:mapping_id>/", verify_target_channel, name="bi_verify_target"),
    path("test-grant-revoke/", test_grant_revoke, name="bi_test_grant_revoke"),
]
