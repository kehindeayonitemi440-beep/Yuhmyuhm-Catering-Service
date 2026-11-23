import os

from django import forms
from .models import Enquiry, Payment


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ["name", "email", "phone", "event_type", "event_date", "guests", "cuisine", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "guests": forms.NumberInput(attrs={"min": 1, "placeholder": "e.g. 80"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class TransferForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["sender_name", "transfer_note", "proof"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sender_name"].required = True

    def clean_proof(self):
        f = self.cleaned_data.get("proof")
        if f:
            if f.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File is larger than 5 MB.")
            if os.path.splitext(f.name)[1].lower() not in (".jpg", ".jpeg", ".png", ".pdf", ".webp"):
                raise forms.ValidationError("Upload a JPG, PNG, WEBP or PDF file.")
        return f
