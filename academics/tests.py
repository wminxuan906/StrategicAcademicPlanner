from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Semester, Module, Assessment
from .forms import AssessmentForm

from django.urls import reverse

class AssessmentCalculationTests(TestCase):

    def setUp(self):
        # Create the user, semester and module shared by these unit tests
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123"
        )

        self.semester = Semester.objects.create(
            user=self.user,
            name="Semester 1",
            academic_year="2025/26"
        )

        self.module = Module.objects.create(
            semester=self.semester,
            module_code="TEST1001",
            module_name="Test Module",
            credits=20
        )

    def test_assessment_grade_calculation(self):
        # Check percentage score and weighted contribution calculations
        assessment = Assessment.objects.create(
            module=self.module,
            assessment_name="Coursework 1",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("20.00"),
            maximum_score=Decimal("100.00"),
            raw_score=Decimal("80.00")
        )

        self.assertEqual(
            assessment.percentage_score,
            Decimal("80.0")
        )

        self.assertEqual(
            assessment.weighted_contribution,
            Decimal("16.00")
        )

    def test_module_academic_progress_calculation(self):
        # Create graded, ungraded and not-yet-added assessment weight
        Assessment.objects.create(
            module=self.module,
            assessment_name="Coursework 1",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("20.00"),
            maximum_score=Decimal("100.00"),
            raw_score=Decimal("80.00")
        )

        Assessment.objects.create(
            module=self.module,
            assessment_name="Coursework 2",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("30.00"),
            maximum_score=Decimal("100.00"),
            raw_score=Decimal("70.00")
        )

        Assessment.objects.create(
            module=self.module,
            assessment_name="Exam",
            assessment_type=Assessment.FINAL_EXAM,
            weight=Decimal("20.00"),
            maximum_score=Decimal("100.00"),
            raw_score=None
        )

        # Check the module-level weight and contribution properties
        self.assertEqual(
            self.module.total_assessment_weight,
            Decimal("70.00")
        )

        self.assertEqual(
            self.module.completed_weight,
            Decimal("50.00")
        )

        self.assertEqual(
            self.module.known_remaining_weight,
            Decimal("20.00")
        )

        self.assertEqual(
            self.module.unannounced_weight,
            Decimal("30.00")
        )

        self.assertEqual(
            self.module.remaining_weight,
            Decimal("50.00")
        )

        self.assertEqual(
            self.module.current_contribution,
            Decimal("37.00")
        )

    def test_assessment_weight_validation(self):
        # Start with 70 percent of the module weight already recorded
        Assessment.objects.create(
            module=self.module,
            assessment_name="Coursework 1",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("70.00"),
            maximum_score=Decimal("100.00")
        )

        # Adding another 40 percent should fail because the total would be 110
        form = AssessmentForm(
            data={
                "module": self.module.id,
                "assessment_name": "Final Exam",
                "assessment_type": Assessment.FINAL_EXAM,
                "weight": "40.00",
                "maximum_score": "100.00",
                "deadline": "",
                "status": Assessment.NOT_STARTED,
                "effort_level": Assessment.MEDIUM,
                "raw_score": "",
            },
            user=self.user
        )

        self.assertFalse(form.is_valid())
        self.assertIn("weight", form.errors)

    def test_required_average_for_target_grade(self):

        # Check the average required across the remaining module weight
        Assessment.objects.create(
            module=self.module,
            assessment_name="Coursework 1",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("50.00"),
            maximum_score=Decimal("100.00"),
            raw_score=Decimal("60.00")
        )

        required_average = self.module.required_average_for(
            Decimal("60.00")
        )

        self.assertEqual(
            required_average,
            Decimal("60.00")
        )

class GradeTrackingIntegrationTests(TestCase):

    def setUp(self):
        # Create and log in a user with saved academic data
        self.user = User.objects.create_user(
            username="integrationuser",
            password="testpassword123"
        )

        self.semester = Semester.objects.create(
            user=self.user,
            name="Semester 1",
            academic_year="2025/26"
        )

        self.module = Module.objects.create(
            semester=self.semester,
            module_code="TEST2001",
            module_name="Integration Test Module",
            credits=20
        )

        self.assessment = Assessment.objects.create(
            module=self.module,
            assessment_name="Coursework 1",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("50.00"),
            maximum_score=Decimal("100.00"),
            raw_score=Decimal("60.00")
        )

        self.client.login(
            username="integrationuser",
            password="testpassword123"
        )

    def test_assessment_mark_update_reflected_in_grade_tracking(self):
        # Update the saved mark before requesting the Grade Tracking page
        self.assessment.raw_score = Decimal("80.00")
        self.assessment.save()

        response = self.client.get(
            reverse("academics:grade_tracking")
        )

        self.assertEqual(response.status_code, 200)

        self.module.refresh_from_db()

        self.assertEqual(
            self.module.completed_weight,
            Decimal("50.00")
        )

        self.assertEqual(
            self.module.current_contribution,
            Decimal("40.00")
        )

        # Confirm that the updated mark is also shown in the response
        self.assertContains(response, "80")

class WhatIfCalculatorIntegrationTests(TestCase):

    def setUp(self):
        # Create a logged-in user with one completed and one remaining assessment
        self.user = User.objects.create_user(
            username="whatifuser",
            password="testpassword123"
        )

        self.semester = Semester.objects.create(
            user=self.user,
            name="Semester 1",
            academic_year="2025/26"
        )

        self.module = Module.objects.create(
            semester=self.semester,
            module_code="TEST5001",
            module_name="What-if Test Module",
            credits=20,
            target_grade=Decimal("70.00")
        )

        self.completed_assessment = Assessment.objects.create(
            module=self.module,
            assessment_name="Coursework 1",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("40.00"),
            maximum_score=Decimal("100.00"),
            raw_score=Decimal("60.00"),
            status=Assessment.GRADED
        )

        self.remaining_assessment = Assessment.objects.create(
            module=self.module,
            assessment_name="Coursework 2",
            assessment_type=Assessment.COURSEWORK,
            weight=Decimal("60.00"),
            maximum_score=Decimal("100.00"),
            raw_score=None,
            status=Assessment.NOT_STARTED
        )

        self.client.login(
            username="whatifuser",
            password="testpassword123"
        )

    def test_academic_data_used_in_what_if_scenario(self):
        # Submit an expected mark through the complete What-if request flow
        response = self.client.post(
            reverse("academics:what_if_calculator"),
            {
                "module": self.module.id,
                "target_grade": "70",
                "action": "calculate_scenario",
                f"expected_{self.remaining_assessment.id}": "80",
            }
        )

        self.assertEqual(response.status_code, 200)

        # Confirm the view completed the scenario calculation
        self.assertTrue(
            response.context["scenario_calculated"]
        )

        # Check the actual, expected and combined grade contributions
        self.assertEqual(
            response.context["actual_contribution"],
            Decimal("24.00")
        )

        self.assertEqual(
            response.context["scenario_contribution"],
            Decimal("48.00")
        )

        self.assertEqual(
            response.context["projected_grade"],
            Decimal("72.00")
        )

        # Confirm that the projected grade meets the selected target
        self.assertEqual(
            response.context["scenario_status"],
            "target_met"
        )
