"""Access reconciliation engine.

Invariant: actual platform access converges to the access dictated by the
user's current subscription. Diff-based and idempotent — re-running with no
change produces zero platform calls and zero audit rows.

The durable worker uses this diff engine plus the provisioning state machine.
The legacy synchronous entry point shares the same live Discord role reconciler.
- Discord roles are granted/revoked on entitlement changes and lapse.
- Telegram channels from a previous plan are revoked on plan change.
- No-op reconciles are silent.
- Discord failures are surfaced and queued for retry rather than reported as success.
"""
import logging
from django.core.cache import cache
from django.utils import timezone

from .access import compute_target_access
from .models import (
    TelegramAccount, DiscordAccount, PlanChannelMapping,
    ChannelMeshDestination, UserChannelAssignment, BotAccessAudit,
)
from .services.channel_mesh import deactivate_revoked_mesh_assignments
from .services.discord import DiscordBotService

logger = logging.getLogger(__name__)
LOCK_TTL = 120  # seconds — only guards concurrent triggers, never held across network calls


def _audit(user_id, action, platform, target, success, error_message=""):
    BotAccessAudit.objects.create(
        user_id=user_id, action=action, platform=platform, target=str(target),
        status="success" if success else "failed",
        error_message=error_message or "",
    )


def reconcile_user_access(user_id):
    lock_key = f"bot_integration:reconcile:{user_id}"
    if not cache.add(lock_key, True, LOCK_TTL):
        return  # another reconcile in flight; it sees fresh state
    try:
        target = compute_target_access(user_id)

        tg = TelegramAccount.objects.filter(user_id=user_id, is_active=True).first()
        if tg:
            _reconcile_telegram(user_id, tg, target)
            deactivate_revoked_mesh_assignments(user_id, target)

        dc = DiscordAccount.objects.filter(user_id=user_id, is_active=True).first()
        if dc and not _reconcile_discord(user_id, dc, target):
            # Keep the older synchronous entry point honest too: it must not
            # swallow a Discord API failure just because the durable worker is
            # the preferred path.
            from apps.jobs.enqueue import enqueue_reconcile
            try:
                enqueue_reconcile(user_id, reason="discord_direct_reconcile_retry")
            except Exception:
                logger.exception("could not queue retry for Discord reconciliation user=%s", user_id)
            return False
        return True
    finally:
        cache.delete(lock_key)


def _reconcile_telegram(user_id, account, target):
    existing = set(UserChannelAssignment.objects.filter(
        user_id=user_id, platform="telegram", is_active=True
    ).values_list("external_id", flat=True))

    if not target.has_plan:
        for channel_id in sorted(existing):
            _tg_revoke(user_id, account, channel_id)
    else:
        for channel_id in sorted(target.telegram_ids - existing):
            _tg_grant(user_id, account, target, channel_id)
        for channel_id in sorted(existing - target.telegram_ids):
            _tg_revoke(user_id, account, channel_id)  # plan-change drift

    account.last_synced_at = timezone.now()
    account.save(update_fields=["last_synced_at"])


# ─────────────────── Provision Contract v1 transport ───────────────────
# Django no longer calls the Telegram Bot API directly. Grant/revoke are
# intent-level operations executed by the self-registered bot bridge.
# Discord roles are reconciled from live guild state in _reconcile_discord below.

from django.conf import settings as _settings
from .services.provision_client import ProvisionClient


def _control_channel_guard(channel_id):
    control = str(getattr(_settings, "PROVISION_CONTROL_CHANNEL_ID", "") or "").strip()
    if control and str(channel_id).strip() == control:
        return "Control/admin channel is not a valid subscriber provisioning target"
    return None




def _tg_notify_grant(account, channel_id, ok, error_message=""):
    """Customer-facing DM on grant success/failure (best-effort, never raises)."""
    try:
        from .services.telegram import TelegramBotService
        name = (PlanChannelMapping.objects
                .filter(platform="telegram", external_id=str(channel_id))
                .values_list("name", flat=True).first())
        if not name:
            name = (ChannelMeshDestination.objects
                    .filter(external_id=str(channel_id))
                    .values_list("name", flat=True).first())
        name = name or str(channel_id)
        if ok:
            text = "\u2705 You're in! You now have access to {}.".format(name)
        else:
            text = ("\u26a0\ufe0f We couldn't add you to {} ({}). "
                    "Self-check: open the bot and press Start, then make sure your "
                    "Telegram privacy settings allow being added to channels. "
                    "If it still fails, contact support from the website.").format(
                        name, error_message or "provider error")
        TelegramBotService.send_message(account.chat_id, text)
    except Exception:
        logger.exception("grant notification failed")

def _tg_grant(user_id, account, target, channel_id):
    tg_id = getattr(account, "telegram_user_id", None)
    if not tg_id:
        _audit(user_id, "grant", "telegram", channel_id, False,
               "Missing telegram_user_id – cannot grant")
        return
    guard = _control_channel_guard(channel_id)
    if guard:
        _audit(user_id, "grant", "telegram", channel_id, False, guard)
        return
    result = ProvisionClient().grant(tg_id, channel_id)
    if result.ok:
        UserChannelAssignment.objects.get_or_create(
            user_id=user_id, platform="telegram", external_id=channel_id,
            defaults={"is_active": True})
        _audit(user_id, "grant", "telegram", channel_id, True, "")
        _tg_notify_grant(account, channel_id, True)
    else:
        _audit(user_id, "grant", "telegram", channel_id, False,
               f"{result.error_code}: {result.error_message}"[:500])
        _tg_notify_grant(account, channel_id, False,
                         result.error_message or result.error_code or "")


def _tg_revoke(user_id, account, channel_id):
    if not account.telegram_user_id:
        _audit(user_id, "revoke", "telegram", channel_id, False,
               "Missing telegram_user_id – cannot ban")
        return
    guard = _control_channel_guard(channel_id)
    if guard:
        _audit(user_id, "revoke", "telegram", channel_id, False, guard)
        return
    result = ProvisionClient().revoke(account.telegram_user_id, channel_id)
    if result.ok:
        UserChannelAssignment.objects.filter(
            user_id=user_id, platform="telegram", external_id=channel_id,
            is_active=True).update(is_active=False, revoked_at=timezone.now())
        _audit(user_id, "revoke", "telegram", channel_id, True, "")
    else:
        _audit(user_id, "revoke", "telegram", channel_id, False,
               f"{result.error_code}: {result.error_message}"[:500])


def _reconcile_discord(user_id, account, target):
    """Drive live Discord roles toward the member's current entitlements.

    Returns False if platform state cannot be read or a mutation fails, allowing
    the durable worker to retry rather than marking a partial sync successful.
    Only roles known to this integration are changed; unrelated server roles
    are preserved.
    """
    actual_roles = DiscordBotService.get_member_roles(account.discord_user_id)
    if actual_roles is None:
        _audit(
            user_id, "sync", "discord", account.discord_user_id, False,
            "Unable to verify live Discord member roles.",
        )
        return False

    active_assignments = set(UserChannelAssignment.objects.filter(
        user_id=user_id, platform="discord", is_active=True,
    ).values_list("external_id", flat=True))
    # Plan-mapped Discord roles are wholly managed by this integration.
    # Including them lets reconciliation correct a stale/missing local cache
    # while still preserving unrelated roles managed manually in the server.
    mapped_roles = set(PlanChannelMapping.objects.filter(
        platform="discord",
    ).values_list("external_id", flat=True))
    managed_roles = (
        set(account.roles or [])
        | active_assignments
        | mapped_roles
        | set(target.discord_ids)
    )
    actual_roles = set(actual_roles)
    current = managed_roles & actual_roles
    failed = False

    # If a previously managed role has already disappeared externally and is
    # not currently entitled, clear the stale local assignment without trying
    # to revoke something Discord confirms is absent.
    stale_absent = managed_roles - actual_roles - set(target.discord_ids)
    if stale_absent:
        UserChannelAssignment.objects.filter(
            user_id=user_id, platform="discord",
            external_id__in=stale_absent, is_active=True,
        ).update(is_active=False, revoked_at=timezone.now())

    for role_id in sorted(set(target.discord_ids) - current):
        ok = DiscordBotService.add_role(account.discord_user_id, role_id)
        if ok:
            current.add(role_id)
        else:
            failed = True
        _audit(user_id, "grant", "discord", role_id, ok)

    for role_id in sorted(current - set(target.discord_ids)):
        ok = DiscordBotService.remove_role(account.discord_user_id, role_id)
        if ok:
            current.discard(role_id)
            UserChannelAssignment.objects.filter(
                user_id=user_id, platform="discord", external_id=role_id,
                is_active=True,
            ).update(is_active=False, revoked_at=timezone.now())
        else:
            failed = True
        _audit(user_id, "revoke", "discord", role_id, ok)

    # Align the assignment ledger with roles which are now present and wanted.
    # Reactivate old rows rather than allowing get_or_create to preserve the
    # revoked flag after a renewed subscription.
    for role_id in sorted(set(target.discord_ids) & current):
        assignment, created = UserChannelAssignment.objects.get_or_create(
            user_id=user_id, platform="discord", external_id=role_id,
            defaults={"is_active": True},
        )
        if not created and not assignment.is_active:
            assignment.is_active = True
            assignment.revoked_at = None
            assignment.save(update_fields=["is_active", "revoked_at"])

    if set(account.roles or []) != current:
        account.roles = sorted(current)
        account.save(update_fields=["roles"])
    return not failed
