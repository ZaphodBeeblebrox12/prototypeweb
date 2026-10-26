from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("support", "0006_update_ticket_field_help_text"),
        ("support", "0006_alter_affiliatelink_plan_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="affiliatelink",
            name="plan",
            field=models.ForeignKey(
                blank=True,
                help_text="Optional: hidden plan auto-assigned when an access request using this link is approved (you can still override)",
                limit_choices_to={"is_hidden": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="affiliate_links",
                to="subscriptions.plan",
            ),
        ),
        migrations.AlterField(
            model_name="supportticket",
            name="admin_notes",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Shown to the user on rejection (and stored for approved tickets)",
            ),
        ),
        migrations.AlterField(
            model_name="supportticket",
            name="affiliate_link",
            field=models.ForeignKey(
                blank=True,
                help_text="Which referral link was used (access requests only)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tickets",
                to="support.affiliatelink",
            ),
        ),
        migrations.AlterField(
            model_name="supportticket",
            name="plan",
            field=models.ForeignKey(
                blank=True,
                help_text="Assigned by the approver at approval time (access requests)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="support_tickets",
                to="subscriptions.plan",
            ),
        ),
        migrations.AlterField(
            model_name="ticketmessage",
            name="author",
            field=models.ForeignKey(
                blank=True,
                help_text="Null = deleted account; body retained, author shown as 'former user'.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="ticketmessage",
            name="is_internal",
            field=models.BooleanField(
                default=False,
                help_text="Staff-only note; never shown to the user.",
            ),
        ),
    ]
