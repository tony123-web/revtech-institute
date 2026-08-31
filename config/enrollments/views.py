from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from cohorts.models import Cohort
from .models import Enrollment

import hashlib
import hmac
import json
import uuid
import requests


def send_enrollment_confirmation_email(
    enrollment,
    reference
):
    student = enrollment.student
    cohort = enrollment.cohort
    program = cohort.program

    dashboard_url = (
        "http://127.0.0.1:8000/dashboard/"
    )

    html_message = render_to_string(
        "enrollments/emails/enrollment_confirmation.html",
        {
            "student": student,
            "enrollment": enrollment,
            "cohort": cohort,
            "program": program,
            "reference": reference,
            "dashboard_url": dashboard_url,
        }
    )

    text_message = (
        f"Hello {student.first_name or student.username},\n\n"
        "Your payment has been successfully verified "
        "and your enrollment is now active.\n\n"
        f"Program: {program.title}\n"
        f"Cohort: {cohort.name}\n"
        f"Amount Paid: ₦{enrollment.amount_paid:,.2f}\n"
        f"Payment Reference: {reference}\n\n"
        "Welcome to RevTech Institute!"
    )

    email = EmailMultiAlternatives(
        subject="Payment Confirmed — Welcome to RevTech Institute",
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[student.email],
    )

    email.attach_alternative(
        html_message,
        "text/html"
    )

    email.send(fail_silently=False)


def verify_and_activate_enrollment(enrollment, reference):

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    verify_url = (
        f"https://api.paystack.co/transaction/verify/{reference}"
    )

    try:
        response = requests.get(
            verify_url,
            headers=headers,
            timeout=30
        )

        data = response.json()

    except requests.RequestException:
        return False, "Could not connect to Paystack."

    except ValueError:
        return False, "Invalid response received from Paystack."

    # Paystack API request itself failed
    if not response.ok or not data.get("status"):
        return False, "Paystack transaction verification failed."

    transaction = data.get("data", {})

    # Transaction must be successful
    if transaction.get("status") != "success":
        return False, "Payment was not successful."

    # Verify the amount
    expected_amount = int(
        enrollment.cohort.price * 100
    )

    paid_amount = transaction.get("amount")

    if paid_amount != expected_amount:
        return False, "Payment amount could not be verified."

    # Make sure the transaction reference matches
    if transaction.get("reference") != reference:
        return False, "Transaction reference mismatch."

    # If already activated, don't process it again
    if enrollment.payment_verified and enrollment.is_active:
        return True, "Enrollment is already active."

    # Payment has been fully verified
    enrollment.payment_verified = True
    enrollment.status = Enrollment.Status.ACTIVE
    enrollment.is_active = True
    enrollment.amount_paid = enrollment.cohort.price
    enrollment.payment_date = timezone.now()

    enrollment.save(
        update_fields=[
            "payment_verified",
            "status",
            "is_active",
            "amount_paid",
            "payment_date",
        ]
    )
    return True, "Payment successful! Your enrollment is now active."

@login_required
def enroll_in_cohort(request, cohort_id):

    cohort = get_object_or_404(
        Cohort,
        id=cohort_id,
        is_open=True
    )

    # Prevent enrollment after registration deadline
    if (
        cohort.registration_deadline
        and cohort.registration_deadline < timezone.now().date()
    ):
        messages.error(
            request,
            "Registration for this cohort has closed."
        )

        return redirect(
            "cohort_detail",
            cohort.slug
        )

    # Check capacity
    active_enrollments = Enrollment.objects.filter(
        cohort=cohort,
        status=Enrollment.Status.ACTIVE
    ).count()

    if active_enrollments >= cohort.capacity:
        messages.error(
            request,
            "This cohort is already full."
        )

        return redirect(
            "cohort_detail",
            cohort.slug
        )

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        cohort=cohort,
        defaults={
            "status": Enrollment.Status.PENDING,
            "is_active": False,
            "payment_verified": False,
        }
    )

    if not created:

        if enrollment.status == Enrollment.Status.ACTIVE:
            messages.info(
                request,
                "You are already enrolled in this cohort."
            )

            return redirect(
                "cohort_detail",
                cohort.slug
            )

        if enrollment.status == Enrollment.Status.PENDING:
            messages.info(
                request,
                "You already have a pending enrollment."
            )

            return redirect(
                "payment",
                enrollment.id
            )

    return redirect(
        "payment",
        enrollment.id
    )

@login_required
def payment_view(request, enrollment_id):

    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        student=request.user,
        status=Enrollment.Status.PENDING
    )

    return render(
        request,
        "enrollments/payment.html",
        {
            "enrollment": enrollment,
            "cohort": enrollment.cohort,
        }
    )

@login_required
def initialize_payment(request, enrollment_id):

    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        student=request.user,
        status=Enrollment.Status.PENDING
    )

    cohort = enrollment.cohort

    # Amount comes from our database.
    amount = int(cohort.price * 100)

    # Generate unique Paystack reference
    reference = f"REVTECH-{uuid.uuid4().hex[:20]}"

    callback_url = request.build_absolute_uri(
        reverse("payment_callback")
    )

    payload = {
        "email": request.user.email,
        "amount": amount,
        "currency": "NGN",
        "reference": reference,
        "callback_url": callback_url,

        "metadata": {
            "enrollment_id": str(enrollment.id),
            "student_id": request.user.id,
            "cohort_id": str(cohort.id),
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=30
        )

        data = response.json()

    except requests.RequestException:
        messages.error(
            request,
            "Unable to connect to Paystack. Please try again."
        )

        return redirect(
            "payment",
            enrollment.id
        )

    except ValueError:
        messages.error(
            request,
            "Invalid response received from Paystack."
        )

        return redirect(
            "payment",
            enrollment.id
        )

    if not response.ok or not data.get("status"):

        # NEVER print your secret key
        print("PAYSTACK RESPONSE:", data)

        messages.error(
            request,
            data.get(
                "message",
                "Unable to initialize payment."
            )
        )

        return redirect(
            "payment",
            enrollment.id
        )

    enrollment.payment_reference = reference

    enrollment.save(
        update_fields=[
            "payment_reference"
        ]
    )

    authorization_url = data["data"]["authorization_url"]

    return redirect(authorization_url)

@login_required
def payment_callback(request):

    reference = request.GET.get("reference")

    if not reference:
        messages.error(
            request,
            "Payment reference was not provided."
        )

        return redirect("cohorts")

    enrollment = get_object_or_404(
        Enrollment,
        payment_reference=reference,
        student=request.user
    )

    success, message = verify_and_activate_enrollment(
        enrollment,
        reference
    )

    if not success:

        messages.error(
            request,
            message
        )

        return redirect(
            "payment",
            enrollment_id=enrollment.id
        )

    messages.success(
        request,
        message
    )

    return redirect("dashboard")

@csrf_exempt
def paystack_webhook(request):

    # Webhook must be POST
    if request.method != "POST":
        return JsonResponse(
            {
                "status": False,
                "message": "Method not allowed"
            },
            status=405
        )

    # Raw Paystack request body
    payload = request.body

    # Paystack signature
    signature = request.headers.get(
        "x-paystack-signature"
    )

    if not signature:
        return JsonResponse(
            {
                "status": False,
                "message": "Missing signature"
            },
            status=400
        )

    # Generate expected signature
    expected_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        payload,
        hashlib.sha512
    ).hexdigest()

    # Secure signature comparison
    if not hmac.compare_digest(
        signature,
        expected_signature
    ):
        return JsonResponse(
            {
                "status": False,
                "message": "Invalid signature"
            },
            status=401
        )

    # Decode JSON
    try:
        data = json.loads(payload)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "status": False,
                "message": "Invalid JSON"
            },
            status=400
        )

    event = data.get("event")
    print("PAYSTACK WEBHOOK RECEIVED:", event)
    transaction_data = data.get(
        "data",
        {}
    )

    # We only process successful charges
    if event != "charge.success":
        return JsonResponse(
            {
                "status": True,
                "message": "Event ignored"
            },
            status=200
        )

    reference = transaction_data.get(
        "reference"
    )
    print("PAYSTACK WEBHOOK REFERENCE:", reference)
    if not reference:
        return JsonResponse(
            {
                "status": False,
                "message": "Missing transaction reference"
            },
            status=400
        )

    # Find enrollment
    try:

        enrollment = Enrollment.objects.get(
            payment_reference=reference
        )

    except Enrollment.DoesNotExist:

        return JsonResponse(
            {
                "status": False,
                "message": "Enrollment not found"
            },
            status=404
        )

    # Verify directly with Paystack
    success, message = verify_and_activate_enrollment(
        enrollment,
        reference
    )

    if not success:

        return JsonResponse(
            {
                "status": False,
                "message": message
            },
            status=400
        )

    return JsonResponse(
        {
            "status": True,
            "message": message
        },
        status=200
    )

# Handle confirmation from LinkAll the central webhook url
@csrf_exempt
def paystack_confirm_revtech(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "status": False,
                "message": "Method not allowed"
            },
            status=405
        )

    provided_secret = request.headers.get(
        "X-RevTech-Webhook-Secret"
    )

    if not provided_secret:
        return JsonResponse(
            {
                "status": False,
                "message": "Missing webhook secret"
            },
            status=401
        )

    if not hmac.compare_digest(
            provided_secret,
            settings.REVTECH_WEBHOOK_SECRET
    ):
        return JsonResponse(
            {
                "status": False,
                "message": "Invalid webhook secret"
            },
            status=401
        )


    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "status": False,
                "message": "Invalid JSON"
            },
            status=400
        )

    reference = data.get("reference")

    if not reference:
        return JsonResponse(
            {
                "status": False,
                "message": "Missing transaction reference"
            },
            status=400
        )

    # Make sure this endpoint only handles RevTech references
    if not reference.startswith("REVTECH-"):
        return JsonResponse(
            {
                "status": False,
                "message": "Invalid RevTech reference"
            },
            status=400
        )

    try:
        enrollment = Enrollment.objects.get(
            payment_reference=reference
        )

    except Enrollment.DoesNotExist:
        return JsonResponse(
            {
                "status": False,
                "message": "Enrollment not found"
            },
            status=404
        )

    # Verify directly with Paystack
    success, message = verify_and_activate_enrollment(
        enrollment,
        reference
    )
    send_enrollment_confirmation_email(
        enrollment,
        reference
    )
    if not success:
        return JsonResponse(
            {
                "status": False,
                "message": message
            },
            status=400
        )

    return JsonResponse(
        {
            "status": True,
            "message": message
        },
        status=200
    )





