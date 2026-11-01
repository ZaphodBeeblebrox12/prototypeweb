from django.db import migrations, models


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
                    ("stripe", "Stripe"),
                    ("razorpay", "Razorpay"),
                    ("simulator", "Staging simulator — no money collected"),
                ],
                help_text="Payment provider",
                max_length=20,
            ),
        ),
    ]
