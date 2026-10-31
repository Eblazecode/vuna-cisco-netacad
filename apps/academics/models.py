import uuid
from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True

class Faculty(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=180, unique=True)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ["name"]
    def __str__(self): return self.name

class Department(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name="departments")
    name = models.CharField(max_length=180)
    code = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["faculty", "name"], name="uniq_department_per_faculty")]
    def __str__(self): return f"{self.name} ({self.faculty.code})"

class AcademicProgramme(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="programmes")
    name = models.CharField(max_length=180)
    code = models.CharField(max_length=30, unique=True)
    award = models.CharField(max_length=100, blank=True)
    duration_years = models.PositiveSmallIntegerField(default=4)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ["name"]
    def __str__(self): return self.name

class AcademicSession(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, unique=True, help_text="Example: 2026/2027")
    starts_on = models.DateField()
    ends_on = models.DateField()
    is_current = models.BooleanField(default=False)
    is_open_for_registration = models.BooleanField(default=False)
    class Meta: ordering = ["-starts_on"]
    def __str__(self): return self.name
