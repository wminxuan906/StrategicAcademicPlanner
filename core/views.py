from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from academics.models import Semester

from django.utils import timezone
from academics.models import Semester, Assessment
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm

from .forms import AccountUpdateForm
from django.contrib.auth import update_session_auth_hash

@login_required(login_url="/accounts/login/")
def dashboard(request):

    semesters = Semester.objects.filter(user=request.user)

    semester_id = request.GET.get("semester")

    # Use the selected semester or default to the first available semester
    if semester_id:
        selected_semester = get_object_or_404(
            Semester,
            id=semester_id,
            user=request.user
        )
    else:
        selected_semester = semesters.first()

    modules_count = 0
    assessments_count = 0
    upcoming_count = 0
    focus_assessments = []
    academic_guidance = []

    # Only calculate dashboard data when the user has a semester
    if selected_semester:

        # Count modules and assessments in the selected semester
        modules_count = selected_semester.modules.count()

        assessments = Assessment.objects.filter(
            module__semester=selected_semester
        )

        assessments_count = assessments.count()

        today = timezone.localdate()

        # Count unfinished assessments with a current or future deadline
        upcoming_count = assessments.filter(
            deadline__isnull=False,
            deadline__gte=today,
        ).exclude(
            status__in=[
                Assessment.SUBMITTED,
                Assessment.GRADED,
            ]
        ).count()

        focus_assessments = []

        # Exclude submitted and graded assessments from prioritisation
        unfinished_assessments = assessments.exclude(
            status__in=[
                Assessment.SUBMITTED,
                Assessment.GRADED,
            ]
        )

        # Check each unfinished assessment against the attention factors
        for assessment in assessments:
            if assessment.status in [
                Assessment.SUBMITTED,
                Assessment.GRADED,
            ]:
                continue

            attention_factor = []

            # Factor 1: the deadline is within the next 14 days
            if(
                assessment.deadline
                and today <= assessment.deadline <= today + timedelta(days=14)
            ):
                attention_factor.append("Close deadline")

            # Factor 2: the assessment has a high effort level
            if assessment.effort_level == Assessment.HIGH:
                attention_factor.append("High effort")

            # Factor 3: it has the highest weight among unfinished module work
            module_unfinished = unfinished_assessments.filter(
                module=assessment.module
            )

            highest_weight = module_unfinished.order_by(
                "-weight"
            ).first()

            if(
                highest_weight
                and assessment.weight == highest_weight.weight
            ):
                attention_factor.append("High contribution")

            module = assessment.module

            # Factor 4: current module performance is below the saved target
            if (
                module.target_grade is not None
                and module.completed_weight > 0
            ):
                current_performance = (
                    module.current_contribution
                    / module.completed_weight
                ) * 100

                if current_performance < module.target_grade:
                    attention_factor.append("Below target")

            # Only show assessments that meet at least one attention factor
            if attention_factor:
                focus_assessments.append(
                    {
                        "assessment": assessment,
                        "factors": attention_factor,
                        "factor_count": len(attention_factor),
                    }
                )

        # Rank by the number of factors, then use the earlier deadline
        focus_assessments.sort(
            key=lambda item: (
                -item["factor_count"],
                item["assessment"].deadline or today + timedelta(days=9999),
            )
        )

        modules = selected_semester.modules.all()

        # Calculate the average still required to reach each module target
        for module in modules:
            if module.target_grade is not None:

                required_average = module.required_average_for(
                    module.target_grade
                )

                academic_guidance.append(
                    {
                        "module": module,
                        "target_grade": module.target_grade,
                        "required_average": required_average,
                    }
                )
        
    # Pass the dashboard summary, priorities and guidance to the template
    context = {
        "semesters": semesters,
        "selected_semester": selected_semester,
        "modules_count": modules_count,
        "assessments_count": assessments_count,
        "upcoming_count" : upcoming_count,
        "focus_assessments": focus_assessments,
        "academic_guidance": academic_guidance,
    }

    return render(request, "dashboard.html", context)


@login_required(login_url="/accounts/login/")
def settings(request):

    # Display both forms with the current user's existing information
    account_form = AccountUpdateForm(
        instance=request.user
    )

    password_form = PasswordChangeForm(
        user=request.user
    )

    # Update username and email
    if request.method == "POST" and request.POST.get("form_type") == "account":

        account_form = AccountUpdateForm(
            request.POST,
            instance=request.user
        )

        if account_form.is_valid():
            account_form.save()

            messages.success(
                request,
                "Account information updated successfully."
            )

            return redirect("core:settings")

    # Change password
    if request.method == "POST" and request.POST.get("form_type") == "password":

        password_form = PasswordChangeForm(
            user=request.user,
            data=request.POST
        )

        if password_form.is_valid():

            user = password_form.save()

            # Keep the user logged in after changing the password
            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect("core:settings")

    return render(
        request,
        "settings.html",
        {
            "account_form": account_form,
            "password_form": password_form,
        }
    )