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


# Only the first two VPA pilot figures are static lesson illustrations. The newer
# learner-facing manuscripts use prose section headings; support both those headings
# and the older scripted progression labels without rewriting the course source.
_VPA_FIGURES = {
    "1.1": (
        (
            ("**Level 1 — Notice (easy):**", "### Begin with the facts"),
            "vpa-m01-l01-stage1-spot-volume-mobile.svg",
            "Candidate candle and its local volume baseline",
        ),
        (
            ("**Level 2 — Compare (guided):**", "### Worked comparison — same colour, different evidence"),
            "vpa-m01-l01-candle-context-compare-mobile.svg",
            "Similar candle shapes in different contexts",
        ),
    ),
}
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
    """Keep the lesson manuscript intact while removing clearly internal blocks.

    The teaching manuscripts use the same Markdown heading level for some
    subheadings inside narration and for the outer lesson sections. Splitting
    every H3 therefore truncates the lesson body on nested case-analysis titles.
    Work directly with the already isolated lesson segment instead.
    """
    lesson_heading = _LESSON_HEADER.match(segment)
    if lesson_heading is None:
        raise CommandError("A VPA lesson segment has no lesson heading.")

    student_markdown = segment[lesson_heading.end():].strip()
    internal_sections = []

    # Remove only explicitly instructor-only/answer sections, preserving the
    # knowledge-check questions in the learner experience.
    internal_heading = re.compile(
        r"^###\s+(?:instructor notes|answer key|model answers?|answer explanations?)\b.*$",
        re.I | re.M,
    )
    matches = list(internal_heading.finditer(student_markdown))
    for match in matches:
        next_heading = re.search(r"^###\s+", student_markdown[match.end():], re.M)
        end = match.end() + next_heading.start() if next_heading else len(student_markdown)
        internal_sections.append(student_markdown[match.start():end].strip())

    for match in reversed(matches):
        next_heading = re.search(r"^###\s+", student_markdown[match.end():], re.M)
        end = match.end() + next_heading.start() if next_heading else len(student_markdown)
        student_markdown = student_markdown[:match.start()] + student_markdown[end:]

    # These production-only metadata lines are not part of the actual lesson.
    student_markdown = re.sub(
        r"(?im)^\*\*(?:beginner checkpoint|target delivered duration):\*\*[^\n]*(?:\n|$)",
        "",
        student_markdown,
    )
    # Keep learner questions visible, but never leak explicitly labelled answers.
    learner_lines = []
    for line in student_markdown.splitlines():
        if re.match(
            r"^\s*(?:[-*]\s*)?(?:\*\*)?(?:answer|correct answer|model answer|expected answer)(?:\*\*)?\s*[:—-]",
            line,
            re.I,
        ):
            internal_sections.append(line.strip())
        else:
            learner_lines.append(line)
    student_markdown = "\n".join(learner_lines)
    # Asset manifest and ChartLab implementation comments are not lesson prose.
    student_markdown = re.sub(r"<!--.*?-->", "", student_markdown, flags=re.S)
    student_markdown = re.sub(r"\n{3,}", "\n\n", student_markdown).strip()

    # The working branch already contains a learner-oriented version of the
    # VPA modules; the feature branch may instead contain longer teaching
    # manuscripts. Preserve either canonical structure rather than assuming a
    # single heading scheme. Native details elements keep existing feedback
    # available without immediately displaying the answer to the learner.
    revealed = []
    learner_lines = []
    for line in student_markdown.splitlines():
        feedback = re.match(r"^\s*\*\*Feedback:\*\*\s*(.+)$", line, re.I)
        if feedback:
            revealed.append(feedback.group(1).strip())
            learner_lines.extend([
                "<details>",
                "<summary>Feedback</summary>",
                "",
                feedback.group(1).strip(),
                "",
                "</details>",
            ])
        else:
            learner_lines.append(line)
    student_markdown = "\n".join(learner_lines).strip()

    has_structure = re.search(r"(?m)^###\s+.+$", student_markdown)
    if not student_markdown or not has_structure or len(student_markdown) < 120:
        found = [heading for heading, _body in h3_sections(segment)]
        raise CommandError(
            "A VPA lesson has no usable learner-facing content. "
            f"Available section headings: {found!r}"
        )
    if revealed:
        internal_sections.append(
            "Feedback content is also rendered as learner-controlled disclosure blocks.\n\n"
            + "\n\n".join(revealed)
        )
    return student_markdown, "\n\n".join(internal_sections)

def estimate_duration(segment):
    match = _DURATION.search(segment)
    if match:
        number = re.search(r"\d+", match.group(1))
        if number:
            return max(1, min(180, int(number.group(0))))
    return 15


def embed_vpa_figures(lesson_number, student_markdown, assets_root, figure_counters):
    """Embed selected, approved static SVG figures at stable teaching anchors."""
    specs = _VPA_FIGURES.get(str(lesson_number), ())
    if not specs:
        return student_markdown, ""

    module_number = int(str(lesson_number).split(".", 1)[0])
    media_notes = []
    for anchors, filename, caption in specs:
        if not (Path(assets_root) / filename).is_file():
            raise CommandError(
                f"Required VPA lesson figure is missing: "
                f"{Path(assets_root) / filename}"
            )

        if isinstance(anchors, str):
            anchors = (anchors,)
        placed = False
        for anchor in anchors:
            pattern = re.compile(rf"(?m)^({re.escape(anchor)}[^\\n]*)$")

            def add_figure(match, filename=filename, caption=caption):
                figure_counters[module_number] = figure_counters.get(module_number, 0) + 1
                figure_number = f"{module_number}.{figure_counters[module_number]}"
                image = (
                    f"![Figure {figure_number} — {caption}]"
                    f"(/static/academy/vpa/{filename})"
                )
                figure_caption = f"*{caption}.*"
                return f"{match.group(1)}\\n\\n{image}\\n\\n{figure_caption}"

            student_markdown, replacements = pattern.subn(
                add_figure, student_markdown, count=1
            )
            if replacements == 1:
                placed = True
                break
        if not placed:
            raise CommandError(
                f"Cannot place VPA figure {filename}: lesson {lesson_number} "
                f"does not contain any supported anchor from {anchors!r}."
            )
        media_notes.append(
            f"Figure {module_number}.{figure_counters[module_number]} uses {filename}. "
            "It is a static explanatory figure, not a submitted activity. The later "
            "continuation/failure outcomes remain excluded until learner-response-gated "
            "reveal is implemented."
        )

    return student_markdown, "\\n".join(media_notes)


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
        figure_counters = {}
        figure_assets_root = (
            repository_root / "course-source" / "volume-price-analysis" / "assets" / "exports"
        )
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
                    learner_body, media_notes = embed_vpa_figures(
                        f"{module_number}.{lesson_position}",
                        learner_body,
                        figure_assets_root,
                        figure_counters,
                    )
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
                    "media_notes": media_notes,
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
                        + (
                            f"\n\nMedia / production notes:\n{item['media_notes']}"
                            if item["media_notes"] else ""
                        )
                    ),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {course.title} with {len(modules)} unpublished modules and "
                f"{len(parsed_lessons)} unpublished lessons. No Plan or CourseOffer was created."
            )
        )
