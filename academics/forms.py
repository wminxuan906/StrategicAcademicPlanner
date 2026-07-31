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

        if user:
            self.fields["semester"].queryset = Semester.objects.filter(
                user=user
            ).order_by("-academic_year", "name")
        else:
            self.fields["semester"].queryset = Semester.objects.none()


class AssessmentForm(forms.ModelForm):

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
                    "min": 0,
                    "step": "0.01",
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

            "raw_score": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "step": "0.01",
                    "placeholder": "Optional",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):

        super().__init__(*args, **kwargs)

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

            self.fields["module"].queryset = Module.objects.none()