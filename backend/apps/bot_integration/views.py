import json
import secrets
import logging
import hmac
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import (
    BotConfig, TelegramAccount, TelegramVerificationToken,
    DiscordAccount, BotAccessAudit, PlanChannelMapping, UserChannelAssignment,
)
from .services.telegram import TelegramBotService
from .services.discord import DiscordBotService
from .services.profile_sync import sync_telegram_profile_for_user
from .services.channel_sync import sync_channel_memberships_for_user

logger = logging.getLogger(__name__)


@login_required
def start_telegram_connect(request):
    """Generate a deep link to the existing TradeThesis Telegram bot."""
    # A disconnect is not complete until managed channel access has been
    # revoked. Do not allow a replacement identity to race that cleanup.
    from apps.jobs.models import ProvisioningOperation
    active_account_linked = TelegramAccount.objects.filter(
        user=request.user, is_active=True
    ).exists()
    if active_account_linked:
        messages.info(
            request,
            "Telegram is already connected. Disconnect it first and wait for "
            "managed community access to be removed before linking another account.",
        )
        return redirect(f"{reverse('dashboard')}#connections")

    pending_account_disconnect = TelegramAccount.objects.filter(
        user=request.user, is_active=False
    ).exists()
    orphaned_access = (
        not TelegramAccount.objects.filter(user=request.user).exists()
        and (
            UserChannelAssignment.objects.filter(
                user=request.user, platform="telegram", is_active=True,
            ).exists()
            or ProvisioningOperation.objects.filter(
                user_id=request.user.pk,
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
        )
    )
    if orphaned_access:
        from django.db import transaction
        from apps.jobs.enqueue import enqueue_reconcile
        try:
            with transaction.atomic():
                # Expire any link token minted before the orphaned cleanup
                # was detected, so a delayed /start cannot restore the old link.
                TelegramVerificationToken.objects.filter(user=request.user).delete()
                enqueue_reconcile(request.user.pk, reason="orphaned_telegram_cleanup")
        except Exception:
            logger.exception("Could not queue orphaned Telegram cleanup user=%s", request.user.pk)
        messages.error(
            request,
            "A previous Telegram connection still has community access to clean up. "
            "We're resolving it before allowing a new Telegram link. Contact support "
            "if this status does not clear.",
        )
        return redirect(f"{reverse('dashboard')}#connections")

    if pending_account_disconnect:
        messages.error(
            request,
            "Your previous Telegram disconnect is still being completed. "
            "Retry disconnecting from Connected accounts before linking again.",
        )
        return redirect(f"{reverse('dashboard')}#connections")

    # Verification and normal channel access share one bot identity.
    # BotConfig is the canonical credential source used by TelegramBotService.
    config = BotConfig.get_config()
    bot_username = (config.telegram_bot_username or "").strip().lstrip("@")
    bot_token = (config.telegram_bot_token or "").strip()
    if not config.is_active or not bot_username or not bot_token:
        messages.error(
            request,
            "Telegram is not configured yet. Please contact support.",
        )
        return redirect(f"{reverse('dashboard')}#connections")

    # Delete old unused tokens for this user.
    TelegramVerificationToken.objects.filter(user=request.user).delete()

    token = TelegramVerificationToken.create_token(request.user)
    deep_link = f"https://t.me/{bot_username}?start=verify_{token.token}"
    return redirect(deep_link)

@login_required
@require_POST
def unlink_telegram(request):
    """Request a safe Telegram disconnect; revoke paid access before deleting identity."""
    from django.db import transaction
    from apps.jobs.enqueue import enqueue_reconcile

    account = TelegramAccount.objects.filter(user=request.user).first()
    if account is None:
        from apps.jobs.models import ProvisioningOperation
        open_grant_states = [
            ProvisioningOperation.ST_PENDING,
            ProvisioningOperation.ST_CREATING,
            ProvisioningOperation.ST_CREATED,
            ProvisioningOperation.ST_SENDING,
            ProvisioningOperation.ST_SENT,
            ProvisioningOperation.ST_UNKNOWN,
        ]
        orphaned_access = (
            UserChannelAssignment.objects.filter(
                user=request.user, platform="telegram", is_active=True,
            ).exists()
            or ProvisioningOperation.objects.filter(
                user_id=request.user.pk,
                operation=ProvisioningOperation.OP_GRANT,
                state__in=open_grant_states,
            ).exists()
        )
        if not orphaned_access:
            messages.info(request, "No Telegram account is currently linked.")
            return redirect(f"{reverse('dashboard')}#connections")
        try:
            with transaction.atomic():
                TelegramVerificationToken.objects.filter(user=request.user).delete()
                enqueue_reconcile(request.user.pk, reason="orphaned_telegram_cleanup")
        except Exception:
            logger.exception("Orphaned Telegram cleanup retry could not be queued user=%s", request.user.pk)
            messages.error(
                request,
                "We couldn't queue the Telegram access cleanup. Please contact support.",
            )
        else:
            messages.info(
                request,
                "Telegram access cleanup has been queued again. A new link will only "
                "be offered after the previous managed access is resolved.",
            )
        return redirect(f"{reverse('dashboard')}#connections")

    try:
        # The account row (including telegram_user_id) is the credential needed
        # to revoke paid-channel membership. Keep it, but pause all new grants.
        # State change and durable job enqueue commit or roll back together.
        with transaction.atomic():
            # Invalidate any link flow started before the disconnect request.
            TelegramVerificationToken.objects.filter(user=request.user).delete()
            account = TelegramAccount.objects.select_for_update().get(
                pk=account.pk, user=request.user
            )
            if account.is_active:
                account.is_active = False
                account.save(update_fields=["is_active"])
            enqueue_reconcile(request.user.id, reason="telegram_unlink")
    except Exception:
        logger.exception("Telegram disconnect could not be queued user=%s", request.user.pk)
        messages.error(
            request,
            "We couldn't safely start the Telegram disconnect. Your account "
            "remains linked; please try again.",
        )
        return redirect(f"{reverse('dashboard')}#connections")

    messages.info(
        request,
        "Telegram disconnect requested. TradeThesis will remove managed "
        "community access before completing the disconnect. You can retry "
        "from Connected accounts if it remains pending.",
    )
    return redirect(f"{reverse('dashboard')}#connections")


def _discord_connections_redirect():
    """Return members to the canonical Connections section of the Member Desk."""
    return redirect(f"{reverse('dashboard')}#connections")


@login_required
@require_POST
def unlink_discord(request):
    """Remove managed Discord roles before disconnecting the linked account."""
    dc = DiscordAccount.objects.filter(user=request.user).first()
    if dc is None:
        # Older OAuth flows stored only User.discord_id and never created the
        # managed DiscordAccount row. Reconcile any roles TradeThesis owns
        # before clearing that legacy identity; never treat an unreadable
        # provider state as a successful disconnect.
        legacy_id = str(getattr(request.user, "discord_id", "") or "").strip()
        if not legacy_id:
            messages.info(request, "No Discord account is currently linked.")
            return _discord_connections_redirect()

        actual_roles = DiscordBotService.get_member_roles(legacy_id)
        if actual_roles is None:
            messages.error(
                request,
                "We couldn't verify your Discord roles. Your legacy identity "
                "has been kept so access cleanup can be retried.",
            )
            return _discord_connections_redirect()

        managed_roles = set(UserChannelAssignment.objects.filter(
            user=request.user, platform="discord", is_active=True,
        ).values_list("external_id", flat=True))
        managed_roles.update(PlanChannelMapping.objects.filter(
            platform="discord",
        ).values_list("external_id", flat=True))
        roles_to_remove = managed_roles & set(actual_roles)
        failed_roles = []
        for role_id in sorted(roles_to_remove):
            if DiscordBotService.remove_role(legacy_id, role_id):
                UserChannelAssignment.objects.filter(
                    user=request.user, platform="discord", external_id=role_id,
                    is_active=True,
                ).update(is_active=False, revoked_at=timezone.now())
                BotAccessAudit.objects.create(
                    user=request.user, action="revoke", platform="discord",
                    target=role_id, status="success",
                )
            else:
                failed_roles.append(role_id)
                BotAccessAudit.objects.create(
                    user=request.user, action="revoke", platform="discord",
                    target=role_id, status="failed",
                    error_message="Role removal failed during legacy Discord disconnect.",
                )

        remaining_roles = DiscordBotService.get_member_roles(legacy_id)
        unresolved = (
            failed_roles
            or remaining_roles is None
            or bool(managed_roles & set(remaining_roles or []))
        )
        if unresolved:
            messages.error(
                request,
                "Some managed Discord roles could not be verified as removed. "
                "Your legacy identity remains in place; retry disconnecting "
                "or contact support.",
            )
            return _discord_connections_redirect()

        from apps.audit.models import AuditLog
        legacy_username = request.user.discord_username
        request.user.discord_id = None
        request.user.discord_username = ""
        request.user.discord_avatar = ""
        request.user.discord_verified = False
        request.user.save(update_fields=[
            "discord_id", "discord_username", "discord_avatar", "discord_verified",
        ])
        AuditLog.log(
            action="discord_disconnected",
            user=request.user,
            object_type="user",
            object_id=request.user.id,
            metadata={
                "discord_id": legacy_id,
                "discord_username": legacy_username or "",
                "legacy_identity_only": True,
            },
        )
        BotAccessAudit.objects.create(
            user=request.user, action="unlink", platform="discord",
            target=legacy_id, status="success",
        )
        messages.success(
            request,
            "Legacy Discord connection cleared and TradeThesis-managed roles removed.",
        )
        return _discord_connections_redirect()

    # Pause grants before any outbound role-removal request. This closes the
    # race where the background worker could re-grant a role during disconnect.
    dc.is_active = False
    dc.save(update_fields=["is_active"])

    role_ids = set(dc.roles or [])
    role_ids.update(UserChannelAssignment.objects.filter(
        user=request.user, platform="discord", is_active=True,
    ).values_list("external_id", flat=True))
    # Every role mapped to a TradeThesis plan is integration-managed. Include
    # mappings as a recovery source if a previous partial failure left local
    # account/assignment caches out of date.
    role_ids.update(PlanChannelMapping.objects.filter(
        platform="discord",
    ).values_list("external_id", flat=True))

    failed_roles = []
    remaining_roles = set(dc.roles or [])
    for role_id in sorted(role_ids):
        if DiscordBotService.remove_role(dc.discord_user_id, role_id):
            remaining_roles.discard(role_id)
            UserChannelAssignment.objects.filter(
                user=request.user, platform="discord", external_id=role_id,
                is_active=True,
            ).update(is_active=False, revoked_at=timezone.now())
            BotAccessAudit.objects.create(
                user=request.user,
                action="revoke",
                platform="discord",
                target=role_id,
                status="success",
            )
        else:
            failed_roles.append(role_id)
            # Persist every failed managed role even if the account/assignment
            # caches were stale, so it remains retryable if the plan mapping is
            # later edited or removed.
            remaining_roles.add(role_id)
            BotAccessAudit.objects.create(
                user=request.user,
                action="revoke",
                platform="discord",
                target=role_id,
                status="failed",
                error_message="Role removal failed during Discord disconnect.",
            )

    dc.roles = sorted(remaining_roles)
    dc.save(update_fields=["roles"])

    if failed_roles:
        # Keep the association so a later attempt still knows which Discord
        # identity needs revocation. Never claim a disconnect completed while
        # a managed paid role may still be present.
        messages.error(
            request,
            "Some Discord roles could not be removed. Your account remains "
            "linked so access removal can be retried; please try again or "
            "contact support.",
        )
        return _discord_connections_redirect()

    old_id = dc.discord_user_id
    dc.delete()
    BotAccessAudit.objects.create(
        user=request.user,
        action="unlink",
        platform="discord",
        target=old_id,
        status="success",
    )
    messages.success(request, "Discord disconnected and managed roles removed.")
    return _discord_connections_redirect()


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """Handle Telegram webhook updates in Django.

    Native Telegram delivery uses X-Telegram-Bot-Api-Secret-Token. The signed
    HMAC path remains temporarily available for controlled rollback to the
    legacy bridge; normal account-linking and provisioning no longer require it.
    """
    native_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    expected_secret = (getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "") or "").strip()
    if native_header is not None:
        if not expected_secret or not hmac.compare_digest(native_header, expected_secret):
            return JsonResponse({"ok": False, "error": "invalid Telegram webhook secret"}, status=401)
        body = request.body
    else:
        # Rollback compatibility only. Native Telegram webhook requests must
        # authenticate with the separate Telegram secret-token header.
        from .provision_auth import verify_signed_request
        body, auth_err = verify_signed_request(request)
        if auth_err:
            return JsonResponse({"ok": False, "error": auth_err}, status=401)

    try:
        data = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        return HttpResponse(status=400)

    logger.info("Telegram webhook received update_id=%s", data.get("update_id"))
    message = data.get("message")
    if not isinstance(message, dict) or not isinstance(message.get("text"), str):
        return JsonResponse({"ok": True})

    chat = message.get("chat") or {}
    from_user = message.get("from") or {}
    chat_id = chat.get("id")
    telegram_user_id = from_user.get("id")
    # Linking must only occur from a human user's private conversation with
    # the bot. Group/channel posts are acknowledged but never used to link.
    if (chat.get("type") != "private" or from_user.get("is_bot")
            or not isinstance(chat_id, int) or isinstance(chat_id, bool)
            or not isinstance(telegram_user_id, int) or isinstance(telegram_user_id, bool)):
        return JsonResponse({"ok": True})

    text = message["text"].strip()
    normalized = text.lower().strip(" !.,?\t\n")
    welcome = (
        "👋 Welcome to TradeThesis! To connect your account, open your Dashboard "
        "and tap Connect Telegram. If you already have a subscription, "
        "we’ll check your community access after linking."
    )
    if normalized in {"hi", "hello", "hey", "start"}:
        TelegramBotService.send_message(chat_id, welcome)
        return JsonResponse({"ok": True})

    parts = text.split(maxsplit=1)
    command = parts[0].split("@", 1)[0].lower() if parts else ""
    if command != "/start":
        return JsonResponse({"ok": True})
    payload = parts[1].strip() if len(parts) > 1 else ""
    if not payload:
        TelegramBotService.send_message(chat_id, welcome)
        return JsonResponse({"ok": True})
    if not payload.startswith("verify_") or not payload[7:]:
        TelegramBotService.send_message(
            chat_id,
            "⚠️ That link doesn’t look right. Open your TradeThesis Dashboard and tap "
            "Connect Telegram to get a fresh one.",
        )
        return JsonResponse({"ok": True})

    token_str = payload[7:]
    from django.contrib.auth import get_user_model
    from django.db import IntegrityError, transaction
    from apps.jobs.enqueue import enqueue_reconcile

    User = get_user_model()
    status = "linked"
    user = None
    try:
        with transaction.atomic():
            token = (
                TelegramVerificationToken.objects.select_for_update()
                .select_related("user").get(token=token_str)
            )
            user = token.user
            if not token.is_valid():
                token.delete()
                status = "expired"
            else:
                existing_account = TelegramAccount.objects.select_for_update().filter(
                    user_id=user.id
                ).first()
                if existing_account is not None and not existing_account.is_active:
                    # A delayed deep link must never reactivate an identity while
                    # paid access revocation is still running.
                    token.delete()
                    status = "disconnect_pending"
                elif existing_account is not None:
                    # A link is immutable while active. Rebinding to a new
                    # Telegram identity must go through managed unlink first,
                    # otherwise the old identity's paid memberships are orphaned.
                    token.delete()
                    if (
                        existing_account.chat_id == chat_id
                        and existing_account.telegram_user_id == telegram_user_id
                    ):
                        status = "already_linked"
                    else:
                        status = "account_conflict"
                elif (
                    TelegramAccount.objects.filter(chat_id=chat_id)
                    .exclude(user_id=user.id).exists()
                    or User.objects.filter(
                        telegram_id=telegram_user_id
                    ).exclude(pk=user.id).exists()
                ):
                    # Preserve the token so support can resolve the existing link;
                    # don't replace or detach another TradeThesis user's account,
                    # including a legacy Telegram Login Widget identity.
                    status = "conflict"
                else:
                    TelegramAccount.objects.update_or_create(
                        user=user,
                        defaults={
                            "chat_id": chat_id,
                            "telegram_user_id": telegram_user_id,
                            "is_active": True,
                            "username": from_user.get("username") or "",
                            "first_name": from_user.get("first_name") or "",
                        },
                    )
                    token.delete()
                    BotAccessAudit.objects.create(
                        user=user, action="link", platform="telegram",
                        target=str(chat_id), status="success",
                    )
                    enqueue_reconcile(user.id, reason="telegram_link")
                    transaction.on_commit(
                        lambda uid=user.id: sync_telegram_profile_for_user(uid)
                    )
                    transaction.on_commit(
                        lambda uid=user.id: sync_channel_memberships_for_user(uid)
                    )
    except TelegramVerificationToken.DoesNotExist:
        # Telegram may retry a webhook after its first successful response.
        # Treat the already-linked identity as idempotent rather than telling
        # the member their once-valid token is invalid.
        if TelegramAccount.objects.filter(chat_id=chat_id).exists():
            TelegramBotService.send_message(
                chat_id, "🎉 You’re already connected to TradeThesis."
            )
        else:
            TelegramBotService.send_message(
                chat_id, "⚠️ We couldn’t use that link. Return to your TradeThesis Dashboard and "
                "tap Connect Telegram to get a fresh one."
            )
            return JsonResponse({"ok": True})
        return JsonResponse({"ok": True})
    except IntegrityError:
        # Translate only the expected Telegram-identity uniqueness race.
        # Other integrity errors (such as outbox failures) must remain server
        # errors instead of being mislabeled as a user conflict.
        already_owned = (
            user is not None
            and TelegramAccount.objects.filter(chat_id=chat_id)
            .exclude(user_id=user.id).exists()
        )
        if not already_owned:
            raise
        status = "conflict"

    if status == "expired":
        TelegramBotService.send_message(
            chat_id, "⏳ This link has expired. No worries—return to your TradeThesis Dashboard "
            "and tap Connect Telegram to get a fresh one."
        )
        return JsonResponse({"ok": True})
    if status == "conflict":
        if user is not None:
            BotAccessAudit.objects.create(
                user=user, action="link", platform="telegram",
                target=str(chat_id), status="failed",
                error_message="Telegram identity is already linked to another TradeThesis user.",
            )
        TelegramBotService.send_message(
            chat_id,
            "⚠️ This Telegram account is already linked to another TradeThesis account. "
            "Please contact support so we can help resolve it.",
        )
        return JsonResponse({"ok": True})
    if status == "disconnect_pending":
        TelegramBotService.send_message(
            chat_id,
            "⏳ Your previous Telegram disconnect is still being completed. "
            "Please return to your TradeThesis Member Desk and retry connecting "
            "after the pending disconnect has finished.",
        )
        return JsonResponse({"ok": True})
    if status == "already_linked":
        TelegramBotService.send_message(
            chat_id, "🎉 This Telegram account is already connected to TradeThesis."
        )
        return JsonResponse({"ok": True})
    if status == "account_conflict":
        if user is not None:
            BotAccessAudit.objects.create(
                user=user,
                action="link",
                platform="telegram",
                target=str(chat_id),
                status="failed",
                error_message="A different Telegram account is already linked; disconnect before rebinding.",
            )
        TelegramBotService.send_message(
            chat_id,
            "⚠️ A different Telegram account is already connected to your TradeThesis "
            "profile. Disconnect it from your Member Desk and wait for access cleanup "
            "before linking another account.",
        )
        return JsonResponse({"ok": True})

    TelegramBotService.send_message(
        chat_id, "🎉 You’re connected! Your TradeThesis account is now linked to Telegram. "
        "We’ll check your subscription access and let you know when everything’s ready."
    )
    return JsonResponse({"ok": True})


@login_required
def discord_oauth_start(request):
    """Begin a session-bound OAuth flow for linking and joining the community."""
    if getattr(request.user, "is_banned", False):
        return render(request, "accounts/banned.html", {
            "ban_reason": request.user.ban_reason,
        })
    if DiscordAccount.objects.filter(
        user=request.user, is_active=False
    ).exists():
        messages.error(
            request,
            "A previous Discord disconnect is still pending. Retry disconnecting "
            "from Connections before linking Discord again.",
        )
        return _discord_connections_redirect()

    config = BotConfig.get_config()
    required_config = (
        config.discord_client_id,
        config.discord_client_secret,
        config.discord_redirect_uri,
        config.discord_bot_token,
        config.discord_guild_id,
    )
    if not config.is_active or not all(required_config):
        messages.error(
            request,
            "Discord is not fully configured yet. Please contact support.",
        )
        return _discord_connections_redirect()

    state = secrets.token_urlsafe(32)
    request.session["discord_oauth_state"] = state

    from urllib.parse import urlencode

    auth_url = "https://discord.com/api/oauth2/authorize?" + urlencode({
        "client_id": config.discord_client_id,
        "redirect_uri": config.discord_redirect_uri,
        "response_type": "code",
        "scope": "identify guilds.join",
        "state": state,
    })
    return redirect(auth_url)


@login_required
def discord_oauth_callback(request):
    """Validate OAuth, join the configured guild, link the account, then sync roles."""
    import requests

    if getattr(request.user, "is_banned", False):
        return render(request, "accounts/banned.html", {
            "ban_reason": request.user.ban_reason,
        })

    code = request.GET.get("code")
    state = request.GET.get("state")
    error = request.GET.get("error")
    session_state = request.session.pop("discord_oauth_state", None)

    if (
        error
        or not code
        or not state
        or not session_state
        or not secrets.compare_digest(state, session_state)
    ):
        messages.error(request, "Discord authentication failed. Please try connecting again.")
        return _discord_connections_redirect()

    config = BotConfig.get_config()
    required_config = (
        config.discord_client_id,
        config.discord_client_secret,
        config.discord_redirect_uri,
        config.discord_bot_token,
        config.discord_guild_id,
    )
    if not config.is_active or not all(required_config):
        messages.error(request, "Discord is not fully configured yet. Please contact support.")
        return _discord_connections_redirect()

    token_data = {
        "client_id": config.discord_client_id,
        "client_secret": config.discord_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.discord_redirect_uri,
    }
    try:
        token_response = requests.post(
            "https://discord.com/api/oauth2/token",
            data=token_data,
            timeout=10,
        )
    except requests.RequestException:
        logger.warning("Discord OAuth token exchange request failed")
        messages.error(request, "Discord could not be reached. Please try again.")
        return _discord_connections_redirect()

    if token_response.status_code != 200:
        messages.error(request, "Discord authorization expired or was rejected. Please try again.")
        return _discord_connections_redirect()
    try:
        token_payload = token_response.json()
    except ValueError:
        token_payload = {}
    access_token = token_payload.get("access_token") if isinstance(token_payload, dict) else None
    if not access_token:
        messages.error(request, "Discord did not return a usable access token. Please try again.")
        return _discord_connections_redirect()

    try:
        user_response = requests.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
    except requests.RequestException:
        logger.warning("Discord OAuth profile request failed")
        messages.error(request, "Discord could not return your profile. Please try again.")
        return _discord_connections_redirect()

    if user_response.status_code != 200:
        messages.error(request, "Discord could not verify your account. Please try again.")
        return _discord_connections_redirect()
    try:
        user_info = user_response.json()
    except ValueError:
        user_info = {}
    if not isinstance(user_info, dict):
        user_info = {}

    discord_id = str(user_info.get("id") or "").strip()
    username = str(user_info.get("username") or "").strip()[:255]
    if not discord_id:
        messages.error(request, "Discord did not return an account ID. Please try again.")
        return _discord_connections_redirect()

    from django.contrib.auth import get_user_model
    User = get_user_model()
    canonical_identity_exists = DiscordAccount.objects.filter(
        discord_user_id=discord_id
    ).exclude(user=request.user).exists()
    legacy_identity_exists = User.objects.filter(
        discord_id=discord_id
    ).exclude(pk=request.user.pk).exists()
    if canonical_identity_exists or legacy_identity_exists:
        messages.error(request, "This Discord account is already linked to another TradeThesis account.")
        return _discord_connections_redirect()

    current_account = DiscordAccount.objects.filter(user=request.user).first()
    if current_account and not current_account.is_active:
        messages.error(
            request,
            "A previous Discord disconnect is still pending. Retry disconnecting "
            "from Connections before linking Discord again.",
        )
        return _discord_connections_redirect()

    if current_account and current_account.discord_user_id != discord_id:
        messages.error(
            request,
            "A different Discord account is already linked. Disconnect it before linking another account.",
        )
        return _discord_connections_redirect()

    # This endpoint adds the user to the configured guild if needed. If it
    # fails, do not save a link that cannot receive the planned role sync.
    if not DiscordBotService.add_member(discord_id, access_token):
        BotAccessAudit.objects.create(
            user=request.user,
            action="link",
            platform="discord",
            target=discord_id,
            status="failed",
            error_message="Discord guild join failed; account was not linked.",
        )
        messages.error(
            request,
            "Discord could not add you to the TradeThesis server. Please try again "
            "or contact support if the problem continues.",
        )
        return _discord_connections_redirect()

    try:
        from django.db import transaction

        with transaction.atomic():
            DiscordAccount.objects.update_or_create(
                user=request.user,
                defaults={
                    "discord_user_id": discord_id,
                    "guild_id": config.discord_guild_id,
                    "username": username,
                    "is_active": True,
                },
            )
            BotAccessAudit.objects.create(
                user=request.user,
                action="link",
                platform="discord",
                target=discord_id,
                status="success",
            )
            # The account link, audit event and durable sync job form one
            # database transaction. Never leave a saved link without a job.
            from apps.jobs.enqueue import enqueue_reconcile
            enqueue_reconcile(request.user.pk, reason="discord_link")
    except Exception:
        logger.exception("Discord link transaction failed after guild join")
        messages.error(
            request,
            "Discord added you to the server, but TradeThesis could not finish "
            "linking the account. Please try connecting again; no account link "
            "was saved.",
        )
        return _discord_connections_redirect()

    messages.success(
        request,
        "Discord connected. Your active community roles will sync shortly.",
    )
    return _discord_connections_redirect()


# ════════════════════════════════════════════════════════════════════════════
# Bot bridge self-registration / heartbeat  (Provision Contract v1)
# HMAC-authenticated API endpoints — NOT user-facing, NOT login-protected;
# authentication is the shared-secret signature itself.
# ════════════════════════════════════════════════════════════════════════════

import json as _json
from urllib.parse import urlsplit as _urlsplit

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .provision_auth import verify_signed_request
from .runtime_models import BotRuntimeState


def _allowed_base_url(url: str) -> bool:
    """Validate the bot-reported URL without becoming an SSRF primitive."""
    try:
        parts = _urlsplit(url)
    except ValueError:
        return False
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return False
    # Intentionally support local/private deployment (127.0.0.1, LAN IPs,
    # private hostnames).  Only obviously-dangerous targets are refused.
    blocked = {"169.254.169.254", "metadata.google.internal"}
    return parts.hostname not in blocked


@csrf_exempt
@require_POST
def bot_register(request):
    body, err = verify_signed_request(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=401)
    try:
        data = _json.loads(body.decode() or "{}")
    except ValueError:
        return JsonResponse({"ok": False, "error": "malformed JSON"}, status=400)

    instance_id = str(data.get("instance_id") or "").strip()
    base_url = str(data.get("base_url") or "").strip()
    contract = data.get("contract", "")
    version = data.get("version")
    operations = data.get("operations") or []

    if not instance_id:
        return JsonResponse({"ok": False, "error": "instance_id required"}, status=400)
    if not _allowed_base_url(base_url):
        return JsonResponse({"ok": False, "error": "invalid base_url"}, status=400)
    if not isinstance(operations, list):
        return JsonResponse({"ok": False, "error": "operations must be a list"}, status=400)

    bot_info = data.get("bot") if isinstance(data.get("bot"), dict) else {}
    state = BotRuntimeState.touch(
        instance_id,
        base_url=base_url,
        contract=str(contract),
        contract_version=int(version or 0),
        operations=operations,
        bot_telegram_id=bot_info.get("id"),
        bot_username=str(bot_info.get("username") or ""),
        status=(BotRuntimeState.STATUS_ONLINE
                if contract == "provision" and version == 1
                else BotRuntimeState.STATUS_INCOMPATIBLE),
    )
    return JsonResponse({"ok": True, "instance_id": state.instance_id,
                         "status": state.status})


@csrf_exempt
@require_POST
def bot_heartbeat(request):
    body, err = verify_signed_request(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=401)
    try:
        data = _json.loads(body.decode() or "{}")
    except ValueError:
        return JsonResponse({"ok": False, "error": "malformed JSON"}, status=400)

    instance_id = str(data.get("instance_id") or "").strip()
    try:
        state = BotRuntimeState.objects.get(instance_id=instance_id)
    except BotRuntimeState.DoesNotExist:
        # Django lost our state (DB reset etc.) — force the bot to re-register.
        return JsonResponse({"ok": False, "error": "unknown instance"}, status=404)

    updates = {"status": BotRuntimeState.STATUS_ONLINE if state.is_compatible()
               else BotRuntimeState.STATUS_INCOMPATIBLE}
    base_url = str(data.get("base_url") or "").strip()
    if base_url and _allowed_base_url(base_url) and base_url != state.base_url:
        updates["base_url"] = base_url
    for key, value in updates.items():
        setattr(state, key, value)
    # Heartbeat proves liveness: stamp last_seen so the freshness-based
    # endpoint resolution (ProvisionClient) keeps selecting this instance.
    state.last_seen = timezone.now()
    state.save(update_fields=[*updates.keys(), "last_seen", "updated_at"])
    return JsonResponse({"ok": True, "instance_id": state.instance_id})




@login_required
def sync_telegram_channels(request):
    """On-demand membership snapshot refresh; return to the current member desk."""
    sync_channel_memberships_for_user(request.user.id)
    messages.success(request, 'Channel membership refreshed.')
    return redirect('dashboard')

