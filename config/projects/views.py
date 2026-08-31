from django.db.models.query_utils import select_related_descend
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm,ProjectImageForm
from enrollments.models import Enrollment
from .models import Project,ProjectImage
from django.contrib import messages



def project_list(request):
    projects = Project.objects.filter(
    is_published=True
    ).select_related(
    "student",
    "cohort",
    "cohort__program"
    ).prefetch_related(
    "images"
    )


    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects
        }
    )


def project_detail(request, project_id):
    if request.user.is_authenticated:
        project = get_object_or_404(
            Project.objects
            .select_related(
                "student",
                "cohort",
                "cohort__program"
            )
            .prefetch_related(
                "images"
            ),
            id=project_id,
        )
    else:
        project = get_object_or_404(
            Project.objects.select_related(
                "student",
                "cohort",
                "cohort__program"
            ).prefetch_related(
                "images"
            ),
            id=project_id,
            is_published=True
        )
    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project
        }
    )

@login_required
def project_create(request):
    enrollment = Enrollment.objects.filter(
        student=request.user,
        status=Enrollment.Status.ACTIVE,
        is_active=True,
        payment_verified=True
    ).select_related("cohort").first()

    if not enrollment:
        messages.error(
            request,
            "You need an active enrollment before submitting a project."
        )
        return redirect("dashboard")


# Check whether the student already submitted a project
    existing_project = Project.objects.filter(
        student=request.user,
        cohort=enrollment.cohort
    ).first()

    if existing_project:
        messages.info(
            request,
            "You have already submitted a project for this cohort."
        )

        return redirect(
            "project_detail",
            existing_project.id
        )


    if request.method == "POST":

        project_form = ProjectForm(request.POST)
        image_form = ProjectImageForm(
            request.POST,
            request.FILES
        )

        if project_form.is_valid():

            project = project_form.save(
                commit=False
            )

            project.student = request.user
            project.cohort = enrollment.cohort
            project.is_published = False
            project.is_featured = False

            project.save()


        # Save screenshots
            images = request.FILES.getlist("images")

            for index, image in enumerate(images, start=1):

                ProjectImage.objects.create(
                    project=project,
                    image=image,
                    order=index
                )


            messages.success(
                request,
                "Your project has been submitted successfully. "
                "It will be reviewed before publication."
            )

            return redirect(
                "project_detail",
                existing_project.id
            )

        else:

            print(
                "PROJECT FORM ERRORS:",
                project_form.errors
        )

    else:

        project_form = ProjectForm()
        image_form = ProjectImageForm()


    return render(
        request,
        "projects/project_form.html",
        {
            "form": project_form,
            "image_form": image_form,
            "cohort": enrollment.cohort,
        }
    )

@login_required
def my_projects(request):
    projects = Project.objects.filter(
        student=request.user
    ).select_related(
        "cohort",
        "cohort__program"
    ).prefetch_related(
     "images"
    )

    return render(
        request,
        "projects/my_projects.html",
        {
            "projects": projects
        }
    )

@login_required
def project_edit(request, project_id):
    project = get_object_or_404(
        Project,
        id=project_id,
        student=request.user
    )

    # Published projects cannot be edited by students
    if project.is_published:
        messages.error(
            request,
            "Published projects cannot be edited."
        )
        return redirect(
            "project_detail",
            project.id
        )

    if request.method == "POST":

        form = ProjectForm(
            request.POST,
            instance=project
        )

        image_form = ProjectImageForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            project = form.save(
                commit=False
            )

            # Keep ownership and cohort unchanged
            project.student = request.user
            project.save()


            # Add newly uploaded screenshots
            images = request.FILES.getlist("images")

            if images:

                last_image = project.images.order_by(
                    "-order"
                ).first()

                next_order = (
                    last_image.order + 1
                    if last_image
                    else 1
                )

                for index, image in enumerate(
                    images,
                    start=next_order
                ):

                    ProjectImage.objects.create(
                        project=project,
                        image=image,
                        order=index
                    )


            messages.success(
                request,
                "Your project has been updated successfully."
            )

            return redirect(
                "my_projects"
            )

    else:

        form = ProjectForm(
            instance=project
        )

        image_form = ProjectImageForm()


    return render(
        request,
        "projects/project_edit.html",
        {
            "form": form,
            "image_form": image_form,
            "project": project,
        }
    )














