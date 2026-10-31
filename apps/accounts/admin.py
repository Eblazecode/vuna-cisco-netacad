from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "role", "is_active")
    fieldsets = UserAdmin.fieldsets + (("VUNA Access", {"fields": ("role", "phone_number", "must_change_password", "mfa_enabled")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("VUNA Access", {"fields": ("email", "role", "phone_number")}),)
