"""Forms for support tickets and follow-up replies."""
import os

from PIL import Image, UnidentifiedImageError
from django import forms

from .models import (
    ALLOWED_IMAGE_EXTENSIONS,
    IMAGE_FORMATS_BY_EXTENSION,
    MAX_ATTACHMENT_BYTES,
    MAX_ATTACHMENTS_PER_TICKET,
    AffiliateLink,
    SupportTicket,
)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """FileField that accepts multiple uploads (Django 3.2+ pattern)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_clean(d, initial) for d in data]
            if len(result) > MAX_ATTACHMENTS_PER_TICKET:
                raise forms.ValidationError(
                    f"Too many files: maximum {MAX_ATTACHMENTS_PER_TICKET} screenshots.")
            return result
        return single_clean(data, initial)


class SupportTicketForm(forms.ModelForm):
    affiliate_link = forms.ModelChoiceField(
        queryset=AffiliateLink.objects.filter(is_active=True),
        required=False,
        label="Referral link used",
        help_text="Which of our referral links you signed up through.",
    )
    attachments = MultipleFileField(
        required=False,
        label="Screenshots",
        help_text=f"Up to {MAX_ATTACHMENTS_PER_TICKET} images (PNG/JPG/GIF/WEBP, max 5 MB each). "
                  "Required for access requests; optional for other issues.")

    class Meta:
        model = SupportTicket
        fields = ["category", "affiliate_link", "message"]
        widgets = {
            "category": forms.Select(attrs={"autocomplete": "off"}),
            "message": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Describe your request or issue...",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attachments"].widget.attrs.update({
            "accept": "image/png,image/jpeg,image/gif,image/webp",
        })

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get("category")
        attachments = cleaned.get("attachments") or []

        for upload in attachments:
            filename = getattr(upload, "name", "") or ""
            extension = os.path.splitext(filename)[1].lower()
            if extension not in ALLOWED_IMAGE_EXTENSIONS:
                self.add_error(
                    "attachments",
                    f"{filename or 'File'}: Only PNG, JPG, JPEG, GIF and WEBP images are allowed.",
                )
                continue
            if (getattr(upload, "size", 0) or 0) > MAX_ATTACHMENT_BYTES:
                self.add_error(
                    "attachments",
                    f"{filename}: Each image must be 5 MB or smaller.",
                )
                continue

            stream = getattr(upload, "file", upload)
            try:
                original_position = stream.tell()
            except (AttributeError, OSError):
                original_position = 0
            try:
                image = Image.open(stream)
                image_format = image.format
                image.verify()
                if image_format not in IMAGE_FORMATS_BY_EXTENSION[extension]:
                    raise ValueError("extension mismatch")
            except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
                self.add_error(
                    "attachments",
                    f"{filename}: This file is not a valid image matching its extension.",
                )
            finally:
                try:
                    stream.seek(original_position)
                except (AttributeError, OSError):
                    pass

        if category == SupportTicket.Category.ACCESS:
            if not cleaned.get("affiliate_link"):
                self.add_error("affiliate_link", "Select the referral link you used.")
            elif not cleaned["affiliate_link"].is_active:
                self.add_error("affiliate_link", "Select an active referral link.")
            if not attachments:
                self.add_error("attachments", "Upload at least one screenshot for access requests.")
        return cleaned


class TicketReplyForm(forms.Form):
    body = forms.CharField(
        max_length=10000,
        label="Your reply",
        widget=forms.Textarea(attrs={
            "rows": 4,
            "placeholder": "Add information that may help resolve this ticket...",
        }),
    )
