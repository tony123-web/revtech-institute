from django.urls import path
from . import views

urlpatterns = [
    path("", views.store_home, name="store_home"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("request-device/", views.request_device, name="request_device"),
]
