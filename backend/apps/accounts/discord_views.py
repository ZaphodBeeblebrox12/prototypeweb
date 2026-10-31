"""
Discord authentication views for account verification.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response



def check_banned(view_func):
    """Decorator to check if user is banned."""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_banned:
            return render(request, "accounts/banned.html", {
                "ban_reason": request.user.ban_reason
            })
        return view_func(request, *args, **kwargs)
    return wrapper


@method_decorator(login_required, name="dispatch")
@method_decorator(check_banned, name="dispatch")
class DiscordConnectView(View):
    """Initiate Discord OAuth2 connection flow."""

    def get(self, request):
        """Compatibility entry point for the canonical Discord connection flow."""
        from apps.bot_integration.views import discord_oauth_start
        return discord_oauth_start(request)


@method_decorator(login_required, name="dispatch")
@method_decorator(check_banned, name="dispatch")
class DiscordCallbackView(View):
    """Handle Discord OAuth2 callback."""

    def get(self, request):
        """Delegate callbacks to the managed Discord guild-join and role-sync flow.

        BotConfig.discord_redirect_uri may still point at this historical URL;
        it must therefore complete the same canonical flow rather than writing
        only legacy User.discord_id fields.
        """
        from apps.bot_integration.views import discord_oauth_callback
        return discord_oauth_callback(request)


@method_decorator(login_required, name="dispatch")
@method_decorator(check_banned, name="dispatch")
class DiscordDisconnectView(View):
    """Disconnect Discord account from user profile."""

    def post(self, request):
        """Delegate disconnect to canonical managed-role removal."""
        from apps.bot_integration.views import unlink_discord
        return unlink_discord(request)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def discord_connect_api(request):
    """Return the canonical same-origin Discord connection route.

    The browser must visit this route so the canonical BotConfig, session-bound
    state, guild-join and role-sync lifecycle is used. The route then redirects
    to Discord; this API no longer constructs OAuth URLs from legacy env vars.
    """
    if getattr(request.user, "is_banned", False):
        return Response(
            {"error": "Account is banned"},
            status=status.HTTP_403_FORBIDDEN,
        )
    return Response({
        "authorization_url": request.build_absolute_uri(
            reverse("bot_integration:discord_connect")
        )
    })
