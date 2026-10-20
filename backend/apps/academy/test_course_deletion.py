from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .admin import CourseAdmin, CourseMediaAssetAdmin
from .models import Course, CourseMediaAsset


User = get_user_model()


class CourseDeletionAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="course-delete-admin",
            password="test-password",
            role="admin",
        )
        self.request = RequestFactory().post("/admin/academy/course/")
        self.request.user = self.user
        self.site = AdminSite()
        self.site.register(Course, CourseAdmin)
        self.site.register(CourseMediaAsset, CourseMediaAssetAdmin)
        self.course = Course.objects.create(
            title="Disposable draft course",
            slug="disposable-draft-course",
        )
        self.asset = CourseMediaAsset.objects.create(
            course=self.course,
            asset_key="figures/disposable-chart.png",
            alt_text="A test chart",
        )

    def test_course_delete_confirmation_allows_owned_media_for_content_admin(self):
        course_admin = self.site._registry[Course]
        deletable, model_count, perms_needed, protected = course_admin.get_deleted_objects(
            Course.objects.filter(pk=self.course.pk),
            self.request,
        )

        self.assertNotIn(CourseMediaAsset._meta.verbose_name, perms_needed)
        self.assertEqual(protected, [])
        self.assertEqual(model_count.get(CourseMediaAsset._meta.verbose_name_plural), 1)
        self.assertTrue(deletable)

    def test_deleting_course_removes_its_media_record_but_direct_asset_delete_stays_disabled(self):
        media_admin = self.site._registry[CourseMediaAsset]
        self.assertFalse(media_admin.has_delete_permission(self.request, self.asset))

        course_admin = self.site._registry[Course]
        course_admin.delete_queryset(
            self.request,
            Course.objects.filter(pk=self.course.pk),
        )

        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())
        self.assertFalse(CourseMediaAsset.objects.filter(pk=self.asset.pk).exists())
