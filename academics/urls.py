from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    path("", views.academic_management, name="academic_management"),
    path("semesters/", views.semester_list, name="semester_list"),
    path("semesters/create/", views.semester_create, name="semester_create"),

    path(
        "semesters/<int:semester_id>/edit/",
        views.semester_update,
        name="semester_update"
    ),

    path(
        "semesters/<int:semester_id>/delete/",
        views.semester_delete,
        name="semester_delete"
    ),
]
