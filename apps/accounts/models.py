import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", "Super Administrator"
    UNIVERSITY_MANAGEMENT = "UNIVERSITY_MANAGEMENT", "University Management"
    ACADEMY_DIRECTOR = "ACADEMY_DIRECTOR", "Academy Director"
    ACADEMY_COORDINATOR = "ACADEMY_COORDINATOR", "Academy Coordinator"
    FACULTY_ADMIN = "FACULTY_ADMIN", "Faculty Administrator"
    DEPARTMENT_ADMIN = "DEPARTMENT_ADMIN", "Department Administrator"
    FINANCE_OFFICER = "FINANCE_OFFICER", "Finance Officer"
    INSTRUCTOR = "INSTRUCTOR", "Instructor"
    LAB_OFFICER = "LAB_OFFICER", "Laboratory Officer"
    STUDENT = "STUDENT", "Student"
    AUDITOR = "AUDITOR", "Auditor"

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.STUDENT)
    phone_number = models.CharField(max_length=30, blank=True)
    must_change_password = models.BooleanField(default=False)
    mfa_enabled = models.BooleanField(default=False)
    faculty = models.ForeignKey("academics.Faculty", on_delete=models.PROTECT, null=True, blank=True, related_name="scoped_users")
    department = models.ForeignKey("academics.Department", on_delete=models.PROTECT, null=True, blank=True, related_name="scoped_users")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.get_full_name() or self.email
