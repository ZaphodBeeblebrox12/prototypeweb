"""Outgoing messages for TradeThesis's dedicated verification bot only."""
from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramVerificationBotService:
    """Keep verification replies separate from the channel/mesh bot identity."""

    @classmethod
    def send_message(cls, chat_id: int, text: str) -> bool:
        token = (getattr(settings, "TELEGRAM_VERIFICATION_BOT_TOKEN", "") or "").strip()
        if not token or chat_id is None:
            logger.warning("Verification bot message skipped: missing configuration or chat id")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            response = requests.post(
                url,
                json={"chat_id": chat_id, "text": text},
                timeout=(5, 10),
            )
            if response.status_code != 200:
                logger.warning("Verification bot rejected a reply (HTTP %s)", response.status_code)
                return False
            payload: Any = response.json()
            if not isinstance(payload, dict) or payload.get("ok") is not True:
                logger.warning("Verification bot reply was not accepted by Telegram")
                return False
            return True
        except (requests.RequestException, ValueError) as exc:
            # Exception text can contain the token-bearing URL; log only the class.
            logger.warning("Verification bot reply failed (%s)", type(exc).__name__)
            return False
