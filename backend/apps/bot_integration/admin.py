from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html
from .models import (
    BotConfig, TelegramAccount, DiscordAccount, PlanChannelMapping,
    UserChannelAssignment, BotAccessAudit, TelegramVerificationToken,
    CommunityChannel, ChannelMembershipSnapshot,
)
from .services.telegram import TelegramBotService


@admin.register(BotConfig)
class BotConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'telegram_bot_username', 'discord_bot_token_preview']
    fieldsets = (
        ('Telegram', {
            'fields': ('telegram_bot_token', 'telegram_bot_username', 'telegram_webhook_url'),
            'description': (
                'Telegram username: enter WITHOUT the @ prefix (e.g. titanpipbot). '
                'A leading @ is removed automatically. Native webhook authentication '
                'uses TELEGRAM_WEBHOOK_SECRET from the hosting environment; the Set '
                'Webhook button opens a confirmation form before applying the change.'
            )
        }),
        ('Discord', {
            'fields': ('discord_bot_token', 'discord_guild_id', 'discord_client_id', 'discord_client_secret', 'discord_redirect_uri'),
            'description': (
                'Use credentials from the same Discord Application. Register the exact '
                'public callback URL in Developer Portal: https://<academy-host>/bot/discord/callback/. '
                'The bot must be in this guild, have CREATE_INSTANT_INVITE and MANAGE_ROLES, '
                'and its highest role must be above every role mapped to a plan. '
                'OAuth linking uses identify and guilds.join.'
            ),
        }),
        ('Status', {'fields': ('is_active',)}),
        ('Bot Actions', {
            'fields': ('telegram_actions',),
            'classes': ('collapse',),
            'description': 'Click the buttons below to test the bot and set the webhook.'
        }),
    )
    readonly_fields = ['telegram_actions', 'discord_bot_token_preview']

    def discord_bot_token_preview(self, obj):
        token = obj.discord_bot_token
        if token:
            return f"{token[:10]}..."
        return "Not set"
    discord_bot_token_preview.short_description = "Discord Token (preview)"

    def telegram_actions(self, obj):
        """Render action buttons using named URLs."""
        test_url = reverse('admin:test_telegram_bot')
        webhook_url = reverse('admin:set_telegram_webhook')
        return format_html(
            '<div style="display: flex; gap: 10px; margin-top: 10px;">'
            '<a class="button" href="{}" style="background: #28a745; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px;">'
            '📡 Test Telegram Bot</a>'
            '<a class="button" href="{}" style="background: #007bff; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px;">'
            '🔗 Set Telegram Webhook</a>'
            '</div>',
            test_url, webhook_url
        )
    telegram_actions.short_description = "Telegram Bot Actions"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test-telegram/', self.admin_site.admin_view(self.test_telegram), name='test_telegram_bot'),
            path('set-webhook/', self.admin_site.admin_view(self.set_webhook), name='set_telegram_webhook'),
        ]
        return custom_urls + urls

    def test_telegram(self, request):
        """Test Telegram bot connection."""
        config = BotConfig.get_config()
        if not config.telegram_bot_token:
            self.message_user(request, "❌ Telegram bot token is not set.", level='ERROR')
            return redirect(request.META.get('HTTP_REFERER', '../'))

        bot_info = TelegramBotService.get_bot_info()
        if bot_info and bot_info.get('ok'):
            username = bot_info.get('result', {}).get('username', '')
            first_name = bot_info.get('result', {}).get('first_name', '')
            if not config.telegram_bot_username and username:
                config.telegram_bot_username = username
                config.save(update_fields=['telegram_bot_username'])
            self.message_user(
                request,
                f"✅ Bot connected! Name: {first_name}, Username: @{username}",
                level='SUCCESS'
            )
        else:
            error = bot_info.get('description', 'Unknown error') if bot_info else 'No response'
            self.message_user(request, f"❌ Bot test failed: {error}", level='ERROR')

        return redirect(request.META.get('HTTP_REFERER', '../'))

    def set_webhook(self, request):
        """Configure the native Telegram webhook after a CSRF-protected POST."""
        from django.conf import settings
        from django.template.response import TemplateResponse

        config = BotConfig.get_config()
        webhook_url = (config.telegram_webhook_url or "").strip()
        if not webhook_url:
            site_url = (getattr(settings, "SITE_BASE_URL", "") or "").strip().rstrip("/")
            if site_url:
                webhook_url = f"{site_url}/bot/telegram/webhook/"

        if request.method != "POST":
            return TemplateResponse(
                request,
                "admin/bot_integration/set_telegram_webhook_confirm.html",
                {
                    **self.admin_site.each_context(request),
                    "opts": self.model._meta,
                    "title": "Set Telegram webhook",
                    "webhook_url": webhook_url,
                    "secret_configured": bool(
                        getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "")
                    ),
                    "token_configured": bool(config.telegram_bot_token),
                },
            )

        if not config.telegram_bot_token:
            self.message_user(request, "❌ Bot token not set.", level="ERROR")
        elif not webhook_url:
            self.message_user(
                request, "❌ No webhook URL configured and SITE_BASE_URL is not set.",
                level="ERROR",
            )
        elif not getattr(settings, "TELEGRAM_WEBHOOK_SECRET", ""):
            self.message_user(
                request, "❌ TELEGRAM_WEBHOOK_SECRET is missing from the hosting environment.",
                level="ERROR",
            )
        elif TelegramBotService.set_webhook(webhook_url):
            self.message_user(
                request, f"✅ Native Telegram webhook set to {webhook_url}",
                level="SUCCESS",
            )
        else:
            self.message_user(
                request,
                "❌ Telegram rejected the webhook. Check the HTTPS URL, token and TELEGRAM_WEBHOOK_SECRET format.",
                level="ERROR",
            )
        return redirect(request.META.get("HTTP_REFERER", "../"))



@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'chat_id', 'telegram_user_id', 'linked_at', 'is_active', 'last_synced_at']
    raw_id_fields = ['user']
    search_fields = ['user__username', 'chat_id', 'telegram_user_id']


@admin.register(DiscordAccount)
class DiscordAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'discord_user_id', 'username', 'linked_at', 'is_active']
    raw_id_fields = ['user']
    search_fields = ['user__username', 'discord_user_id']


@admin.register(PlanChannelMapping)
class PlanChannelMappingAdmin(admin.ModelAdmin):
    list_display = ['plan', 'platform', 'external_id', 'name']
    list_filter = ['platform', 'plan']
    search_fields = ['external_id', 'name']


@admin.register(UserChannelAssignment)
class UserChannelAssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'external_id', 'assigned_at', 'is_active']
    list_filter = ['platform', 'is_active']
    raw_id_fields = ['user']

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
    list_display = ['user', 'action', 'platform', 'status', 'created_at']
    list_filter = ['action', 'platform', 'status', 'created_at']
    raw_id_fields = ['user']
    readonly_fields = [f.name for f in BotAccessAudit._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False





@admin.register(CommunityChannel)
class CommunityChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'external_id', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active']
    search_fields = ['name', 'external_id']


@admin.register(ChannelMembershipSnapshot)
class ChannelMembershipSnapshotAdmin(admin.ModelAdmin):
    list_display = ['user', 'channel', 'is_member', 'checked_at']
    list_filter = ['is_member', 'channel']
    search_fields = ['user__username', 'channel__name']
    readonly_fields = ['user', 'channel', 'is_member', 'checked_at']

    def has_add_permission(self, request):
        return False


@admin.register(TelegramVerificationToken)
class TelegramVerificationTokenAdmin(admin.ModelAdmin):
    # Issued verification tokens: read-only audit, never add/change/delete.
    list_display = ['user', 'token', 'created_at', 'expires_at']
    raw_id_fields = ['user']
    readonly_fields = [f.name for f in TelegramVerificationToken._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


