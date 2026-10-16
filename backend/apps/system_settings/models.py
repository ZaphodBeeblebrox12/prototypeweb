"""
System settings models for community platform.
"""
from django.db import models


class SystemSetting(models.Model):
    """Key-value system settings."""

    key = models.CharField(max_length=255, unique=True, db_index=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_public = models.BooleanField(
        default=False,
        help_text="If True, this setting can be read by non-admin users"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.key

    @classmethod
    def get(cls, key, default=None):
        """Get setting value by key."""
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set(cls, key, value, description="", is_public=False):
        """Set setting value by key."""
        obj, created = cls.objects.update_or_create(
            key=key,
            defaults={
                "value": value,
                "description": description,
                "is_public": is_public,
            }
        )
        return obj
