from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    path("", views.academic_management, name="academic_management"),
]
