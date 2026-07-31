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

    def __str__(self):
        return f"{self.assessment_name} - {self.module.module_code}"
