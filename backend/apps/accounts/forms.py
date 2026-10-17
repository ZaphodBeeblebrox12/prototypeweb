"""TradeThesis-specific signup validation.

The email adapter hook is also used by password-reset forms, so uniqueness
checks against the custom User model belong in signup validation rather than
in DefaultAccountAdapter.clean_email().
"""
from django import forms
from allauth.account.forms import SignupForm

from apps.accounts.models import User


class TradeThesisSignupForm(SignupForm):
    """Keep the custom User.email unique constraint as a form-level error."""

    def clean_email(self):
        email = super().clean_email()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )
        return email
