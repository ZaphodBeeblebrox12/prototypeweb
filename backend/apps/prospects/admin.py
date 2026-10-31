from django.contrib import admin

from .models import ProspectEnquiry


@admin.register(ProspectEnquiry)
class ProspectEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "short_reference", "programme", "name", "email", "status", "created_at",
    )
    list_filter = ("programme", "status", "created_at")
    search_fields = ("name", "email", "question")
    readonly_fields = tuple(
        field.name for field in ProspectEnquiry._meta.fields
        if field.name not in {"status", "staff_notes", "assigned_to"}
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
