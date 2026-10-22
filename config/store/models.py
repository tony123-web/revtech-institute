import uuid
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator


def product_image_upload_path(instance, filename):
    return f"store/products/{instance.product.id}/{filename}"


class Product(models.Model):
    class Category(models.TextChoices):
        LAPTOP = "laptop", "Laptop"
        SMARTPHONE = "smartphone", "Smartphone"
        TABLET = "tablet", "Tablet"
        ACCESSORY = "accessory", "Accessory"
        OTHER = "other", "Other"

    class Condition(models.TextChoices):
        NEW = "new", "New"
        USED = "used", "Used"
        REFURBISHED = "refurbished", "Refurbished"

    class Availability(models.TextChoices):
        AVAILABLE = "available", "Available"
        OUT_OF_STOCK = "out_of_stock", "Out of stock"
        PRE_ORDER = "pre_order", "Available on request"
        DISCONTINUED = "discontinued", "Discontinued"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.LAPTOP,
    )

    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=150, blank=True)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    condition = models.CharField(
        max_length=20,
        choices=Condition.choices,
        default=Condition.USED,
    )

    availability = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
    )

    specifications = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            'Enter specifications as JSON, e.g. '
            '{"processor": "Core i5", "ram": "8GB", "storage": "512GB SSD"}'
        ),
    )

    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "product"
            candidate = base_slug
            counter = 2

            while Product.objects.filter(
                slug=candidate
            ).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1

            self.slug = candidate

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.name}"


class ProductImage(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to=product_image_upload_path,
    )

    alt_text = models.CharField(max_length=200, blank=True)

    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "created_at"]
        verbose_name = "Product image"
        verbose_name_plural = "Product images"

    def __str__(self):
        return f"Image for {self.product.name}"



class DeviceRequest(models.Model):
    class DeviceType(models.TextChoices):
        LAPTOP = "laptop", "Laptop"
        SMARTPHONE = "smartphone", "Smartphone"
        TABLET = "tablet", "Tablet"
        OTHER = "other", "Other"

    class ConditionPreference(models.TextChoices):
        ANY = "any", "New or used"
        NEW = "new", "New"
        USED = "used", "Used"
        REFURBISHED = "refurbished", "Refurbished"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONTACTED = "contacted", "Customer contacted"
        SOURCING = "sourcing", "Sourcing device"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
    )

    preferred_brand = models.CharField(
        max_length=100,
        blank=True,
    )

    budget_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    budget_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    condition_preference = models.CharField(
        max_length=20,
        choices=ConditionPreference.choices,
        default=ConditionPreference.ANY,
    )

    intended_use = models.CharField(
        max_length=200,
        blank=True,
        help_text="For example: programming, engineering, study or business.",
    )

    specifications = models.TextField(
        help_text="Describe the device or specifications you need.",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Device Request"
        verbose_name_plural = "Device Requests"

    def __str__(self):
        return f"{self.full_name} - {self.get_device_type_display()}"




