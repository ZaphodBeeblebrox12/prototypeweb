from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academy", "0019_course_sharing_copy"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="seo_title",
            field=models.CharField(
                blank=True,
                help_text="Optional search title. Leave blank to use the course title.",
                max_length=200,
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="seo_description",
            field=models.CharField(
                blank=True,
                help_text="Optional search description. Leave blank to use the course summary.",
                max_length=320,
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="seo_primary_topic",
            field=models.CharField(
                blank=True,
                help_text="The main search topic this public course overview serves.",
                max_length=160,
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="seo_indexable",
            field=models.BooleanField(
                default=True,
                help_text="Allow indexing when the deployment, publication status and catalogue visibility also permit it.",
            ),
        ),
    ]
