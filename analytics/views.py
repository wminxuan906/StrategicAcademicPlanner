from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from academics.models import Assessment, Semester


@login_required(login_url="/accounts/login/")
def analytics(request):

    # Get semesters that belong to the current user
    semesters = Semester.objects.filter(
        user=request.user
    ).order_by(
        "-academic_year",
        "name"
    )

    # Get the selected semester from the URL
    semester_id = request.GET.get("semester")

    if semester_id:
        selected_semester = get_object_or_404(
            Semester,
            id=semester_id,
            user=request.user
        )
    else:
        selected_semester = semesters.first()

    module_performance = []
    weight_completion = []

    upcoming_workload = [
        {
            "label": "Next 7 days",
            "count": 0,
            "bar_width": 0,
        },
        {
            "label": "8–14 days",
            "count": 0,
            "bar_width": 0,
        },
        {
            "label": "Later",
            "count": 0,
            "bar_width": 0,
        },
    ]

    if selected_semester:

        modules = selected_semester.modules.prefetch_related(
            "assessments"
        ).all()

        # Calculate current module performance and compare it with target grade
        for module in modules:

            completed_weight = module.completed_weight

            if completed_weight > 0:
                current_performance = (
                    module.current_contribution
                    / completed_weight
                ) * Decimal("100")

                current_performance = round(
                    current_performance,
                    2
                )
            else:
                current_performance = None

            if module.target_grade is not None:
                target_grade = round(
                    module.target_grade,
                    2
                )
            else:
                target_grade = None

            if current_performance is None and target_grade is None:
                continue

            module_performance.append(
                {
                    "module": module,
                    "current_performance": current_performance,
                    "target_grade": target_grade,

                    # These values are only used to control the chart height
                    "current_height": (
                        min(
                            max(float(current_performance), 0),
                            100
                        )
                        if current_performance is not None
                        else 0
                    ),

                    "target_height": (
                        min(
                            max(float(target_grade), 0),
                            100
                        )
                        if target_grade is not None
                        else 0
                    ),
                }
            )

        # Calculate completed and remaining assessment weight
        for module in modules:

            assessments = module.assessments.all()

            # Assessments with a recorded mark are counted as completed
            completed_weight = sum(
                (
                    assessment.weight
                    for assessment in assessments
                    if assessment.raw_score is not None
                ),
                Decimal("0"),
            )

            remaining_weight = sum(
                (
                    assessment.weight
                    for assessment in assessments
                    if assessment.raw_score is None
                ),
                Decimal("0"),
            )

            # Assessment weight that has not yet been added to the system
            recorded_weight = completed_weight + remaining_weight

            not_added_weight = max(
                Decimal("100") - recorded_weight,
                Decimal("0")
            )

            weight_completion.append(
                {
                    "module": module,
                    "completed_weight": completed_weight,
                    "remaining_weight": remaining_weight,
                    "not_added_weight": not_added_weight,

                    "completed_width": min(
                        max(float(completed_weight), 0),
                        100
                    ),

                    "remaining_width": min(
                        max(float(remaining_weight), 0),
                        100
                    ),

                    "not_added_width": min(
                        max(float(not_added_weight), 0),
                        100
                    ),
                }
            )
    

        today = timezone.localdate()

        # Only unfinished assessments with a future deadline are included
        upcoming_assessments = Assessment.objects.filter(
            module__semester=selected_semester,
            status__in=[
                Assessment.NOT_STARTED,
                Assessment.IN_PROGRESS,
            ],
            deadline__isnull=False,
            deadline__gte=today,
        )

        # Count assessments by deadline range
        next_7_days_count = upcoming_assessments.filter(
            deadline__lte=today + timedelta(days=7)
        ).count()

        days_8_to_14_count = upcoming_assessments.filter(
            deadline__gt=today + timedelta(days=7),
            deadline__lte=today + timedelta(days=14),
        ).count()

        later_count = upcoming_assessments.filter(
            deadline__gt=today + timedelta(days=14)
        ).count()

        workload_counts = [
            next_7_days_count,
            days_8_to_14_count,
            later_count,
        ]

        max_count = max(workload_counts) if workload_counts else 0

        # Make the largest workload bar 100% wide
        if max_count > 0:
            workload_widths = [
                round(
                    (count / max_count) * 100,
                    2
                )
                for count in workload_counts
            ]
        else:
            workload_widths = [0, 0, 0]

        upcoming_workload = [
            {
                "label": "Next 7 days",
                "count": next_7_days_count,
                "bar_width": workload_widths[0],
            },
            {
                "label": "8–14 days",
                "count": days_8_to_14_count,
                "bar_width": workload_widths[1],
            },
            {
                "label": "Later",
                "count": later_count,
                "bar_width": workload_widths[2],
            },
        ]

    context = {
        "semesters": semesters,
        "selected_semester": selected_semester,
        "module_performance": module_performance,
        "weight_completion": weight_completion,
        "upcoming_workload": upcoming_workload,
    }

    return render(
        request,
        "analytics.html",
        context
    )