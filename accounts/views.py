from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register(request):
    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:login")

    return render(request, "accounts/register.html", {"form": form})


def login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    for field in form.fields.values():
        field.widget.attrs.update({"class": "form-control"})

    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        return redirect("core:dashboard")

    return render(request, "accounts/login.html", {"form": form})


def logout(request):
    auth_logout(request)
    return redirect("accounts:login")
