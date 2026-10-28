from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0012_google_drive_support_attachment_folder"),
        ("subscriptions", "0019_alter_geoplanprice_interval_alter_planprice_interval"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="access_type",
            field=models.CharField(
                choices=[
                    ("free", "Free course"),
                    ("membership", "Included in free membership"),
                    ("paid", "Paid individual purchase"),
                    ("mixed", "Free membership or individual purchase"),
                ],
                default="paid",
                help_text=(
                    "Controls learner access. Existing courses retain paid-offer behaviour unless "
                    "an administrator explicitly changes this setting."
                ),
                max_length=16,
            ),
        ),
        migrations.CreateModel(
            name="PlanCourseAccess",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("course", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="plan_access",
                    to="academy.course",
                )),
                ("plan", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="academy_course_access",
                    to="subscriptions.plan",
                )),
            ],
            options={
                "ordering": ["course__position", "course__title"],
                "constraints": [
                    models.UniqueConstraint(fields=("plan", "course"), name="academy_plan_course_access_uq")
                ],
                "indexes": [
                    models.Index(fields=["course", "is_active"], name="academy_plan_access_course_idx")
                ],
            },
        ),
    ]
