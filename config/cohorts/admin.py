from django.contrib import admin

from .models import Cohort, SeminarRoom, SeminarResource,Discussion,DiscussionReply


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "program",
        "start_date",
        "end_date",
        "capacity",
        "is_open",
    )

    list_filter = (
        "is_open",
        "program",
    )

    search_fields = (
        "name",
        "program__title",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    ordering = (
        "-start_date",
    )

@admin.register(SeminarRoom)
class SeminarRoomAdmin(admin.ModelAdmin):
        list_display = (
            "title",
            "cohort",
            "is_active",
            "created_at",
        )

        list_filter = (
            "is_active",
            "cohort",
        )

        search_fields = (
            "title",
            "cohort__name",
        )

@admin.register(SeminarResource)
class SeminarResourceAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "seminar_room",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "seminar_room",
    )

    search_fields = (
        "title",
        "description",
    )

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "post_type",
        "author",
        "seminar_room",
        "is_active",
        "created_at",
    )

    list_filter = (
        "post_type",
        "is_active",
        "seminar_room",
    )

    search_fields = (
        "title",
        "content",
        "author__username",
    )

@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):

    list_display = (
        "discussion",
        "author",
        "created_at",
        "is_active",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "content",
        "author__username",
        "discussion__title",
    )





