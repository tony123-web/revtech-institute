from django.urls import path

from . import views


urlpatterns = [

    path(
        "enroll/<uuid:cohort_id>/",
        views.enroll_in_cohort,
        name="enroll_in_cohort"
    ),
    path(
            "payment/<uuid:enrollment_id>/",
            views.payment_view,
            name="payment"
    ),
    path(
            "payment/<uuid:enrollment_id>/initialize/",
            views.initialize_payment,
            name="initialize_payment"
    ),
    path(
        "payment/callback/",
        views.payment_callback,
        name="payment_callback"
    ),
    path(
        "payment/webhook/",
        views.paystack_webhook,
        name="paystack_webhook",
    ),
# Handle confirmation from LinkAll the central webhook url
    path(
        "payment/paystack-confirm/",
        views.paystack_confirm_revtech,
        name="paystack_confirm_revtech",
    ),
]