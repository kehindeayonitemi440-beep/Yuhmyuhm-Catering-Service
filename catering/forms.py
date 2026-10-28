from django import forms
from .models import Enquiry


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ["name", "event_type", "event_date", "guests", "cuisine", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "guests": forms.NumberInput(attrs={"min": 1, "placeholder": "e.g. 80"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
