from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.course_list,
        name="courses"
    ),

    path(
        "<slug:slug>/",
        views.program_detail,
        name="program_detail"
    ),

]