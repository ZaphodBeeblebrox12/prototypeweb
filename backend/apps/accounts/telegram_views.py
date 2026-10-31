"""Legacy Telegram Login Widget compatibility, using canonical bot identity."""
import hashlib
import hmac
import time
import uuid

from django.contrib.auth import login
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from apps.accounts.models import User, UserPreference
from apps.audit.models import AuditLog
from apps.bot_integration.models import BotConfig, TelegramAccount


MAX_TELEGRAM_AUTH_AGE_SECONDS = 24 * 60 * 60
MAX_TELEGRAM_FUTURE_SKEW_SECONDS = 60


class TelegramAuthView(View):
    """Render the legacy Telegram Login Widget using the canonical bot config."""

    def get(self, request):
        config = BotConfig.get_config()
        bot_username = (config.telegram_bot_username or "").strip().lstrip("@")
        bot_token = (config.telegram_bot_token or "").strip()
        if not config.is_active or not bot_username or not bot_token:
            return HttpResponseBadRequest("Telegram bot not configured")

        callback_url = request.build_absolute_uri(reverse("telegram_callback"))
        return render(request, "accounts/telegram_login.html", {
            "bot_username": bot_username,
            "callback_url": callback_url,
        })


@method_decorator(csrf_exempt, name="dispatch")
class TelegramCallbackView(View):
    """Authenticate a Telegram user without attaching accounts by username."""

    @staticmethod
    def _error(request, message, status_code):
        if request.content_type == "application/json":
            return JsonResponse({"error": message}, status=status_code)
        return HttpResponse(message, status=status_code)

    def post(self, request):
        is_json = request.content_type == "application/json"
        if is_json:
            try:
                import json
                data = json.loads(request.body.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return JsonResponse({"error": "Invalid JSON body"}, status=400)
        else:
            data = request.POST.dict()

        if not isinstance(data, dict):
            return self._error(request, "Invalid Telegram authentication data", 400)

        required_fields = ("id", "hash", "auth_date")
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return self._error(request, f"Missing field: {missing[0]}", 400)

        # The Login Widget must use the same configured bot as the member
        # dashboard deep-link and webhook flows. Never use a public test-token
        # fallback in a deployed environment.
        config = BotConfig.get_config()
        bot_token = (config.telegram_bot_token or "").strip()
        if not config.is_active or not bot_token:
            return self._error(request, "Telegram bot not configured", 503)

        raw_telegram_id = str(data.get("id") or "").strip()
        try:
            telegram_id = int(raw_telegram_id)
            auth_date = int(data.get("auth_date"))
        except (TypeError, ValueError):
            return self._error(request, "Invalid Telegram identity or auth date", 400)
        if telegram_id <= 0 or auth_date <= 0:
            return self._error(request, "Invalid Telegram identity or auth date", 400)

        now = int(time.time())
        if (
            auth_date > now + MAX_TELEGRAM_FUTURE_SKEW_SECONDS
            or now - auth_date > MAX_TELEGRAM_AUTH_AGE_SECONDS
        ):
            return self._error(
                request,
                "Telegram authentication has expired. Please sign in again.",
                403,
            )

        data_fields = []
        for key in (
            "auth_date", "first_name", "id", "last_name", "photo_url", "username"
        ):
            value = data.get(key)
            if value:
                data_fields.append(f"{key}={value}")
        data_check_string = "\n".join(sorted(data_fields))
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        calculated_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        check_hash = str(data.get("hash") or "")
        if not hmac.compare_digest(calculated_hash, check_hash):
            return self._error(request, "Invalid authentication hash", 403)

        username = str(data.get("username") or "").strip()[:64]
        first_name = str(data.get("first_name") or "").strip()[:150]
        last_name = str(data.get("last_name") or "").strip()[:150]

        # Prefer the current canonical managed link. If an unlink is pending,
        # do not allow this older login route to reactivate it.
        canonical_accounts = list(
            TelegramAccount.objects.filter(
                Q(telegram_user_id=telegram_id) | Q(chat_id=telegram_id)
            ).select_related("user")[:2]
        )
        if len(canonical_accounts) > 1:
            return self._error(
                request,
                "This Telegram identity has conflicting TradeThesis links. Contact support.",
                409,
            )
        if canonical_accounts:
            account = canonical_accounts[0]
            if not account.is_active:
                return self._error(
                    request,
                    "Your Telegram disconnect is still being completed. Try again after it finishes.",
                    403,
                )
            user = account.user
        else:
            # Telegram usernames are mutable and can be reused. Never use one
            # as proof that a Telegram identity owns an existing TradeThesis
            # account; only the stable numeric Telegram ID may match.
            user = User.objects.filter(telegram_id=telegram_id).first()

        created = user is None
        if created:
            user = User.objects.create(
                telegram_id=telegram_id,
                telegram_username=username,
                telegram_verified=True,
                first_name=first_name,
                last_name=last_name,
                username=f"tg_{telegram_id}_{uuid.uuid4().hex[:8]}",
                is_active=True,
            )
            UserPreference.objects.get_or_create(user=user)
            AuditLog.log(
                action="user_created",
                user=user,
                object_type="user",
                object_id=str(user.id),
                metadata={
                    "telegram_id": telegram_id,
                    "telegram_username": username,
                },
            )

        if getattr(user, "is_banned", False):
            return self._error(request, "Account is banned", 403)

        # A canonical account or a pre-existing numeric-ID match can refresh
        # profile metadata; it cannot change which TradeThesis user owns that ID.
        conflicting_user = User.objects.filter(
            telegram_id=telegram_id
        ).exclude(pk=user.pk).exists()
        if conflicting_user:
            return self._error(
                request,
                "This Telegram account is already connected to another user.",
                409,
            )
        user.telegram_id = telegram_id
        user.telegram_username = username
        user.telegram_verified = True
        user.first_name = first_name or user.first_name
        user.last_name = last_name or user.last_name
        user.save(update_fields=[
            "telegram_id", "telegram_username", "telegram_verified",
            "first_name", "last_name",
        ])

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        if is_json:
            return JsonResponse({
                "success": True,
                "created": created,
                "user_id": str(user.id),
                "telegram_id": user.telegram_id,
                "telegram_username": user.telegram_username,
            }, status=200)
        return redirect("dashboard")
