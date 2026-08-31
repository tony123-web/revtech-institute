from django import forms
from .models import Project



class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project

        fields = [
            "title",
            "description",
            "technologies",
            "github_url",
            "live_url",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Project title"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder": "Describe your project...",
                    "rows": 6
                }
            ),

            "technologies": forms.TextInput(
                attrs={
                    "placeholder": "Python, Django, HTML, CSS, JavaScript"
                }
            ),

            "github_url": forms.URLInput(
                attrs={
                    "placeholder": "https://github.com/..."
                }
            ),

            "live_url": forms.URLInput(
                attrs={
                    "placeholder": "https://..."
                }
            ),
        }


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
class ProjectImageForm(forms.Form):
    images = forms.FileField(
        required=False,
        widget=MultipleFileInput(
            attrs={
                "accept": "image/*"
            }
        ),
        label="Project Screenshots"
    )










