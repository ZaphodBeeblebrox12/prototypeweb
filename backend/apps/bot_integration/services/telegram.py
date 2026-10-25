import requests
import logging
import time
from datetime import timedelta
from functools import wraps
from typing import Optional, Dict, Any
from django.utils import timezone

from .telegram_transport import (
    ERR_CONFIG,
    ERR_MISSING_CHAT_ID,
    OUTCOME_INDETERMINATE,
    OUTCOME_REJECTED,
    TelegramMessageResult,
    TelegramMessageTransport,
)

logger = logging.getLogger(__name__)


def retry_on_flood(max_retries=3, base_delay=1):
    """Decorator to retry on Telegram flood wait (error 429)."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                result = func(*args, **kwargs)
                if not isinstance(result, dict):
                    return result
                if result.get("ok"):
                    return result
                if result.get("error_code") == 429:
                    retry_after = result.get("parameters", {}).get("retry_after", base_delay * (2 ** attempt))
                    logger.warning(f"Flood wait {retry_after}s, retry {attempt+1}/{max_retries}")
                    time.sleep(retry_after)
                    continue
                return result
            return {"ok": False, "error": "Max retries exceeded"}
        return wrapper
    return decorator


class TelegramBotService:
    @classmethod
    def _get_config(cls):
        from ..models import BotConfig
        return BotConfig.get_config()

    @classmethod
    def _get_token(cls):
        return cls._get_config().telegram_bot_token

    @classmethod
    @retry_on_flood()
    def _api_request(cls, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        token = cls._get_token()
        if not token:
            return {"ok": False, "error": "No bot token"}
        url = f"https://api.telegram.org/bot{token}/{method}"
        try:
            resp = requests.post(url, json=params or {}, timeout=(5, 10))
        except requests.exceptions.Timeout:
            return {
                "ok": False, "error_code": "timeout",
                "description": "Request to Telegram API timed out",
                "transport_error": True,
            }
        except requests.exceptions.RequestException as exc:
            # Exception strings can include the token-bearing API URL.
            logger.warning("Telegram API request failed: %s", type(exc).__name__)
            return {
                "ok": False, "error_code": "network_error",
                "description": "Network error contacting Telegram API",
                "transport_error": True,
            }

        try:
            payload = resp.json()
        except ValueError:
            return {
                "ok": False,
                "error_code": resp.status_code,
                "description": f"Telegram returned an unreadable response (HTTP {resp.status_code})",
                "transport_error": resp.status_code >= 500,
            }
        if not isinstance(payload, dict):
            return {
                "ok": False, "error_code": resp.status_code,
                "description": "Unexpected response from Telegram API",
                "transport_error": resp.status_code >= 500,
            }
        if not payload.get("ok") and resp.status_code >= 500:
            payload["transport_error"] = True
        return payload

    # ------------------------------------------------------------------
    # Reusable message transport (Stage 1)
    #
    # Shared by marketing and transactional/system messaging alike. This
    # path applies NO marketing-consent gate and performs NO provisioning /
    # entitlement operations - business layers decide the message class and
    # apply any consent check ABOVE it.
    #
    # Semantics:
    #   outcome == "accepted"       -> provider accepted; message_id captured
    #   outcome == "rejected"       -> definite provider rejection
    #   outcome == "indeterminate"  -> timeout/network/unparseable response;
    #                                  the request MAY have been processed,
    #                                  so NEVER report as SENT
    # ------------------------------------------------------------------

    @classmethod
    def send_message_result(cls, chat_id, text: str) -> TelegramMessageResult:
        """Send a text message and return the rich TelegramMessageResult."""
        try:
            token = cls._get_token() or ""
        except Exception as exc:  # config/DB unavailable -> indeterminate
            logger.warning("Telegram bot config unavailable: %s", type(exc).__name__)
            token = ""
        if not token:
            return TelegramMessageResult(
                outcome=OUTCOME_INDETERMINATE,
                error_code=ERR_CONFIG,
                error_message="Telegram bot token is not configured",
            )
        if chat_id is None or isinstance(chat_id, bool) or str(chat_id).strip() == "":
            return TelegramMessageResult(
                outcome=OUTCOME_REJECTED,
                error_code=ERR_MISSING_CHAT_ID,
                error_message="chat_id is required and was not provided",
            )
        transport = TelegramMessageTransport(token=token)
        return transport.send_message(chat_id=chat_id, text=text)

    @classmethod
    def send_message(cls, chat_id: int, text: str) -> bool:
        # Backward-compatible bool wrapper (unchanged contract for existing
        # callers: only a definite provider acceptance returns True).
        return cls.send_message_result(chat_id, text).ok

    @classmethod
    def create_one_time_invite_link_result(
        cls, channel_id: str, expire_seconds: int = 86400,
    ) -> tuple[Optional[str], str, bool]:
        """Return (invite_link, error, retryable) without conflating failure classes."""
        expire_date = int((timezone.now() + timedelta(seconds=expire_seconds)).timestamp())
        result = cls._api_request("createChatInviteLink", {
            "chat_id": channel_id,
            "expire_date": expire_date,
            "member_limit": 1,
        })
        if result.get("ok"):
            result_payload = result.get("result")
            if isinstance(result_payload, dict):
                invite_link = result_payload.get("invite_link")
                if isinstance(invite_link, str) and invite_link.strip():
                    return invite_link, "", False
        error = (result.get("description") or result.get("error")
                 or "Telegram did not return a usable invite link")
        code = result.get("error_code")
        retryable = bool(result.get("transport_error")) or code in {
            429, 500, 502, 503, 504,
        } or any(word in error.lower() for word in (
            "timeout", "timed out", "network", "temporarily unavailable",
        ))
        # Do not log raw HTTP objects or exception strings; only provider
        # descriptions/codes are retained, never the bot token-bearing URL.
        logger.warning(
            "Telegram invite creation failed channel=%s code=%s retryable=%s",
            channel_id, code, retryable,
        )
        return None, error, retryable

    @classmethod
    def create_one_time_invite_link(
        cls, channel_id: str, expire_seconds: int = 86400,
    ) -> Optional[str]:
        link, _error, _retryable = cls.create_one_time_invite_link_result(
            channel_id, expire_seconds,
        )
        return link

    @classmethod
    def ban_user(cls, channel_id: str, user_id: int) -> tuple[bool, str]:
        """
        Ban a user from a Telegram channel.
        Returns (success, error_message). Treats "user already not in chat" as success.
        """
        if not user_id:
            return False, "Missing telegram_user_id"
        result = cls._api_request("banChatMember", {
            "chat_id": channel_id,
            "user_id": user_id
        })
        if result.get("ok"):
            return True, ""
        error = result.get("description", "")
        if "user not found" in error.lower() or "chat member not found" in error.lower():
            logger.info(f"User {user_id} already not in channel {channel_id}, treating as banned")
            return True, ""
        return False, f"Ban failed: {error} (code {result.get('error_code')})"

    @classmethod
    def unban_user(cls, channel_id: str, user_id: int) -> tuple[bool, str]:
        if not user_id:
            return False, "Missing telegram_user_id"
        result = cls._api_request("unbanChatMember", {
            "chat_id": channel_id,
            "user_id": user_id,
            "only_if_banned": True
        })
        if result.get("ok"):
            return True, ""
        error = result.get("description", "")
        return False, f"Unban failed: {error} (code {result.get('error_code')})"

    @classmethod
    def is_member(cls, channel_id: str, user_id: int) -> Optional[bool]:
        """Return True/False only when Telegram reports membership conclusively.

        None means Telegram could not establish the state. Callers must not
        interpret an API/network error as proof that the user is absent.
        """
        response = cls._api_request("getChatMember", {
            "chat_id": channel_id, "user_id": user_id,
        })
        if not response.get("ok"):
            return None
        member = response.get("result") or {}
        status = member.get("status")
        if status in ("creator", "administrator", "member"):
            return True
        if status in ("left", "kicked"):
            return False
        if status == "restricted" and isinstance(member.get("is_member"), bool):
            return member["is_member"] is True
        return None

    @classmethod
    def verify_channel(cls, channel_id: str) -> Dict[str, Any]:
        """Inspect a channel and the configured bot's current admin rights."""
        chat_response = cls._api_request("getChat", {"chat_id": channel_id})
        if not chat_response.get("ok"):
            return {
                "ok": False,
                "error": chat_response.get("description") or chat_response.get("error")
                         or "Telegram could not read this channel",
                "detail": {},
            }

        bot_response = cls._api_request("getMe")
        if not bot_response.get("ok"):
            return {
                "ok": False,
                "error": bot_response.get("description") or bot_response.get("error")
                         or "Telegram bot identity could not be verified",
                "detail": {},
            }
        bot_id = (bot_response.get("result") or {}).get("id")
        member_response: Dict[str, Any] = (
            cls._api_request("getChatMember", {"chat_id": channel_id, "user_id": bot_id})
            if bot_id
            else {"ok": False}
        )
        member: Dict[str, Any] = (
            (member_response.get("result") or {}) if member_response.get("ok") else {}
        )
        status = member.get("status", "unknown")
        detail = {
            "title": (chat_response.get("result") or {}).get("title")
                     or (chat_response.get("result") or {}).get("username")
                     or str(channel_id),
            "type": (chat_response.get("result") or {}).get("type", ""),
            "bot_status": status,
            "can_administer": status in ("administrator", "creator"),
            "can_invite_users": bool(member.get("can_invite_users"))
                                if status == "administrator" else status == "creator",
            "can_restrict_members": bool(member.get("can_restrict_members"))
                                    if status == "administrator" else status == "creator",
        }
        if not member_response.get("ok"):
            detail["bot_status"] = "unknown"
            detail["can_administer"] = False
        return {"ok": True, "detail": detail, "error": ""}

    @classmethod
    def get_bot_info(cls):
        return cls._api_request("getMe")

    @classmethod
    def get_user_profile_photos(cls, user_id: int, limit: int = 1):
        return cls._api_request("getUserProfilePhotos",
                                {"user_id": user_id, "limit": limit})

    @classmethod
    def get_file(cls, file_id: str):
        return cls._api_request("getFile", {"file_id": file_id})

    @classmethod
    def set_webhook(cls, url=None):
        """Register native Telegram delivery with the secret-token header."""
        import re
        from django.conf import settings

        config = cls._get_config()
        webhook_url = url or config.telegram_webhook_url
        secret_token = (getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "") or "").strip()
        if not webhook_url or not secret_token:
            logger.error("Cannot set Telegram webhook: URL or TELEGRAM_WEBHOOK_SECRET is missing")
            return False
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,256}", secret_token):
            logger.error("Cannot set Telegram webhook: secret token format is invalid")
            return False
        result = cls._api_request("setWebhook", {
            "url": webhook_url,
            "secret_token": secret_token,
            "allowed_updates": ["message"],
        })
        return bool(result.get("ok", False))
