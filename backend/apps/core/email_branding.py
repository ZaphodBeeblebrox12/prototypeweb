"""Shared TradeThesis identity for every outbound email."""
import re
from email.utils import formataddr, parseaddr


_PREFIX_RE = re.compile(r"^\s*\[(?:example\.com|tradethesis)\]\s*", re.IGNORECASE)


def normalise_email_subject(subject):
    """Give every outbound subject one canonical TradeThesis prefix."""
    value = " ".join(str(subject or "").splitlines()).strip()
    while _PREFIX_RE.match(value):
        value = _PREFIX_RE.sub("", value, count=1).strip()
    return f"[TradeThesis] {value}" if value else "[TradeThesis]"


def normalise_from_email(from_email, default_from_email):
    """Keep the configured sender address while making the visible sender brand-safe."""
    candidate = str(from_email or default_from_email or "").strip()
    _display_name, address = parseaddr(candidate)
    if not address:
        candidate = str(default_from_email or "").strip()
        _display_name, address = parseaddr(candidate)
    if not address:
        return candidate
    return formataddr(("TradeThesis", address))
