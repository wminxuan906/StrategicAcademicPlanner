from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/accounts/login/")
def academic_management(request):
    return render(request, "academic_management.html")
