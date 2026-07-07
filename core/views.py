from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/accounts/login/")
def dashboard(request):
    return render(request, "dashboard.html")


@login_required(login_url="/accounts/login/")
def settings(request):
    return render(request, "settings.html")
