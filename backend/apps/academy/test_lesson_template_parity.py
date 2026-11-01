from pathlib import Path

from django.conf import settings
from django.template.loader import get_template
from django.test import SimpleTestCase


class LessonTemplateParityTests(SimpleTestCase):
    def test_all_lesson_routes_use_one_canonical_experience_template(self):
        member_template = get_template("academy/lesson.html").template.source
        import_template = get_template(
            "academy/course_import_website_preview.html"
        ).template.source
        experience = get_template(
            "academy/partials/lesson_experience.html"
        ).template.source

        include = 'include "academy/partials/lesson_experience.html"'
        self.assertIn(include, member_template)
        self.assertIn(include, import_template)
        self.assertIn('<header class="tt-course-header tt-course-header--depth">', experience)
        self.assertIn('<div class="tt-room-grid">', experience)
        self.assertNotIn('<header class="tt-course-header tt-course-header--depth">', member_template)
        self.assertNotIn('<header class="tt-course-header tt-course-header--depth">', import_template)

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
