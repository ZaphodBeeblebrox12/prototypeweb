"""Regression coverage for the custom allauth confirmation email templates."""
from types import SimpleNamespace

import pytest
from django.template.loader import render_to_string


@pytest.mark.parametrize(
    "template_prefix",
    [
        "account/email/email_confirmation_signup",
        "account/email/email_confirmation_message",
    ],
)
def test_confirmation_email_templates_render_subject_and_confirmation_link(template_prefix):
    confirmation_url = "https://staging.example.test/accounts/confirm-email/test-key/"
    context = {
        "user": SimpleNamespace(get_username=lambda: "staging-user"),
        "current_site": SimpleNamespace(name="TradeThesis"),
        "activate_url": confirmation_url,
        "key": "test-key",
    }

    subject = render_to_string(f"{template_prefix}_subject.txt", context).strip()
    body = render_to_string(f"{template_prefix}.txt", context)

    assert subject
    assert "TradeThesis" in subject
    assert confirmation_url in body
    assert "staging-user" in body
