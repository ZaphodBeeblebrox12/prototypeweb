import base64
import json
import uuid
from unittest.mock import Mock, patch

from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Course, CourseImport, CourseImportAsset, CourseModule, Lesson, LessonInstructorMaterial

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

    @patch(
        "apps.academy.course_builder_api.course_asset_storage.status",
        return_value={
            "backend": "github", "label": "private GitHub repository",
            "durable": True, "writes_enabled": True,
        },
    )
    def test_builder_api_exposes_durable_asset_storage_status(self, storage_status):
        response = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["asset_storage"],
            {
                "backend": "github", "label": "private GitHub repository",
                "durable": True, "writes_enabled": True,
            },
        )
        storage_status.assert_called_once_with()

    def test_local_only_existing_asset_is_migrated_when_durable_storage_is_configured(self):
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload("builder-migrate-local-image")),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        stable_id = uuid.uuid4()
        asset = CourseImportAsset.objects.create(
            course_import=record,
            asset_key="builder/legacy-local-image",
            stable_asset_id=stable_id,
            file="academy/course-imports/legacy-local-image.png",
        )
        with patch(
            "apps.academy.course_builder_api.course_asset_storage.status",
            return_value={"backend": "github", "label": "private GitHub repository", "durable": True, "writes_enabled": True},
        ), patch(
            "apps.academy.course_builder_api.course_asset_storage.remote_exists",
            return_value=False,
        ), patch(
            "apps.academy.course_builder_api._copy_existing_asset",
            return_value=True,
        ) as migrate_asset:
            from .course_builder_api import _store_images

            _store_images(record, {})

        migrate_asset.assert_called_once()
        migrated_id, migrated_asset = migrate_asset.call_args.args
        self.assertEqual(migrated_id, stable_id)
        self.assertEqual(migrated_asset.pk, asset.pk)

    def test_existing_saved_builder_draft_can_be_resaved_when_course_slug_is_taken(self):
        slug = "builder-draft-slug-collision"
        first = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload(slug)),
            content_type="application/json",
        )
        self.assertEqual(first.status_code, 200, first.content)
        record_id = first.json()["record_id"]

        # Simulate a pre-existing Academy Course row with the same slug. Saving
        # the already-owned CourseImport draft must update that draft, not fail
        # the slug check or silently edit the existing Course.
        Course.objects.create(
            title="Existing Academy course",
            slug=slug,
            status=Course.Status.DRAFT,
        )
        payload = self.draft_payload(slug)
        payload["course"]["serverDraftId"] = record_id
        payload["course"]["summary"] = "Updated without changing the existing course."

        second = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(second.json()["record_id"], record_id)
        record = CourseImport.objects.get(pk=record_id)
        self.assertEqual(
            record.payload["builder_state"]["summary"],
            "Updated without changing the existing course.",
        )
        self.assertEqual(Course.objects.get(slug=slug).title, "Existing Academy course")

    def test_new_builder_draft_still_rejects_an_existing_course_slug(self):
        slug = "existing-academy-course-slug"
        Course.objects.create(
            title="Existing Academy course",
            slug=slug,
            status=Course.Status.DRAFT,
        )
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload(slug)),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("unique slug", response.json()["detail"])

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

    def test_builder_question_image_is_saved_as_learner_safe_figure_reference(self):
        from .course_builder_api import _asset_uuid, _build_import_payload

        state = self.draft_payload("builder-question-image")["course"]
        lesson = state["modules"][0]["lessons"][0]
        image_id = "question-chart-01"
        lesson["images"] = [{
            "id": image_id,
            "name": "resistance-chart.png",
            "title": "Repeated resistance test",
            "alt": "Price testing the same resistance area three times",
            "caption": "Notice the closes around the marked zone.",
            "data": "data:image/png;base64," + base64.b64encode(b"fake image bytes").decode("ascii"),
        }]
        lesson["image"] = lesson["images"][0]
        lesson["questions"][0]["imageId"] = image_id

        imported, image_sources = _build_import_payload(state, "builder-question-image")
        saved_lesson = imported["modules"][0]["lessons"][0]
        stable_id = _asset_uuid("builder-question-image", image_id)
        question = saved_lesson["content_json"]["questions"][0]

        self.assertEqual(question["image_asset_id"], stable_id)
        self.assertIn(stable_id, saved_lesson["content_json"]["asset_ids"])
        self.assertEqual(
            saved_lesson["content_json"]["figures"][stable_id],
            {
                "title": "Repeated resistance test",
                "alt": "Price testing the same resistance area three times",
                "caption": "Notice the closes around the marked zone.",
            },
        )
        self.assertIn("builder/" + image_id, image_sources)
        self.assertNotIn("correctIndex", json.dumps(saved_lesson["content_json"]))
        self.assertNotIn("explanation", json.dumps(saved_lesson["content_json"]))

    def test_practice_question_image_hydration_uses_resolved_asset_url(self):
        from .views import _practice_questions_with_images

        questions = [{
            "id": "question-1",
            "prompt": "What does this chart show?",
            "options": ["A", "B"],
            "image_asset_id": "asset-uuid",
        }]
        hydrated = _practice_questions_with_images(
            questions,
            {"asset-uuid": "/academy/media/asset-uuid/"},
            {"asset-uuid": {"title": "Chart A", "alt": "A price chart", "caption": "Look at the retest."}},
        )

        self.assertEqual(hydrated[0]["image_url"], "/academy/media/asset-uuid/")
        self.assertEqual(hydrated[0]["image_title"], "Chart A")
        self.assertEqual(hydrated[0]["image_alt"], "A price chart")
        self.assertEqual(hydrated[0]["image_caption"], "Look at the retest.")
        self.assertNotIn("image_url", questions[0])

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

    def test_builder_persists_titled_image_groups_with_stable_asset_ids(self):
        from .course_builder_api import _build_import_payload

        state = self.draft_payload("builder-image-group")["course"]
        lesson = state["modules"][0]["lessons"][0]
        first_id = "builder-image-long"
        second_id = "builder-image-near-miss"
        group_id = "image-group-method-two"
        source = (
            "Introduce the comparison.\n\n"
            f"[[image-group:{group_id}]]\n\n"
            "Explain what differs between the cases."
        )
        lesson["content"] = source
        lesson["images"] = [
            {
                "id": first_id,
                "name": "chart-long-candidate.png",
                "title": "Long candidate",
                "alt": "Price rises alongside the upper band.",
                "caption": "Both conditions must hold.",
                "data": "data:image/png;base64," + base64.b64encode(b"fake first image").decode("ascii"),
            },
            {
                "id": second_id,
                "name": "chart-near-miss.png",
                "title": "Near miss",
                "alt": "Price moves sideways while one condition fails.",
                "caption": "One condition is not met.",
                "data": "data:image/png;base64," + base64.b64encode(b"fake second image").decode("ascii"),
            },
        ]
        lesson["image"] = lesson["images"][0]
        lesson["imageGroups"] = [{
            "id": group_id,
            "title": "Method II: price position and money flow",
            "imageIds": [first_id, second_id],
            "note": "Read both inputs together.",
        }]

        imported, image_sources = _build_import_payload(state, "builder-image-group")
        saved_lesson = imported["modules"][0]["lessons"][0]
        figure_map = saved_lesson["content_json"]["figures"]
        group = figure_map[group_id]
        asset_ids = saved_lesson["content_json"]["asset_ids"]
        self.assertEqual(saved_lesson["content_markdown"], source)
        self.assertEqual(group["type"], "image-group")
        self.assertEqual(group["title"], "Method II: price position and money flow")
        self.assertEqual(group["note"], "Read both inputs together.")
        self.assertEqual(len(group["image_ids"]), 2)
        self.assertIn("builder/" + first_id, image_sources)
        self.assertIn("builder/" + second_id, image_sources)
        self.assertTrue(set(group["image_ids"]).issubset(set(asset_ids)))
        self.assertEqual(figure_map[group["image_ids"][0]]["title"], "Long candidate")
        self.assertEqual(figure_map[group["image_ids"][1]]["title"], "Near miss")
        self.assertNotIn("chart-long-candidate.png", group["title"])
        self.assertNotIn("Purpose-built teaching aid", saved_lesson["content_markdown"])

    def test_legacy_filename_title_is_cleared_when_cleaning_image_metadata(self):
        from .course_builder_api import _clean_image_payload

        state = self.draft_payload("builder-filename-title")["course"]
        lesson = state["modules"][0]["lessons"][0]
        lesson["images"] = [{
            "id": "legacy-image",
            "name": "BANKNIFTY_2023-08-06_16-51-56_bd975.png",
            "title": "BANKNIFTY_2023-08-06_16-51-56_bd975.png",
            "alt": "BANKNIFTY price chart",
            "caption": "",
            "data": "",
        }]
        cleaned, _image_sources, _asset_specs = _clean_image_payload(state, "builder-filename-title")
        cleaned_image = cleaned["modules"][0]["lessons"][0]["images"][0]
        self.assertEqual(cleaned_image["title"], "")
        self.assertEqual(cleaned_image["name"], "BANKNIFTY_2023-08-06_16-51-56_bd975.png")

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


    def test_admin_can_delete_saved_builder_draft_and_it_disappears_from_the_list(self):
        saved = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload("builder-delete-course")),
            content_type="application/json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        record_id = saved.json()["record_id"]
        self.assertTrue(CourseImport.objects.filter(pk=record_id).exists())

        deleted = self.client.delete(
            reverse("staff_course_builder_api"),
            data=json.dumps({"serverDraftId": record_id}),
            content_type="application/json",
        )
        self.assertEqual(deleted.status_code, 200, deleted.content)
        self.assertEqual(deleted.json()["deleted_id"], record_id)
        record = CourseImport.objects.get(pk=record_id)
        self.assertEqual(record.status, CourseImport.Status.DELETED)

        refreshed = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        self.assertNotIn(record_id, [draft["serverDraftId"] for draft in refreshed.json()["drafts"]])

    def test_course_builder_delete_does_not_remove_a_submitted_review_item(self):
        saved = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.draft_payload("builder-delete-review-guard")),
            content_type="application/json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        record = CourseImport.objects.get(pk=saved.json()["record_id"])
        record.status = CourseImport.Status.REVIEW
        record.save(update_fields=["status"])

        deleted = self.client.delete(
            reverse("staff_course_builder_api"),
            data=json.dumps({"serverDraftId": str(record.pk)}),
            content_type="application/json",
        )
        self.assertEqual(deleted.status_code, 404)
        self.assertTrue(CourseImport.objects.filter(pk=record.pk).exists())


    def test_stale_browser_copy_cannot_recreate_a_deleted_builder_draft(self):
        payload = self.draft_payload("builder-delete-stale-copy")
        saved = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        record_id = saved.json()["record_id"]

        deleted = self.client.delete(
            reverse("staff_course_builder_api"),
            data=json.dumps({"serverDraftId": record_id}),
            content_type="application/json",
        )
        self.assertEqual(deleted.status_code, 200, deleted.content)

        # Simulate a second open tab that still holds the old serverDraftId.
        payload["course"]["serverDraftId"] = record_id
        stale_save = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(stale_save.status_code, 410, stale_save.content)
        self.assertTrue(stale_save.json()["draft_deleted"])
        self.assertEqual(
            CourseImport.objects.get(pk=record_id).status,
            CourseImport.Status.DELETED,
        )
        refreshed = self.client.get(reverse("staff_course_builder_api"))
        self.assertNotIn(
            record_id,
            [draft["serverDraftId"] for draft in refreshed.json()["drafts"]],
        )


    def test_get_retires_legacy_builder_draft_after_course_was_deleted_in_admin(self):
        payload = self.draft_payload()
        saved = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        record_id = saved.json()["record_id"]
        record = CourseImport.objects.get(pk=record_id)

        course = Course.objects.create(
            title=payload["course"]["title"],
            slug=payload["course"]["slug"],
            status=Course.Status.PUBLISHED,
        )
        LogEntry.objects.create(
            user=self.admin,
            content_type=ContentType.objects.get_for_model(Course),
            object_id=str(course.pk),
            object_repr=course.title,
            action_flag=DELETION,
            change_message="Deleted course in Django Admin",
        )
        # Simulate a legacy deletion that happened before the new CourseAdmin
        # cleanup hook was deployed.
        Course.objects.filter(pk=course.pk).delete()

        refreshed = self.client.get(reverse("staff_course_builder_api"))
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        self.assertNotIn(record_id, [draft["serverDraftId"] for draft in refreshed.json()["drafts"]])
        record.refresh_from_db()
        self.assertEqual(record.status, CourseImport.Status.DELETED)


    def test_published_course_can_be_loaded_into_builder_as_a_separate_review_revision(self):
        course = Course.objects.create(
            title="Published Edit Course",
            slug="published-edit-course",
            summary="Live summary",
            description="Live description",
            category="Chart reading",
            level="Intermediate",
            estimated_duration="Self-paced",
            learning_outcomes=["Keep a written process."],
            position=7,
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(
            course=course, title="Foundations", slug="foundations",
            description="Live module description", position=1, is_published=True,
        )
        lesson = Lesson.objects.create(
            module=module, title="Lesson One", slug="lesson-one",
            summary="Live lesson summary", format="reading",
            content_markdown="## Live lesson\n\nOriginal published lesson content.",
            content_json={
                "schema_version": 1, "source_id": "1.1", "asset_ids": [], "figures": {},
                "related_course_ids": [],
                "questions": [{
                    "id": "question-live", "prompt": "Which option is correct?",
                    "options": ["First option", "Second option"],
                }],
                "notebook": {"title": "My notebook", "prompts": []}, "video_url": "",
            },
            position=1, is_published=True,
        )
        LessonInstructorMaterial.objects.create(
            lesson=lesson,
            rubric_json={"questions": [{
                "id": "question-live", "prompt": "Which option is correct?",
                "options": ["First option", "Second option"], "correctIndex": 1,
                "explanation": "The second option matches the evidence.", "imageId": "",
            }]},
        )
        loaded = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps({"action": "begin_edit_published_course", "courseId": str(course.pk)}),
            content_type="application/json",
        )
        self.assertEqual(loaded.status_code, 200, loaded.content)
        state = loaded.json()["course"]
        self.assertEqual(state["serverCourseId"], str(course.pk))
        self.assertEqual(state["modules"][0]["id"], str(module.pk))
        self.assertEqual(state["modules"][0]["lessons"][0]["id"], str(lesson.pk))
        self.assertEqual(state["modules"][0]["lessons"][0]["content"], "## Live lesson\n\nOriginal published lesson content.")
        self.assertEqual(state["modules"][0]["lessons"][0]["questions"][0]["correctIndex"], 1)

        state["summary"] = "Revised summary"
        state["modules"][0]["lessons"][0]["content"] = "## Live lesson\n\nReviewed replacement content."
        saved = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps({"course": state, "mode": "save", "sync_source": False}),
            content_type="application/json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        record = CourseImport.objects.get(pk=saved.json()["record_id"])
        self.assertEqual(record.target_course_id, course.pk)
        course.refresh_from_db()
        lesson.refresh_from_db()
        self.assertEqual(course.summary, "Live summary")
        self.assertIn("Original published lesson content.", lesson.content_markdown)
        self.assertEqual(record.status, CourseImport.Status.DRAFT)

        revision_state = saved.json()["draft"]
        revision_state["summary"] = "Revised summary"
        revision_state["modules"][0]["lessons"][0]["content"] = "## Live lesson\n\nReviewed replacement content."
        submitted = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps({"course": revision_state, "mode": "submit", "sync_source": False}),
            content_type="application/json",
        )
        self.assertEqual(submitted.status_code, 200, submitted.content)
        record.refresh_from_db()
        self.assertEqual(record.target_course_id, course.pk)
        self.assertEqual(record.status, CourseImport.Status.REVIEW)

        from .importing import publish_course_import
        published_again = publish_course_import(record, user=self.admin)
        self.assertEqual(published_again.pk, course.pk)
        self.assertEqual(Course.objects.filter(slug="published-edit-course").count(), 1)
        self.assertEqual(Course.objects.get(pk=course.pk).summary, "Revised summary")
        self.assertEqual(CourseModule.objects.get(pk=module.pk).pk, module.pk)
        self.assertEqual(Lesson.objects.get(pk=lesson.pk).content_markdown, "## Live lesson\n\nReviewed replacement content.")
        self.assertEqual(CourseImport.objects.get(pk=record.pk).status, CourseImport.Status.PUBLISHED)

    def test_coming_soon_catalogue_entry_exposes_only_announcement_metadata(self):
        CourseImport.objects.create(
            course_slug="coming-soon-options-course", title="Options Course",
            manifest_version="course-builder-v1", content_hash="a" * 64,
            source_manifest="builder://coming-soon-options-course",
            status=CourseImport.Status.DRAFT,
            payload={
                "builder_state": {
                    "title": "Options Course", "slug": "coming-soon-options-course",
                    "summary": "A practical options course is nearly ready.",
                    "description": "A longer internal draft description.",
                    "category": "Options", "level": "Intermediate", "comingSoon": True,
                },
                "modules": [{
                    "title": "Secret module title",
                    "lessons": [{
                        "title": "Private lesson body",
                        "content_markdown": "PRIVATE LESSON TEXT THAT MUST NOT LEAK",
                        "instructor_material": {"questions": [{"prompt": "SECRET ANSWER KEY"}]},
                    }],
                }],
            },
        )
        self.client.logout()
        response = self.client.get(reverse("academy_public_catalogue"))
        self.assertEqual(response.status_code, 200, response.content)
        teaser = next(item for item in response.json()["courses"] if item["status"] == "coming-soon")
        self.assertEqual(teaser["title"], "Options Course")
        self.assertEqual(teaser["description"], "A practical options course is nearly ready.")
        self.assertEqual(teaser["modules"][0]["title"], "Course outline")
        body = json.dumps(teaser)
        self.assertNotIn("PRIVATE LESSON TEXT", body)
        self.assertNotIn("SECRET ANSWER KEY", body)
        self.assertNotIn("Secret module title", body)
