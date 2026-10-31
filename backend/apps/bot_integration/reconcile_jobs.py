"""Durable reconciliation: one ProvisioningOperation per (user, channel, intent).

The existing diff engine (compute_target_access vs UserChannelAssignment)
decides WHICH operations are needed.  Each needed operation gets ONE open
ProvisioningOperation row; retries reuse its id/link; a NEW lifecycle
(grant after revoke completed) creates a NEW row.
"""

import logging
from datetime import timedelta
from types import SimpleNamespace

from django.db.models import Q

from django.utils import timezone

from apps.bot_integration.models import (
    BotAccessAudit, DiscordAccount, TelegramAccount, UserChannelAssignment)
from apps.bot_integration.reconcile import (
    _audit, _control_channel_guard, _reconcile_discord, compute_target_access)
from apps.jobs.models import ProvisioningOperation
from apps.jobs.operations import DefiniteProvisioningError, execute_operation

logger = logging.getLogger(__name__)

# Persistent resend throttle for membership-recovery invites (6 hours).
INVITE_RESEND_THROTTLE = timedelta(hours=6)


class ProvisionTransport:
    """Direct Telegram Bot API transport using the singleton BotConfig token.

    Invite creation and invite delivery are separate so a URL can be persisted
    to ProvisioningOperation before a DM attempt is made.
    """

    def __init__(self, client=None):
        from apps.bot_integration.services.telegram import TelegramBotService
        self.client = client or TelegramBotService

    @staticmethod
    def _retryable(error_message):
        message = (error_message or "").lower()
        return any(term in message for term in (
            "timeout", "network", "rate limit", "429", "500", "502",
            "503", "504", "temporarily unavailable",
        ))

    def create_invite_link(self, telegram_user_id, channel_id,
                           idempotency_key=None):
        # A re-grant lifts a previous ban before minting a fresh one-use link.
        if not telegram_user_id:
            return None
        ok, error = self.client.unban_user(channel_id, telegram_user_id)
        if not ok:
            if self._retryable(error):
                logger.warning("Telegram unban outcome uncertain/retryable for channel %s",
                               channel_id)
                return None
            raise DefiniteProvisioningError(
                error or "Telegram rejected the unban request."
            )

        link, error, retryable = self.client.create_one_time_invite_link_result(channel_id)
        if link:
            return link
        if retryable:
            logger.warning("Telegram invite creation outcome uncertain/retryable for channel %s",
                           channel_id)
            return None
        raise DefiniteProvisioningError(
            error or "Telegram rejected invite creation."
        )

    def send_invite_dm(self, telegram_user_id, channel_id, invite_link):
        # Telegram sendMessage has no idempotency key; never report an
        # indeterminate result as successful delivery.
        result = self.client.send_message_result(
            telegram_user_id,
            "🔓 Your TradeThesis subscription is active. Join your channel here: "
            + str(invite_link),
        )
        if result.ok:
            return True
        if getattr(result, "outcome", "") == "indeterminate":
            return None
        return False

    def is_member(self, telegram_user_id, channel_id):
        return self.client.is_member(channel_id, telegram_user_id)

    def revoke(self, telegram_user_id, channel_id, idempotency_key=None):
        if not telegram_user_id:
            return SimpleNamespace(
                ok=False, retryable=False, error_code="missing_telegram_user_id",
                error_message="Missing telegram_user_id",
            )
        ok, error = self.client.ban_user(channel_id, telegram_user_id)
        return SimpleNamespace(
            ok=ok,
            retryable=(not ok and self._retryable(error)),
            error_code="" if ok else "telegram_api_error",
            error_message="" if ok else (error or "Telegram revoke failed"),
        )

def _get_or_create_operation(user_id, channel_id, operation, telegram_user_id):
    """Reuse the OPEN operation for this intent; else create a new one."""
    open_states = [ProvisioningOperation.ST_PENDING, ProvisioningOperation.ST_CREATING,
                   ProvisioningOperation.ST_CREATED, ProvisioningOperation.ST_SENDING,
                   ProvisioningOperation.ST_SENT, ProvisioningOperation.ST_UNKNOWN]
    op = (ProvisioningOperation.objects
          .filter(user_id=user_id, channel_id=channel_id, operation=operation,
                  state__in=open_states)
          .order_by("id").first())
    if op is not None:
        return op
    return ProvisioningOperation.objects.create(
        user_id=user_id, channel_id=channel_id, operation=operation,
        telegram_user_id=telegram_user_id)


def _finalize_grant(user_id, channel_id):
    UserChannelAssignment.objects.get_or_create(
        user_id=user_id, platform="telegram", external_id=channel_id,
        defaults={"is_active": True})
    UserChannelAssignment.objects.filter(
        user_id=user_id, platform="telegram", external_id=channel_id,
        is_active=False).update(is_active=True, revoked_at=None)
    _audit(user_id, "grant", "telegram", channel_id, True, "")


def _finalize_revoke(user_id, channel_id):
    UserChannelAssignment.objects.filter(
        user_id=user_id, platform="telegram", external_id=channel_id,
        is_active=True).update(is_active=False, revoked_at=timezone.now())
    _audit(user_id, "revoke", "telegram", channel_id, True, "")


def _stamp_invite_sent(user_id, channel_id):
    """Stamp the persistent resend throttle; call ONLY when an invite was
    actually (re)sent (or plausibly sent in the ST_UNKNOWN window)."""
    UserChannelAssignment.objects.filter(
        user_id=user_id, platform="telegram", external_id=channel_id,
    ).update(last_invite_sent_at=timezone.now())


def _supersede_open_grants(user_id, channel_id):
    """Close any OPEN grant operations for this user/channel.

    Called when a revoke completes.  ProvisioningOperation's documented
    invariant is "a NEW grant after a completed revoke gets a NEW row";
    without this, _get_or_create_operation would reuse a stale ST_SENT
    grant whose recovery path only re-sends the persisted invite and never
    reaches the bot's unban.  Closed ops are terminal (failed/superseded),
    so re-grants create a fresh lifecycle.
    """
    ProvisioningOperation.objects.filter(
        user_id=user_id, channel_id=channel_id,
        operation=ProvisioningOperation.OP_GRANT,
        state__in=[ProvisioningOperation.ST_PENDING,
                   ProvisioningOperation.ST_CREATING,
                   ProvisioningOperation.ST_CREATED,
                   ProvisioningOperation.ST_SENDING,
                   ProvisioningOperation.ST_SENT,
                   ProvisioningOperation.ST_UNKNOWN],
    ).update(state=ProvisioningOperation.ST_FAILED,
             last_error="superseded_by_revoke")


def _release_resend_claim(assignment_pk, claimed_at, previous):
    """Return a claimed resend window without clobbering a newer claim."""
    qs = UserChannelAssignment.objects.filter(
        pk=assignment_pk, last_invite_sent_at=claimed_at)
    qs.update(last_invite_sent_at=previous)


def _recover_membership(user_id, telegram_user_id, channel_id, transport):
    """Recover access for an entitled user who is no longer a channel member.

    The assignment stays active throughout: is_active tracks the
    authorized/provisioned ENTITLEMENT, not live membership.  A read-only
    membership probe runs BEFORE any invite; an undetermined result (None)
    never triggers a resend.  Resends reuse the persisted open
    ProvisioningOperation/invite link where one exists; only when no
    reusable operation exists is a new one created.

    The 6h resend throttle is an ATOMIC CLAIM (one conditional UPDATE both
    checks and takes the window), so concurrent reconciles -- e.g. an
    interactive test harness and the background jobs worker both running
    run_user_reconcile for the same user -- can never both pass the check.
    The claim is released (timestamp restored) unless an invite actually
    went out (SENT) or plausibly went out (UNKNOWN window).
    """
    assignment = UserChannelAssignment.objects.filter(
        user_id=user_id, platform="telegram", external_id=channel_id,
        is_active=True).first()
    if assignment is None:
        return
    now = timezone.now()
    cutoff = now - INVITE_RESEND_THROTTLE
    previous_ts = assignment.last_invite_sent_at
    claimed = UserChannelAssignment.objects.filter(
        pk=assignment.pk, is_active=True,
    ).filter(
        Q(last_invite_sent_at__isnull=True)
        | Q(last_invite_sent_at__lt=cutoff),
    ).update(last_invite_sent_at=now)
    if not claimed:
        return  # another reconcile claimed the window first; do not resend
    member = transport.is_member(telegram_user_id, channel_id)
    if member is not False:
        # True: nothing to recover.  None: undetermined -- never send.
        # Either way no invite went out: release the claim.
        _release_resend_claim(assignment.pk, now, previous_ts)
        return
    op = _get_or_create_operation(user_id, channel_id,
                                  ProvisioningOperation.OP_GRANT, telegram_user_id)
    execute_operation(op, transport)
    if op.state in (ProvisioningOperation.ST_SENT, ProvisioningOperation.ST_UNKNOWN):
        # Keep the claim: an invite actually went out (SENT), or plausibly
        # went out (UNKNOWN = documented irreducible window).
        pass
    else:
        _release_resend_claim(assignment.pk, now, previous_ts)
    if op.state == ProvisioningOperation.ST_COMPLETED:
        _audit(user_id, "grant", "telegram", channel_id, True,
               "membership recovered")
    elif op.state == ProvisioningOperation.ST_FAILED:
        _audit(user_id, "grant", "telegram", channel_id, False,
               op.last_error[:500])
        raise RuntimeError(
            f"Telegram membership recovery failed for channel {channel_id}: {op.last_error[:300]}"
        )


def run_user_reconcile(user_id: int, transport=None) -> None:
    """Reconcile Telegram and Discord access for every active entitlement.

    Inactive TelegramAccount rows represent an in-progress disconnect. Keep
    their Telegram identity until all managed channel revokes are verified.
    Provider failures raise so the durable worker retries instead of silently
    completing a partial access change.
    """
    target = compute_target_access(user_id)
    account = TelegramAccount.objects.filter(user_id=user_id).first()
    if account is None:
        # Older unlink code deleted TelegramAccount before reconciliation. Its
        # audit event retained the private chat ID (equal to the numeric user
        # ID for the private bot conversation); use that only as a recovery
        # credential for revocation, never to create or re-link an account.
        from django.db.models import Q
        from apps.jobs.models import ProvisioningOperation
        open_grant_states = [
            ProvisioningOperation.ST_PENDING,
            ProvisioningOperation.ST_CREATING,
            ProvisioningOperation.ST_CREATED,
            ProvisioningOperation.ST_SENDING,
            ProvisioningOperation.ST_SENT,
            ProvisioningOperation.ST_UNKNOWN,
        ]
        orphaned_assignments = set(
            UserChannelAssignment.objects.filter(
                user_id=user_id, platform="telegram", is_active=True,
            ).values_list("external_id", flat=True)
        )
        open_grants = set(
            ProvisioningOperation.objects.filter(
                user_id=user_id,
                operation=ProvisioningOperation.OP_GRANT,
                state__in=open_grant_states,
            ).values_list("channel_id", flat=True)
        )
        if orphaned_assignments or open_grants:
            prior_unlink = BotAccessAudit.objects.filter(
                user_id=user_id, action="unlink", platform="telegram",
            ).order_by("-created_at", "-pk").first()
            try:
                tg_id = int(prior_unlink.target) if prior_unlink else 0
            except (TypeError, ValueError):
                tg_id = 0
            if tg_id <= 0:
                raise RuntimeError(
                    f"Telegram assignments exist without a recoverable Telegram identity for user {user_id}"
                )

            transport = transport or ProvisionTransport()
            orphan_targets = orphaned_assignments | open_grants
            # Include the most recently granted destinations as a final recovery
            # source. This catches an invite operation that was closed or lost
            # its assignment row during the old eager-delete flow.
            orphan_targets |= set(
                ProvisioningOperation.objects.filter(
                    user_id=user_id,
                    operation=ProvisioningOperation.OP_GRANT,
                ).values_list("channel_id", flat=True)
            )
            for channel_id in sorted(orphan_targets):
                error = _control_channel_guard(channel_id)
                if error:
                    _audit(user_id, "revoke", "telegram", channel_id, False, error)
                    raise RuntimeError(error)
                op = _get_or_create_operation(
                    user_id, channel_id, ProvisioningOperation.OP_REVOKE, tg_id
                )
                execute_operation(op, transport)
                if op.state == ProvisioningOperation.ST_COMPLETED:
                    _finalize_revoke(user_id, channel_id)
                    _supersede_open_grants(user_id, channel_id)
                else:
                    message = op.last_error or f"revoke remains unresolved ({op.state})"
                    _audit(user_id, "revoke", "telegram", channel_id, False, message[:500])
                    raise RuntimeError(
                        f"Orphaned Telegram revoke failed for channel {channel_id}: {message[:300]}"
                    )

    if account is not None:
        tg_id = account.telegram_user_id or account.chat_id
        if not tg_id:
            raise RuntimeError(
                f"Telegram account has no usable numeric identity for user {user_id}"
            )

        existing = set(UserChannelAssignment.objects.filter(
            user_id=user_id, platform="telegram", is_active=True,
        ).values_list("external_id", flat=True))

        disconnecting = not account.is_active
        wanted = (
            {str(channel_id) for channel_id in target.telegram_ids}
            if target.has_plan and not disconnecting else set()
        )
        revoke_targets = existing - wanted
        grant_targets = wanted - existing

        if disconnecting:
            # Sweep all known managed grant destinations as well as current
            # entitlements. This catches a sent/unknown invite or stale local
            # assignment even if the assignment ledger is incomplete.
            historical_grants = set(
                ProvisioningOperation.objects.filter(
                    user_id=user_id,
                    operation=ProvisioningOperation.OP_GRANT,
                ).values_list("channel_id", flat=True)
            )
            revoke_targets |= historical_grants
            revoke_targets |= {str(channel_id) for channel_id in target.telegram_ids}

        guard = _control_channel_guard
        transport = transport or ProvisionTransport()

        # Revokes always run first. A failed or unverified revoke is NOT
        # success: raise to leave the durable job retryable and retain identity.
        for channel_id in sorted(revoke_targets):
            error = guard(channel_id)
            if error:
                _audit(user_id, "revoke", "telegram", channel_id, False, error)
                raise RuntimeError(error)
            op = _get_or_create_operation(
                user_id, channel_id, ProvisioningOperation.OP_REVOKE, tg_id
            )
            execute_operation(op, transport)
            if op.state == ProvisioningOperation.ST_COMPLETED:
                _finalize_revoke(user_id, channel_id)
                _supersede_open_grants(user_id, channel_id)
            elif op.state == ProvisioningOperation.ST_FAILED:
                _audit(user_id, "revoke", "telegram", channel_id, False, op.last_error[:500])
                raise RuntimeError(
                    f"Telegram revoke failed for channel {channel_id}: {op.last_error[:300]}"
                )
            else:
                raise RuntimeError(
                    f"Telegram revoke remains unresolved for channel {channel_id} ({op.state})"
                )

        # Grants only run while the Telegram account is active.
        for channel_id in sorted(grant_targets):
            error = guard(channel_id)
            if error:
                _audit(user_id, "grant", "telegram", channel_id, False, error)
                raise RuntimeError(error)
            op = _get_or_create_operation(
                user_id, channel_id, ProvisioningOperation.OP_GRANT, tg_id
            )
            execute_operation(op, transport)
            if op.state in (ProvisioningOperation.ST_COMPLETED, ProvisioningOperation.ST_SENT):
                # SENT means the invite DM was accepted; membership can still
                # be pending. The assignment records the entitlement, not presence.
                _finalize_grant(user_id, channel_id)
                if op.state == ProvisioningOperation.ST_SENT:
                    _stamp_invite_sent(user_id, channel_id)
            elif op.state == ProvisioningOperation.ST_FAILED:
                _audit(user_id, "grant", "telegram", channel_id, False, op.last_error[:500])
                raise RuntimeError(
                    f"Telegram grant failed for channel {channel_id}: {op.last_error[:300]}"
                )
            else:
                raise RuntimeError(
                    f"Telegram grant remains unresolved for channel {channel_id} ({op.state})"
                )

        # Membership recovery applies only to a still-linked, active identity.
        for channel_id in sorted(wanted & existing):
            _recover_membership(user_id, tg_id, channel_id, transport)

        if disconnecting:
            remaining = UserChannelAssignment.objects.filter(
                user_id=user_id, platform="telegram", is_active=True,
            ).exists()
            open_grants = ProvisioningOperation.objects.filter(
                user_id=user_id,
                operation=ProvisioningOperation.OP_GRANT,
                state__in=[
                    ProvisioningOperation.ST_PENDING,
                    ProvisioningOperation.ST_CREATING,
                    ProvisioningOperation.ST_CREATED,
                    ProvisioningOperation.ST_SENDING,
                    ProvisioningOperation.ST_SENT,
                    ProvisioningOperation.ST_UNKNOWN,
                ],
            ).exists()
            if remaining or open_grants:
                raise RuntimeError(
                    f"Telegram disconnect still has unresolved access for user {user_id}"
                )

            old_chat_id = account.chat_id
            from django.db import transaction
            with transaction.atomic():
                locked_account = TelegramAccount.objects.select_for_update().filter(
                    pk=account.pk, is_active=False
                ).first()
                if locked_account is not None:
                    locked_account.delete()
                    BotAccessAudit.objects.create(
                        user_id=user_id,
                        action="unlink",
                        platform="telegram",
                        target=str(old_chat_id),
                        status="success",
                    )
            # Confirmation is best effort and happens only after access is
            # removed. A blocked bot must not undo a successful disconnect.
            try:
                from apps.bot_integration.services.telegram import TelegramBotService
                TelegramBotService.send_message(
                    old_chat_id,
                    "🔓 Telegram disconnected. TradeThesis has removed your managed "
                    "community access. You can reconnect from your Member Desk.",
                )
            except Exception:
                logger.exception(
                    "Telegram disconnect confirmation failed user=%s", user_id
                )
        else:
            account.last_synced_at = timezone.now()
            account.save(update_fields=["last_synced_at"])

    discord_account = DiscordAccount.objects.filter(
        user_id=user_id, is_active=True
    ).first()
    if discord_account and not _reconcile_discord(
        user_id, discord_account, target
    ):
        raise RuntimeError(
            f"Discord role reconciliation failed for user {user_id}; retry scheduled"
        )
