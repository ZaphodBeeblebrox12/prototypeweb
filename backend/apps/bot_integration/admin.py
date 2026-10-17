from django.conf import settings
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html
from .models import (
    BotConfig, TelegramAccount, DiscordAccount, PlanChannelMapping,
    UserChannelAssignment, BotAccessAudit, TelegramVerificationToken,
    CommunityChannel, ChannelMembershipSnapshot
)
from .services.telegram import TelegramBotService


@admin.register(BotConfig)
class BotConfigAdmin(admin.ModelAdmin):
    list_display = [
        "id", "is_active", "telegram_username_from_environment",
        "telegram_token_configured", "discord_bot_token_preview",
    ]
    fieldsets = (
        ("Telegram (shared environment configuration)", {
            "fields": ("telegram_environment_status",),
            "description": (
                "The staging Telegram bot token and username come from the shared "
                "Render Environment Group: TELEGRAM_BOT_TOKEN and "
                "TELEGRAM_BOT_USERNAME. Do not store the token in this database."
            ),
        }),
        ("Discord", {
            "fields": (
                "discord_bot_token", "discord_guild_id",
                "discord_client_id", "discord_client_secret",
                "discord_redirect_uri",
            )
        }),
        ("Status", {"fields": ("is_active",)}),
        ("Bot Actions", {
            "fields": ("telegram_actions",),
            "classes": ("collapse",),
            "description": (
                "Test the Telegram API credentials. Account verification also "
                "requires the separate signed polling/Provision bridge to be online."
            ),
        }),
    )
    readonly_fields = [
        "telegram_actions", "telegram_environment_status",
        "discord_bot_token_preview",
    ]

    def telegram_username_from_environment(self, obj):
        username = (getattr(settings, "TELEGRAM_BOT_USERNAME", "") or "").strip().lstrip("@")
        return f"@{username}" if username else "Not configured"
    telegram_username_from_environment.short_description = "Telegram bot"

    def telegram_token_configured(self, obj):
        return bool((getattr(settings, "TELEGRAM_BOT_TOKEN", "") or "").strip())
    telegram_token_configured.boolean = True
    telegram_token_configured.short_description = "Token configured"

    def telegram_environment_status(self, obj):
        username = self.telegram_username_from_environment(obj)
        token_status = "configured" if self.telegram_token_configured(obj) else "missing"
        return format_html(
            "<strong>Bot username:</strong> {}<br><strong>API token:</strong> {}",
            username, token_status,
        )
    telegram_environment_status.short_description = "Render environment status"

    def discord_bot_token_preview(self, obj):
        token = obj.discord_bot_token
        if token:
            return f"{token[:10]}..."
        return "Not set"
    discord_bot_token_preview.short_description = "Discord Token (preview)"

    def telegram_actions(self, obj):
        """Render the safe bot-test action; native Telegram webhooks are not used."""
        test_url = reverse("admin:test_telegram_bot")
        return format_html(
            '<a class="button" href="{}" '
            'style="background:#28a745;color:white;padding:8px 15px;'
            'text-decoration:none;border-radius:4px;">'
            '📡 Test Telegram Bot</a>',
            test_url,
        )
    telegram_actions.short_description = "Telegram Bot Actions"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "test-telegram/",
                self.admin_site.admin_view(self.test_telegram),
                name="test_telegram_bot",
            ),
        ]
        return custom_urls + urls

    def test_telegram(self, request):
        """Test the centrally configured Telegram bot token."""
        if not (getattr(settings, "TELEGRAM_BOT_TOKEN", "") or "").strip():
            self.message_user(
                request,
                "Telegram bot token is missing. Add TELEGRAM_BOT_TOKEN to the shared Render Environment Group.",
                level="ERROR",
            )
            return redirect(request.META.get("HTTP_REFERER", "../"))

        bot_info = TelegramBotService.get_bot_info()
        if bot_info and bot_info.get("ok"):
            api_username = bot_info.get("result", {}).get("username", "")
            first_name = bot_info.get("result", {}).get("first_name", "")
            configured_username = (
                getattr(settings, "TELEGRAM_BOT_USERNAME", "") or ""
            ).strip().lstrip("@")
            if not configured_username:
                self.message_user(
                    request,
                    f"Telegram API connected as @{api_username} ({first_name}). "
                    "Now set TELEGRAM_BOT_USERNAME in the shared Render Environment Group.",
                    level="WARNING",
                )
            elif configured_username != api_username:
                self.message_user(
                    request,
                    f"Telegram API connected as @{api_username}, but TELEGRAM_BOT_USERNAME "
                    f"is set to @{configured_username}. Correct the shared environment value.",
                    level="WARNING",
                )
            else:
                self.message_user(
                    request,
                    f"Telegram API connected as @{api_username} ({first_name}).",
                    level="SUCCESS",
                )
        else:
            error = bot_info.get("description", "Unknown error") if bot_info else "No response"
            self.message_user(request, f"Telegram bot test failed: {error}", level="ERROR")

        return redirect(request.META.get("HTTP_REFERER", "../"))


@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = ["user", "chat_id", "telegram_user_id", "linked_at", "is_active", "last_synced_at"]
    raw_id_fields = ["user"]
    search_fields = ["user__username", "chat_id", "telegram_user_id"]


@admin.register(DiscordAccount)
class DiscordAccountAdmin(admin.ModelAdmin):
    list_display = ["user", "discord_user_id", "username", "linked_at", "is_active"]
    raw_id_fields = ["user"]
    search_fields = ["user__username", "discord_user_id"]


@admin.register(PlanChannelMapping)
class PlanChannelMappingAdmin(admin.ModelAdmin):
    list_display = ["plan", "platform", "external_id", "name"]
    list_filter = ["platform", "plan"]
    search_fields = ["external_id", "name"]


@admin.register(UserChannelAssignment)
class UserChannelAssignmentAdmin(admin.ModelAdmin):
    list_display = ["user", "platform", "external_id", "assigned_at", "is_active"]
    list_filter = ["platform", "is_active"]
    raw_id_fields = ["user"]

    # Lifecycle-controlled fields are owned by reconciliation; admins must not
    # hand-edit entitlement/timestamps (would desync from reconcile).
    def get_readonly_fields(self, request, obj=None):
        base = list(super().get_readonly_fields(request, obj))
        for f in ("is_active", "last_invite_sent_at", "revoked_at"):
            if f not in base:
                base.append(f)
        return base


@admin.register(BotAccessAudit)
class BotAccessAuditAdmin(admin.ModelAdmin):
    # Access audit trail: fully read-only, never add/change/delete.
    list_display = ["user", "action", "platform", "status", "created_at"]
    list_filter = ["action", "platform", "status"]
    raw_id_fields = ["user"]
    readonly_fields = [f.name for f in BotAccessAudit._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CommunityChannel)
class CommunityChannelAdmin(admin.ModelAdmin):
    list_display = ["name", "platform", "external_id", "is_active", "created_at"]
    list_filter = ["platform", "is_active"]
    search_fields = ["name", "external_id"]


@admin.register(ChannelMembershipSnapshot)
class ChannelMembershipSnapshotAdmin(admin.ModelAdmin):
    list_display = ["user", "channel", "is_member", "checked_at"]
    list_filter = ["is_member", "channel"]
    search_fields = ["user__username", "channel__name"]
    readonly_fields = ["user", "channel", "is_member", "checked_at"]

    def has_add_permission(self, request):
        return False


@admin.register(TelegramVerificationToken)
class TelegramVerificationTokenAdmin(admin.ModelAdmin):
    # Issued verification tokens: read-only audit, never add/change/delete.
    list_display = ["user", "token", "created_at", "expires_at"]
    raw_id_fields = ["user"]
    readonly_fields = [f.name for f in TelegramVerificationToken._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
