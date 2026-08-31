from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.project_list,
        name="project_list"
    ),

    path(
        "<uuid:project_id>/",
        views.project_detail,
        name="project_detail"
    ),
    path(
        "submit/",
        views.project_create,
        name="project_create"
    ),
    path(
        "my-projects/",
        views.my_projects,
        name="my_projects"
    ),
    path(
        "<uuid:project_id>/edit/",
        views.project_edit,
        name="project_edit"
    ),
]
