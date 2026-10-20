from django.urls import path

from . import views

app_name = "academy"

urlpatterns = [
    path("", views.academy_home, name="home"),
    path("course/<slug:course_slug>/", views.course_detail, name="course-detail"),
    path("course-import/<uuid:import_id>/website-preview/", views.course_import_website_preview, name="course-import-preview"),
    path("course/<slug:course_slug>/lesson/<uuid:lesson_id>/", views.lesson_detail, name="lesson"),
    path("course/<slug:course_slug>/lesson/<uuid:lesson_id>/admin-preview/", views.admin_lesson_preview, name="admin-lesson-preview"),
    path("lesson/<uuid:lesson_id>/progress/", views.lesson_progress, name="lesson-progress"),
    path("lesson/<uuid:lesson_id>/quiz/submit/", views.lesson_quiz_submit, name="lesson-quiz-submit"),
    path("lesson/<uuid:lesson_id>/notebook/", views.lesson_notebook_submit, name="lesson-notebook-submit"),
    path("media/<uuid:asset_id>/", views.media_asset, name="media-asset"),
]
