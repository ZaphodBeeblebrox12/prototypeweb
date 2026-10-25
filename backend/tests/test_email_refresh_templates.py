"""Smoke tests for the branded HTML templates added in the email refresh."""
from datetime import date
from types import SimpleNamespace

import pytest
from django.template.loader import render_to_string


@pytest.mark.parametrize(
    ("template", "context", "expected"),
    [
        (
            "growth/email/welcome_day1_body.html",
            {
                "username": "alice",
                "dashboard_url": "https://academy.example.test/dashboard/",
                "support_url": "https://academy.example.test/support/",
            },
            "Open your dashboard",
        ),
        (
            "growth/email/welcome_day3_body.html",
            {
                "username": "alice",
                "connect_url": "https://academy.example.test/bot/telegram/connect/",
                "dashboard_url": "https://academy.example.test/dashboard/",
                "support_url": "https://academy.example.test/support/",
            },
            "Connect Telegram",
        ),
        (
            "growth/email/winback_body.html",
            {
                "username": "alice",
                "code": "WELCOME123",
                "percent_off": 20,
                "valid_until": date(2026, 11, 30),
                "dashboard_url": "https://academy.example.test/dashboard/",
            },
            "WELCOME123",
        ),
        (
            "growth/email/gift_invite_body.html",
            {
                "sender_name": "Sam",
                "plan_name": "Pro",
                "duration_days": 30,
                "message": "A gift for your learning journey.",
                "claim_url": "https://academy.example.test/gifts/claim/test-token/",
                "expires_at": date(2026, 11, 30),
            },
            "Claim your gift",
        ),
        (
            "growth/gift_claimed_body.html",
            {
                "user": SimpleNamespace(username="alice"),
                "plan_name": "Pro",
                "duration_days": 30,
                "subscription_expires": date(2026, 11, 30),
                "sender_name": "Sam",
                "dashboard_url": "https://academy.example.test/dashboard/",
            },
            "Your gift is active",
        ),
        (
            "subscriptions/email/reminder_pre_expiry_body.html",
            {
                "username": "alice",
                "plan_name": "Pro",
                "days": 3,
                "dashboard_url": "https://academy.example.test/dashboard/",
            },
            "Renew subscription",
        ),
        (
            "subscriptions/email/reminder_post_expiry_body.html",
            {
                "username": "alice",
                "plan_name": "Pro",
                "dashboard_url": "https://academy.example.test/dashboard/",
            },
            "Renew subscription",
        ),
    ],
)
def test_refreshed_html_email_templates_render_with_trade_thesis_branding(
    template, context, expected
):
    context = {
        **context,
        "site_name": "TradeThesis",
        "logo_url": "https://assets.example.test/tradethesis-horizontal.png",
        "support_url": context.get(
            "support_url", "https://academy.example.test/support/"
        ),
    }

    html = render_to_string(template, context)

    assert expected in html
    assert "TradeThesis" in html
    assert "https://assets.example.test/tradethesis-horizontal.png" in html
