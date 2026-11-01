from pathlib import Path

from django.conf import settings
from django.template.loader import get_template
from django.test import SimpleTestCase


class LessonTemplateParityTests(SimpleTestCase):
    def test_member_and_every_admin_preview_use_one_lesson_page(self):
        templates_root = Path(settings.BASE_DIR) / "templates" / "academy"
        lesson_page = get_template("academy/lesson.html").template.source
        experience = get_template(
            "academy/partials/lesson_experience.html"
        ).template.source
        course_overview = get_template("academy/course_detail.html").template.source
        views_source = " ".join(
            (Path(settings.BASE_DIR) / "apps" / "academy" / "views.py")
            .read_text(encoding="utf-8")
            .split()
        )

        shared_include = '{% include "academy/partials/lesson_experience.html" %}'
        self.assertIn(shared_include, lesson_page)
        self.assertIn(
            '<header class="tt-course-header tt-course-header--depth">',
            experience,
        )
        self.assertIn('<div class="tt-room-grid">', experience)
        self.assertNotIn(
            '<header class="tt-course-header tt-course-header--depth">',
            lesson_page,
        )
        self.assertNotIn('<div class="tt-room-grid">', lesson_page)
        self.assertNotIn(
            '<header class="tt-course-header tt-course-header--depth">',
            course_overview,
        )
        self.assertNotIn('<div class="tt-room-grid">', course_overview)

        # Member lessons, published admin previews and draft lessons all render lesson.html.
        self.assertIn(
            'return render(request, "academy/lesson.html", preview_context)',
            views_source,
        )
        # Draft course overviews reuse the template for published course overviews.
        self.assertIn(
            'return render(request, "academy/course_detail.html", preview_context)',
            views_source,
        )

        # The deleted duplicate must not silently reappear.
        self.assertFalse(
            (templates_root / "course_import_website_preview.html").exists(),
            "Do not recreate a Course Import-specific page template.",
        )
        static_root = Path(settings.BASE_DIR) / "static" / "academy"
        self.assertFalse((static_root / "course-import-preview.css").exists())
        self.assertFalse((static_root / "member-learning-preview.css").exists())

    def test_only_shared_lesson_partial_owns_the_learning_room_shell(self):
        templates_root = Path(settings.BASE_DIR) / "templates" / "academy"
        experience_path = templates_root / "partials" / "lesson_experience.html"
        owned_markers = (
            '<header class="tt-course-header tt-course-header--depth">',
            '<div class="tt-room-grid">',
        )
        for template_path in templates_root.rglob("*.html"):
            source = template_path.read_text(encoding="utf-8")
            for marker in owned_markers:
                if marker in source:
                    self.assertEqual(
                        template_path,
                        experience_path,
                        f"{template_path.relative_to(templates_root)} "
                        "duplicates lesson layout markup",
                    )

    def test_course_import_overview_uses_its_own_shared_course_page_styles(self):
        course_overview = get_template("academy/course_detail.html").template.source
        css_path = (
            Path(settings.BASE_DIR) / "static" / "academy" / "course-admin-preview.css"
        )
        css = css_path.read_text(encoding="utf-8")

        self.assertIn("course-admin-preview.css", course_overview)
        self.assertNotIn("learning-room.css", course_overview)
        self.assertIn(".main-content:has(> .tt-admin-course-preview)", css)
        self.assertIn("width: min(1600px, 100%)", css)
        self.assertNotIn(".tt-lesson-experience", css)
        self.assertNotIn(".tt-tab-panel", css)

    def test_canonical_header_geometry_is_owned_by_learning_room_css(self):
        css_path = Path(settings.BASE_DIR) / "static" / "academy" / "learning-room.css"
        css = css_path.read_text(encoding="utf-8")

        self.assertIn(".tt-lesson-experience .tt-course-header--depth", css)
        self.assertIn("padding-bottom: 25px;", css)
        self.assertIn("position: absolute;", css)
        self.assertIn("bottom: 0;", css)
        self.assertIn("margin: 0;", css)

    def test_member_and_preview_video_keep_the_same_protected_player_markup(self):
        experience = get_template(
            "academy/partials/lesson_experience.html"
        ).template.source

        video_panel = experience.index('<section class="tt-lesson-video-panel"')
        lesson_tabs = experience.index(
            '{% if admin_preview %}{% include "academy/partials/lesson_tabs.html"'
        )

        self.assertLess(video_panel, lesson_tabs)
        self.assertIn("data-protected-video", experience[video_panel:lesson_tabs])
        self.assertIn("data-video-watermark", experience[video_panel:lesson_tabs])
        self.assertIn("data-video-player-status", experience[video_panel:lesson_tabs])
