from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Semester, Module, Assessment
from .forms import (
    SemesterForm,
    ModuleForm,
    AssessmentForm,
    WhatIfCalculatorForm,
)

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

@login_required(login_url="/accounts/login/")
def what_if_calculator(request):
    selected_module = None
    target_grade = None
    assessments = []
    remaining_assessments = []
    completed_assessment_count = 0

    actual_contribution = Decimal("0")
    scenario_contribution = Decimal("0")
    projected_grade = None
    gap_to_target = None

    published_weight = Decimal("0")
    unpublished_weight = Decimal("0")
    entered_expected_weight = Decimal("0")

    scenario_status = None
    scenario_calculated = False
    scenario_errors = []
    calculation_breakdown = []

    if request.method == "POST":
        form = WhatIfCalculatorForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            selected_module = form.cleaned_data["module"]
            submitted_target = form.cleaned_data["target_grade"]
            action = request.POST.get("action")

            if submitted_target is not None:
                target_grade = submitted_target
            else:
                target_grade = selected_module.target_grade

            actual_contribution = (
                selected_module.current_contribution
            )

            assessments = list(
                selected_module.assessments
                .all()
                .order_by(
                    "deadline",
                    "assessment_name",
                )
            )

            remaining_assessments = [
                assessment
                for assessment in assessments
                if assessment.raw_score is None
            ]

            completed_assessment_count = sum(
                1
                for assessment in assessments
                if assessment.raw_score is not None
            )

            published_weight = sum(
                (assessment.weight for assessment in assessments),
                Decimal("0"),
            )

            unpublished_weight = max(
                Decimal("100") - published_weight,
                Decimal("0"),
            )

            confirmed_weight = Decimal("0")

            for assessment in assessments:
                assessment.scenario_mark = None

                if assessment.raw_score is None:
                    continue

                confirmed_weight += assessment.weight

                calculation_breakdown.append(
                    {
                        "assessment_name": assessment.assessment_name,
                        "result_type": "Actual",
                        "weight": assessment.weight,
                        "mark": assessment.raw_score,
                        "maximum_score": assessment.maximum_score,
                        "percentage": assessment.percentage_score,
                        "contribution": assessment.weighted_contribution,
                    }
                )

            if action == "load_module":
                form = WhatIfCalculatorForm(
                    user=request.user,
                    initial={
                        "module": selected_module,
                    },
                )

            if action == "calculate_scenario":
                if target_grade is None:
                    scenario_errors.append(
                        "Enter a target grade for this scenario."
                    )
                for assessment in remaining_assessments:
                    entered_value = request.POST.get(
                        f"expected_{assessment.id}",
                        "",
                    ).strip()

                    if not entered_value:
                        continue

                    assessment.scenario_mark = entered_value

                    try:
                        expected_mark = Decimal(entered_value)

                    except InvalidOperation:
                        scenario_errors.append(
                            f"Enter a valid mark for "
                            f"{assessment.assessment_name}."
                        )
                        continue

                    if expected_mark < Decimal("0"):
                        scenario_errors.append(
                            f"The expected mark for "
                            f"{assessment.assessment_name} "
                            f"cannot be below 0."
                        )
                        continue

                    if (
                        assessment.maximum_score is None
                        or assessment.maximum_score <= Decimal("0")
                    ):
                        scenario_errors.append(
                            f"{assessment.assessment_name} does not "
                            f"have a valid maximum score."
                        )
                        continue

                    if expected_mark > assessment.maximum_score:
                        scenario_errors.append(
                            f"The expected mark for "
                            f"{assessment.assessment_name} "
                            f"cannot exceed "
                            f"{assessment.maximum_score}."
                        )
                        continue

                    assessment.scenario_mark = expected_mark

                    expected_percentage = (
                        expected_mark
                        / assessment.maximum_score
                    ) * Decimal("100")

                    contribution = (
                        expected_percentage
                        * assessment.weight
                    ) / Decimal("100")

                    scenario_contribution += contribution
                    entered_expected_weight += assessment.weight

                    calculation_breakdown.append(
                        {
                            "assessment_name": assessment.assessment_name,
                            "result_type": "Expected",
                            "weight": assessment.weight,
                            "mark": expected_mark,
                            "maximum_score": assessment.maximum_score,
                            "percentage": expected_percentage,
                            "contribution": contribution,
                        }
                    )

                if not scenario_errors:
                    projected_grade = (
                        actual_contribution
                        + scenario_contribution
                    )

                    unentered_published_weight = max(
                        published_weight
                        - confirmed_weight
                        - entered_expected_weight,
                        Decimal("0"),
                    )

                    if unentered_published_weight > Decimal("0"):
                        scenario_status = "incomplete"
                        gap_to_target = None

                    elif unpublished_weight > Decimal("0"):
                        scenario_status = "partial_projection"
                        gap_to_target = None

                    else:
                        gap_to_target = projected_grade - target_grade

                        if projected_grade >= target_grade:
                            scenario_status = "target_met"

                        else:
                            scenario_status = "below_target"

                    scenario_calculated = True

    else:
        form = WhatIfCalculatorForm(
            user=request.user,
        )

    return render(
        request,
        "academics/what_if_calculator.html",
        {
            "form": form,
            "selected_module": selected_module,
            "target_grade": target_grade,
            "assessments": assessments,
            "remaining_assessments": remaining_assessments,
            "completed_assessment_count": completed_assessment_count,
            "actual_contribution": actual_contribution,
            "scenario_contribution": scenario_contribution,
            "projected_grade": projected_grade,
            "gap_to_target": gap_to_target,
            "published_weight": published_weight,
            "unpublished_weight": unpublished_weight,
            "scenario_status": scenario_status,
            "scenario_calculated": scenario_calculated,
            "scenario_errors": scenario_errors,
            "calculation_breakdown": calculation_breakdown,
            "page_title": "What-if Calculator",
        },
    )