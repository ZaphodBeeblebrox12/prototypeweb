from django.template.loader import get_template
from django.test import SimpleTestCase


class LessonTemplateParityTests(SimpleTestCase):
    def test_member_lesson_uses_the_approved_preview_layout(self):
        source = get_template("academy/lesson.html").template.source

        self.assertIn("tt-member-learning-preview", source)
        self.assertIn("academy/member-learning-preview.css", source)

    def test_member_video_is_visible_before_the_primary_lesson_content(self):
        source = get_template("academy/lesson.html").template.source

        video_panel = source.index('<section class="tt-member-video-panel"')
        lesson_tabs = source.index(
            '{% if admin_preview %}{% include "academy/partials/lesson_tabs.html"'
        )

        self.assertLess(video_panel, lesson_tabs)
        self.assertIn("data-protected-video", source[video_panel:lesson_tabs])
        self.assertIn("data-video-watermark", source[video_panel:lesson_tabs])
        self.assertIn("data-video-player-status", source[video_panel:lesson_tabs])
