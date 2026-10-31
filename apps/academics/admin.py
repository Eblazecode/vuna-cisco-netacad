from django.contrib import admin
from .models import Faculty, Department, AcademicProgramme, AcademicSession
admin.site.register(Faculty)
admin.site.register(Department)
admin.site.register(AcademicProgramme)
admin.site.register(AcademicSession)
