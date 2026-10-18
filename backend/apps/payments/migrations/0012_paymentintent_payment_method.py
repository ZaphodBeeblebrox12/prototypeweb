# Store the normalized, provider-reported payment instrument for each payment.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0011_creator_billing_foundation"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentintent",
            name="payment_method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("card", "Card"),
                    ("upi", "UPI"),
                    ("netbanking", "Net banking"),
                    ("wallet", "Wallet"),
                    ("emi", "EMI / cardless EMI"),
                    ("pay_later", "Pay later"),
                    ("bank_transfer", "Bank transfer"),
                    ("bank_debit", "Bank debit"),
                    ("bank_redirect", "Bank redirect"),
                    ("cash", "Cash"),
                    ("other", "Other"),
                ],
                default="",
                help_text="Verified payment instrument type from the provider; blank means not reported.",
                max_length=24,
            ),
        ),
    ]
