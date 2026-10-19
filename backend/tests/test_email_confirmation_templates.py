"""Regression coverage for branded Allauth confirmation email templates."""
from types import SimpleNamespace

import pytest
from django.template.loader import render_to_string


@pytest.mark.parametrize(
    "template_prefix",
    [
        "account/email/email_confirmation_signup",
        "account/email/email_confirmation",
    ],
)
def test_confirmation_email_templates_render_subject_text_and_html(template_prefix):
    confirmation_url = "https://staging.example.test/accounts/confirm-email/test-key/"
    context = {
        "user": SimpleNamespace(get_username=lambda: "staging-user", username="staging-user"),
        "current_site": SimpleNamespace(name="TradeThesis", domain="tradethesis.example"),
        "activate_url": confirmation_url,
        "password_reset_url": confirmation_url,
        "key": "test-key",
        "logo_url": "https://tradethesis.example/assets/tradethesis-horizontal.png",
    }

    subject = render_to_string(f"{template_prefix}_subject.txt", context).strip()
    body = render_to_string(f"{template_prefix}_message.txt", context)
    html_body = render_to_string(f"{template_prefix}_message.html", context)

    assert "TradeThesis" in subject
    assert confirmation_url in body
    assert "staging-user" in body
    assert "TradeThesis" in html_body
    assert confirmation_url in html_body
    assert "Confirm email address" in html_body
