from django.db import migrations, models


def preserve_existing_flagship_placements(apps, schema_editor):
    Course = apps.get_model("academy", "Course")
    Course.objects.filter(slug__in=("trading-path", "construct")).update(
        catalogue_role="flagship"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0010_demote_published_placeholder_courses"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="catalogue_role",
            field=models.CharField(
                choices=[
                    ("flagship", "Flagship programme"),
                    ("supporting", "Supporting programme"),
                    ("mini", "Mini-course"),
                    ("hidden", "Not listed on the Courses page"),
                ],
                default="mini",
                help_text="Controls which section of the public Courses page displays this course.",
                max_length=16,
            ),
        ),
        migrations.RunPython(
            preserve_existing_flagship_placements,
            migrations.RunPython.noop,
        ),
    ]
