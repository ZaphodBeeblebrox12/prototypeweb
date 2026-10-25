"""Demote only obvious published Course Builder starter records."""
from django.db import migrations
from django.db.models import Q


_PLACEHOLDER_TITLES = (
    "New micro-course draft",
    "Untitled course",
    "Untitled micro-course",
)
_PLACEHOLDER_SUMMARIES = (
    "Add a concise course promise here.",
    "A clear, practical description of what learners will study and why it matters.",
    "Describe the learner, what the course covers and what they can practise after completing it.",
)


def demote_published_placeholders(apps, schema_editor):
    Course = apps.get_model("academy", "Course")
    placeholder_copy = Q()
    for title in _PLACEHOLDER_TITLES:
        placeholder_copy |= Q(title__iexact=title)
    for summary in _PLACEHOLDER_SUMMARIES:
        placeholder_copy |= Q(summary__iexact=summary) | Q(description__iexact=summary)
    Course.objects.filter(status="published").filter(placeholder_copy).update(status="draft")


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0009_courseimport_deleted_status"),
    ]

    operations = [
        migrations.RunPython(demote_published_placeholders, migrations.RunPython.noop),
    ]
