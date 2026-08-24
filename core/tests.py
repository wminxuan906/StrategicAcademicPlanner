from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from academics.models import Semester, Module, Assessment

class DashboardIntegrationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboarduser",
            password="testpassword123"
        )

        self.semester = Semester.objects.create(
            user=self.user,
            name="Semester 1",
            academic_year="2025/26"
        )

        self.module = Module.objects.create(
            semester=self.semester,
            module_code="TEST3001",
            module_name="Dashboard Test Module",
            credits=20,
            target_grade=Decimal("70.00")
        )

        # A completed assessment is needed so that current performance can be compared with the target grade.
        Assessment.objects.create(
            module=self.module,
            assessment_name="Completed Coursework",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("20.00"),
            maximum_score=Decimal("100.00"),
            raw_score=Decimal("60.00"),
            status=Assessment.GRADED,
            effort_level=Assessment.MEDIUM
        )

        self.client.login(
            username="dashboarduser",
            password="testpassword123"
        )

    def test_assessment_data_reflected_in_dashboard_prioritisation(self):
        today = timezone.localdate()

        priority_assessment = Assessment.objects.create(
            module=self.module,
            assessment_name="Priority Coursework",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("40.00"),
            maximum_score=Decimal("100.00"),
            deadline=today + timedelta(days=7),
            status=Assessment.NOT_STARTED,
            effort_level=Assessment.HIGH
        )

        lower_priority_assessment = Assessment.objects.create(
            module=self.module,
            assessment_name="Lower Priority Coursework",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("20.00"),
            maximum_score=Decimal("100.00"),
            deadline=today + timedelta(days=10),
            status=Assessment.NOT_STARTED,
            effort_level=Assessment.MEDIUM
        )

        response = self.client.get(
            reverse("core:dashboard"),
            {"semester": self.semester.id}
        )

        self.assertEqual(response.status_code, 200)

        focus_assessments = response.context["focus_assessments"]

        self.assertEqual(len(focus_assessments), 2)

        # Higher-priority assessment should appear first.
        self.assertEqual(
            focus_assessments[0]["assessment"],
            priority_assessment
        )

        self.assertEqual(
            focus_assessments[0]["factor_count"],
            4
        )

        self.assertIn(
            "Close deadline",
            focus_assessments[0]["factors"]
        )
        self.assertIn(
            "High effort",
            focus_assessments[0]["factors"]
        )
        self.assertIn(
            "High contribution",
            focus_assessments[0]["factors"]
        )
        self.assertIn(
            "Below target",
            focus_assessments[0]["factors"]
        )

        # Lower-priority assessment should appear second.
        self.assertEqual(
            focus_assessments[1]["assessment"],
            lower_priority_assessment
        )

        self.assertEqual(
            focus_assessments[1]["factor_count"],
            2
        )

        self.assertIn(
            "Close deadline",
            focus_assessments[1]["factors"]
        )
        self.assertIn(
            "Below target",
            focus_assessments[1]["factors"]
        )