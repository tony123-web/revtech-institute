from urllib.parse import quote
from django.conf import settings
from django.shortcuts import get_object_or_404, render,redirect
from django.db.models import Q
from .models import Product,DeviceRequest
import logging
from django.contrib import messages
from core.emails import device_request_email
from .forms import DeviceRequestForm

def store_home(request):
    products = Product.objects.filter(
        is_published=True
    ).prefetch_related("images")

    search_query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(brand__icontains=search_query)
            | Q(model_name__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    valid_categories = Product.Category.values

    if category in valid_categories:
        products = products.filter(category=category)

    context = {
        "products": products,
        "categories": Product.Category.choices,
        "selected_category": category,
        "search_query": search_query,
    }

    return render(request, "store/store_home.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("images"),
        slug=slug,
        is_published=True,
    )

    whatsapp_number = getattr(
        settings,
        "REVTECH_WHATSAPP_NUMBER",
        "",
    )

    whatsapp_number = "".join(
        char for char in whatsapp_number if char.isdigit()
    )

    whatsapp_url = None

    if (
        whatsapp_number
        and product.availability
        != Product.Availability.DISCONTINUED
    ):
        message = (
            f"Hello RevTech, I am interested in "
            f"{product.brand} {product.name}. model is {product.model_name}"
            f"Please provide more information about "
            f"its price and availability."
        )
        whatsapp_url = (
            f"https://wa.me/{whatsapp_number}"
            f"?text={quote(message)}"
        )

    context = {
        "product": product,
        "images": product.images.all(),
        "whatsapp_url": whatsapp_url,
    }

    return render(
        request,
        "store/product_detail.html",
        context,
    )


logger = logging.getLogger(__name__)


def request_device(request):
    if request.method == "POST":
        form = DeviceRequestForm(request.POST)

        if form.is_valid():
            device_request = form.save()

            budget = "Not specified"
            if (
                device_request.budget_min is not None
                or device_request.budget_max is not None
            ):
                minimum = (
                    f"₦{device_request.budget_min:,.2f}"
                    if device_request.budget_min is not None
                    else "No minimum"
                )
                maximum = (
                    f"₦{device_request.budget_max:,.2f}"
                    if device_request.budget_max is not None
                    else "No maximum"
                )
                budget = f"{minimum} – {maximum}"

            subject = (
                f"New RevTech Store device request: "
                f"{device_request.get_device_type_display()}"
            )

            message = f"""
                            A new device request has been submitted on RevTech Store.
                            
                            Request ID: {device_request.id}
                            
                            CUSTOMER
                            Name: {device_request.full_name}
                            Phone: {device_request.phone_number}
                            Email: {device_request.email or "Not provided"}
                            
                            DEVICE REQUIREMENTS
                            Device type: {device_request.get_device_type_display()}
                            Preferred brand: {device_request.preferred_brand or "Not specified"}
                            Budget: {budget}
                            Condition: {device_request.get_condition_preference_display()}
                            Intended use: {device_request.intended_use or "Not specified"}
                            
                            Specifications:
                            {device_request.specifications}
                            
                            Log in to the RevTech admin dashboard to review and manage this request.
            """
            student=settings.REVTECH_STORE_NOTIFICATION_EMAIL
            try:
                device_request_email(student, message, subject, device_request)
            except Exception:
                # The request is already saved, so don't lose it
                # just because the email service failed.
                logger.exception(
                    "Email notification failed for device request %s",
                    device_request.id,
                )

            messages.success(
                request,
                "Your device request has been submitted successfully. "
                "RevTech will contact you about your requirements.",
            )
            return redirect("request_device")

    else:
        form = DeviceRequestForm()

    return render(
        request,
        "store/request_device.html",
        {"form": form},
    )



