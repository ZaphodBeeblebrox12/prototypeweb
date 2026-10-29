"""Regression tests for preserving a learner's intended course through authentication."""
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

import pytest
from django.test import RequestFactory
from django.urls import reverse

from apps.accounts.adapters import CustomAccountAdapter


COURSE_DESTINATION = "/learn/course/support-resistance-draft/"


@pytest.mark.django_db
def test_login_preserves_a_safe_course_destination(client):
    """A learner who signs in from a course page returns to that course."""
    from allauth.account.models import EmailAddress
    from apps.accounts.models import User

    user = User.objects.create_user(
        username="course-learner",
        email="course-learner@example.com",
        password="Str0ng!Pass9",
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        primary=True,
        verified=True,
    )

    response = client.post(
        f"{reverse('account_login')}?next={COURSE_DESTINATION}",
        {
            "login": user.email,
            "password": "Str0ng!Pass9",
            "next": COURSE_DESTINATION,
        },
    )

    assert response.status_code == 302
    assert response.url == COURSE_DESTINATION


@pytest.mark.django_db
def test_confirmation_email_carries_safe_course_destination():
    """The confirmation link keeps the course URL across the email round trip."""
    adapter = CustomAccountAdapter()
    request = RequestFactory().post(
        "/accounts/signup/",
        {"next": COURSE_DESTINATION},
        HTTP_HOST="testserver",
    )
    email_address = SimpleNamespace(
        user=SimpleNamespace(email="learner@example.com"),
        email="learner@example.com",
    )
    confirmation = SimpleNamespace(email_address=email_address, key="test-key")

    with (
        patch.object(
            adapter,
            "get_email_confirmation_url",
            return_value="https://academy.test/accounts/confirm-email/test-key/",
        ),
        patch(
            "apps.accounts.adapters.get_current_site",
            return_value=SimpleNamespace(domain="academy.test"),
        ),
        patch.object(adapter, "send_mail") as send_mail,
    ):
        adapter.send_confirmation_mail(request, confirmation, signup=True)

    context = send_mail.call_args.args[2]
    url = urlsplit(context["activate_url"])
    assert url.path == "/accounts/confirm-email/test-key/"
    assert parse_qs(url.query)["next"] == [COURSE_DESTINATION]



def test_email_confirmation_returns_to_the_requested_course():
    """After email confirmation, the destination comes from the validated link."""
    adapter = CustomAccountAdapter()
    request = RequestFactory().get(
        "/accounts/confirm-email/test-key/",
        {"next": COURSE_DESTINATION},
    )

    assert adapter.get_email_confirmation_redirect_url(request) == COURSE_DESTINATION

def test_confirmation_destination_rejects_external_redirects():
    """An attacker cannot turn the course return parameter into an open redirect."""
    adapter = CustomAccountAdapter()
    request = RequestFactory().post(
        "/accounts/signup/",
        {"next": "https://evil.example/collect"},
        HTTP_HOST="testserver",
    )

    assert adapter._safe_redirect_destination(request) == ""
