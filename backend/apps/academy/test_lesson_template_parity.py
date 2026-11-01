from django.template.loader import get_template
from django.test import SimpleTestCase


class LessonTemplateParityTests(SimpleTestCase):
    def test_member_lesson_uses_the_approved_preview_layout(self):
        source = get_template("academy/lesson.html").template.source

        self.assertIn("tt-member-learning-preview", source)
        self.assertIn("academy/member-learning-preview.css", source)

    def test_member_video_is_available_below_the_primary_lesson_content(self):
        source = get_template("academy/lesson.html").template.source

        lesson_tabs = source.index(
            '{% if admin_preview %}{% include "academy/partials/lesson_tabs.html"'
        )
        video_disclosure = source.index(
            '<details class="tt-lesson-video-disclosure">'
        )

        self.assertLess(lesson_tabs, video_disclosure)
        self.assertIn("data-protected-video", source[video_disclosure:])
        self.assertIn("data-video-watermark", source[video_disclosure:])
        self.assertIn("data-video-player-status", source[video_disclosure:])
