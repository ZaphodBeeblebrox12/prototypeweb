import json

from django.contrib.auth import get_user_model
from django.test import TestCase
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
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        self.assertEqual(record.status, CourseImport.Status.REVIEW)
        self.assertEqual(record.payload["builder_state"]["title"], "Builder API Course")
        self.assertEqual(record.payload["modules"][0]["lessons"][0]["content_markdown"], "## Notice\n\nDescribe what is visible before drawing a conclusion.")
        self.assertNotIn("correctIndex", record.payload["modules"][0]["lessons"][0]["content_json"])

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
