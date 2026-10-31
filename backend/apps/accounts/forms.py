"""TradeThesis-specific allauth forms.

Email uniqueness is a sign-up rule, not a global email-field rule: password
reset must accept an address that already belongs to an account.
"""
from django import forms
from allauth.account.forms import SignupForm

from apps.accounts.models import User


class TradeThesisSignupForm(SignupForm):
    """Reject emails already present on the user model during sign-up."""

    def clean_email(self):
        email = super().clean_email()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )
        return email
