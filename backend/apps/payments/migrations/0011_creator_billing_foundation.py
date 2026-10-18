# Creator billing foundation.
import decimal
import uuid

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


def create_default_billing_settings(apps, schema_editor):
    BillingSettings = apps.get_model("payments", "BillingSettings")
    BillingSettings.objects.using(schema_editor.connection.alias).get_or_create(
        pk=1,
        defaults={
            "seller_name": "TradeThesis",
            "invoice_prefix": "TT",
            "tax_enabled": False,
            "tax_label": "GST",
            "tax_rate_percentage": decimal.Decimal("0.00"),
            "tax_inclusive": False,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("payments", "0010_refund_commercial_context")]

    operations = [
        migrations.AddField(model_name="paymentintent", name="subtotal_cents",
                            field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name="paymentintent", name="tax_enabled",
                            field=models.BooleanField(default=False)),
        migrations.AddField(model_name="paymentintent", name="tax_rate_percentage",
                            field=models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=5)),
        migrations.AddField(model_name="paymentintent", name="tax_label",
                            field=models.CharField(blank=True, default="GST", max_length=30)),
        migrations.AddField(model_name="paymentintent", name="tax_amount_cents",
                            field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name="paymentintent", name="tax_inclusive",
                            field=models.BooleanField(default=False)),
        migrations.CreateModel(
            name="BillingSettings",
            fields=[
                ("id", models.PositiveSmallIntegerField(default=1, editable=False, primary_key=True, serialize=False)),
                ("seller_name", models.CharField(default="TradeThesis", max_length=150)),
                ("legal_name", models.CharField(blank=True, default="", max_length=255)),
                ("address", models.TextField(blank=True, default="")),
                ("country", models.CharField(blank=True, default="", max_length=2)),
                ("support_email", models.EmailField(blank=True, default="", max_length=254)),
                ("tax_registration_number", models.CharField(blank=True, default="", max_length=100)),
                ("invoice_prefix", models.CharField(default="TT", max_length=20)),
                ("tax_enabled", models.BooleanField(default=False, help_text="Leave disabled until your accountant confirms whether and how tax applies to your sales.")),
                ("tax_label", models.CharField(default="GST", max_length=30)),
                ("tax_rate_percentage", models.DecimalField(
                    decimal_places=2, default=decimal.Decimal("0.00"), max_digits=5,
                    validators=[
                        django.core.validators.MinValueValidator(decimal.Decimal("0.00")),
                        django.core.validators.MaxValueValidator(decimal.Decimal("100.00")),
                    ],
                    help_text="Simple fixed percentage applied to all new checkouts while tax is enabled. Not a jurisdiction-aware tax engine.",
                )),
                ("tax_inclusive", models.BooleanField(default=False, help_text="When enabled, treat the listed price as tax-inclusive. Confirm this treatment before enabling tax.")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "business and tax setting", "verbose_name_plural": "business and tax settings"},
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("invoice_number", models.CharField(max_length=50, unique=True)),
                ("issue_date", models.DateField(default=timezone.localdate)),
                ("issued_at", models.DateTimeField(default=timezone.now)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("seller_name", models.CharField(max_length=150)),
                ("seller_legal_name", models.CharField(blank=True, default="", max_length=255)),
                ("seller_address", models.TextField(blank=True, default="")),
                ("seller_country", models.CharField(blank=True, default="", max_length=2)),
                ("seller_support_email", models.EmailField(blank=True, default="", max_length=254)),
                ("seller_tax_registration_number", models.CharField(blank=True, default="", max_length=100)),
                ("customer_name", models.CharField(blank=True, default="", max_length=255)),
                ("customer_email", models.EmailField(blank=True, default="", max_length=254)),
                ("description", models.CharField(max_length=255)),
                ("subtotal_cents", models.PositiveIntegerField(default=0)),
                ("tax_enabled", models.BooleanField(default=False)),
                ("tax_rate_percentage", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=5)),
                ("tax_label", models.CharField(blank=True, default="", max_length=30)),
                ("tax_amount_cents", models.PositiveIntegerField(default=0)),
                ("tax_inclusive", models.BooleanField(default=False)),
                ("total_cents", models.PositiveIntegerField(default=0)),
                ("transaction_reference", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("payment_intent", models.OneToOneField(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="invoice", to="payments.paymentintent")),
            ],
            options={
                "ordering": ["-issue_date", "-issued_at"],
                "permissions": [("export_invoice", "Can export invoice register")],
            },
        ),
        migrations.RunPython(create_default_billing_settings, migrations.RunPython.noop),
    ]
