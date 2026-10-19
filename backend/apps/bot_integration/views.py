import json
import secrets
import logging
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
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
    ChannelMesh, ChannelMeshDestination,
)
from .services.telegram import TelegramBotService
from .services.telegram_verification import TelegramVerificationBotService
from .services.discord import DiscordBotService
from .services.profile_sync import sync_telegram_profile_for_user
from .services.channel_sync import sync_channel_memberships_for_user

logger = logging.getLogger(__name__)


@login_required
def start_telegram_connect(request):
    """Generate a deep link to the dedicated Telegram verification bot."""
    bot_username = (
        getattr(settings, "TELEGRAM_VERIFICATION_BOT_USERNAME", "") or ""
    ).strip().lstrip("@")
    bot_token = (
        getattr(settings, "TELEGRAM_VERIFICATION_BOT_TOKEN", "") or ""
    ).strip()
    if not bot_username or not bot_token:
        messages.error(
            request,
            "Telegram verification is not configured yet. Please contact support.",
        )
        return redirect("dashboard")

    # Delete old unused tokens for this user.
    TelegramVerificationToken.objects.filter(user=request.user).delete()

    token = TelegramVerificationToken.create_token(request.user)
    deep_link = f"https://t.me/{bot_username}?start=verify_{token.token}"
    return redirect(deep_link)

@login_required
@require_POST
def unlink_telegram(request):
    """Disconnect Telegram account from user profile."""
    try:
        tg = TelegramAccount.objects.get(user=request.user)
        old_chat_id = tg.chat_id
        tg.delete()
        BotAccessAudit.objects.create(
            user=request.user,
            action='unlink',
            platform='telegram',
            target=str(old_chat_id),
            status='success'
        )
        from apps.jobs.enqueue import enqueue_reconcile
        enqueue_reconcile(request.user.id, reason="telegram_unlink")
        messages.success(request, "Telegram account unlinked.")
    except TelegramAccount.DoesNotExist:
        pass
    return redirect('dashboard')


def _discord_connections_redirect():
    """Return members to the canonical Connections section of the Member Desk."""
    return redirect(f"{reverse('dashboard')}#connections")


@login_required
@require_POST
def unlink_discord(request):
    """Remove managed Discord roles before disconnecting the linked account."""
    dc = DiscordAccount.objects.filter(user=request.user).first()
    if dc is None:
        messages.info(request, "No Discord account is currently linked.")
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
    """Handle Telegram bot updates (deep link verification).

    Updates arrive via the dedicated verification bot's polling loop, which forwards
    /start verify_<token> updates here over HTTP (Option 1 architecture —
    Django runs on localhost and cannot receive Telegram webhooks directly).
    Requests must carry the Provision Contract v1 HMAC signature; native
    Telegram webhook delivery is not used.
    """
    from .provision_auth import verify_signed_request
    body, auth_err = verify_signed_request(request)
    if auth_err:
        return JsonResponse({"ok": False, "error": auth_err}, status=401)
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    logger.info("Telegram webhook received update_id=%s", data.get("update_id"))

    if 'message' not in data or 'text' not in data['message']:
        return JsonResponse({"ok": True})

    text = data['message']['text']
    chat_id = data['message']['chat']['id']
    from_user = data['message'].get('from', {})
    telegram_user_id = from_user.get('id')

    if not text.startswith('/start'):
        return JsonResponse({"ok": True})

    parts = text.split()
    if len(parts) != 2 or not parts[1].startswith('verify_'):
        TelegramVerificationBotService.send_message(
            chat_id,
            "\U0001f44b Hi! To link your account: open the website, go to"
            " Dashboard and press Connect Telegram. Already paid? Connecting"
            " grants your channel access automatically.")
        return JsonResponse({"ok": True})

    token_str = parts[1][7:]  # remove 'verify_'

    try:
        token = TelegramVerificationToken.objects.select_related('user').get(token=token_str)
        if not token.is_valid():
            TelegramVerificationBotService.send_message(chat_id, "❌ Verification link expired. Please request a new one on the website.")
            token.delete()
            return JsonResponse({"ok": False})

        user = token.user
        # Transactional outbox: account + audit + job commit atomically.
        from django.db import transaction as _tx
        from apps.jobs.enqueue import enqueue_reconcile
        with _tx.atomic():
            TelegramAccount.objects.update_or_create(
                user=user,
                defaults={
                    'chat_id': chat_id,
                    'telegram_user_id': telegram_user_id,
                    'is_active': True,
                    'username': from_user.get('username') or '',
                    'first_name': from_user.get('first_name') or '',
                }
            )
            token.delete()

            BotAccessAudit.objects.create(
                user=user,
                action='link',
                platform='telegram',
                target=str(chat_id),
                status='success'
            )

            enqueue_reconcile(user.id, reason="telegram_link")
            # Best-effort avatar enrichment AFTER the transaction commits.
            _tx.on_commit(lambda: sync_telegram_profile_for_user(user.id))
            _tx.on_commit(lambda: sync_channel_memberships_for_user(user.id))

        TelegramVerificationBotService.send_message(chat_id, "✅ Your account is now linked! We'll sync your subscription access shortly.")

        return JsonResponse({"ok": True})

    except TelegramVerificationToken.DoesNotExist:
        TelegramVerificationBotService.send_message(chat_id, "❌ Invalid verification code.")
        return JsonResponse({"ok": False})


@login_required
def discord_oauth_start(request):
    """Begin a session-bound OAuth flow for linking and joining the community."""
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

    if DiscordAccount.objects.filter(discord_user_id=discord_id).exclude(
        user=request.user
    ).exists():
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




@csrf_exempt
@require_POST
def bot_mesh_inventory(request):
    """Return enabled Mesh spawn inventory to the authenticated allocator.

    The response lists only registered, active Meshes and active spawns.
    It does not include members or assign anyone to a destination.
    """
    body, err = verify_signed_request(request)
    if err:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)

    try:
        data = _json.loads(body.decode() or "{}")
    except (UnicodeDecodeError, ValueError):
        return JsonResponse({"ok": False, "error": "malformed JSON"}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({"ok": False, "error": "JSON object required"}, status=400)

    mesh_key = str(data.get("mesh_key") or "").strip()
    meshes = ChannelMesh.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            "destinations",
            queryset=ChannelMeshDestination.objects.filter(is_active=True).order_by(
                "name", "external_id"
            ),
        )
    ).order_by("key")
    if mesh_key:
        meshes = meshes.filter(key=mesh_key)

    inventory = [
        {
            "mesh_key": mesh.key,
            "mesh_name": mesh.name,
            "source_chat_id": mesh.source_chat_id,
            "source_name": mesh.source_name,
            "spawns": [
                {
                    "spawn_chat_id": destination.external_id,
                    "name": destination.name,
                    "chat_type": destination.chat_type,
                }
                for destination in mesh.destinations.all()
            ],
        }
        for mesh in meshes
    ]
    return JsonResponse({"ok": True, "meshes": inventory}, status=200)


@csrf_exempt
@require_POST
def bot_mesh_assignment(request):
    """Accept a spawn decision from the existing allocator over the signed bridge.

    This endpoint records the allocator's selected spawn; it never chooses one.
    The Telegram user ID is resolved to a linked Django account before checking
    active entitlement and the Mesh/spawn configuration.
    """
    body, err = verify_signed_request(request)
    if err:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)

    try:
        data = _json.loads(body.decode() or "{}")
    except (UnicodeDecodeError, ValueError):
        return JsonResponse({"ok": False, "error": "malformed JSON"}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({"ok": False, "error": "JSON object required"}, status=400)

    raw_telegram_id = data.get("telegram_user_id")
    if isinstance(raw_telegram_id, bool) or not str(raw_telegram_id or "").isdigit():
        return JsonResponse(
            {"ok": False, "error": "positive telegram_user_id required"}, status=400
        )
    telegram_user_id = int(raw_telegram_id)
    if telegram_user_id <= 0:
        return JsonResponse(
            {"ok": False, "error": "positive telegram_user_id required"}, status=400
        )

    mesh_key = str(data.get("mesh_key") or "").strip()
    spawn_chat_id = str(data.get("spawn_chat_id") or "").strip()
    if not mesh_key or not spawn_chat_id:
        return JsonResponse(
            {"ok": False, "error": "mesh_key and spawn_chat_id are required"},
            status=400,
        )

    accounts = TelegramAccount.objects.filter(
        telegram_user_id=telegram_user_id, is_active=True
    ).select_related("user")
    if accounts.count() != 1:
        return JsonResponse(
            {"ok": False, "error": "linked Telegram account not found or ambiguous"},
            status=404 if not accounts.exists() else 409,
        )
    account = accounts.first()

    mesh = ChannelMesh.objects.filter(key=mesh_key, is_active=True).first()
    if mesh is None:
        return JsonResponse(
            {"ok": False, "error": "active Mesh not found"}, status=404
        )
    destination = ChannelMeshDestination.objects.filter(
        mesh=mesh, external_id=spawn_chat_id, is_active=True
    ).first()
    if destination is None:
        return JsonResponse(
            {"ok": False, "error": "active spawn not found in the requested Mesh"},
            status=404,
        )

    from .services.channel_mesh import assign_user_to_mesh_spawn

    try:
        assignment = assign_user_to_mesh_spawn(account.user, mesh, destination)
    except ValidationError as exc:
        return JsonResponse(
            {"ok": False, "error": "; ".join(exc.messages)}, status=409
        )
    except Exception:
        logger.exception(
            "Channel Mesh assignment failed for linked Telegram user %s", telegram_user_id
        )
        return JsonResponse(
            {"ok": False, "error": "assignment could not be saved"}, status=500
        )

    return JsonResponse({
        "ok": True,
        "assignment": {
            "mesh_key": assignment.mesh.key,
            "spawn_chat_id": assignment.destination.external_id,
            "active": assignment.is_active,
        },
    }, status=200)


@login_required
def sync_telegram_channels(request):
    """On-demand membership snapshot refresh; return to the current member desk."""
    sync_channel_memberships_for_user(request.user.id)
    messages.success(request, 'Channel membership refreshed.')
    return redirect('dashboard')

