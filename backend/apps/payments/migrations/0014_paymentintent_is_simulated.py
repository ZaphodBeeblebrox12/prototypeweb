from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0013_simulator_payment_provider"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentintent",
            name="is_simulated",
            field=models.BooleanField(
                default=False,
                help_text="Staging-only payment simulation. No money was collected.",
            ),
        ),
    ]
