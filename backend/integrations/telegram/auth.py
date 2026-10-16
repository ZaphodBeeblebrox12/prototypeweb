"""
Telegram authentication utilities with VERBOSE DEBUG logging.
"""
import hashlib
import hmac
import logging
from dataclasses import dataclass
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class TelegramAuthData:
    """Data class for Telegram authentication data."""
    id: int
    auth_date: int
    first_name: str
    hash: str
    last_name: str = ""
    username: str = ""
    photo_url: str = ""


def verify_telegram_auth_hash(data: dict, token: str) -> bool:
    """
    Verify Telegram authentication data hash with DEBUG logging.
    """
    logger.info("-" * 60)
    logger.info("VERIFYING TELEGRAM AUTH HASH")
    logger.info("-" * 60)

    received_hash = data.get("hash")
    logger.info(f"Received hash: {received_hash}")

    if not received_hash:
        logger.error("No hash received in data!")
        return False

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        return False

    # Build data-check-string (exclude hash, skip empty values)
    fields = {}
    for key in ["auth_date", "first_name", "id", "last_name", "photo_url", "username"]:
        value = data.get(key)
        if value:  # Skip empty values
            fields[key] = str(value)

    logger.info(f"Fields for hash calculation: {fields}")

    # Sort alphabetically and join with newlines
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(fields.items())
    )

    logger.info(f"Data check string: {repr(data_check_string)}")

    # Compute SHA256 of token
    secret_key = hashlib.sha256(token.encode()).digest()
    logger.info(f"Secret key (SHA256 of token): {secret_key.hex()[:16]}...")

    # Compute HMAC-SHA256
    computed_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    logger.info(f"Computed hash: {computed_hash}")
    logger.info(f"Received hash: {received_hash}")
    logger.info(f"Hashes match: {computed_hash == received_hash}")

    # Secure comparison
    result = hmac.compare_digest(computed_hash, received_hash)
    logger.info("-" * 60)
    return result


def parse_telegram_auth_data(data: dict) -> TelegramAuthData:
    """Parse and validate Telegram auth data."""
    logger.info(f"Parsing Telegram auth data: {data}")
    return TelegramAuthData(
        id=int(data.get("id", 0)),
        auth_date=int(data.get("auth_date", 0)),
        first_name=data.get("first_name", ""),
        hash=data.get("hash", ""),
        last_name=data.get("last_name", ""),
        username=data.get("username", ""),
        photo_url=data.get("photo_url", ""),
    )
