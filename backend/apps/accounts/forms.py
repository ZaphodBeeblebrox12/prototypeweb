"""TradeThesis-specific allauth forms.

Email uniqueness is a sign-up rule, not a global email-field rule: password
reset must accept an address that already belongs to an account.
"""
from django import forms
from allauth.account.forms import SignupForm

from apps.accounts.models import User


class TradeThesisSignupForm(SignupForm):
    """Collect and persist a member's name as part of account creation."""

    first_name = forms.CharField(
        label="First name",
        max_length=255,
        required=True,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "given-name",
                "placeholder": "Your first name",
            }
        ),
    )
    last_name = forms.CharField(
        label="Last name",
        max_length=255,
        required=True,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "family-name",
                "placeholder": "Your last name",
            }
        ),
    )

    def clean_email(self):
        email = super().clean_email()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )
        return email

    def clean_first_name(self):
        value = (self.cleaned_data.get("first_name") or "").strip()
        if not value:
            raise forms.ValidationError("Enter your first name.")
        return value

    def clean_last_name(self):
        value = (self.cleaned_data.get("last_name") or "").strip()
        if not value:
            raise forms.ValidationError("Enter your last name.")
        return value

    def save(self, request):
        """Let allauth create the account, then persist the collected name fields."""
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save(update_fields=["first_name", "last_name"])
        return user
