from django.contrib import admin
from .models import Product, ProductImage,DeviceRequest


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ("image", "alt_text", "sort_order")
    ordering = ("sort_order",)
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "category",
        "price",
        "condition",
        "availability",
        "is_published",
        "is_featured",
    )

    list_filter = (
        "category",
        "condition",
        "availability",
        "is_published",
        "is_featured",
    )

    search_fields = ("name", "brand", "model_name")
    list_editable = ("is_published", "is_featured")
    inlines = [ProductImageInline]

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Product information", {
            "fields": (
                "name",
                "slug",
                "category",
                "brand",
                "model_name",
                "description",
            )
        }),
        ("Price and availability", {
            "fields": (
                "price",
                "condition",
                "availability",
            )
        }),
        ("Specifications", {
            "fields": ("specifications",)
        }),
        ("Publication", {
            "fields": (
                "is_published",
                "is_featured",
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "image",
        "alt_text",
        "sort_order",
        "created_at",
    )

    list_filter = ("created_at",)
    search_fields = (
        "product__name",
        "product__brand",
        "alt_text",
    )

    list_select_related = ("product",)
    ordering = ("product__name", "sort_order")
    readonly_fields = ("created_at",)

    fields = (
        "product",
        "image",
        "alt_text",
        "sort_order",
        "created_at",
    )


@admin.register(DeviceRequest)
class DeviceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "device_type",
        "phone_number",
        "budget_max",
        "status",
        "created_at",
    )

    list_filter = (
        "device_type",
        "condition_preference",
        "status",
        "created_at",
    )

    search_fields = (
        "full_name",
        "phone_number",
        "email",
        "preferred_brand",
        "specifications",
    )

    list_editable = ("status",)
    list_select_related = False
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        ("Customer Information", {
            "fields": (
                "id",
                "full_name",
                "phone_number",
                "email",
            )
        }),
        ("Device Requirements", {
            "fields": (
                "device_type",
                "preferred_brand",
                "budget_min",
                "budget_max",
                "condition_preference",
                "intended_use",
                "specifications",
            )
        }),
        ("Request Management", {
            "fields": (
                "status",
                "admin_notes",
                "created_at",
                "updated_at",
            )
        }),
    )



