from django.urls import path

from . import video_protection, views

app_name = "academy"

urlpatterns = [
    path("", views.academy_home, name="home"),
    path("free-membership/", views.free_membership_landing, name="free-membership"),
    path(
        "free-membership/join/",
        views.join_free_membership_from_landing,
        name="join-free-membership-landing",
    ),
    path("course/<slug:course_slug>/", views.course_detail, name="course-detail"),
    path(
        "course/<slug:course_slug>/enrol-free/",
        views.enrol_free_course,
        name="enrol-free-course",
    ),
    path(
        "course/<slug:course_slug>/join-free-membership/",
        views.join_free_membership_for_course,
        name="join-free-membership",
    ),
    path(
        "course-import/<uuid:import_id>/website-preview/",
        views.course_import_website_preview,
        name="course-import-preview",
    ),
    path("course/<slug:course_slug>/lesson/<uuid:lesson_id>/", views.lesson_detail, name="lesson"),
    path(
        "course/<slug:course_slug>/lesson/<uuid:lesson_id>/admin-preview/",
        views.admin_lesson_preview,
        name="admin-lesson-preview",
    ),
    path("lesson/<uuid:lesson_id>/progress/", views.lesson_progress, name="lesson-progress"),
    path(
        "lesson/<uuid:lesson_id>/quiz/submit/", views.lesson_quiz_submit, name="lesson-quiz-submit"
    ),
    path(
        "lesson/<uuid:lesson_id>/notebook/",
        views.lesson_notebook_submit,
        name="lesson-notebook-submit",
    ),
    path(
        "lesson/<uuid:lesson_id>/reflection/",
        views.lesson_reflection_submit,
        name="lesson-reflection-submit",
    ),
    path("media/<uuid:asset_id>/", views.media_asset, name="media-asset"),
    path(
        "video/<uuid:video_id>/manifest.m3u8",
        video_protection.protected_video_manifest,
        name="protected-video-manifest",
    ),
    path(
        "video/<uuid:video_id>/key/",
        video_protection.protected_video_key,
        name="protected-video-key",
    ),
    path(
        "video/<uuid:video_id>/segment/<str:segment_name>/",
        video_protection.protected_video_segment,
        name="protected-video-segment",
    ),
]
