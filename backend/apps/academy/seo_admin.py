"""Course-level SEO inventory and content-quality audit for the TradeThesis Admin Desk."""

import re
from collections import Counter

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET

from .course_card_utils import is_course_card_recommendable
from .models import Course
from .permissions import is_course_content_admin


def _clean_text(value):
    return re.sub(r"\\s+", " ", str(value or "")).strip()


def _course_indexability_reasons(course, global_enabled):
    reasons = []
    if not global_enabled:
        reasons.append("Site-wide indexing is disabled for this deployment.")
    if course.status != Course.Status.PUBLISHED:
        reasons.append("The course is not published.")
    if not course.seo_indexable:
        reasons.append("Indexing is disabled for this course.")
    if course.catalogue_role == Course.CatalogueRole.HIDDEN:
        reasons.append("The course is hidden from the public catalogue.")
    if not course.published_lesson_count:
        reasons.append("The course has no published lessons.")
    if not is_course_card_recommendable(course.title, course.summary, course.description):
        reasons.append("The course does not currently meet the public catalogue content checks.")
    return reasons


@login_required
@require_GET
def seo_dashboard(request):
    """Show an audit of public course-overview SEO without exposing lesson content."""
    if not request.user.is_active or not is_course_content_admin(request.user):
        raise PermissionDenied

    global_enabled = bool(getattr(settings, "TRADETHESIS_SEO_INDEXABLE", False))
    courses = (
        Course.objects.annotate(
            published_lesson_count=Count(
                "modules__lessons",
                filter=Q(
                    modules__is_published=True,
                    modules__lessons__is_published=True,
                ),
                distinct=True,
            )
        )
        .order_by("position", "title")
    )

    rows = []
    for course in courses:
        title = _clean_text(course.seo_title) or f"{course.title} · TradeThesis Academy"
        description_source = (
            _clean_text(course.seo_description)
            or _clean_text(course.summary)
            or _clean_text(course.description)
        )
        description = description_source[:320]
        reasons = _course_indexability_reasons(course, global_enabled)
        issues = []

        if not description_source:
            issues.append({
                "level": "warning",
                "label": "No search description",
                "detail": "Add a course summary or SEO description so the public overview has a useful search snippet.",
            })
        elif len(description) > 160:
            issues.append({
                "level": "advice",
                "label": "Description may be truncated",
                "detail": "The current description exceeds 160 characters. Review it for a clearer search snippet.",
            })
        elif len(description) < 70:
            issues.append({
                "level": "advice",
                "label": "Description is brief",
                "detail": "Consider adding what the learner will practise or understand.",
            })

        if len(title) > 70:
            issues.append({
                "level": "advice",
                "label": "Title may be too long",
                "detail": "Review the wording; Google may display a rewritten or shortened title.",
            })
        if not _clean_text(course.seo_primary_topic):
            issues.append({
                "level": "advice",
                "label": "Primary topic not recorded",
                "detail": "Add an editorial topic to keep the page focused. This is for planning, not a meta-keywords tag.",
            })

        rows.append({
            "course": course,
            "title": title,
            "description": description,
            "title_source": "Custom" if _clean_text(course.seo_title) else "Course title fallback",
            "description_source": (
                "Custom" if _clean_text(course.seo_description)
                else "Course copy" if description_source
                else "Missing"
            ),
            "indexable": not reasons,
            "indexability_reasons": reasons,
            "issues": issues,
            "needs_attention": any(issue["level"] == "warning" for issue in issues),
            "published_lesson_count": course.published_lesson_count,
        })

    duplicate_counts = Counter(row["title"].casefold() for row in rows)
    for row in rows:
        if duplicate_counts[row["title"].casefold()] > 1:
            row["issues"].append({
                "level": "warning",
                "label": "Duplicate search title",
                "detail": "Another course currently resolves to the same search title. Give the public pages distinct titles.",
            })
            row["needs_attention"] = True

    published_count = sum(row["course"].status == Course.Status.PUBLISHED for row in rows)
    indexable_count = sum(row["indexable"] for row in rows)
    blocked_count = sum(
        row["course"].status == Course.Status.PUBLISHED and not row["indexable"]
        for row in rows
    )
    missing_description_count = sum(row["description_source"] == "Missing" for row in rows)
    missing_topic_count = sum(not _clean_text(row["course"].seo_primary_topic) for row in rows)
    attention_count = sum(row["needs_attention"] for row in rows)

    query = _clean_text(request.GET.get("q"))
    active_filter = request.GET.get("filter", "all")
    if active_filter not in {"all", "attention", "indexable", "blocked"}:
        active_filter = "all"

    filtered_rows = rows
    if query:
        needle = query.casefold()
        filtered_rows = [
            row for row in filtered_rows
            if needle in row["course"].title.casefold()
            or needle in row["course"].slug.casefold()
            or needle in _clean_text(row["course"].seo_primary_topic).casefold()
        ]
    if active_filter == "attention":
        filtered_rows = [row for row in filtered_rows if row["needs_attention"]]
    elif active_filter == "indexable":
        filtered_rows = [row for row in filtered_rows if row["indexable"]]
    elif active_filter == "blocked":
        filtered_rows = [
            row for row in filtered_rows
            if row["course"].status == Course.Status.PUBLISHED and not row["indexable"]
        ]

    context = {
        "rows": filtered_rows,
        "query": query,
        "active_filter": active_filter,
        "global_indexing_enabled": global_enabled,
        "published_count": published_count,
        "indexable_count": indexable_count,
        "blocked_count": blocked_count,
        "attention_count": attention_count,
        "missing_description_count": missing_description_count,
        "missing_topic_count": missing_topic_count,
        "course_builder_url": reverse("staff_course_builder_preview"),
        "robots_url": request.build_absolute_uri(reverse("academy_robots")),
        "sitemap_url": request.build_absolute_uri(reverse("academy_sitemap")),
    }
    return render(request, "admin/desk_seo.html", context)
