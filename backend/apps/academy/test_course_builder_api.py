import base64
import json
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Course, CourseImport, CourseModule, Lesson


User = get_user_model()


class CourseBuilderApiTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="course-author",
            password="test-password",
            role="admin",
        )
        self.client.force_login(self.admin)

    def draft_payload(self, slug="builder-api-course"):
        return {
            "course": {
                "id": "course-local-1",
                "title": "Builder API Course",
                "slug": slug,
                "summary": "A practical course summary.",
                "description": "Course description.",
                "category": "Chart reading",
                "level": "Intermediate",
                "duration": "Self-paced",
                "price": "",
                "status": "draft",
                "outcomes": ["Describe evidence before interpreting it."],
                "modules": [{
                    "id": "module-local-1",
                    "title": "Module 01 — Foundations",
                    "description": "Start with observable evidence.",
                    "lessons": [{
                        "id": "lesson-local-1",
                        "title": "Lesson 1.1 — First principles",
                        "summary": "Separate evidence from interpretation.",
                        "format": "reading",
                        "minutes": 12,
                        "videoUrl": "https://media.example.test/lesson.mp4",
                        "notebook": {"title": "A useful notebook", "prompts": [{"label": "Observe", "text": "What evidence is visible?"}]},
                        "content": "## Notice\n\nDescribe what is visible before drawing a conclusion.",
                        "questions": [{
                            "id": "question-local-1",
                            "prompt": "What should you identify first?",
                            "options": ["Visible evidence", "A prediction", "A target"],
                            "correctIndex": 0,
                            "explanation": "Start with what can be observed.",
                        }],
                        "images": [],
                        "image": None,
                        "relatedCourseIds": [],
                    }],
                }],
            },
            "mode": "save",
        }

    def test_admin_can_save_shared_draft(self):
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload()),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()["ok"])
        self.assertIsNone(response.json()["github_source_synced"])
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        self.assertEqual(record.status, CourseImport.Status.DRAFT)
        self.assertEqual(record.payload["builder_state"]["title"], "Builder API Course")
        self.assertEqual(record.payload["modules"][0]["lessons"][0]["content_markdown"], "## Notice\n\nDescribe what is visible before drawing a conclusion.")
        saved_lesson = record.payload["modules"][0]["lessons"][0]
        self.assertEqual(saved_lesson["content_json"]["video_url"], "https://media.example.test/lesson.mp4")
        self.assertEqual(saved_lesson["content_json"]["notebook"]["title"], "A useful notebook")
        self.assertEqual(record.payload["course"]["learning_outcomes"], ["Describe evidence before interpreting it."])
        self.assertNotIn("correctIndex", saved_lesson["content_json"])

    @override_settings(
        ACADEMY_GITHUB_ASSET_REPOSITORY="ZaphodBeeblebrox12/prototypeweb",
        ACADEMY_GITHUB_ASSET_TOKEN="test-token",
        ACADEMY_GITHUB_ASSET_BRANCH="my-new-branch",
    )
    @patch("apps.academy.course_builder_api.requests.put")
    @patch("apps.academy.course_builder_api.requests.get")
    def test_explicit_save_syncs_source_snapshot_to_existing_repo(self, github_get, github_put):
        github_get.return_value = Mock(status_code=404)
        github_put.return_value = Mock(status_code=201)
        payload = self.draft_payload("github-source-course")
        payload["sync_source"] = True

        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()["github_source_synced"])
        self.assertIn(
            "/course-source/builder-drafts/github-source-course.json",
            github_put.call_args.args[0],
        )
        saved_json = json.loads(base64.b64decode(github_put.call_args.kwargs["json"]["content"]))
        self.assertEqual(
            saved_json["modules"][0]["lessons"][0]["content_markdown"],
            "## Notice\n\nDescribe what is visible before drawing a conclusion.",
        )
        self.assertEqual(github_put.call_args.kwargs["json"]["branch"], "my-new-branch")

    def test_published_quiz_keeps_answer_key_private(self):
        from .importing import publish_course_import
        from .models import LessonInstructorMaterial

        payload = self.draft_payload("private-quiz-course")
        payload["mode"] = "submit"
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        course = publish_course_import(record, user=self.admin)
        self.assertEqual(course.learning_outcomes, ["Describe evidence before interpreting it."])
        self.assertEqual(course.category, "Chart reading")
        lesson = Lesson.objects.get(module__course=course)
        self.assertEqual(lesson.content_json["video_url"], "https://media.example.test/lesson.mp4")
        self.assertEqual(lesson.content_json["notebook"]["prompts"][0]["label"], "Observe")

        self.assertEqual(lesson.content_json["questions"][0]["options"][0], "Visible evidence")
        self.assertNotIn("correctIndex", json.dumps(lesson.content_json))
        self.assertNotIn("explanation", json.dumps(lesson.content_json))
        instructor = LessonInstructorMaterial.objects.get(lesson=lesson)
        self.assertEqual(instructor.rubric_json["questions"][0]["correctIndex"], 0)
        self.assertIn("Start with what can be observed.", instructor.answer_key_markdown)

    def test_related_course_uses_published_course_uuid(self):
        related = Course.objects.create(
            title="Related published course",
            slug="related-published-course",
            status=Course.Status.PUBLISHED,
        )
        related_module = CourseModule.objects.create(
            course=related, title="Related module", slug="related-module",
            position=1, is_published=True,
        )
        Lesson.objects.create(
            module=related_module, title="Related lesson", slug="related-lesson",
            position=1, is_published=True, content_markdown="A related lesson.",
        )
        payload = self.draft_payload("course-with-related-reference")
        payload["course"]["modules"][0]["lessons"][0]["relatedCourseIds"] = [str(related.pk)]
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        saved = record.payload["modules"][0]["lessons"][0]["content_json"]["related_course_ids"]
        self.assertEqual(saved, [str(related.pk)])

    def test_notebook_reflections_are_saved_to_learner_progress(self):
        from .models import LessonProgress

        course = Course.objects.create(
            title="Notebook course", slug="notebook-course",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course, title="Module One", slug="module-one",
            position=1, is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module, title="Lesson One", slug="lesson-one",
            position=1, is_preview=True, is_published=True,
            content_json={"notebook": {"title": "Notebook", "prompts": [
                {"label": "Observe", "text": "What is visible?"}
            ]}},
        )
        response = self.client.post(
            reverse("academy:lesson-notebook-submit", args=[lesson.pk]),
            data={"prompt_0": "Price held the prior support zone."},
        )
        self.assertEqual(response.status_code, 200, response.content)
        progress = LessonProgress.objects.get(user=self.admin, lesson=lesson)
        self.assertEqual(
            progress.response_json["notebook_responses"],
            ["Price held the prior support zone."],
        )

    def test_course_builder_is_not_available_to_regular_staff(self):
        staff = User.objects.create_user(
            username="ordinary-staff",
            password="test-password",
            role="staff",
        )
        self.client.force_login(staff)
        response = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(response.status_code, 403)

    def test_public_catalogue_includes_published_courses_only(self):
        published = Course.objects.create(
            title="Published API Course",
            slug="published-api-course",
            summary="A published course.",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=published, title="Module One", slug="module-one",
            position=1, is_published=True,
        )
        Lesson.objects.create(
            module=module, title="Lesson One", slug="lesson-one",
            position=1, content_markdown="A safe lesson body.",
            is_published=True,
        )
        Course.objects.create(
            title="Private Draft Course",
            slug="private-draft-course",
            status=Course.Status.DRAFT,
        )
        self.client.logout()
        response = self.client.get(reverse("academy_public_catalogue"))
        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.json()["courses"]]
        self.assertIn("Published API Course", titles)
        self.assertNotIn("Private Draft Course", titles)
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
