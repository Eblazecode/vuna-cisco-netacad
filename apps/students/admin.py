from django.contrib import admin
from .models import Student, StudentDocument, StudentStatusHistory
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("matric_number", "last_name", "first_name", "faculty", "department", "status")
    search_fields = ("matric_number", "first_name", "last_name", "email")
    list_filter = ("status", "faculty", "department")
    readonly_fields = ("submitted_at", "verified_at", "created_at", "updated_at")
admin.site.register(StudentDocument)
admin.site.register(StudentStatusHistory)
