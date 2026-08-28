from django.shortcuts import render


def cohort_list(request):
    return render(request, "cohorts/cohort_list.html")