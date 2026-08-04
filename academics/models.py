from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Semester(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="semesters",
    )
    name = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "academic_year"],
                name="unique_semester_per_user",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.academic_year})"


class Module(models.Model):
    semester = models.ForeignKey(
        Semester, 
        on_delete=models.CASCADE, 
        related_name="modules")
    module_code = models.CharField(max_length=20)
    module_name = models.CharField(max_length=100)
    credits = models.PositiveIntegerField(default=20)
    target_grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["semester", "module_code"],
                name="unique_module_code_per_semester",
            )
        ]

    @property
    def total_assessment_weight(self):
        return sum(
            (
                assessment.weight
                for assessment in self.assessments.all()
            ),
            Decimal("0"),
        )

    @property
    def completed_weight(self):
        return sum(
            (
                assessment.weight
                for assessment in self.assessments.all()
                if assessment.is_graded
            ),
            Decimal("0"),
        )

    @property
    def known_remaining_weight(self):
        return sum(
            (
                assessment.weight
                for assessment in self.assessments.all()
                if not assessment.is_graded
            ),
            Decimal("0"),
        )

    @property
    def unannounced_weight(self):
        return max(
            Decimal("100") - self.total_assessment_weight,
            Decimal("0"),
        )

    @property
    def remaining_weight(self):
        return max(
            Decimal("100") - self.completed_weight,
            Decimal("0"),
        )

    @property
    def current_contribution(self):
        return sum(
            (
                assessment.weighted_contribution
                for assessment in self.assessments.all()
                if assessment.weighted_contribution is not None
            ),
            Decimal("0"),
        )

    def required_average_for(self, target_grade):
        if target_grade is None:
            return None

        if self.remaining_weight == Decimal("0"):
            return None

        return (
            (
                target_grade
                - self.current_contribution
            )
            / self.remaining_weight
        ) * Decimal("100")

    def target_status_for(self, target_grade):
        if target_grade is None:
            return "no_target"

        if self.remaining_weight == Decimal("0"):
            if self.current_contribution >= target_grade:
                return "achieved"

            return "not_achieved"

        required_average = self.required_average_for(target_grade)

        if required_average <= Decimal("0"):
            return "achieved"

        if required_average > Decimal("100"):
            return "not_achievable"

        if required_average >= Decimal("80"):
            return "challenging"

        return "achievable"

    def __str__(self):
        return f"{self.module_code} - {self.module_name}"


class Assessment(models.Model):
    COURSEWORK = "Coursework"
    QUIZ = "Quiz"
    LAB = "Lab"
    PRESENTATION = "Presentation"
    FINAL_EXAM = "Final Exam"
    OTHER = "Other"

    ASSESSMENT_TYPE_CHOICES = [
        (COURSEWORK, "Coursework"),
        (QUIZ, "Quiz"),
        (LAB, "Lab"),
        (PRESENTATION, "Presentation"),
        (FINAL_EXAM, "Final Exam"),
        (OTHER, "Other"),
    ]

    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    SUBMITTED = "Submitted"
    GRADED = "Graded"

    STATUS_CHOICES = [
        (NOT_STARTED, "Not Started"),
        (IN_PROGRESS, "In Progress"),
        (SUBMITTED, "Submitted"),
        (GRADED, "Graded"),
    ]

    module = models.ForeignKey(
        Module, 
        on_delete=models.CASCADE, 
        related_name="assessments",
    )
    assessment_name = models.CharField(max_length=100)
    assessment_type = models.CharField(
        max_length=20, 
        choices=ASSESSMENT_TYPE_CHOICES,
    )
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    maximum_score = models.DecimalField(max_digits=6, decimal_places=2)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=NOT_STARTED,
    )
    raw_score = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def percentage_score(self):
        if self.raw_score is None or not self.maximum_score:
            return None

        return (self.raw_score / self.maximum_score) * 100

    @property
    def weighted_contribution(self):
        percentage = self.percentage_score

        if percentage is None:
            return None

        return (percentage * self.weight) / 100

    @property
    def is_graded(self):
        return self.raw_score is not None
    
    def __str__(self):
        return f"{self.assessment_name} - {self.module.module_code}"
