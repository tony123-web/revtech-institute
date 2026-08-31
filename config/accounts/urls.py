from django.urls import path

from .import views
from .views import (
    RevTechPasswordResetView,
    RevTechPasswordResetDoneView,
    RevTechPasswordResetConfirmView,
    RevTechPasswordResetCompleteView,
)


urlpatterns = [
    path(
        "register/",
        views.register_view,
        name="register"
    ),

    path(
        "verify/<uuid:token>/",
        views.verify_email_view,
        name="verify_email"
    ),

    path(
        "verification-sent/",
        views.verification_sent_view,
        name="verification_sent"
    ),
    path(
        "verification/resend/",
        views.resend_verification_view,
        name="resend_verification",
    ),
    path(
        "profile/complete/",
        views.complete_profile_view,
        name="complete_profile"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),
    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
    path(
        "password-reset/",
        RevTechPasswordResetView.as_view(),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        RevTechPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),

    path(
        "password-reset/<uidb64>/<token>/",
        RevTechPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    path(
        "password-reset/complete/",
        RevTechPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "profile/",
        views.profile_view,
        name="profile"
    ),

    path(
        "profile/edit/",
        views.edit_profile_view,
        name="edit_profile"
    ),
]