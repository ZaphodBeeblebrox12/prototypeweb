"""Validate or import the source-backed Academy catalogue as unpublished drafts.

This is a small orchestration command for the three courses with canonical
lesson importers. It deliberately creates no commerce Plans or CourseOffers,
does not publish content, and refuses to overwrite existing course records.
"""
from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.academy.models import (
    Course,
    CourseModule,
    CourseOffer,
    Lesson,
    LessonInstructorMaterial,
)


COURSES = (
    ("seed_trading_path", "trading-path", 4, 30),
    ("seed_support_resistance", "support-resistance", 6, 18),
    ("seed_volume_price_analysis", "volume-price-analysis", 6, 30),
)


class Command(BaseCommand):
    help = (
        "Validate all source-backed Academy courses, or import their 78 lessons "
        "as unpublished drafts with --apply."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Create draft records after all source validation passes.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        slugs = [slug for _command, slug, _modules, _lessons in COURSES]

        # Importers are create-only. Fail before doing source work or writing any
        # rows if this catalogue is already present, rather than partially
        # updating editor-reviewed content.
        if apply_changes:
            existing = list(
                Course.objects.filter(slug__in=slugs).values_list("slug", flat=True)
            )
            if existing:
                raise CommandError(
                    "Catalogue import is create-only; these course slugs already "
                    f"exist: {', '.join(sorted(existing))}. No rows were changed."
                )

        captured = StringIO()
        for command_name, _slug, _modules, _lessons in COURSES:
            try:
                call_command(command_name, stdout=captured)
            except CommandError as exc:
                raise CommandError(
                    f"Catalogue preflight failed in {command_name}: {exc}"
                ) from exc

        if not apply_changes:
            self.stdout.write(
                self.style.SUCCESS(
                    "Validated 3 canonical course sources: 16 modules and 78 lessons. "
                    "No database changes made. Re-run with --apply to create drafts."
                )
            )
            return

        # Keep all three course imports in one transaction. If one importer or
        # the post-import checks fails, the complete catalogue import rolls back.
        with transaction.atomic():
            for command_name, _slug, _modules, _lessons in COURSES:
                try:
                    call_command(command_name, apply=True, stdout=captured)
                except CommandError as exc:
                    raise CommandError(
                        f"Catalogue import failed in {command_name}; all catalogue "
                        f"writes are being rolled back: {exc}"
                    ) from exc

            for _command_name, slug, expected_modules, expected_lessons in COURSES:
                course = Course.objects.get(slug=slug)
                modules = list(CourseModule.objects.filter(course=course))
                lessons = list(Lesson.objects.filter(module__course=course))
                material_count = LessonInstructorMaterial.objects.filter(
                    lesson__module__course=course
                ).count()

                valid = (
                    course.status == Course.Status.DRAFT
                    and len(modules) == expected_modules
                    and len(lessons) == expected_lessons
                    and material_count == expected_lessons
                    and all(not module.is_published for module in modules)
                    and all(not lesson.is_published for lesson in lessons)
                    and all(lesson.content_markdown.strip() for lesson in lessons)
                    and not CourseOffer.objects.filter(course=course).exists()
                )
                if not valid:
                    raise CommandError(
                        f"Post-import verification failed for {slug}; all catalogue "
                        "writes are being rolled back."
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "Imported 3 courses as drafts: 16 unpublished modules, 78 "
                "unpublished lessons, 78 separate instructor-material records, "
                "and no commerce offers. Nothing was published or made saleable."
            )
        )
