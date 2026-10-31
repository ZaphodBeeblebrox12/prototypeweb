from django import forms

from .models import STARTING_POINT_CHOICES


class ProspectEnquiryForm(forms.Form):
    name = forms.CharField(max_length=120, label="Your name")
    email = forms.EmailField(label="Email address")
    phone = forms.CharField(max_length=40, required=False, label="Phone or WhatsApp (optional)")
    starting_point = forms.ChoiceField(
        choices=[("", "Choose one (optional)"), *STARTING_POINT_CHOICES[1:]],
        required=False,
        label="Where are you starting from?",
    )
    question = forms.CharField(
        max_length=2000,
        required=False,
        label="What would you most like to know?",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    contact_consent = forms.BooleanField(
        required=True,
        label="TradeThesis may contact me about this enquiry using the details I provided.",
        error_messages={"required": "Please confirm that we may contact you about this enquiry."},
    )
    marketing_opt_in = forms.BooleanField(
        required=False,
        label="Send me occasional TradeThesis course and learning updates (optional).",
    )
    # Honeypot. It is visually hidden from people but remains in the HTML for basic bot traps.
    website = forms.CharField(required=False, label="Leave this field empty")

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_name(self):
        return " ".join(self.cleaned_data["name"].split())
