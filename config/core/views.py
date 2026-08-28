from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from cohorts.models import SeminarRoom, Discussion
from courses.models import Lesson,LessonProgress,Module
from cohorts.forms import DiscussionForm
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


def home(request):
    return render(request, "core/home.html")


def about(request):
    return render(request, "core/about.html")


def contact(request):
    return render(request, "core/contact.html")


@login_required
def dashboard(request):

    enrollments = request.user.enrollments.filter(
        is_active=True
    ).select_related(
        "cohort",
        "cohort__program"
    )

    for enrollment in enrollments:

        cohorts = enrollment.cohort

        total_lessons = cohorts.modules.aggregate(
            total=Count("lessons")
        )["total"] or 0

        completed_lessons = cohorts.modules.aggregate(
            completed=Count(
                "lessons",
                filter=Q(
                    lessons__student_progress__student=request.user,
                    lessons__student_progress__completed=True
                )
            )
        )["completed"] or 0

        if total_lessons > 0:
            progress = round(
                (completed_lessons / total_lessons) * 100
            )
        else:
            progress = 0

        enrollment.progress = progress
        enrollment.total_lessons = total_lessons
        enrollment.completed_lessons = completed_lessons

        next_lesson = None

        modules = cohorts.modules.prefetch_related(
            "lessons"
        ).all()

        for module in modules:
            for lesson in module.lessons.all():

                completed = lesson.student_progress.filter(
                    student=request.user,
                    completed=True
                ).exists()

                if not completed:
                    next_lesson = lesson
                    break

            if next_lesson:
                break

        enrollment.next_lesson = next_lesson

    context = {
        "enrollments": enrollments,
    }

    return render(
        request,
        "core/dashboard.html",
        context
    )

@login_required
def cohort_detail(request, cohort_id):
    enrollment = get_object_or_404(
        request.user.enrollments.select_related(
            "cohort",
            "cohort__program"
        ),
        cohort_id=cohort_id,
        is_active=True
    )

    cohort = enrollment.cohort

    modules = cohort.modules.filter(
        is_active=True
    ).prefetch_related(
        "lessons"
    )

    return render(
        request,
        "core/cohort_detail.html",
        {
            "cohort": cohort,
            "modules": modules,
        }
    )

@login_required
def module_detail(request, module_id):
    module = get_object_or_404(
        Module.objects.select_related(
            "cohort",
            "cohort__program"
        ),
        id=module_id,
        is_active=True
    )

    # Make sure the student belongs to this module's cohort
    enrollment = request.user.enrollments.filter(
        cohort=module.cohort,
        is_active=True
    ).first()

    if not enrollment:
        return render(
            request,
            "core/access_denied.html",
            status=403
        )

    lessons = module.lessons.filter(
        is_active=True
    )

    return render(
        request,
        "core/module_detail.html",
        {
            "module": module,
            "lessons": lessons,
            "cohort": module.cohort,
        }
    )

@login_required
def seminar_room(request, cohort_id):
    seminar_room = get_object_or_404(
        SeminarRoom,
        cohort_id=cohort_id,
        is_active=True
    )
    enrollment = request.user.enrollments.filter(
        cohort_id=cohort_id,
        is_active=True
    ).first()
    if not enrollment:
        return render(
            request,
            "core/access_denied.html",
            status=403
        )
    resources = seminar_room.resources.filter(
        is_active=True
    )

    context = {
        "seminar_room": seminar_room,
        "cohort": seminar_room.cohort,
        "resources": resources,
    }

    return render(
        request,
        "core/seminar_room.html",
        context
    )

@login_required
def discussions(request, cohort_id):
    seminar_room = get_object_or_404(
        SeminarRoom,
        cohort_id=cohort_id,
        is_active=True
    )

    enrollment = request.user.enrollments.filter(
        cohort_id=cohort_id,
        is_active=True
    ).first()

    if not enrollment:
        return render(
            request,
            "core/access_denied.html",
            status=403
        )
    discussions = seminar_room.discussions.filter(
        is_active=True
    ).select_related(
        "author"
    )
    return render(
        request,
        "core/discussions.html",
        {
            "seminar_room": seminar_room,
            "cohort": seminar_room.cohort,
            "discussions": discussions,
        }
    )

@login_required
def create_discussion(request, cohort_id):
    seminar_room = get_object_or_404(
        SeminarRoom,
        cohort_id=cohort_id,
        is_active=True
    )
    enrollment = request.user.enrollments.filter(
        cohort_id=cohort_id,
        is_active=True
    ).first()
    if not enrollment:
        return render(
            request,
            "core/access_denied.html",
            status=403
        )

    if request.method == "POST":
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(
                commit=False
            )
            discussion.seminar_room = seminar_room
            discussion.author = request.user

            discussion.save()

            return redirect(
                "discussion_detail",
                discussion_id=discussion.id
            )

    else:
        form = DiscussionForm()

    return render(
        request,
        "core/create_discussion.html",
        {
            "form": form,
            "cohort": seminar_room.cohort,
        }
    )

@login_required
def discussion_detail(request, discussion_id):
    discussion = get_object_or_404(
        Discussion.objects.select_related(
            "seminar_room",
            "seminar_room__cohort",
            "author"
        ),
        id=discussion_id,
        is_active=True
    )

    cohort = discussion.seminar_room.cohort

    enrollment = request.user.enrollments.filter(
        cohort=cohort,
        is_active=True
    ).first()

    if not enrollment:
        return render(
            request,
            "core/access_denied.html",
            status=403
        )

    replies = discussion.replies.filter(
        is_active=True
    ).select_related("author")

    return render(
        request,
        "core/discussion_detail.html",
        {
            "discussion": discussion,
            "replies": replies,
            "cohort": cohort,
        }
    )


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related(
            "module",
            "module__cohort",
            "module__cohort__program"
        ),
        id=lesson_id,
        is_active=True
    )

    cohort = lesson.module.cohort

    enrollment = request.user.enrollments.filter(
        cohort=cohort,
        is_active=True
    ).first()

    if not enrollment:
        return render(
            request,
            "core/access_denied.html",
            status=403
        )

    assignments = lesson.assignments.filter(
        is_active=True
    )

    return render(
        request,
        "core/lesson_detail.html",
        {
            "lesson": lesson,
            "module": lesson.module,
            "cohort": cohort,
            "assignments": assignments,
        }
    )

@login_required
def update_lesson_progress(request, lesson_id):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required."},
            status=405
        )
    lesson = get_object_or_404(
        Lesson,
        id=lesson_id,
        is_active=True
    )
    enrollment = request.user.enrollments.filter(
        cohort__program=lesson.module.program,
        is_active=True
    ).first()

    if not enrollment:
        return JsonResponse(
            {"error": "You are not enrolled in this program."},
            status=403
        )

    watched_seconds = request.POST.get(
        "watched_seconds",
        0
    )

    try:
        watched_seconds = int(watched_seconds)
    except (TypeError, ValueError):
        watched_seconds = 0

    watched_seconds = min(
        watched_seconds,
        lesson.duration_seconds
    )

    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )

    progress.watched_seconds = max(
        progress.watched_seconds,
        watched_seconds
    )

    if lesson.duration_seconds > 0:

        completion_percentage = (
            progress.watched_seconds /
            lesson.duration_seconds
        ) * 100

        if completion_percentage >= 90:
            progress.completed = True

    if progress.completed and not progress.completed_at:
        from django.utils import timezone
        progress.completed_at = timezone.now()

    progress.save()

    return JsonResponse({
        "watched_seconds": progress.watched_seconds,
        "completed": progress.completed,
    })




