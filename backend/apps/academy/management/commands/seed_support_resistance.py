"""Import Support & Resistance lesson drafts from its canonical production manifest.

This command is intentionally draft-only. It separates marked answers from learner
copy and does not publish lessons, provision ChartLab, create offers, or sell access.
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

_SNR_FIGURES = {
    1: (
        ("1.1", "L01-A-01-clean.svg", "Repeated lower reactions around a broad area (illustrative chart).", "Price revisits a similar lower area in this illustrative sequence; no support boundary is drawn."),
    ),
    2: (
        ("1.2", "L02-A-01-clean.svg", "An upward sequence with pullbacks and higher turns (illustrative chart).", "An illustrative rising sequence with pullbacks and generally higher turning points."),
    ),
    3: (
        ("2.1", "L03-A-01-clean.svg", "A price sequence before major swing points are selected (illustrative chart).", "An illustrative chart with major and minor turns, before any candidate points are selected."),
    ),
    4: (
        ("2.2", "L04-A-01-clean.svg", "Lower reactions before zone boundaries are drawn (illustrative chart).", "Related lower reactions with varied wick lows; no zone boundaries are drawn."),
    ),
    5: (
        ("2.3", "L05-A-01-overmarked.svg", "Candidate areas before reducing chart clutter (illustrative chart).", "An illustrative chart with candidate areas, some overlapping or less relevant."),
    ),
    6: (
        ("3.1", "L06-A-01-clean.svg", "Lower-reaction practice with the boundaries hidden (illustrative chart).", "An illustrative chart with three lower reactions and zone boundaries hidden."),
    ),
    7: (
        ("3.2", "L07-A-01-overmarked.svg", "An overmarked chart before redundant areas are removed (illustrative chart).", "An illustrative chart with multiple candidate zones before editing for readability."),
    ),
    8: (
        ("3.3", "L08-A-01-many-crossings.svg", "Frequent crossings and mixed behaviour near an area (illustrative chart).", "Price crosses and revisits a band frequently in this illustrative example."),
        ("3.4", "L08-A-02-fewer-interpretable.svg", "Fewer visits with clearer contextual reactions (illustrative chart).", "Fewer visits to an area with clearer contextual reactions; this is not a strength score."),
    ),
    15: (
        ("6.1", "L15-A-01-clean.svg", "Price between two contextual areas, with no trade prescribed (illustrative chart).", "Price sits between two candidate reaction areas; no entry or outcome is marked."),
    ),
}

_LESSON_HEADING = re.compile(
    r"^#{1,6}\s+(?:LESSON|Lesson)\s+0?(\d{1,2})\b[^\n]*$",
    re.I | re.M,
)
_H2 = re.compile(r"^##\s+(.+?)\s*$", re.M)
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
_ANSWER_LABEL = re.compile(
    r"^\s*(?:\*\*)?(?:correct(?: answer)?|model answer|suggested answer|expected answer|answer key|reference answer)(?:\*\*)?\s*[:—-]\s*",
    re.I,
)
_ANSWER_HEADING = re.compile(
    r"(?:model answers?|answer key|reference analysis|scoring rubric|scoring guidance|"
    r"acceptable response example|model answer|instructor.only|instructor notes|"
    r"facilitator notes|references and use)",
    re.I,
)
_ANSWER_EXAMPLE_LABEL = re.compile(
    r"^\s*\*\*(?:acceptable response example|model answer|expected response|suggested answer):?\*\*\s*:?\s*$",
    re.I,
)


def embed_snr_figures(lesson_number, module_position, learner_markdown, static_root):
    """Embed only curated, first-view Support & Resistance figures in draft lessons."""
    figures = _SNR_FIGURES.get(int(lesson_number), ())
    if not figures:
        return learner_markdown, ""

    expected_module = int(figures[0][0].split(".", 1)[0])
    if module_position != expected_module:
        raise CommandError(
            f"Support & Resistance Lesson {lesson_number} maps to Module {module_position}, "
            f"but its figure numbering expects Module {expected_module}."
        )

    heading_matches = list(_HEADING.finditer(learner_markdown))
    heading = next(
        (
            match for match in heading_matches
            if "student-facing" in match.group(2).casefold()
        ),
        heading_matches[0] if heading_matches else None,
    )
    if heading is None:
        raise CommandError(
            f"Support & Resistance Lesson {lesson_number} has no heading "
            "for its approved figure."
        )

    blocks = []
    notes = []
    for figure_number, filename, caption, description in figures:
        if not (Path(static_root) / filename).is_file():
            raise CommandError(
                f"Approved Support & Resistance figure is missing: "
                f"{Path(static_root) / filename}"
            )
        blocks.append(
            f"![Figure {figure_number} — {description}]"
            f"(/static/academy/support-resistance/{filename})\n\n*{caption}*"
        )
        notes.append(
            f"Figure {figure_number} uses curated static asset {filename}. It is an "
            "illustrative first-view image only; it does not implement a response-gated "
            "reveal or a ChartLab interaction."
        )

    injected = (
        learner_markdown[:heading.end()]
        + "\n\n"
        + "\n\n".join(blocks)
        + "\n\n"
        + learner_markdown[heading.end():]
    )
    injected = re.sub(r"\n{3,}", "\n\n", injected).strip()
    return injected, "\n".join(notes)


def lesson_segments(script):
    """Return canonical script segments indexed by lesson number."""
    starts = list(_LESSON_HEADING.finditer(script))
    segments = {}
    for index, start in enumerate(starts):
        number = int(start.group(1))
        end = starts[index + 1].start() if index + 1 < len(starts) else len(script)
        if number in segments:
            raise CommandError(f"Canonical script defines Lesson {number} more than once.")
        segments[number] = script[start.start():end].strip()
    return segments


def h2_sections(markdown_text):
    """Return level-two sections as (heading, body) tuples."""
    matches = list(_H2.finditer(markdown_text))
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown_text)
        sections.append((match.group(1).strip(), markdown_text[match.end():end].strip()))
    return sections


def remove_internal_blocks(markdown_text):
    """Remove marked answer/instructor blocks and return them separately."""
    matches = list(_HEADING.finditer(markdown_text))
    removed_ranges = []
    internal = []
    for index, match in enumerate(matches):
        title = match.group(2).strip()
        if not _ANSWER_HEADING.search(title):
            continue
        level = len(match.group(1))
        end = len(markdown_text)
        for following in matches[index + 1:]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        removed_ranges.append((match.start(), end))
        internal.append(markdown_text[match.start():end].strip())

    chars = list(markdown_text)
    for start, end in removed_ranges:
        for pos in range(start, end):
            chars[pos] = "\n" if chars[pos] == "\n" else " "
    text_without_blocks = "".join(chars)

    kept = []
    answer_lines = list(internal)
    lines = text_without_blocks.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if _ANSWER_EXAMPLE_LABEL.match(stripped):
            collected = [line]
            index += 1
            while (
                index < len(lines)
                and lines[index].strip()
                and not _HEADING.match(lines[index])
            ):
                collected.append(lines[index])
                index += 1
            answer_lines.append("\n".join(collected).strip())
            continue

        label_match = _ANSWER_LABEL.match(line)
        inline_match = re.search(
            r"\s+(?:\*\*)?(?:correct(?: answer)?|model answer|suggested answer|expected answer)(?:\*\*)?\s*[:—-]\s*",
            line,
            re.I,
        )
        if label_match:
            collected = [line]
            index += 1
            while index < len(lines) and lines[index].strip() and not _HEADING.match(lines[index]):
                collected.append(lines[index])
                index += 1
            answer_lines.append("\n".join(collected).strip())
            continue
        if inline_match:
            before = line[:inline_match.start()].rstrip()
            after = line[inline_match.start():].strip()
            if before:
                kept.append(before)
            answer_lines.append(after)
            index += 1
            continue

        kept.append(line)
        index += 1

    learner_markdown = re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()
    learner_markdown = re.sub(r"^#\s*TradeThesis.*\n+", "", learner_markdown, flags=re.I | re.M).strip()
    return learner_markdown, "\n\n".join(x for x in answer_lines if x)


def extract_snr_student_body(lesson_number, segment):
    """Extract the intended student script without production-only answer blocks."""
    sections = h2_sections(segment)
    selected = []

    if lesson_number <= 12:
        target = next(
            (
                (heading, body)
                for heading, body in sections
                if re.match(r"^3\.\s+", heading)
                and re.search(r"student-facing|lesson narrative|lesson script", heading, re.I)
            ),
            None,
        )
        if target is None:
            raise CommandError(
                f"Lesson {lesson_number:02d} has no clearly marked Section 3 student script."
            )
        selected = [target]
    elif lesson_number <= 17:
        allowed = (
            "learning outcomes",
            "student-facing opening",
            "core teaching script",
            "expanded reading",
            "worked historical case",
            "guided practice",
            "practice task",
            "knowledge check",
            "misconceptions to address",
            "lesson close",
            "chartlab study",
            "chart reading notes",
        )
        selected = [
            (heading, body)
            for heading, body in sections
            if any(key in heading.casefold() for key in allowed)
            and not _ANSWER_HEADING.search(heading)
        ]
    else:
        for heading, body in sections:
            if re.match(r"^(?:3\.\s+.*learner-facing|4\.\s+student-facing|5\.\s+final knowledge check)", heading, re.I):
                selected.append((heading, body))

    if not selected:
        raise CommandError(f"Lesson {lesson_number:02d} has no extractable student-facing sections.")

    combined = "\n\n".join(f"## {heading}\n\n{body}" for heading, body in selected)
    learner_body, answer_key = remove_internal_blocks(combined)
    if not learner_body.strip():
        raise CommandError(f"Lesson {lesson_number:02d} produced an empty learner body.")
    return learner_body, answer_key


def estimate_duration(segment):
    patterns = (
        r"(?im)^\*\*(?:planned|estimated|intended|target delivered) duration:\*\*\s*([^\n]+)",
        r"(?im)^\*\*(?:duration|estimated duration):\*\*\s*([^\n]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, segment)
        if match:
            number = re.search(r"\d+", match.group(1))
            if number:
                return max(1, min(180, int(number.group(0))))
    # Timed lesson sections frequently end around the 15-minute mark.
    return 15


def build_instructor_notes(item, source_path, manifest_status, extra=""):
    lines = [
        f"Canonical source: {source_path}",
        f"Manifest status: {manifest_status}",
        f"Lesson ID: {item.get('lesson_id', '')}",
        f"Activity ID: {item.get('activity_id', '')}",
        "",
        "Learner goal:",
        str(item.get("learner_goal", "")),
        "",
        "Interaction pattern:",
        str(item.get("interaction_pattern", "")),
        "",
        "Submission requirement:",
        str(item.get("submission_requirement", "")),
        "",
        "Special rules / release dependencies:",
        str(item.get("special_rules", "")),
    ]
    if extra.strip():
        lines.extend(["", "Additional instructor and media notes:", extra.strip()])
    lines.extend([
        "",
        "Imported as a draft only. Confirm lesson media, progressive reveal, assessment behavior, "
        "authentic case dependencies, accessibility, and learner-facing wording before publication.",
    ])
    return "\n".join(lines)


class Command(BaseCommand):
    help = "Validate or create unpublished Support & Resistance draft records from the canonical manifest."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Create draft course/module/lesson records. Without it, validate sources only.",
        )

    def handle(self, *args, **options):
        repository_root = Path(settings.BASE_DIR).parent
        course_root = repository_root / "course-content" / "support-resistance"
        manifest_path = course_root / "production" / "course_content_manifest.json"
        if not manifest_path.is_file():
            raise CommandError(f"Support & Resistance manifest not found: {manifest_path}")

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Cannot read Support & Resistance manifest: {exc}") from exc

        raw_lessons = manifest.get("lessons", [])
        raw_modules = manifest.get("modules", [])
        if len(raw_lessons) != 18 or len(raw_modules) != 6:
            raise CommandError(
                f"Expected 18 lessons in six modules; found {len(raw_lessons)} lessons and "
                f"{len(raw_modules)} modules."
            )

        script_texts = {}
        for item in manifest.get("canonical_scripts", []):
            relative = Path(str(item.get("path", "")))
            script_path = (course_root / relative).resolve()
            if course_root.resolve() not in script_path.parents or not script_path.is_file():
                raise CommandError(f"Canonical lesson script is missing or outside course source: {relative}")
            script_texts[str(relative)] = script_path.read_text(encoding="utf-8")

        module_for_lesson = {}
        for position, module in enumerate(raw_modules, start=1):
            for lesson_id in module.get("lessons", []):
                if lesson_id in module_for_lesson:
                    raise CommandError(f"Lesson {lesson_id} is assigned to multiple modules.")
                module_for_lesson[lesson_id] = (position, module)

        parsed = []
        static_figure_root = repository_root / "backend" / "static" / "academy" / "support-resistance"
        for item in raw_lessons:
            source_rel = str(item.get("canonical_script_path", ""))
            script = script_texts.get(source_rel)
            if script is None:
                raise CommandError(
                    f"Lesson {item.get('lesson_id')} references a script missing from canonical_scripts: {source_rel}"
                )
            number = int(item.get("lesson_number", 0))
            source_segments = lesson_segments(script)
            segment = source_segments.get(number)
            if not segment:
                raise CommandError(f"Cannot locate Lesson {number:02d} in {source_rel}.")
            learner_body, answer_key = extract_snr_student_body(number, segment)
            membership = module_for_lesson.get(item.get("lesson_id"))
            if membership is None:
                raise CommandError(f"Lesson {item.get('lesson_id')} is not assigned to a module.")
            module_position, module = membership
            learner_body, media_notes = embed_snr_figures(
                number, module_position, learner_body, static_figure_root
            )
            parsed.append({
                **item,
                "module_position": module_position,
                "module_title": str(module["title"]),
                "source_path": source_rel,
                "body": learner_body,
                "answer_key": answer_key,
                "media_notes": media_notes,
                "duration_minutes": estimate_duration(segment),
            })

        if len({item["lesson_id"] for item in parsed}) != 18:
            raise CommandError("Lesson IDs in the manifest are not unique.")
        if not options["apply"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Validated {len(parsed)} lesson scripts across {len(raw_modules)} modules. "
                    "No database changes made. Re-run with --apply to create unpublished drafts."
                )
            )
            return

        with transaction.atomic():
            if Course.objects.filter(slug="support-resistance").exists():
                raise CommandError(
                    "A course with slug 'support-resistance' already exists. This importer is create-only "
                    "to avoid overwriting course edits or published content."
                )
            title = manifest.get("title", "TradeThesis — Support & Resistance")
            course = Course.objects.create(
                title=title,
                slug="support-resistance",
                summary=(
                    "Eighteen lessons across six modules: understand, find, draw and evaluate zones, "
                    "read behaviour, examine breakouts and review conditional scenarios."
                ),
                description=(
                    f"{manifest.get('content_principle', '')}\n\n"
                    f"Source status: {manifest.get('status', 'Draft')}. "
                    "This import is unpublished and not approved for release. ChartLab requires the "
                    "agreed sequence (Clear W · Lesson 5, Uneven Lows · Lesson 8, Wider Neckline · "
                    "Lesson 14). Lessons requiring authentic instructor cases remain blocked until "
                    "the original records are supplied and reviewed."
                ),
                status=Course.Status.DRAFT,
                position=20,
            )
            module_objects = {}
            for position, module in enumerate(raw_modules, start=1):
                module_title = str(module["title"])
                module_objects[position] = CourseModule.objects.create(
                    course=course,
                    title=module_title,
                    slug=slugify(module_title),
                    description="Draft module imported from the canonical course manifest.",
                    position=position,
                    is_published=False,
                )

            for item in parsed:
                title = str(item["title"])
                lesson = Lesson.objects.create(
                    module=module_objects[item["module_position"]],
                    title=title,
                    slug=slugify(f"{int(item['lesson_number']):02d}-{title}"),
                    summary=str(item.get("learner_goal", ""))[:360],
                    format=Lesson.Format.READING,
                    content_markdown=item["body"],
                    position=int(item["lesson_number"]),
                    duration_minutes=item["duration_minutes"],
                    is_preview=False,
                    is_published=False,
                    release_day=1,
                )
                LessonInstructorMaterial.objects.create(
                    lesson=lesson,
                    answer_key_markdown=item["answer_key"],
                    instructor_notes=build_instructor_notes(
                        item, item["source_path"], str(manifest.get("status", "Draft")),
                        extra=item["media_notes"],
                    ),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {course.title} with {len(raw_modules)} unpublished modules and "
                f"{len(parsed)} unpublished lessons. No Plan or CourseOffer was created."
            )
        )
