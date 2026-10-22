from django import forms
from .models import DeviceRequest


class DeviceRequestForm(forms.ModelForm):
    class Meta:
        model = DeviceRequest
        fields = [
            "full_name",
            "phone_number",
            "email",
            "device_type",
            "preferred_brand",
            "budget_min",
            "budget_max",
            "condition_preference",
            "intended_use",
            "specifications",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Your full name",
            }),
            "phone_number": forms.TextInput(attrs={
                "placeholder": "e.g. 08012345678",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Your email address (optional)",
            }),
            "preferred_brand": forms.TextInput(attrs={
                "placeholder": "e.g. HP, Dell, Apple, Samsung",
            }),
            "budget_min": forms.NumberInput(attrs={
                "placeholder": "Minimum budget (₦)",
                "min": "0",
                "step": "0.01",
            }),
            "budget_max": forms.NumberInput(attrs={
                "placeholder": "Maximum budget (₦)",
                "min": "0",
                "step": "0.01",
            }),
            "intended_use": forms.TextInput(attrs={
                "placeholder": "e.g. programming, engineering, study",
            }),
            "specifications": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": (
                    "Describe the device you need, such as RAM, storage, "
                    "processor, battery life, or other requirements."
                ),
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        minimum = cleaned_data.get("budget_min")
        maximum = cleaned_data.get("budget_max")

        if (
            minimum is not None
            and maximum is not None
            and maximum < minimum
        ):
            self.add_error(
                "budget_max",
                "Maximum budget cannot be lower than minimum budget.",
            )

        return cleaned_data
