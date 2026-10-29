"""
Custom allauth adapter for Google authentication.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django import forms
from django.conf import settings
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from apps.accounts.models import User


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to handle Google login and prevent duplicate emails."""

    def pre_social_login(self, request, sociallogin):
        """
        Handle pre-social login.
        Check if user with this email already exists and connect accounts.
        """
        email = sociallogin.user.email
        if not email:
            return

        try:
            existing_user = User.objects.get(email=email)
            # If user exists with this email, connect the social account
            if not sociallogin.is_existing:
                sociallogin.connect(request, existing_user)
                # Log the login
                from apps.audit.models import AuditLog
                AuditLog.log(
                    action="login_google",
                    user=existing_user,
                    object_type="user",
                    object_id=existing_user.id,
                    metadata={"provider": "google", "email": email}
                )
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        """
        Save user with telegram_verified=False for Google users.
        Google users are automatically verified via allauth.
        """
        user = super().save_user(request, sociallogin, form)

        # Set telegram_verified to False for Google login
        user.telegram_verified = False

        # Generate username from email if not set
        if not user.username:
            base_username = user.email.split('@')[0] if user.email else "user"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user.username = username

        user.save()

        # Create user preferences
        from apps.accounts.models import UserPreference
        UserPreference.objects.get_or_create(user=user)

        # Log the signup
        from apps.audit.models import AuditLog
        AuditLog.log(
            action="signup_google",
            user=user,
            object_type="user",
            object_id=user.id,
            metadata={"provider": "google", "email": user.email}
        )

        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter with email verification support."""

    def clean_email(self, email):
        """Reject duplicate email addresses before the unique DB constraint is hit."""
        email = super().clean_email(email)
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )
        return email


    def _safe_redirect_destination(self, request):
        """Return a same-site destination requested during the course journey."""
        candidate = (
            request.POST.get(self.redirect_field_name)
            or request.GET.get(self.redirect_field_name)
        )
        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return candidate
        return ""

    def get_login_redirect_url(self, request):
        """Respect safe return destinations after login while enforcing verification."""
        user = request.user

        # Do not grant access via an unverified email address.
        if user.email and not self._is_email_verified(user):
            return reverse("account_email_verification_sent")

        # DefaultAccountAdapter validates and honours the requested next= URL,
        # falling back to LOGIN_REDIRECT_URL when no safe destination is supplied.
        return super().get_login_redirect_url(request)

    def get_logout_redirect_url(self, request):
        return "/"

    def send_mail(self, template_prefix, email, context):
        """Add TradeThesis branding and absolute account links to Allauth mail."""
        context.setdefault("logo_url", getattr(settings, "EMAIL_LOGO_URL", ""))
        base_url = str(getattr(settings, "SITE_BASE_URL", "") or "").rstrip("/")
        if base_url:
            context.setdefault("dashboard_url", f"{base_url}/dashboard/")
            context.setdefault("support_url", f"{base_url}/support/")
        return super().send_mail(template_prefix, email, context)

    def _is_email_verified(self, user):
        """Check if user's email is verified."""
        try:
            email_address = EmailAddress.objects.filter(user=user, verified=True).first()
            return email_address is not None
        except:
            return False

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """Send confirmation email with custom context."""
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        next_url = self._safe_redirect_destination(request)
        if next_url:
            # Email verification is a separate browser visit, so explicitly carry
            # the safe same-site destination through the confirmation link.
            parts = urlsplit(activate_url)
            query = dict(parse_qsl(parts.query, keep_blank_values=True))
            query[self.redirect_field_name] = next_url
            activate_url = urlunsplit(
                (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
            )

        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": get_current_site(request),
            "key": emailconfirmation.key,
        }
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            # Allauth appends _message.{html,txt} to this prefix.
            email_template = 'account/email/email_confirmation'

        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)
