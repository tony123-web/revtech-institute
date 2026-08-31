from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.files.storage import default_storage
from cohorts.models import SeminarRoom, Discussion,DiscussionReply,Cohort
from courses.forms import AssignmentSubmissionForm
from courses.models import Lesson,LessonProgress,Module,Assignment,AssignmentSubmission
from cohorts.forms import DiscussionForm
from projects.models import Project
from django.db.models import Count, Q
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404


def home(request):
    cohort = (
        Cohort.objects
        .filter(is_open=True)
        .select_related("program")
        .prefetch_related(
            "weeks__modules__lessons"
        )
        .order_by("start_date")
        .first()
    )
    featured_projects = Project.objects.filter(
        is_published=True,
        is_featured=True
    ).select_related(
        "student",
        "cohort"
    ).prefetch_related(
        "images"
    )[:2]

    return render(request, "core/home.html",
                  {
                      "cohort":cohort,
                      'featured_projects':featured_projects
                }
    )


def about(request):
    return render(request, "core/about.html")


def contact(request):
    return render(request, "core/contact.html")


@login_required
def dashboard(request):
    profile = request.user.profile
    if not profile.is_complete:
        return redirect("complete_profile")
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
def core_cohort_detail(request, slug):
    cohort = get_object_or_404(
        Cohort.objects.prefetch_related(
            "weeks__modules__lessons",
            "weeks__modules__lessons__assignments",
        ),
        slug=slug,
    )

    enrollment = request.user.enrollments.filter(
        cohort=cohort,
        is_active=True,
    ).first()

    if not enrollment:
        return render(
            request,
            "core/access_denied.html",
            status=403,
        )

    return render(
        request,
        "core/cohort_detail.html",
        {
            "cohort": cohort,
            "weeks": cohort.weeks.all(),
        },
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
    cohort = get_object_or_404(
        Cohort.objects.prefetch_related(
            "weeks__modules__lessons",
            "weeks__modules__lessons__assignments",
            "announcements",
        ),
        id=cohort_id,
    )
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
    assignments = Assignment.objects.filter(
        lesson__module__cohort=seminar_room.cohort,
        is_active=True
    ).select_related(
        "lesson",
        "lesson__module"
    ).prefetch_related(
        "submissions"
    )
    submissions = AssignmentSubmission.objects.filter(
        assignment__lesson__module__cohort=seminar_room.cohort
    ).select_related(
        "student",
        "assignment",
    )

    if request.user.is_staff:
        visible_submissions = submissions
    else:
        visible_submissions = submissions.filter(
            models.Q(student=request.user) |
            models.Q(is_visible_to_cohort=True)
        )
    context = {
        "seminar_room": seminar_room,
        "cohort": seminar_room.cohort,
        "resources": resources,
        "assignments":assignments,
        "weeks": cohort.weeks.all(),
        "submissions": visible_submissions,
        "enrollment": enrollment,
        "announcements": cohort.announcements.filter(
            is_active=True
        ),
        "members": cohort.enrollments.filter(
            is_active=True
        ).select_related("student"),
        "projects": cohort.projects.filter(
            is_published=True
        ).select_related("student"),
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
def create_reply(request, discussion_id):
    discussion = get_object_or_404(
        Discussion.objects.select_related(
            "seminar_room",
            "seminar_room__cohort"
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

    if request.method == "POST":

        content = request.POST.get("content", "").strip()

        if content:

            DiscussionReply.objects.create(
                discussion=discussion,
                author=request.user,
                content=content
            )

    return redirect(
        "discussion_detail",
        discussion_id=discussion.id
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
        ),
        id=lesson_id,
        is_active=True,
    )

    cohort = lesson.module.cohort

    enrollment = request.user.enrollments.filter(
        cohort=cohort,
        is_active=True,
    ).first()

    if not enrollment:
        return render(
            request,
            "core/access_denied.html",
            status=403,
        )

    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
    )

    return render(
        request,
        "core/lesson_detail.html",
        {
            "lesson": lesson,
            "module": lesson.module,
            "cohort": cohort,
            "progress": progress,
        },
    )


@login_required
@require_GET
def lesson_video_url(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related(
            "module",
            "module__cohort",
        ),
        id=lesson_id,
        is_active=True,
    )
    cohort = lesson.module.cohort
    enrollment = request.user.enrollments.filter(
        cohort=cohort,
        is_active=True,
    ).first()

    if not enrollment:
        return JsonResponse(
            {"error": "You are not enrolled in this cohort."},
            status=403,
        )

    if not lesson.video_file:
        return JsonResponse(
            {"error": "No uploaded video available."},
            status=404,
        )

    video_url = default_storage.url(
        lesson.video_file.name
    )

    return JsonResponse({
        "url": video_url
    })


@login_required
@require_POST
def update_lesson_progress(request, lesson_id):
    lesson = get_object_or_404(
        Lesson,
        id=lesson_id,
        is_active=True,
    )

    enrollment = request.user.enrollments.filter(
        cohort=lesson.module.cohort,
        is_active=True,
    ).first()

    if not enrollment:
        return JsonResponse(
            {"error": "Access denied."},
            status=403,
        )

    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
    )

    try:
        watched_seconds = int(
            request.POST.get(
                "watched_seconds",
                0
            )
        )
    except (TypeError, ValueError):
        watched_seconds = 0

    # Never allow negative values.
    watched_seconds = max(
        0,
        watched_seconds
    )

    # Never allow watched time beyond the actual lesson duration.
    if lesson.duration_seconds:
        watched_seconds = min(
            watched_seconds,
            lesson.duration_seconds
        )

    # Don't allow progress to move backwards.
    if watched_seconds > progress.watched_seconds:
        progress.watched_seconds = watched_seconds

    # 90% completion rule
    if lesson.duration_seconds:
        completion_threshold = (
            lesson.duration_seconds * 0.90
        )

        if progress.watched_seconds >= completion_threshold:

            progress.completed = True

            if not progress.completed_at:
                from django.utils import timezone

                progress.completed_at = timezone.now()

    progress.save()

    percentage = 0

    if lesson.duration_seconds:

        percentage = min(
            100,
            round(
                (
                    progress.watched_seconds /
                    lesson.duration_seconds
                ) * 100
            )
        )

    return JsonResponse({
        "watched_seconds": progress.watched_seconds,
        "percentage": percentage,
        "completed": progress.completed,
    })

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(
        Assignment.objects.select_related(
            "lesson",
            "lesson__module",
            "lesson__module__cohort",
        ),
        id=assignment_id,
        is_active=True,
    )

    cohort = assignment.lesson.module.cohort

    enrollment = request.user.enrollments.filter(
        cohort=cohort,
        is_active=True,
    ).first()

    if not enrollment:
        return render(
            request,
            "core/access_denied.html",
            status=403,
        )

    submission = AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=request.user,
    ).first()

    if request.method == "POST":

        form = AssignmentSubmissionForm(
            request.POST,
            instance=submission,
        )

        if form.is_valid():

            submission = form.save(
                commit=False
            )

            submission.assignment = assignment
            submission.student = request.user

            submission.save()

            return redirect(
                "assignment_detail",
                assignment_id=assignment.id,
            )

    else:

        form = AssignmentSubmissionForm(
            instance=submission
        )

    return render(
        request,
        "core/assignment_detail.html",
        {
            "assignment": assignment,
            "lesson": assignment.lesson,
            "module": assignment.lesson.module,
            "cohort": cohort,
            "submission": submission,
            "form": form,
        },
    )

@login_required
def review_submission(request, submission_id):
    if not request.user.is_staff:
        return render(
            request,
            "core/access_denied.html",
            status=403
        )

    submission = get_object_or_404(
        AssignmentSubmission.objects.select_related(
            "student",
            "assignment",
            "assignment__lesson",
            "assignment__lesson__module",
            "assignment__lesson__module__cohort",
        ),
        id=submission_id,
    )

    if request.method == "POST":

        feedback = request.POST.get(
            "instructor_feedback",
            ""
        ).strip()

        submission.instructor_feedback = feedback

        submission.is_visible_to_cohort = (
            request.POST.get("is_visible_to_cohort") == "on"
        )

        submission.save()

        return redirect(
            "seminar_room",
            cohort_id=(
                submission.assignment
                .lesson
                .module
                .cohort
                .id
            )
        )

    return render(
        request,
        "core/review_submission.html",
        {
            "submission": submission,
        }
    )






