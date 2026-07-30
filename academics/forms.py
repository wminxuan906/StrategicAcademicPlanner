from django import forms
from .models import Semester


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