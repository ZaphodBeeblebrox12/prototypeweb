"""Import Volume Price Analysis manuscripts as unpublished Academy drafts.

The source is still a teaching manuscript. This command keeps knowledge checks
out of learner copy, creates no price/offer, and does not publish any content.
"""
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

_MODULE_FILES = (
    "MODULE_01_READ_THE_MARKET.md",
    "MODULE_02_BUYING_SELLING_PRESSURE.md",
    "MODULE_03_TRADE_SETUPS.md",
    "MODULE_04_FALSE_BREAKOUTS.md",
    "MODULE_05_VOLUME_PROFILE.md",
    "MODULE_06_COMPLETE_TRADE_PLAN.md",
)
_LESSON_HEADER = re.compile(
    r"^##\s+Lesson\s+(\d+)\.(\d+)\s+[—–-]\s*(.+?)\s*$",
    re.I | re.M,
)
_H3 = re.compile(r"^###\s+(.+?)\s*$", re.M)
_DURATION = re.compile(
    r"(?im)^\*\*(?:target delivered duration|planned duration|estimated duration|intended duration):\*\*\s*([^\n]+)"
)
_SELECTED_SECTIONS = (
    "learning objective",
    "outline and timing",
    "full narration script",
    "extended spoken case analysis",
    "learner progression",
)
_INTERNAL_SECTIONS = ("knowledge check", "answer key", "instructor notes", "model answer")


def lesson_segments(module_markdown):
    """Yield lesson number, sequence, title, and manuscript section."""
    matches = list(_LESSON_HEADER.finditer(module_markdown))
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(module_markdown)
        segment = module_markdown[match.start():end].strip()
        segment = re.split(r"^##\s+Module\s+\d+\s+instructor notes\b", segment, maxsplit=1, flags=re.I | re.M)[0].strip()
        result.append((int(match.group(1)), int(match.group(2)), match.group(3).strip(), segment))
    return result


def h3_sections(markdown_text):
    matches = list(_H3.finditer(markdown_text))
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown_text)
        sections.append((match.group(1).strip(), markdown_text[match.end():end].strip()))
    return sections


def extract_vpa_student_body(segment):
    """Keep the objective, narration and practice progression; isolate knowledge checks."""
    sections = h3_sections(segment)
    student_sections = []
    internal_sections = []
    for heading, body in sections:
        lowered = heading.casefold()
        if any(term in lowered for term in _INTERNAL_SECTIONS):
            internal_sections.append(f"### {heading}\n\n{body}")
            continue
        if any(term in lowered for term in _SELECTED_SECTIONS):
            student_sections.append((heading, body))

    if not student_sections:
        raise CommandError("A VPA lesson has no extractable teaching narration.")

    student_markdown = "\n\n".join(
        f"### {heading}\n\n{body}" for heading, body in student_sections if body
    )
    student_markdown = re.sub(r"\n{3,}", "\n\n", student_markdown).strip()
    if not student_markdown:
        raise CommandError("A VPA lesson produced an empty learner manuscript.")
    return student_markdown, "\n\n".join(internal_sections)


def estimate_duration(segment):
    match = _DURATION.search(segment)
    if match:
        number = re.search(r"\d+", match.group(1))
        if number:
            return max(1, min(180, int(number.group(0))))
    return 15


class Command(BaseCommand):
    help = "Validate or create unpublished Volume Price Analysis course drafts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Create draft records. Without it, validate all module manuscripts only.",
        )

    def handle(self, *args, **options):
        repository_root = Path(settings.BASE_DIR).parent
        lessons_root = repository_root / "course-source" / "volume-price-analysis" / "lessons"
        if not lessons_root.is_dir():
            raise CommandError(f"Volume Price Analysis source folder not found: {lessons_root}")

        modules = []
        parsed_lessons = []
        for position, filename in enumerate(_MODULE_FILES, start=1):
            source_path = (lessons_root / filename).resolve()
            if lessons_root.resolve() not in source_path.parents or not source_path.is_file():
                raise CommandError(f"VPA module manuscript missing: {filename}")
            source = source_path.read_text(encoding="utf-8")
            title_match = re.search(r"(?im)^#\s+Module\s+\d+\s+[—–-]\s*(.+?)\s*$", source)
            if not title_match:
                raise CommandError(f"Cannot read module title from {filename}.")
            module_title = title_match.group(1).strip()
            modules.append({
                "position": position,
                "title": module_title,
                "slug": slugify(module_title),
                "source_path": str(source_path.relative_to(repository_root)),
            })

            lesson_items = lesson_segments(source)
            if len(lesson_items) != 5:
                raise CommandError(
                    f"{filename} should contain five lessons; found {len(lesson_items)}."
                )
            for module_number, lesson_position, title, segment in lesson_items:
                if module_number != position:
                    raise CommandError(
                        f"{filename} contains Lesson {module_number}.{lesson_position}, "
                        f"but is mapped to module {position}."
                    )
                try:
                    learner_body, internal_material = extract_vpa_student_body(segment)
                except CommandError as exc:
                    found_sections = [heading for heading, _body in h3_sections(segment)]
                    raise CommandError(
                        f"{filename}, Lesson {module_number}.{lesson_position} ({title}): {exc} "
                        f"Available section headings: {found_sections!r}"
                    ) from exc
                parsed_lessons.append({
                    "module_position": position,
                    "lesson_position": lesson_position,
                    "lesson_number": f"{module_number}.{lesson_position}",
                    "title": title,
                    "segment": segment,
                    "body": learner_body,
                    "internal_material": internal_material,
                    "duration_minutes": estimate_duration(segment),
                    "source_path": str(source_path.relative_to(repository_root)),
                })

        if len(parsed_lessons) != 30:
            raise CommandError(
                f"Expected 30 VPA lessons in six modules; found {len(parsed_lessons)}."
            )
        if not options["apply"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Validated {len(parsed_lessons)} lessons across {len(modules)} VPA modules. "
                    "No database changes made. Re-run with --apply to create unpublished drafts."
                )
            )
            return

        with transaction.atomic():
            if Course.objects.filter(slug="volume-price-analysis").exists():
                raise CommandError(
                    "A course with slug 'volume-price-analysis' already exists. This importer is "
                    "create-only so it will not overwrite draft edits or published content."
                )
            course = Course.objects.create(
                title="Volume Price Analysis",
                slug="volume-price-analysis",
                summary=(
                    "Thirty draft lessons across six modules, from reading activity behind candles "
                    "to building a conditional trade plan."
                ),
                description=(
                    "Imported from the Volume Price Analysis teaching manuscripts as an unpublished draft. "
                    "The content requires editorial review and any promised chart assets/interactions must "
                    "be checked before release. No checkout offer or community access is configured."
                ),
                status=Course.Status.DRAFT,
                position=30,
            )

            module_objects = {}
            for module in modules:
                module_objects[module["position"]] = CourseModule.objects.create(
                    course=course,
                    title=module["title"],
                    slug=module["slug"],
                    description=(
                        f"Unpublished teaching manuscript. Canonical source: {module['source_path']}"
                    ),
                    position=module["position"],
                    is_published=False,
                )

            for item in parsed_lessons:
                number = item["lesson_number"]
                lesson = Lesson.objects.create(
                    module=module_objects[item["module_position"]],
                    title=item["title"],
                    slug=slugify(f"lesson-{number}-{item['title']}"),
                    summary="Draft teaching manuscript imported for review; not published.",
                    format=Lesson.Format.READING,
                    content_markdown=item["body"],
                    position=item["lesson_position"],
                    duration_minutes=item["duration_minutes"],
                    is_preview=False,
                    is_published=False,
                    release_day=1,
                )
                LessonInstructorMaterial.objects.create(
                    lesson=lesson,
                    answer_key_markdown=item["internal_material"],
                    instructor_notes=(
                        f"Canonical source: {item['source_path']}\n"
                        f"Lesson number: {number}\n\n"
                        "Knowledge-check material is stored separately from learner narration. "
                        "Confirm answer-feedback design, chart media and timing before publication."
                    ),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {course.title} with {len(modules)} unpublished modules and "
                f"{len(parsed_lessons)} unpublished lessons. No Plan or CourseOffer was created."
            )
        )
