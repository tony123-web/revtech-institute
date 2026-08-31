from django import forms
from .models import AssignmentSubmission


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission

        fields = [
            "github_url",
            "comment",
        ]

        widgets = {
            "github_url": forms.URLInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "https://github.com/username/project"
                }
            ),

            "comment": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "placeholder": "Tell your instructor about your submission...",
                    "rows": 5,
                }
            ),
        }