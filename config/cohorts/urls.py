from django.urls import path

from .views import cohort_list, cohort_detail,upcoming_cohort


urlpatterns = [
    path(
        "",
        cohort_list,
        name="cohorts"
    ),
    path(
        "upcoming/",
        upcoming_cohort,
        name="recent_upcoming_cohort"
    ),
    path(
        "<slug:slug>/",
        cohort_detail,
        name="cohort_detail"
    ),

]