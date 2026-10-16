"""Import the Trading Path content as unpublished Academy records.

The import intentionally creates no commerce Plan or CourseOffer. Review media,
source accuracy, release rules and privacy before changing any publication state.
"""
import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.academy.models import (
    Course,
    CourseModule,
    Lesson,
    LessonInstructorMaterial,
)

_FRONT_MATTER = re.compile(r"\A---[ \t]*\r?\n.*?\r?\n---[ \t]*(?:\r?\n|$)", re.S)
_ANSWER_DETAILS = re.compile(
    r"<details>\s*<summary>[^<]*(?:answer\s*key|answers)[^<]*</summary>.*?</details>",
    re.I | re.S,
)
_ANSWER_LINES = re.compile(r"^Answers?:[^\n]*(?:\n(?!#{1,6}\s).*)*", re.I | re.M)
_CHART_NOTES = re.compile(
    r"^📊[ \t]*(?:CHART NEEDED:|No chart needed today[^\n]*|Diagram already made:).*?(?=\n{2,}|\Z)",
    re.I | re.M | re.S,
)


def split_lesson_source(source):
    """Return student-facing Markdown, answer-key Markdown and media notes."""
    body = _FRONT_MATTER.sub("", source, count=1).strip()
    answers = []
    notes = []

    def collect(pattern, content, target):
        def take(match):
            target.append(match.group(0).strip())
            return "\n\n"
        return pattern.sub(take, content)

    body = collect(_ANSWER_DETAILS, body, answers)
    body = collect(_ANSWER_LINES, body, answers)
    body = collect(_CHART_NOTES, body, notes)
    body = re.sub(r"^#\s+Day\s+\d+\s+[—–-].*\n+", "", body, count=1, flags=re.M)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body, "\n\n".join(answers).strip(), "\n\n".join(notes).strip()


def lesson_summary(body, fallback):
    match = re.search(
        r"^##\s+What you'll learn\s*\n(.*?)(?=^##\s|\Z)",
        body,
        re.I | re.M | re.S,
    )
    if match:
        bullets = re.findall(r"^\s*[-*]\s+(.+)$", match.group(1), re.M)
        if bullets:
            return " ".join(item.strip() for item in bullets[:3])[:360]
    return fallback[:360]


def duration_minutes(value):
    match = re.search(r"\d+", str(value))
    return max(1, int(match.group(0))) if match else 10


class Command(BaseCommand):
    help = "Validate or import all 30 Trading Path lessons as unpublished Academy drafts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Create draft records. Without this flag the command only validates source files.",
        )

    def handle(self, *args, **options):
        repository_root = Path(settings.BASE_DIR).parent
        manifest_path = repository_root / "course-integration" / "curriculum.json"
        source_root = repository_root / "course-source" / "starter-drip-course"

        if not manifest_path.is_file():
            raise CommandError(f"Trading Path curriculum manifest not found: {manifest_path}")

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Cannot read Trading Path curriculum manifest: {exc}") from exc

        lessons = manifest.get("lessons", [])
        levels = manifest.get("levels", [])
        if len(lessons) != 30 or len(levels) != 4:
            raise CommandError(
                f"Expected 30 lessons in four levels; found {len(lessons)} lessons and {len(levels)} levels."
            )

        parsed = []
        source_root_resolved = source_root.resolve()
        for item in lessons:
            relative = Path(str(item.get("source_file", "")))
            source_path = (source_root / relative).resolve()
            if source_root_resolved not in source_path.parents or not source_path.is_file():
                raise CommandError(f"Lesson source is missing or outside the course folder: {relative}")
            source = source_path.read_text(encoding="utf-8")
            learner_body, answer_key, media_notes = split_lesson_source(source)
            if not learner_body:
                raise CommandError(f"Lesson has no learner-facing content: {relative}")
            parsed.append({
                **item,
                "source_path": str(relative),
                "body": learner_body,
                "answer_key": answer_key,
                "media_notes": media_notes,
            })

        by_level = {int(level["level"]): level for level in levels}
        if any(int(item.get("level", 0)) not in by_level for item in parsed):
            raise CommandError("A lesson refers to a level that is missing from the manifest.")

        if not options["apply"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Validated {len(parsed)} lesson sources across {len(levels)} levels. "
                    "No database changes made. Re-run with --apply to create draft records."
                )
            )
            return

        with transaction.atomic():
            if Course.objects.filter(slug="trading-path").exists():
                raise CommandError(
                    "A course with slug 'trading-path' already exists. This importer is create-only "
                    "to avoid overwriting draft edits or published content."
                )

            product = manifest.get("product", {})
            course = Course.objects.create(
                title=product.get("name", "The TradeThesis Trading Path"),
                slug="trading-path",
                summary=(
                    "Thirty lessons across foundations, technical tools, trading mechanics and "
                    "psychology. Imported as a draft for content and delivery review."
                ),
                description=(
                    "Draft content import from the Trading Path source package. This command does "
                    "not configure pricing, enrolment, timed release, Telegram delivery, resources "
                    "or publishing. Review the lesson content and media before release."
                ),
                status=Course.Status.DRAFT,
                position=10,
            )

            module_by_level = {}
            for level in levels:
                number = int(level["level"])
                title = str(level["name"])
                module_by_level[number] = CourseModule.objects.create(
                    course=course,
                    title=title,
                    slug=slugify(title),
                    description=f"Days {level['first_day']}–{level['last_day']}. Draft import.",
                    position=number,
                    is_published=False,
                )

            for item in parsed:
                level_number = int(item["level"])
                title = str(item["title"])
                lesson = Lesson.objects.create(
                    module=module_by_level[level_number],
                    title=title,
                    slug=slugify(title),
                    summary=lesson_summary(item["body"], f"Day {item['day']} of the Trading Path."),
                    format=Lesson.Format.READING,
                    content_markdown=item["body"],
                    position=int(item["day"]),
                    duration_minutes=duration_minutes(item.get("duration")),
                    is_preview=False,
                    is_published=False,
                    release_day=int(item["day"]),
                )
                LessonInstructorMaterial.objects.create(
                    lesson=lesson,
                    answer_key_markdown=item["answer_key"],
                    instructor_notes=(
                        f"Imported from {item['source_path']}. Verify lesson duration and media."
                        + (f"\n\nMedia / production notes:\n{item['media_notes']}" if item["media_notes"] else "")
                    ),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {course.title} with {len(levels)} draft modules and "
                f"{len(parsed)} unpublished lessons. No offer or payment plan was created."
            )
        )
