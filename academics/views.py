from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Semester
from .forms import SemesterForm


@login_required(login_url="/accounts/login/")
def academic_management(request):
    return render(request, "academic_management.html")


@login_required(login_url="/accounts/login/")
def semester_list(request):

    semesters = Semester.objects.filter(
        user=request.user
    )

    return render(
        request,
        "academics/semester_list.html",
        {
            "semesters": semesters,
            "page_title": "Semesters"
        }
    )


@login_required(login_url="/accounts/login/")
def semester_create(request):

    if request.method == "POST":

        form = SemesterForm(request.POST)

        if form.is_valid():

            semester = form.save(commit=False)

            semester.user = request.user

            semester.save()

            return redirect("academics:semester_list")

    else:

        form = SemesterForm()


    return render(
        request,
        "academics/semester_form.html",
        {
            "form": form
        }
    )


@login_required(login_url="/accounts/login/")
def semester_update(request, semester_id):
    semester = get_object_or_404(
        Semester,
        id=semester_id,
        user=request.user
    )

    if request.method == "POST":
        form = SemesterForm(request.POST, instance=semester)

        if form.is_valid():
            form.save()
            return redirect("academics:semester_list")

    else:
        form = SemesterForm(instance=semester)

    return render(
        request,
        "academics/semester_form.html",
        {
            "form": form,
            "semester": semester,
        }
    )


@login_required(login_url="/accounts/login/")
def semester_delete(request, semester_id):
    semester = get_object_or_404(
        Semester,
        id=semester_id,
        user=request.user
    )

    if request.method == "POST":
        semester.delete()
        return redirect("academics:semester_list")

    return render(
        request,
        "academics/semester_confirm_delete.html",
        {
            "semester": semester
        }
    )