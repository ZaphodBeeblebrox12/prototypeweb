import logging
import mimetypes
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import FileResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils.html import format_html

from .content_rendering import build_lesson_sections
from .course_builder_lifecycle import mark_builder_draft_deleted
from .forms import (
    CourseImportAssetAdminForm,
    CourseMediaAssetAdminForm,
    LessonAdminForm,
    LessonFigureAdminForm,
)
from .importing import (
    inspect_manifest,
    publish_course_import,
    stage_course_import,
    validate_import_for_publish,
)
from .models import (
    Course,
    CourseContentRevision,
    CourseEntitlement,
    CourseEntitlementEvent,
    CourseImport,
    CourseImportAsset,
    CourseMediaAsset,
    CourseModule,
    CourseOffer,
    Lesson,
    LessonInstructorMaterial,
    LessonProgress,
)
from .permissions import is_course_content_admin
from .storage import course_asset_storage

logger = logging.getLogger(__name__)


def _retire_builder_drafts_for_course_slugs(slugs):
    """Retire editable builder drafts when an administrator deletes their course."""
    normalized_slugs = {str(slug) for slug in slugs if slug}
    if not normalized_slugs:
        return
    drafts = CourseImport.objects.select_for_update().filter(
        course_slug__in=normalized_slugs,
        status=CourseImport.Status.DRAFT,
    ).order_by("pk")
    for draft in drafts:
        if draft.payload.get("builder_state"):
            mark_builder_draft_deleted(draft)


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 0
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "status", "position", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "slug", "summary")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (CourseModuleInline,)
    readonly_fields = ("created_at", "updated_at", "status")

    def has_module_permission(self, request):
        return is_course_content_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_add_permission(self, request):
        return is_course_content_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def delete_model(self, request, obj):
        # Builder drafts are separate records and may not have target_course set
        # (older Builder saves predate the published Course row). Retire them by
        # slug so they cannot reappear after this Course is deleted.
        with transaction.atomic():
            _retire_builder_drafts_for_course_slugs([obj.slug])
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        with transaction.atomic():
            courses = list(queryset)
            _retire_builder_drafts_for_course_slugs(course.slug for course in courses)
            super().delete_queryset(request, queryset)

    def get_deleted_objects(self, objs, request):
        """Allow owned media to be removed only as part of deleting its course.

        CourseMediaAssetAdmin intentionally disables direct media deletion. Django's
        delete confirmation checks each related object's ModelAdmin permission too,
        so we waive only that child permission for a course-content admin deleting
        the owning Course. Other related-object permissions and protected relations
        remain enforced.
        """
        deleted_objects, model_count, perms_needed, protected = super().get_deleted_objects(
            objs, request
        )
        if is_course_content_admin(request.user):
            perms_needed.discard(CourseMediaAsset._meta.verbose_name)
        return deleted_objects, model_count, perms_needed, protected


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "position", "is_published")
    list_filter = ("course", "is_published")
    search_fields = ("title", "course__title")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")

    def has_module_permission(self, request):
        return is_course_content_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_add_permission(self, request):
        return is_course_content_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_course_content_admin(request.user)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    list_display = ("title", "module", "format", "position", "release_day", "is_preview", "is_published", "add_figure_link")
    list_filter = ("format", "is_preview", "is_published", "module__course")
    search_fields = ("title", "summary", "module__title", "module__course__title")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")

    def get_urls(self):
        custom = [
            path(
                "<uuid:object_id>/add-figure/",
                self.admin_site.admin_view(self.add_figure_view),
                name="academy_lesson_add_figure",
            ),
        ]
        return custom + super().get_urls()

    @admin.display(description="Add image")
    def add_figure_link(self, obj):
        return format_html(
            '<a href="{}">Add image</a>',
            reverse("admin:academy_lesson_add_figure", args=[obj.pk]),
        )

    def add_figure_view(self, request, object_id):
        if not is_course_content_admin(request.user):
            return HttpResponseForbidden("Administrator course-content access is required.")
        lesson = get_object_or_404(
            Lesson.objects.select_related("module__course"),
            pk=object_id,
        )
        form = LessonFigureAdminForm(request.POST or None, request.FILES or None)

        if request.method == "POST" and form.is_valid():
            upload = form.cleaned_data.get("file")
            stored_name = ""
            asset = None
            try:
                with transaction.atomic():
                    asset = CourseMediaAsset(
                        course=lesson.module.course,
                        asset_key=f"admin-added/{lesson.pk}/{uuid.uuid4().hex}",
                        alt_text=form.cleaned_data["alt_text"],
                        original_url=form.cleaned_data.get("original_url", ""),
                        updated_by=request.user,
                    )
                    if upload:
                        asset.file.save(upload.name, upload, save=False)
                        stored_name = asset.file.name
                    asset.save()

                    CourseContentRevision.objects.create(
                        lesson=lesson,
                        editor=request.user,
                        revision_type=CourseContentRevision.RevisionType.ADMIN_EDIT,
                        title_before=lesson.title,
                        summary_before=lesson.summary,
                        content_markdown_before=lesson.content_markdown,
                        content_json_before=lesson.content_json,
                        fields_changed=["content_markdown", "content_json"],
                    )
                    heading_by_placement = {
                        "idea": "Additional concept figure",
                        "examples": "Additional chart examples",
                        "practice": "Practice figure",
                    }
                    alt = form.cleaned_data["alt_text"]
                    figure_markdown = f"![{alt}] (asset://{asset.pk})"
                    # Markdown image syntax must not contain whitespace between ] and (.
                    figure_markdown = figure_markdown.replace("] (", "](")
                    lesson.content_markdown = (
                        lesson.content_markdown.rstrip()
                        + "\n\n### "
                        + heading_by_placement[form.cleaned_data["placement"]]
                        + "\n\n"
                        + figure_markdown
                        + "\n"
                    )
                    content_json = dict(lesson.content_json) if isinstance(lesson.content_json, dict) else {}
                    asset_ids = list(content_json.get("asset_ids", []))
                    asset_ids.append(str(asset.pk))
                    content_json["asset_ids"] = asset_ids
                    lesson.content_json = content_json
                    lesson.save(update_fields=["content_markdown", "content_json", "updated_at"])

                    from apps.audit.models import AuditLog
                    AuditLog.log(
                        action="academy_lesson_figure_added",
                        user=request.user,
                        object_type="lesson",
                        object_id=lesson.pk,
                        metadata={
                            "course_id": str(lesson.module.course_id),
                            "asset_id": str(asset.pk),
                            "asset_key": asset.asset_key,
                            "placement": form.cleaned_data["placement"],
                            "source_url_used": bool(asset.original_url),
                            "uploaded_file": bool(asset.file),
                        },
                    )
            except Exception:
                if stored_name:
                    course_asset_storage.delete(stored_name)
                logger.exception("Could not add a course figure to lesson %s", lesson.pk)
                form.add_error(None, "The image could not be added. No lesson change was saved; please try again.")
            else:
                messages.success(
                    request,
                    "Image added. You can replace its URL with an uploaded image in Course media assets.",
                )
                return redirect("admin:academy_lesson_change", object_id=lesson.pk)

        context = {
            **self.admin_site.each_context(request),
            "title": f"Add image · {lesson.title}",
            "opts": self.model._meta,
            "original": lesson,
            "lesson": lesson,
            "form": form,
            "changelist_url": reverse("admin:academy_lesson_changelist"),
            "change_url": reverse("admin:academy_lesson_change", args=[lesson.pk]),
        }
        return render(request, "admin/academy/lesson_add_figure.html", context)

    def has_module_permission(self, request):
        return is_course_content_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_add_permission(self, request):
        return is_course_content_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def save_model(self, request, obj, form, change):
        changed_fields = []
        if change:
            previous = Lesson.objects.filter(pk=obj.pk).first()
            if previous:
                watched = ("title", "summary", "content_markdown", "content_json")
                changed_fields = [field for field in watched if getattr(previous, field) != getattr(obj, field)]
                if changed_fields:
                    CourseContentRevision.objects.create(
                        lesson=previous, editor=request.user,
                        revision_type=CourseContentRevision.RevisionType.ADMIN_EDIT,
                        title_before=previous.title, summary_before=previous.summary,
                        content_markdown_before=previous.content_markdown,
                        content_json_before=previous.content_json,
                        fields_changed=changed_fields,
                    )
        super().save_model(request, obj, form, change)
        if changed_fields:
            from apps.audit.models import AuditLog
            AuditLog.log(
                action="academy_lesson_content_updated", user=request.user,
                object_type="lesson", object_id=obj.pk,
                metadata={"fields_changed": changed_fields},
            )

    fieldsets = (
        (None, {"fields": ("module", "title", "slug", "summary", "format", "position", "duration_minutes", "release_day", "is_preview", "is_published")}),
        ("Learner content", {"fields": ("content_markdown", "content_json")}),
        ("System", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(LessonInstructorMaterial)
class LessonInstructorMaterialAdmin(admin.ModelAdmin):
    list_display = ("lesson", "updated_at")
    search_fields = ("lesson__title", "lesson__module__course__title")
    readonly_fields = ("updated_at",)


@admin.register(CourseOffer)
class CourseOfferAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "plan", "access_duration_days", "is_active", "position")
    list_filter = ("is_active", "course")
    search_fields = ("name", "slug", "course__title", "plan__name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


class CourseEntitlementEventInline(admin.TabularInline):
    model = CourseEntitlementEvent
    extra = 0
    can_delete = False
    readonly_fields = tuple(f.name for f in CourseEntitlementEvent._meta.fields)
    ordering = ("-created_at",)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CourseEntitlement)
class CourseEntitlementAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "starts_at", "expires_at", "source", "payment_intent")
    list_filter = ("status", "source", "course")
    search_fields = ("user__username", "user__email", "course__title", "payment_intent__provider_reference")
    readonly_fields = tuple(f.name for f in CourseEntitlement._meta.fields)
    inlines = (CourseEntitlementEventInline,)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CourseEntitlementEvent)
class CourseEntitlementEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "event_type", "entitlement", "payment_intent", "actor")
    list_filter = ("event_type", "created_at")
    readonly_fields = tuple(f.name for f in CourseEntitlementEvent._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "status", "time_spent_seconds", "updated_at")
    list_filter = ("status", "lesson__module__course")
    search_fields = ("user__username", "user__email", "lesson__title")
    readonly_fields = tuple(f.name for f in LessonProgress._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CourseImport)
class CourseImportAdmin(admin.ModelAdmin):
    change_list_template = "admin/academy/courseimport/change_list.html"
    list_display = ("title", "course_slug", "status", "manifest_version", "imported_at", "review_link")
    list_filter = ("status", "imported_at")
    search_fields = ("title", "course_slug", "content_hash")
    readonly_fields = tuple(field.name for field in CourseImport._meta.fields)
    ordering = ("-imported_at",)

    def has_module_permission(self, request):
        return is_course_content_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Review")
    def review_link(self, obj):
        if obj.status not in (CourseImport.Status.REVIEW, CourseImport.Status.PUBLISHED):
            return "Not reviewable"
        return format_html('<a href="{}">Preview course</a>', reverse("admin:academy_courseimport_review", args=[obj.pk]))

    def get_urls(self):
        custom = [
            path(
                "stage-canonical-bollinger/",
                self.admin_site.admin_view(self.stage_canonical_bollinger_view),
                name="academy_courseimport_stage_bollinger",
            ),
            path("<uuid:object_id>/review/", self.admin_site.admin_view(self.review_view), name="academy_courseimport_review"),
            path("<uuid:object_id>/publish/", self.admin_site.admin_view(self.publish_view), name="academy_courseimport_publish"),
            path("<uuid:object_id>/asset/<uuid:asset_id>/", self.admin_site.admin_view(self.asset_view), name="academy_courseimport_asset"),
        ]
        return custom + super().get_urls()

    def _is_authorized(self, request):
        return is_course_content_admin(request.user)

    def stage_canonical_bollinger_view(self, request):
        """Stage the checked-in authored course as a review-only import."""
        if not self._is_authorized(request):
            return HttpResponseForbidden("Administrator course-content access is required.")
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        manifest_path = (
            Path(settings.BASE_DIR).parent
            / "course-source"
            / "understand-bollinger-bands"
            / "course-manifest.json"
        ).resolve()
        try:
            payload, asset_sources, warnings = inspect_manifest(manifest_path)
            record, created, stage_warnings = stage_course_import(
                manifest_path=manifest_path,
                payload=payload,
                asset_sources=asset_sources,
                warnings=warnings,
                imported_by=request.user,
            )
        except (OSError, ValueError, KeyError) as exc:
            logger.warning("Could not stage canonical Bollinger Bands source: %s", exc)
            messages.error(request, f"Could not prepare the authored course: {exc}")
            return redirect("admin:academy_courseimport_changelist")
        except Exception:
            logger.exception("Failed to stage canonical Bollinger Bands source")
            messages.error(
                request,
                "Could not prepare the authored course. Check the server logs for details.",
            )
            return redirect("admin:academy_courseimport_changelist")

        if created:
            messages.success(
                request,
                "Understand Bollinger Bands is staged for administrator review only. "
                "Nothing was published to learners.",
            )
        else:
            messages.info(
                request,
                "An import for this exact source version already exists. "
                "Opening it for review; nothing new was published to learners.",
            )
        combined_warnings = list(dict.fromkeys([*warnings, *stage_warnings]))
        if combined_warnings:
            messages.warning(
                request,
                f"{len(combined_warnings)} asset/source warning(s) need review before publication.",
            )
        return redirect("admin:academy_courseimport_review", object_id=record.pk)

    def review_view(self, request, object_id):
        if not self._is_authorized(request):
            return HttpResponseForbidden("Administrator course-content access is required.")
        record = get_object_or_404(CourseImport, pk=object_id)
        asset_urls = {}
        staged_assets = list(record.assets.all())
        for asset in staged_assets:
            live_asset = CourseMediaAsset.objects.filter(pk=asset.stable_asset_id).first()
            if asset.file or (live_asset and live_asset.file):
                asset_urls[str(asset.stable_asset_id)] = reverse(
                    "admin:academy_courseimport_asset", args=[record.pk, asset.stable_asset_id]
                )
            elif asset.original_url.startswith(("https://", "http://")):
                asset_urls[str(asset.stable_asset_id)] = asset.original_url
            elif live_asset and live_asset.original_url.startswith(("https://", "http://")):
                asset_urls[str(asset.stable_asset_id)] = live_asset.original_url

        review_modules = []
        for module in record.payload.get("modules", []):
            review_lessons = []
            for lesson_data in module.get("lessons", []):
                content_json = lesson_data.get("content_json", {})
                if not isinstance(content_json, dict):
                    content_json = {}
                figure_metadata = content_json.get("figures", {})
                if not isinstance(figure_metadata, dict):
                    figure_metadata = {}
                notebook = content_json.get("notebook") or record.payload.get("notebook", {})
                sections = build_lesson_sections(
                    lesson_data.get("content_markdown", ""),
                    asset_urls,
                    user=request.user,
                    admin_preview=True,
                    figure_metadata=figure_metadata,
                    figure_prefix=f"{module.get('position', 0)}.{lesson_data.get('position', 0)}",
                    module_label=f"Module {module.get('position', '')} · {module.get('title', '')}",
                )
                questions = []
                raw_questions = content_json.get("questions", [])
                if isinstance(raw_questions, list):
                    for raw_question in raw_questions[:50]:
                        if not isinstance(raw_question, dict):
                            continue
                        question = dict(raw_question)
                        asset_id = str(question.get("image_asset_id") or "")
                        image_metadata = figure_metadata.get(asset_id, {})
                        if not isinstance(image_metadata, dict):
                            image_metadata = {}
                        question["image_url"] = asset_urls.get(asset_id, "") if asset_id else ""
                        question["image_title"] = str(image_metadata.get("title") or "Chart")[:240]
                        question["image_alt"] = str(image_metadata.get("alt") or question["image_title"])[:500]
                        question["image_caption"] = str(image_metadata.get("caption") or "")[:500]
                        questions.append(question)

                raw_video_url = content_json.get("video_url", "")
                video_url = raw_video_url.strip() if isinstance(raw_video_url, str) else ""
                if not video_url.startswith(("https://", "http://")):
                    video_url = ""
                video_is_file = video_url.lower().split("?", 1)[0].endswith((".mp4", ".webm", ".ogg"))
                review_lessons.append({
                    "lesson": lesson_data,
                    "sections": sections,
                    "notebook": notebook,
                    "questions": questions,
                    "video_url": video_url,
                    "video_is_file": video_is_file,
                    "tab_id_prefix": f"review-{module.get('position', 0)}-{lesson_data.get('position', 0)}",
                })
            review_modules.append({"module": module, "lessons": review_lessons})

        errors = validate_import_for_publish(record) if record.status == CourseImport.Status.REVIEW else []
        asset_rows = []
        for asset in staged_assets:
            live_asset = CourseMediaAsset.objects.filter(pk=asset.stable_asset_id).first()
            asset_rows.append({
                "asset": asset,
                "has_file": bool(asset.file) or bool(live_asset and live_asset.file),
                "preview_url": asset_urls.get(str(asset.stable_asset_id), ""),
                "original_url": asset.original_url or (live_asset.original_url if live_asset else ""),
                "has_external_source": bool(
                    (asset.original_url or (live_asset.original_url if live_asset else "")).startswith(("https://", "http://"))
                ),
                "status_label": (
                    "Uploaded replacement"
                    if (bool(asset.file) or bool(live_asset and live_asset.file))
                    else (
                        "Using URL for now"
                        if (asset.original_url or (live_asset.original_url if live_asset else "")).startswith(("https://", "http://"))
                        else "Needs upload"
                    )
                ),
                "edit_url": reverse("admin:academy_courseimportasset_change", args=[asset.pk]),
            })
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Review course import",
            "import_record": record,
            "review_modules": review_modules,
            "publish_errors": errors,
            "asset_rows": asset_rows,
            "publish_url": reverse("admin:academy_courseimport_publish", args=[record.pk]),
            "changelist_url": reverse("admin:academy_courseimport_changelist"),
        }
        return render(request, "academy/course_review.html", context)

    def asset_view(self, request, object_id, asset_id):
        if not self._is_authorized(request):
            return HttpResponseForbidden("Administrator course-content access is required.")
        record = get_object_or_404(CourseImport, pk=object_id)
        staged = record.assets.filter(stable_asset_id=asset_id).first()

        # Render a stored copy only when it is actually present. Render Free's
        # filesystem is ephemeral across deploys, so a saved FileField name may
        # outlive its local file. The review-only fallback below reads only a
        # checked-in asset path contained within this course's source package.
        file_field = None
        if staged and staged.file and staged.file.storage.exists(staged.file.name):
            file_field = staged.file

        if file_field is None:
            live = CourseMediaAsset.objects.filter(pk=asset_id).first()
            if live and live.file and live.file.storage.exists(live.file.name):
                file_field = live.file

        if file_field is not None:
            response = FileResponse(
                file_field.open("rb"),
                content_type=mimetypes.guess_type(file_field.name)[0] or "application/octet-stream",
            )
            response["Cache-Control"] = "private, no-store"
            response["X-Content-Type-Options"] = "nosniff"
            return response

        if staged and staged.source_path:
            source_root = (
                Path(settings.BASE_DIR).parent / "course-source" / record.course_slug
            ).resolve()
            source_path = (source_root / staged.source_path).resolve()
            allowed_suffixes = {".svg", ".png", ".jpg", ".jpeg", ".webp"}
            if (
                source_root in source_path.parents
                and source_path.is_file()
                and source_path.suffix.lower() in allowed_suffixes
            ):
                response = FileResponse(
                    source_path.open("rb"),
                    content_type=mimetypes.guess_type(source_path.name)[0] or "application/octet-stream",
                )
                response["Cache-Control"] = "private, no-store"
                response["X-Content-Type-Options"] = "nosniff"
                return response

        from django.http import Http404
        raise Http404("This course image has not been uploaded or found in the checked-in course source.")

    def publish_view(self, request, object_id):
        if not self._is_authorized(request):
            return HttpResponseForbidden("Administrator course-content access is required.")
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])
        record = get_object_or_404(CourseImport, pk=object_id)
        try:
            course = publish_course_import(record, user=request.user)
        except ValidationError as exc:
            for message in exc.messages:
                messages.error(request, message)
            return redirect("admin:academy_courseimport_review", object_id=record.pk)
        messages.success(request, f"{course.title} has been published from the reviewed import.")
        return redirect("admin:academy_course_changelist")


@admin.register(CourseImportAsset)
class CourseImportAssetAdmin(admin.ModelAdmin):
    form = CourseImportAssetAdminForm
    list_display = ("course_import", "asset_key", "source_error", "file", "updated_at")
    list_filter = ("course_import__status",)
    search_fields = ("course_import__title", "asset_key", "alt_text")
    readonly_fields = ("course_import", "asset_key", "stable_asset_id", "source_path", "original_url", "source_error", "created_at", "updated_at")
    fields = ("course_import", "asset_key", "stable_asset_id", "source_path", "original_url", "source_error", "alt_text", "file", "created_at", "updated_at")

    def has_module_permission(self, request):
        return is_course_content_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        from apps.audit.models import AuditLog
        if obj.file:
            obj.source_error = ""
        super().save_model(request, obj, form, change)
        AuditLog.log(
            action="academy_course_import_asset_updated", user=request.user,
            object_type="course_import_asset", object_id=obj.pk,
            metadata={"course_import_id": str(obj.course_import_id), "asset_key": obj.asset_key},
        )


@admin.register(CourseMediaAsset)
class CourseMediaAssetAdmin(admin.ModelAdmin):
    form = CourseMediaAssetAdminForm
    list_display = ("course", "asset_key", "alt_text", "updated_at", "updated_by")
    list_filter = ("course",)
    search_fields = ("course__title", "asset_key", "alt_text")
    readonly_fields = ("course", "asset_key", "source_path", "original_url", "created_at", "updated_at", "updated_by")
    fields = ("course", "asset_key", "source_path", "original_url", "alt_text", "file", "created_at", "updated_at", "updated_by")

    def has_module_permission(self, request):
        return is_course_content_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        from apps.audit.models import AuditLog
        old_name = ""
        if change:
            previous = CourseMediaAsset.objects.filter(pk=obj.pk).first()
            old_name = previous.file.name if previous and previous.file else ""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        if change and old_name != (obj.file.name if obj.file else ""):
            AuditLog.log(
                action="academy_course_media_replaced", user=request.user,
                object_type="course_media_asset", object_id=obj.pk,
                metadata={"asset_key": obj.asset_key, "old_file": old_name, "new_file": obj.file.name if obj.file else ""},
            )


@admin.register(CourseContentRevision)
class CourseContentRevisionAdmin(admin.ModelAdmin):
    list_display = ("lesson", "revision_type", "editor", "created_at")
    list_filter = ("revision_type", "created_at")
    search_fields = ("lesson__title", "lesson__module__course__title")
    readonly_fields = tuple(field.name for field in CourseContentRevision._meta.fields)

    def has_module_permission(self, request):
        return is_course_content_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_course_content_admin(request.user)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
