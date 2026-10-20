"""Regression coverage for safely handling failed GitHub source sync."""
import json
import uuid
from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import CourseImport, CourseImportAsset
from apps.academy.storage import course_asset_storage

User = get_user_model()


@override_settings(
    ACADEMY_GITHUB_ASSET_REPOSITORY="ZaphodBeeblebrox12/prototypeweb",
    ACADEMY_GITHUB_ASSET_TOKEN="test-token",
    ACADEMY_GITHUB_ASSET_BRANCH="my-new-branch",
)
class CourseBuilderGitHubFailureTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="course-builder-failure-author",
            password="test-password",
            role="admin",
        )
        self.client.force_login(self.admin)

    def payload(self, slug, summary="Original saved summary", mode="save"):
        return {
            "mode": mode,
            "course": {
                "title": "GitHub Failure Test Course",
                "slug": slug,
                "summary": summary,
                "description": "A test course.",
                "category": "Chart reading",
                "level": "Intermediate",
                "duration": "Self-paced",
                "outcomes": [],
                "modules": [{
                    "title": "Foundations",
                    "description": "",
                    "lessons": [{
                        "title": "First principles",
                        "summary": "",
                        "format": "reading",
                        "minutes": 12,
                        "content": "## Notice\n\nDescribe the visible evidence first.",
                        "images": [],
                        "notebook": {
                            "title": "Evidence notebook",
                            "prompts": [{"label": "Observe", "text": "What is visible?"}],
                        },
                        "questions": [],
                        "relatedCourseIds": [],
                    }],
                }],
            },
        }

    def save_initial_draft(self, slug):
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(self.payload(slug)),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        record = CourseImport.objects.get(pk=response.json()["record_id"])
        self.assertEqual(record.status, CourseImport.Status.DRAFT)
        return record

    def submit_changed_draft(self, slug, summary="Changed summary"):
        payload = self.payload(slug, summary=summary, mode="submit")
        payload["sync_source"] = True
        return self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )

    def assert_prior_draft_preserved(self, record):
        record.refresh_from_db()
        self.assertEqual(record.status, CourseImport.Status.DRAFT)
        self.assertEqual(
            record.payload["builder_state"]["summary"],
            "Original saved summary",
        )

    def test_repeated_identical_submission_returns_the_existing_review_record(self):
        slug = "idempotent-course-submission"
        payload = self.payload(slug, mode="submit")
        # The test focuses on DB idempotency; source sync has its own mocked tests.
        payload["sync_source"] = False

        first_response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(first_response.status_code, 200, first_response.content)
        first_record_id = first_response.json()["record_id"]

        retry_response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(retry_response.status_code, 200, retry_response.content)
        self.assertTrue(retry_response.json()["submitted"])
        self.assertEqual(retry_response.json()["record_id"], first_record_id)
        self.assertIn("already awaiting review", retry_response.json()["message"].lower())
        self.assertEqual(CourseImport.objects.filter(course_slug=slug).count(), 1)
        self.assertEqual(
            CourseImport.objects.get(pk=first_record_id).status,
            CourseImport.Status.REVIEW,
        )

    def test_github_401_and_403_preserve_the_last_saved_draft(self):
        for status_code in (401, 403):
            with self.subTest(status_code=status_code):
                slug = f"github-denied-{status_code}"
                record = self.save_initial_draft(slug)
                with patch(
                    "apps.academy.course_builder_api.requests.get",
                    return_value=Mock(status_code=status_code),
                ), patch("apps.academy.course_builder_api.requests.put") as github_put:
                    response = self.submit_changed_draft(slug)

                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn("GitHub", str(response.json().get("detail", "")))
                github_put.assert_not_called()
                self.assert_prior_draft_preserved(record)

    def test_failed_submit_does_not_delete_an_existing_draft_image(self):
        slug = "github-failure-preserves-image"
        record = self.save_initial_draft(slug)
        asset = CourseImportAsset.objects.create(
            course_import=record,
            asset_key="builder/removed-image",
            stable_asset_id=uuid.uuid4(),
            alt_text="An existing image",
            file="legacy-image.png",
        )

        with patch.object(course_asset_storage, "delete") as storage_delete, patch(
            "apps.academy.course_builder_api.requests.get",
            return_value=Mock(status_code=401),
        ), patch("apps.academy.course_builder_api.requests.put"):
            response = self.submit_changed_draft(slug)

        self.assertEqual(response.status_code, 400, response.content)
        storage_delete.assert_not_called()
        asset.refresh_from_db()
        self.assertEqual(asset.file.name, "legacy-image.png")
        self.assert_prior_draft_preserved(record)

    def test_github_timeout_preserves_the_last_saved_draft(self):
        slug = "github-timeout-course"
        record = self.save_initial_draft(slug)
        with patch(
            "apps.academy.course_builder_api.requests.get",
            side_effect=requests.Timeout("mock timeout"),
        ), patch("apps.academy.course_builder_api.requests.put") as github_put:
            response = self.submit_changed_draft(slug)

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn("could not be reached", str(response.json().get("detail", "")).lower())
        github_put.assert_not_called()
        self.assert_prior_draft_preserved(record)

    def test_github_write_failure_preserves_the_last_saved_draft(self):
        slug = "github-write-failure-course"
        record = self.save_initial_draft(slug)
        with patch(
            "apps.academy.course_builder_api.requests.get",
            return_value=Mock(status_code=404),
        ), patch(
            "apps.academy.course_builder_api.requests.put",
            return_value=Mock(status_code=500),
        ):
            response = self.submit_changed_draft(slug)

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn("could not save", str(response.json().get("detail", "")).lower())
        self.assert_prior_draft_preserved(record)

    @override_settings(ACADEMY_GITHUB_ASSET_TOKEN="")
    def test_missing_token_blocks_submission_and_preserves_the_saved_draft(self):
        slug = "github-token-missing-course"
        record = self.save_initial_draft(slug)
        payload = self.payload(slug, summary="Changed summary", mode="submit")
        payload["sync_source"] = True

        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn("not configured", str(response.json().get("detail", "")).lower())
        self.assert_prior_draft_preserved(record)
