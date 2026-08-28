from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("core.urls")),
    path("account/", include("accounts.urls")),
    path("programs/", include("courses.urls")),
    path("cohorts/", include("cohorts.urls")),
    path("projects/", include("projects.urls")),
]