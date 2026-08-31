from django.contrib.auth import login,logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .forms import RegistrationForm, ProfileForm, LoginForm,ProfileEditForm
from .models import Profile, EmailVerificationToken
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)



def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend"
            )

            if user.profile.is_complete:
                return redirect("dashboard")

            return redirect("complete_profile")

    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )

def logout_view(request):
    logout(request)
    return redirect('/')

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            base_username = email.split("@")[0]
            username = base_username
            counter = 1

            while User.objects.filter(
                username=username
            ).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False,
            )

            Profile.objects.create(
                user=user,
                role=Profile.Role.STUDENT
            )

            verification = EmailVerificationToken.objects.create(
                user=user
            )

            verification_url = request.build_absolute_uri(
                reverse(
                    "verify_email",
                    kwargs={
                        "token": verification.token
                    }
                )
            )

            html_message = render_to_string(
                "accounts/emails/verification_email.html",
                {
                    "first_name": first_name,
                    "verification_url": verification_url,
                }
            )

            text_message = (
                f"Hello {first_name},\n\n"
                "Welcome to RevTech Institute!\n\n"
                "Please verify your email address using the link below:\n\n"
                f"{verification_url}\n\n"
                "If you did not create this account, "
                "you can safely ignore this email.\n\n"
                "Regards,\n"
                "RevTech Institute"
            )

            email_message = EmailMultiAlternatives(
                subject="Verify your RevTech Institute account",
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )

            email_message.attach_alternative(
                html_message,
                "text/html"
            )

            email_message.send(
                fail_silently=False
            )

            return redirect("verification_sent")

    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )

def verify_email_view(request, token):

    try:
        verification = EmailVerificationToken.objects.get(
            token=token
        )

    except EmailVerificationToken.DoesNotExist:
        return render(
            request,
            "accounts/verification_invalid.html"
        )

    user = verification.user

    # Token expires after 24 hours
    if verification.is_expired:
        return render(
            request,
            "accounts/verification_expired.html",
            {
                "email": user.email
            }
        )

    # Already verified
    if user.is_active:

        verification.delete()

        return redirect("login")

    # Activate account
    user.is_active = True

    user.save(
        update_fields=["is_active"]
    )

    # Token can no longer be used
    verification.delete()

    return render(
        request,
        "accounts/verification_success.html"
    )

def verification_sent_view(request):
    return render(
        request,
        "accounts/verification_sent.html"
    )


def resend_verification_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        if not email:
            return render(
                request,
                "accounts/resend_verification.html",
                {
                    "error": "Please enter your email address."
                }
            )

        try:
            user = User.objects.get(
                email__iexact=email
            )

        except User.DoesNotExist:

            # Do not reveal whether the account exists.
            return redirect("verification_sent")

        # Account already verified
        if user.is_active:
            return redirect("login")

        try:
            verification = (
                EmailVerificationToken.objects.get(
                    user=user
                )
            )

            # Prevent repeated requests
            # within 60 seconds.
            elapsed = (
                timezone.now()
                - verification.created_at
            )

            if elapsed < timedelta(seconds=60):

                remaining = 60 - int(
                    elapsed.total_seconds()
                )

                return render(
                    request,
                    "accounts/resend_verification.html",
                    {
                        "error": (
                            f"Please wait {remaining} "
                            "seconds before requesting "
                            "another verification email."
                        ),
                        "email": email,
                    }
                )

            # Existing token is old enough.
            # Remove it before creating a new one.
            verification.delete()

        except EmailVerificationToken.DoesNotExist:
            pass

        # Create a fresh verification token
        verification = EmailVerificationToken.objects.create(
            user=user
        )

        verification_url = request.build_absolute_uri(
            reverse(
                "verify_email",
                kwargs={
                    "token": verification.token
                }
            )
        )

        html_message = render_to_string(
            "accounts/emails/verification_email.html",
            {
                "first_name": user.first_name,
                "verification_url": verification_url,
            }
        )

        text_message = (
            f"Hello {user.first_name},\n\n"
            "Here is your new RevTech Institute "
            "email verification link:\n\n"
            f"{verification_url}\n\n"
            "This link will expire in 24 hours.\n\n"
            "If you did not create this account, "
            "you can safely ignore this email.\n\n"
            "Regards,\n"
            "RevTech Institute"
        )

        email_message = EmailMultiAlternatives(
            subject="Verify your RevTech Institute account",
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email_message.attach_alternative(
            html_message,
            "text/html"
        )

        email_message.send(
            fail_silently=False
        )

        return redirect("verification_sent")

    return render(
        request,
        "accounts/resend_verification.html"
    )


@login_required
def complete_profile_view(request):
    profile = request.user.profile
    if profile.is_complete:
        return redirect("dashboard")
    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )
        if form.is_valid():
            form.save()
            if profile.is_complete:
                return redirect("dashboard")
    else:
        form = ProfileForm(
            instance=profile
        )
    return render(
        request,
        "accounts/complete_profile.html",
        {
            "form": form
        }
    )


@login_required
def profile_view(request):
    profile = request.user.profile
    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
        }
    )

@login_required
def edit_profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileEditForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user
        )

        if form.is_valid():

            # Update Profile
            form.save()

            # Update User information
            request.user.first_name = form.cleaned_data[
                "first_name"
            ]

            request.user.last_name = form.cleaned_data[
                "last_name"
            ]

            request.user.email = form.cleaned_data[
                "email"
            ]

            request.user.save(
                update_fields=[
                    "first_name",
                    "last_name",
                    "email",
                ]
            )

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect(
                "profile"
            )

    else:

        form = ProfileEditForm(
            instance=profile,
            user=request.user
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form,
            "profile": profile,
        }
    )



class RevTechPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/emails/password_reset_email.txt"
    html_email_template_name = "accounts/emails/password_reset_email.html"
    subject_template_name = "accounts/emails/password_reset_subject.txt"
    success_url = "/account/password-reset/done/"


class RevTechPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class RevTechPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = "/account/password-reset/complete/"


class RevTechPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
