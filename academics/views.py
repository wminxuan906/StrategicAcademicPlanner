from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Semester, Module, Assessment
from .forms import SemesterForm, ModuleForm, AssessmentForm


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


@login_required(login_url="/accounts/login/")
def assessment_list(request):

    assessments = Assessment.objects.filter(
        module__semester__user=request.user
    ).select_related(
        "module",
        "module__semester",
    )

    module_id = request.GET.get("module")

    if module_id:

        assessments = assessments.filter(
            module_id=module_id,
            module__semester__user=request.user,
        )

    return render(
        request,
        "academics/assessment_list.html",
        {
            "assessments": assessments,
            "page_title": "Assessments",
        },
    )


@login_required(login_url="/accounts/login/")
def assessment_create(request):

    if request.method == "POST":

        form = AssessmentForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():

            form.save()

            return redirect("academics:assessment_list")

    else:

        form = AssessmentForm(
            user=request.user,
        )

    return render(
        request,
        "academics/assessment_form.html",
        {
            "form": form,
            "page_title": "Add Assessment",
        },
    )


@login_required(login_url="/accounts/login/")
def assessment_update(request, assessment_id):

    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
        module__semester__user=request.user,
    )

    if request.method == "POST":

        form = AssessmentForm(
            request.POST,
            instance=assessment,
            user=request.user,
        )

        if form.is_valid():

            form.save()

            return redirect("academics:assessment_list")

    else:

        form = AssessmentForm(
            instance=assessment,
            user=request.user,
        )

    return render(
        request,
        "academics/assessment_form.html",
        {
            "form": form,
            "assessment": assessment,
            "page_title": "Edit Assessment",
        },
    )


@login_required(login_url="/accounts/login/")
def assessment_delete(request, assessment_id):

    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
        module__semester__user=request.user,
    )

    if request.method == "POST":

        assessment.delete()

        return redirect("academics:assessment_list")

    return render(
        request,
        "academics/assessment_confirm_delete.html",
        {
            "assessment": assessment,
            "page_title": "Delete Assessment",
        },
    )

@login_required(login_url="/accounts/login/")
def grade_tracking(request):
    modules = (
        Module.objects
        .filter(semester__user=request.user)
        .select_related("semester")
        .prefetch_related("assessments")
        .order_by("semester__academic_year", "module_code")
    )

    context = {
        "modules": modules,
        "page_title": "Grade Tracking",
    }

    return render(
        request,
        "academics/grade_tracking.html",
        context,
    )