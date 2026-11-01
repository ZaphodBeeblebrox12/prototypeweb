from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0012_paymentintent_payment_method"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paymentintent",
            name="provider",
            field=models.CharField(
                choices=[
                    ("stripe", _("Stripe")),
                    ("razorpay", _("Razorpay")),
                ],
                help_text=_("Payment provider"),
                max_length=20,
            ),
        ),
    ]
