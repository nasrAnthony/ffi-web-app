from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

from .models import BlogPost

class ContactForm(forms.Form):
    name = forms.CharField(
        label="Full name",
        max_length=120,
        widget=forms.TextInput(attrs={
            "id": "cf-name",
            "placeholder": "Your Name",
            "autocomplete": "name",
            "required": True,
        }),
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "id": "cf-email",
            "placeholder": "you@example.com",
            "autocomplete": "email",
            "required": True,
        }),
    )

    phone = forms.CharField(
        label="Phone",
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            "id": "cf-phone",
            "placeholder": "Your Phone Number",
            "autocomplete": "tel",
            "inputmode": "numeric",
            "pattern": r"\d{10,15}",
            "title": "Please enter digits only (10–15 numbers)",
            "aria-describedby": "phone-help",
        }),
    )

    preferred_contact = forms.ChoiceField(
        label="Preferred method of communication",
        choices=[("email", "Email"), ("phone", "Phone")],
        widget=forms.RadioSelect(attrs={"class": "radio-option"}),
        initial="email",
    )

    topic = forms.ChoiceField(
        label="Topic",
        choices=[
            ("General Question", "General Question"),
            ("Insurance", "Insurance"),
            ("Investments", "Investments"),
            ("Request Financial Planning", "Request Financial Planning"),
        ],
        widget=forms.Select(attrs={"id": "cf-topic", "aria-label": "Topic"}),
    )

    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={
            "id": "cf-msg",
            "rows": 5,
            "placeholder": "How can we help?",
            "required": True,
        }),
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class BlogBatchUploadForm(forms.Form):
    batch_file = forms.FileField(
        label="Blog batch JSON",
        help_text="Upload a .json file matching the sample schema for up to 10 posts.",
    )

    def clean_batch_file(self):
        batch_file = self.cleaned_data["batch_file"]
        if not batch_file.name.lower().endswith(".json"):
            raise forms.ValidationError("Please upload a .json file.")
        return batch_file


class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = "__all__"
