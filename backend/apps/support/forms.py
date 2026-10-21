"""Forms for support tickets."""
import os

from django import forms

from .models import (
    ALLOWED_IMAGE_EXTENSIONS,
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

        # Validate every upload before the view writes the ticket or attachment.
        # TicketAttachment.save() repeats these checks defensively, but invalid
        # uploads should produce a bound-form error instead of a server error.
        for upload in attachments:
            extension = os.path.splitext(getattr(upload, "name", "") or "")[1].lower()
            if extension not in ALLOWED_IMAGE_EXTENSIONS:
                self.add_error(
                    "attachments",
                    f"{getattr(upload, 'name', 'File')}: Only PNG, JPG, JPEG, GIF and WEBP images are allowed.",
                )
                continue
            if (getattr(upload, "size", 0) or 0) > MAX_ATTACHMENT_BYTES:
                self.add_error(
                    "attachments",
                    f"{getattr(upload, 'name', 'File')}: Each image must be 5 MB or smaller.",
                )

        if category == SupportTicket.Category.ACCESS:
            if not cleaned.get("affiliate_link"):
                self.add_error("affiliate_link", "Select the referral link you used.")
            if not attachments:
                self.add_error("attachments", "Upload at least one screenshot for access requests.")
        return cleaned
