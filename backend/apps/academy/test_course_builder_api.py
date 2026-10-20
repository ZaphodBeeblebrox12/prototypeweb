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
        self.assertEqual(
            response.json()["website_preview_url"],
            reverse("academy:course-import-preview", args=[record.pk]),
        )
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
        github_put.return_value.json.return_value = {
            "content": {"sha": "blob-sha"}, "commit": {"sha": "commit-sha"}
        }
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
        payload["sync_source"] = False
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

    def test_builder_persists_stable_inline_lesson_reference_ids(self):
        destination = Course.objects.create(
            title="Volume and Price Analysis",
            slug="volume-price-analysis",
            summary="Read participation alongside price.",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=destination, title="Volume context", slug="volume-context",
            position=1, is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module, title="Read relative volume", slug="read-relative-volume",
            position=1, is_published=True, is_preview=True,
            content_markdown="## Compare volume\n\nPrivate destination body is not copied.",
        )
        payload = self.draft_payload("course-with-inline-lesson-reference")
        payload["course"]["modules"][0]["lessons"][0]["content"] += (
            f"\n\n[[lesson:{lesson.pk}]]"
        )
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        saved_lesson = record.payload["modules"][0]["lessons"][0]
        self.assertEqual(
            saved_lesson["content_json"]["lesson_reference_ids"],
            [str(lesson.pk)],
        )
        self.assertNotIn("Private destination body", json.dumps(saved_lesson))

    def test_builder_catalogue_includes_only_published_lesson_destinations(self):
        course = Course.objects.create(
            title="Volume Profile", slug="volume-profile",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course, title="Value areas", slug="value-areas",
            position=1, is_published=True,
        )
        Lesson.objects.create(
            module=module, title="Read the value area", slug="read-value-area",
            summary="Understand value migration and acceptance.",
            content_markdown="## Value area\n\nVolume profile helps describe acceptance.",
            position=1, is_published=True,
        )
        Lesson.objects.create(
            module=module, title="Unpublished draft lesson", slug="draft-lesson",
            position=2, is_published=False,
        )
        response = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(response.status_code, 200, response.content)
        references = response.json()["lesson_references"]
        self.assertEqual([item["title"] for item in references], ["Read the value area"])
        self.assertIn("Value area", references[0]["topics"])

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

    def test_builder_preserves_inline_figure_metadata_with_stable_asset_id(self):
        from .course_builder_api import _build_import_payload

        state = self.draft_payload("builder-figure-contract")["course"]
        lesson = state["modules"][0]["lessons"][0]
        image_id = "builder-image-01"
        caption = "Compare one setting at a time before making a judgement."
        lesson["content"] = (
            "Text before the figure.\n\n"
            f"![Band comparison](asset://{image_id})\n\n"
            "Text after the figure."
        )
        lesson["images"] = [{
            "id": image_id,
            "name": "band-comparison.png",
            "title": "What changing the settings changes",
            "alt": "Three cards compare shorter, baseline and longer Bollinger Band windows.",
            "caption": caption,
            "data": "data:image/png;base64," + base64.b64encode(b"fake image bytes").decode("ascii"),
        }]
        lesson["image"] = lesson["images"][0]

        imported, image_sources = _build_import_payload(state, "builder-figure-contract")
        saved_lesson = imported["modules"][0]["lessons"][0]
        figure_map = saved_lesson["content_json"]["figures"]
        self.assertEqual(len(figure_map), 1)
        stable_id, metadata = next(iter(figure_map.items()))
        self.assertEqual(metadata["title"], "What changing the settings changes")
        self.assertEqual(metadata["alt"], "Three cards compare shorter, baseline and longer Bollinger Band windows.")
        self.assertEqual(metadata["caption"], caption)
        self.assertIn(f"asset://{stable_id}", saved_lesson["content_markdown"])
        self.assertIn(stable_id, saved_lesson["content_json"]["asset_ids"])
        self.assertNotIn(caption, saved_lesson["content_markdown"])
        self.assertIn("Text before the figure.", saved_lesson["content_markdown"])
        self.assertIn("Text after the figure.", saved_lesson["content_markdown"])
        self.assertIn("builder/builder-image-01", image_sources)

    def test_builder_persists_native_comparison_figures_by_stable_token(self):
        from .course_builder_api import _build_import_payload

        state = self.draft_payload("builder-native-figure")["course"]
        lesson = state["modules"][0]["lessons"][0]
        figure_id = "figure-block-01"
        source = (
            "Text before the comparison.\n\n"
            f"[[teaching-figure:{figure_id}]]\n\n"
            "Text after the comparison."
        )
        lesson["content"] = source
        lesson["teachingFigures"] = [{
            "id": figure_id,
            "type": "comparison-cards",
            "title": "What changing the settings changes",
            "cards": [
                {"kicker": "SHORTER WINDOW", "title": "More responsive", "body": "Reacts to fewer recent bars."},
                {"kicker": "20 PERIODS · 2 DEVIATIONS", "title": "Common baseline", "body": "A reference, not a law."},
                {"kicker": "LONGER WINDOW", "title": "More smoothed", "body": "Usually reacts more slowly."},
            ],
            "note": "Compare one setting at a time.",
        }]

        imported, image_sources = _build_import_payload(state, "builder-native-figure")
        saved_lesson = imported["modules"][0]["lessons"][0]
        self.assertEqual(saved_lesson["content_markdown"], source)
        self.assertEqual(image_sources, {})
        figure = saved_lesson["content_json"]["figures"][figure_id]
        self.assertEqual(figure["type"], "comparison-cards")
        self.assertEqual(figure["title"], "What changing the settings changes")
        self.assertEqual(figure["cards"][0]["kicker"], "SHORTER WINDOW")
        self.assertEqual(figure["cards"][1]["title"], "Common baseline")
        self.assertEqual(figure["cards"][2]["title"], "More smoothed")
        self.assertEqual(figure["note"], "Compare one setting at a time.")
