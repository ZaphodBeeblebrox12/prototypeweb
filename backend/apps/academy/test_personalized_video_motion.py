import random

from django.test import SimpleTestCase

from apps.academy.management.commands.process_personalized_videos import (
    _position_expression,
)


class PersonalizedVideoMotionExpressionTests(SimpleTestCase):
    def test_expression_is_compact_for_long_lesson_durations(self):
        # A 12-minute lesson previously generated ~13k-character nested if()
        # expressions that FFmpeg rejected as "Missing ')' or too many args".
        expression = _position_expression(random.Random(1234), interval=4, duration=720)

        self.assertLess(len(expression), 200)
        self.assertIn("sin(", expression)
        self.assertNotIn("if(", expression)

    def test_expression_is_deterministic_for_a_viewer_video_seed(self):
        first = _position_expression(random.Random(1234), 4, 720)
        second = _position_expression(random.Random(1234), 4, 720)
        other_viewer = _position_expression(random.Random(5678), 4, 720)

        self.assertEqual(first, second)
        self.assertNotEqual(first, other_viewer)

    def test_motion_stays_inside_the_visible_frame(self):
        # 0.5 +/- (0.34 + 0.10) leaves at least 6% frame margin on each side.
        expression = _position_expression(random.Random(42), 4, 720)

        self.assertIn("0.34*sin(", expression)
        self.assertIn("0.10*sin(", expression)
