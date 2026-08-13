from django import forms
from django.contrib.auth.models import User


class AccountUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Username",
            }
        )

        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Email address",
            }
        )