from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("core-cohort/<slug:slug>/",views.core_cohort_detail,name="core_cohort_detail"),
    path("module/<uuid:module_id>/",views.module_detail,name="module_detail"),
    path("cohort/<uuid:cohort_id>/seminar-room/",views.seminar_room,name="seminar_room"),
    path("cohort/<uuid:cohort_id>/discussions/",views.discussions,name="discussions"),
    path("cohort/<uuid:cohort_id>/discussions/new/",views.create_discussion,name="create_discussion"),
    path("discussion/<uuid:discussion_id>/",views.discussion_detail,name="discussion_detail"),
    path("discussion/<uuid:discussion_id>/reply/",views.create_reply,name="create_reply"),
    path("lesson/<uuid:lesson_id>/",views.lesson_detail,name="lesson_detail",),
    path("lesson/<uuid:lesson_id>/video/",views.lesson_video_url,name="lesson_video_url"),
    path("lesson/<uuid:lesson_id>/progress/",views.update_lesson_progress,name="update_lesson_progress",),
    path("assignment/<uuid:assignment_id>/",views.assignment_detail,name="assignment_detail",),
    path("submission/<uuid:submission_id>/review/",views.review_submission,name="review_submission",),
]


