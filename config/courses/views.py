from django.shortcuts import get_object_or_404, render

from .models import Program


def course_list(request):
    programs = Program.objects.filter(
        is_active=True
    )

    return render(
        request,
        "courses/course_list.html",
        {
            "programs": programs
        }
    )

def program_detail(request, slug):
    program = get_object_or_404(
        Program,
        slug=slug,
        is_active=True
    )

    cohorts = (
        program.cohorts
        .filter(program=program)
        .prefetch_related(
            "weeks__modules__lessons"
        )
    )

    return render(
        request,
        "courses/program_detail.html",
        {
            "program": program,
            "cohorts": cohorts,
        }
    )





