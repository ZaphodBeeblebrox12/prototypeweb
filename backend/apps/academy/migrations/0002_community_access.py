import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="courseoffer",
            name="community_access_days",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Optional included community term, separate from course access. Blank means no community access.",
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
        migrations.AddField(
            model_name="courseentitlement",
            name="community_access_granted_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Set only when the offer includes a separate community entitlement.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="courseentitlement",
            name="community_access_expires_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Separate expiry for included community access; does not change course access.",
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="courseentitlement",
            constraint=models.CheckConstraint(
                check=models.Q(("community_access_expires_at__isnull", True), ("community_access_granted_at__isnull", False), _connector="OR"),
                name="academy_comm_expiry_grant_ck",
            ),
        ),
    ]
