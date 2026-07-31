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

    path("modules/", views.module_list, name="module_list"),
    path("modules/create/", views.module_create, name="module_create"),
    path(
        "modules/<int:module_id>/edit/",
        views.module_update,
        name="module_update",
    ),
    path(
        "modules/<int:module_id>/delete/",
        views.module_delete,
        name="module_delete",
    ),
]
