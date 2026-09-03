from decimal import Decimal
from django import forms
from .models import Semester, Module, Assessment


class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = [
            "name",
            "academic_year",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter semester name"
                }
            ),

            "academic_year": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2026/27"
                }
            ),
        }


class ModuleForm(forms.ModelForm):
    # Use widgets to provide consistent Bootstrap styling and input limits
    class Meta:
        model = Module
        fields = [
            "semester",
            "module_code",
            "module_name",
            "credits",
            "target_grade",
        ]

        widgets = {
            "semester": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "module_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. COMPSCI5001",
                }
            ),

            "module_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter module name",
                }
            ),

            "credits": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "target_grade": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 100,
                    "step": "0.01",
                    "placeholder": "Optional",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit semester choices to semesters owned by the current user
        if user:
            self.fields["semester"].queryset = Semester.objects.filter(
                user=user
            ).order_by("-academic_year", "name")
        else:
            # Show no semester choices when a user is not provided
            self.fields["semester"].queryset = Semester.objects.none()


class AssessmentForm(forms.ModelForm):

    # Collect the assessment details used for planning and grade tracking
    class Meta:
        model = Assessment

        fields = [
            "module",
            "assessment_name",
            "assessment_type",
            "weight",
            "maximum_score",
            "deadline",
            "status",
            "effort_level",
            "raw_score",
        ]

        widgets = {
            "module": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "assessment_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter assessment name",
                }
            ),

            "assessment_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "weight": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 100,
                    "step": "0.01",
                }
            ),

            "maximum_score": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0.01,
                    "step": "0.01",
                    "placeholder": "100",
                }
            ),

            "deadline": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "effort_level": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "raw_score": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "step": "0.5",
                    "placeholder": "Optional",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):

        super().__init__(*args, **kwargs)

        # Limit module choices to modules in the current user's semesters
        if user:

            self.fields["module"].queryset = (
                Module.objects.filter(
                    semester__user=user
                )
                .select_related("semester")
                .order_by(
                    "-semester__academic_year",
                    "module_code",
                )
            )

        else:

            # Show no module choices when a user is not provided
            self.fields["module"].queryset = Module.objects.none()
    
    def clean_weight(self):
        # Validate the submitted weight against other assessments in the module
        weight = self.cleaned_data.get("weight")
        module = self.cleaned_data.get("module")

        if weight is None or module is None:
            return weight

        assessments = Assessment.objects.filter(
            module=module
        )

        # Exclude the current record so its old weight is not counted on update
        if self.instance.pk:
            assessments = assessments.exclude(
                pk=self.instance.pk
            )

        # Add the weights of the module's other assessments
        existing_weight = sum(
            (
                assessment.weight
                for assessment in assessments
            ),
            Decimal("0"),
        )

        total_weight = existing_weight + weight

         # Prevent the total assessment weight from exceeding 100 percent
        if total_weight > Decimal("100"):
            remaining_weight = (
                Decimal("100") - existing_weight
            )

            raise forms.ValidationError(
                "The total assessment weight cannot exceed 100%. "
                f"The maximum available weight is {remaining_weight}%."
            )

        return weight

    def clean(self):
        # Validate values that depend on more than one assessment field
        cleaned_data = super().clean()

        maximum_score = cleaned_data.get("maximum_score")
        raw_score = cleaned_data.get("raw_score")
        status = cleaned_data.get("status")

        # Use a percentage scale when no maximum score is provided
        if maximum_score is None:
            maximum_score = Decimal("100.00")
            cleaned_data["maximum_score"] = maximum_score

        # A valid maximum score must be greater than zero
        if maximum_score <= Decimal("0"):
            self.add_error(
                "maximum_score",
                "Maximum score must be greater than 0."
            )

        # Prevent an actual mark from exceeding the assessment maximum
        if (
            raw_score is not None
            and maximum_score > Decimal("0")
            and raw_score > maximum_score
        ):
            self.add_error(
                "raw_score",
                "Raw score cannot exceed the maximum score."
            )

        # Keep the assessment status consistent with the recorded mark
        if raw_score is not None:
            cleaned_data["status"] = Assessment.GRADED

        elif status == Assessment.GRADED:
            self.add_error(
                "raw_score",
                "A raw score is required for a graded assessment."
            )

        return cleaned_data

class WhatIfCalculatorForm(forms.Form):
    # Start with no module choices until the current user is provided
    module = forms.ModelChoiceField(
        queryset=Module.objects.none(),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    # Allow an optional temporary target between zero and one hundred
    target_grade = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=100,
        decimal_places=2,
        max_digits=5,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": 0,
                "max": 100,
                "step": "1",
                "placeholder": "Enter a temporary target",
            }
        ),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Only show modules that belong to the logged-in user
        if user:
            self.fields["module"].queryset = (
                Module.objects.filter(
                    semester__user=user
                )
                .select_related("semester")
                .order_by(
                    "-semester__academic_year",
                    "module_code",
                )
            )
