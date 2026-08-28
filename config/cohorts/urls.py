from django.urls import path

from . import views


urlpatterns = [
    path("", views.cohort_list, name="cohorts"),
]