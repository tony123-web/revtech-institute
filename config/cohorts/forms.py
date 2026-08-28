from django import forms
from .models import Discussion


class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = [
            "post_type",
            "title",
            "content",
        ]
        widgets = {
            "post_type": forms.Select(
                attrs={
                    "class": "form-input"
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Discussion title"
                }
            ),

            "content": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "placeholder": "Write your question or idea...",
                    "rows": 7
                }
            ),
        }