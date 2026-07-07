from django.contrib import admin

from .models import Assessment, Module, Semester


admin.site.register(Semester)
admin.site.register(Module)
admin.site.register(Assessment)
