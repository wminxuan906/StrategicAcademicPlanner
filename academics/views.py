from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Semester, Module
from .forms import SemesterForm, ModuleForm


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


@login_required(login_url="/accounts/login/")
def module_list(request):
    modules = Module.objects.filter(
        semester__user=request.user
    ).select_related("semester")

    semester_id = request.GET.get("semester")

    if semester_id:
        modules = modules.filter(
            semester_id=semester_id,
            semester__user=request.user
        )

    return render(
        request,
        "academics/module_list.html",
        {
            "modules": modules,
            "page_title": "Modules",
        }
    )


@login_required(login_url="/accounts/login/")
def module_create(request):
    if request.method == "POST":
        form = ModuleForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():
            form.save()
            return redirect("academics:module_list")

    else:
        form = ModuleForm(
            user=request.user
        )

    return render(
        request,
        "academics/module_form.html",
        {
            "form": form,
            "page_title": "Add Module",
        }
    )


@login_required(login_url="/accounts/login/")
def module_update(request, module_id):
    module = get_object_or_404(
        Module,
        id=module_id,
        semester__user=request.user
    )

    if request.method == "POST":
        form = ModuleForm(
            request.POST,
            instance=module,
            user=request.user
        )

        if form.is_valid():
            form.save()
            return redirect("academics:module_list")

    else:
        form = ModuleForm(
            instance=module,
            user=request.user
        )

    return render(
        request,
        "academics/module_form.html",
        {
            "form": form,
            "module": module,
            "page_title": "Edit Module",
        }
    )


@login_required(login_url="/accounts/login/")
def module_delete(request, module_id):
    module = get_object_or_404(
        Module,
        id=module_id,
        semester__user=request.user
    )

    if request.method == "POST":
        module.delete()
        return redirect("academics:module_list")

    return render(
        request,
        "academics/module_confirm_delete.html",
        {
            "module": module,
            "page_title": "Delete Module",
        }
    )