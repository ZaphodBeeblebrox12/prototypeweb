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
    r"^(?:📊[ \t]*(?:CHART NEEDED:|No chart needed today[^\n]*|Diagram already made:)|✅[ \t]*Diagram already made:).*?(?=\n{2,}|\Z)",
    re.I | re.M | re.S,
)
_FIGURE_MARKER = re.compile(
    r"^(?:📊[ \t]*CHART NEEDED:|✅[ \t]*Diagram already made:)",
    re.I,
)
_CHART_PATH = re.compile(r"charts/(?:generated/)?([A-Za-z0-9_-]+\.png)", re.I)


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


def embed_existing_figures(source, generated_root, static_root, module_number, counters):
    """Replace chart markers only when an exact-named image is ready for Django staticfiles."""
    lines = source.splitlines()
    output = []
    production_notes = []
    index = 0

    while index < len(lines):
        line = lines[index]
        marker = _FIGURE_MARKER.match(line)
        path_match = _CHART_PATH.search(line) if marker else None
        if marker is None or path_match is None:
            output.append(line)
            index += 1
            continue

        block = [line]
        index += 1
        while index < len(lines) and lines[index].strip():
            block.append(lines[index])
            index += 1

        filename = Path(path_match.group(1)).name
        source_image = Path(generated_root) / filename
        static_image = Path(static_root) / filename
        if not source_image.is_file() or not static_image.is_file():
            output.extend(block)
            continue

        counters[module_number] = counters.get(module_number, 0) + 1
        figure_number = f"{module_number}.{counters[module_number]}"
        caption = re.sub(r"^L\d+-\d+-", "", Path(filename).stem, flags=re.I)
        caption = caption.replace("-", " ").strip().capitalize()
        image_url = f"/static/academy/course-images/{filename}"
        output.extend(
            [
                "",
                f"![Figure {figure_number} — {caption}]({image_url})",
                "",
                f"*Figure {figure_number} — {caption}.*",
                "",
            ]
        )
        production_notes.append(
            f"Embedded Figure {figure_number} from {filename}. Source chart marker and production brief:\n\n"
            + "\n".join(block)
        )

    learner_source = re.sub(r"\n{3,}", "\n\n", "\n".join(output)).strip()
    return learner_source, "\n\n".join(production_notes).strip()


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
        figure_counters = {}
        generated_root = source_root / "charts" / "generated"
        static_figure_root = repository_root / "backend" / "static" / "academy" / "course-images"
        source_root_resolved = source_root.resolve()
        for item in lessons:
            relative = Path(str(item.get("source_file", "")))
            source_path = (source_root / relative).resolve()
            if source_root_resolved not in source_path.parents or not source_path.is_file():
                raise CommandError(
                    f"Lesson source is missing or outside the course folder: {relative}"
                )
            source = source_path.read_text(encoding="utf-8")
            source_with_figures, embedded_media_notes = embed_existing_figures(
                source,
                generated_root,
                static_figure_root,
                int(item["level"]),
                figure_counters,
            )
            learner_body, answer_key, media_notes = split_lesson_source(source_with_figures)
            media_notes = "\n\n".join(
                value for value in (media_notes, embedded_media_notes) if value
            )
            if not learner_body:
                raise CommandError(f"Lesson has no learner-facing content: {relative}")
            parsed.append(
                {
                    **item,
                    "source_path": str(relative),
                    "body": learner_body,
                    "answer_key": answer_key,
                    "media_notes": media_notes,
                }
            )

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
                catalogue_role=Course.CatalogueRole.FLAGSHIP,
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
                access_type=Course.AccessType.FREE,
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
                        + (
                            f"\n\nMedia / production notes:\n{item['media_notes']}"
                            if item["media_notes"]
                            else ""
                        )
                    ),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {course.title} with {len(levels)} draft modules and "
                f"{len(parsed)} unpublished lessons. No offer or payment plan was created."
            )
        )
