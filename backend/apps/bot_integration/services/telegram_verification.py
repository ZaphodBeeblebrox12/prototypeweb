"""Compatibility wrapper; verification replies use the canonical Telegram bot."""
from .telegram import TelegramBotService


class TelegramVerificationBotService:
    """Legacy import shim which delegates to the single configured bot."""

    @classmethod
    def send_message(cls, chat_id: int, text: str) -> bool:
        return TelegramBotService.send_message(chat_id, text)
