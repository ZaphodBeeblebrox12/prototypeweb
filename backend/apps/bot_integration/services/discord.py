"""Small, status-aware Discord REST client for membership and role sync."""
import logging

import requests

from ..models import BotConfig

logger = logging.getLogger(__name__)

# Discord's documented error codes for objects that are already absent.
_UNKNOWN_MEMBER = "10007"
_UNKNOWN_ROLE = "10011"


class DiscordBotService:
    @classmethod
    def _get_config(cls):
        return BotConfig.get_config()

    @classmethod
    def _get_token(cls):
        return cls._get_config().discord_bot_token

    @classmethod
    def _guild_id(cls):
        return cls._get_config().discord_guild_id

    @classmethod
    def _api_request(cls, endpoint, method="GET", data=None):
        token = cls._get_token()
        if not token:
            return {"ok": False, "error": "Discord bot token is not configured"}

        url = f"https://discord.com/api/v10/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.request(
                method, url, headers=headers, json=data, timeout=10
            )
        except requests.RequestException as exc:
            # Do not log request headers or tokens.
            logger.warning("Discord API request failed (%s %s): %s", method, endpoint, exc)
            return {"ok": False, "error": "Discord API request failed"}

        if response.status_code == 204:
            return {"ok": True, "status_code": 204}

        try:
            payload = response.json()
        except ValueError:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}

        if 200 <= response.status_code < 300:
            payload["ok"] = True
            payload["status_code"] = response.status_code
            return payload

        payload["ok"] = False
        payload["status_code"] = response.status_code
        payload["discord_code"] = str(payload.get("code", ""))
        payload["error"] = (
            payload.get("message") or
            f"Discord API returned HTTP {response.status_code}"
        )
        return payload

    @classmethod
    def add_member(cls, user_id, oauth_access_token):
        """Join the OAuth-authorized user to the configured guild.

        Discord requires the OAuth `guilds.join` scope and the bot to have
        CREATE_INSTANT_INVITE in this guild. The user's access token is used
        for this one request only and is never stored.
        """
        guild_id = cls._guild_id()
        if not guild_id or not cls._get_token() or not oauth_access_token:
            return False
        result = cls._api_request(
            f"/guilds/{guild_id}/members/{user_id}",
            method="PUT",
            data={"access_token": oauth_access_token},
        )
        return result.get("ok") is True

    @classmethod
    def add_role(cls, user_id, role_id):
        guild_id = cls._guild_id()
        if not guild_id:
            return False
        result = cls._api_request(
            f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            method="PUT",
        )
        return result.get("ok") is True

    @classmethod
    def remove_role(cls, user_id, role_id):
        guild_id = cls._guild_id()
        if not guild_id:
            return False
        result = cls._api_request(
            f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            method="DELETE",
        )
        if result.get("ok") is True:
            return True
        # Removing access is idempotently complete when Discord confirms that
        # the member or managed role no longer exists. Do not treat arbitrary
        # 4xx/5xx JSON error bodies as success.
        return (
            result.get("status_code") == 404
            and result.get("discord_code") in {_UNKNOWN_MEMBER, _UNKNOWN_ROLE}
        )

    @classmethod
    def get_bot_info(cls):
        result = cls._api_request("/users/@me")
        if result.get("ok") is True and result.get("id"):
            return result
        return None
