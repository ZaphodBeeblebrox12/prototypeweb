"""
Custom allauth adapter for Google authentication.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.app_settings import EmailVerificationMethod
from django import forms
from django.conf import settings
from allauth.exceptions import ImmediateHttpResponse
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

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


    def pre_login(
        self,
        request,
        user,
        *,
        email_verification,
        signal_kwargs,
        email,
        signup,
        redirect_url,
    ):
        """Keep staff access recoverable while enforcing verification for learners.

        Allauth's mandatory email verification gate runs before the session is
        created. A newly bootstrapped Django superuser may not yet have an
        EmailAddress row, so they would otherwise be unable to enter /admin/.
        Staff/superusers use the normal password check but skip the learner
        email-verification gate; protected learner routes remain governed by
        the app's verification middleware.
        """
        if user.is_staff or user.is_superuser:
            email_verification = EmailVerificationMethod.OPTIONAL
        return super().pre_login(
            request,
            user,
            email_verification=email_verification,
            signal_kwargs=signal_kwargs,
            email=email,
            signup=signup,
            redirect_url=redirect_url,
        )

    def get_login_redirect_url(self, request):
        """Honor the requested destination after login."""
        user = request.user

        # Staff need to access Django admin to resolve account/configuration
        # problems. Learner verification remains mandatory for ordinary users.
        if (
            user.email
            and not (user.is_staff or user.is_superuser)
            and not self._is_email_verified(user)
        ):
            return reverse("account_email_verification_sent")

        # Honour a safe ``next`` target supplied by allauth; otherwise use
        # LOGIN_REDIRECT_URL, which points to the TradeThesis learner dashboard.
        return super().get_login_redirect_url(request)

    def get_logout_redirect_url(self, request):
        return f"{settings.PUBLIC_SITE_URL}/"

    def _is_email_verified(self, user):
        """Check if user's email is verified."""
        try:
            return EmailAddress.objects.filter(
                user=user,
                email__iexact=user.email,
                verified=True,
            ).exists()
        except:
            return False

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """Send confirmation email with custom context."""
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": self.get_email_confirmation_url(
                request, emailconfirmation
            ),
            "current_site": get_current_site(request),
            "key": emailconfirmation.key,
        }
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'

        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)
