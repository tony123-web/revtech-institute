from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from core.emails import send_brevo_email


class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=True
    )

    last_name = forms.CharField(
        max_length=150,
        required=True
    )

    email = forms.EmailField(
        required=True
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=True
    )


    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email


    def clean_password(self):
        password = self.cleaned_data["password"]

        validate_password(password)

        return password


    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError(
                    "The passwords do not match."
                )

        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "profile_image",
            "phone_number",
            "institution",
            "course",
            "bio",
            "skills",
            "github_url",
            "linkedin_url",
            "portfolio_url",
            "central_url",
        ]

        widgets = {
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*"
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "placeholder": "e.g. 08012345678"
                }
            ),

            "institution": forms.TextInput(
                attrs={
                    "placeholder": "Your university or institution"
                }
            ),

            "course": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Mechanical Engineering"
                }
            ),

            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us briefly about yourself..."
                }
            ),

            "skills": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "e.g. Python, Django, HTML, CSS"
                }
            ),

            "github_url": forms.URLInput(
                attrs={
                    "placeholder": "https://github.com/..."
                }
            ),

            "linkedin_url": forms.URLInput(
                attrs={
                    "placeholder": "https://linkedin.com/in/..."
                }
            ),

            "portfolio_url": forms.URLInput(
                attrs={
                    "placeholder": "https://..."
                }
            ),

            "central_url": forms.URLInput(
                attrs={
                    "placeholder": "https://..."
                }
            ),
        }

class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email address"
            }
        )
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password"
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            email = email.lower()

            try:
                user = User.objects.get(
                    email__iexact=email
                )
            except User.DoesNotExist:
                raise forms.ValidationError(
                    "Invalid email or password."
                )

            user = authenticate(
                username=user.username,
                password=password
            )

            if user is None:
                raise forms.ValidationError(
                    "Invalid email or password."
                )

            if not user.is_active:
                raise forms.ValidationError(
                    "Please verify your email before logging in."
                )

            cleaned_data["user"] = user

        return cleaned_data

class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True
    )

    last_name = forms.CharField(
        max_length=150,
        required=True
    )

    email = forms.EmailField(
        required=True
    )

    class Meta:
        model = Profile
        fields = [
            "profile_image",
            "phone_number",
            "institution",
            "course",
            "bio",
            "skills",
            "github_url",
            "linkedin_url",
            "portfolio_url",
            "central_url",
        ]

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

        # Put account fields first
        self.order_fields([
            "first_name",
            "last_name",
            "email",
            "profile_image",
            "phone_number",
            "institution",
            "course",
            "bio",
            "skills",
            "github_url",
            "linkedin_url",
            "portfolio_url",
            "central_url",
        ])


class RevTechPasswordResetForm(PasswordResetForm):

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = render_to_string(
            subject_template_name,
            context
        ).strip()

        text_message = render_to_string(
            email_template_name,
            context
        )

        html_message = ""

        if html_email_template_name:
            html_message = render_to_string(
                html_email_template_name,
                context
            )

        send_brevo_email(
            recipient_email=to_email,
            recipient_name=context["user"].get_full_name(),
            subject=subject,
            html_content=html_message,
            text_content=text_message,
        )





