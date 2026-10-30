from django.db import migrations


def mark_trading_path_free(apps, schema_editor):
    Course = apps.get_model("academy", "Course")
    CourseOffer = apps.get_model("academy", "CourseOffer")
    PlanPrice = apps.get_model("subscriptions", "PlanPrice")
    GeoPlanPrice = apps.get_model("subscriptions", "GeoPlanPrice")

    course = Course.objects.filter(slug="trading-path").first()
    if course is None:
        return

    course.access_type = "free"
    course.save(update_fields=["access_type"])

    # Retire individual purchase offers and prices for this course. Do not
    # delete payment intents, receipts, entitlements or historical records.
    plan_ids = list(
        CourseOffer.objects.filter(course_id=course.pk).values_list("plan_id", flat=True)
    )
    CourseOffer.objects.filter(course_id=course.pk).update(is_active=False)
    if plan_ids:
        PlanPrice.objects.filter(
            plan_id__in=plan_ids,
            interval="one_time",
        ).update(is_active=False)
        GeoPlanPrice.objects.filter(
            plan_id__in=plan_ids,
            interval="one_time",
        ).update(is_active=False)


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0013_course_access_policy_and_plan_course_access"),
    ]

    operations = [
        migrations.RunPython(mark_trading_path_free, migrations.RunPython.noop),
    ]
