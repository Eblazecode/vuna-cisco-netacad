import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models.functions import Lower

class StudentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending Verification"
    ACTIVE = "ACTIVE", "Active"
    REJECTED = "REJECTED", "Rejected"
    SUSPENDED = "SUSPENDED", "Suspended"
    GRADUATED = "GRADUATED", "Graduated"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="student_profile", null=True, blank=True)
    matric_number = models.CharField(max_length=40, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    phone_number = models.CharField(max_length=30, blank=True)
    faculty = models.ForeignKey("academics.Faculty", on_delete=models.PROTECT, related_name="students")
    department = models.ForeignKey("academics.Department", on_delete=models.PROTECT, related_name="students")
    programme = models.ForeignKey("academics.AcademicProgramme", on_delete=models.PROTECT, related_name="students", null=True, blank=True)
    academic_level = models.CharField(max_length=20, blank=True)
    admission_year = models.PositiveSmallIntegerField(null=True, blank=True)
    current_session = models.ForeignKey("academics.AcademicSession", on_delete=models.PROTECT, related_name="students", null=True, blank=True)
    status = models.CharField(max_length=16, choices=StudentStatus.choices, default=StudentStatus.PENDING, db_index=True)
    photograph = models.ImageField(upload_to="students/photographs/%Y/%m/", blank=True)
    emergency_contact_name = models.CharField(max_length=180, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)
    registration_channel = models.CharField(max_length=20, choices=[("SELF", "Self-service"), ("ADMIN", "Administrator")], default="SELF")
    submitted_at = models.DateTimeField(default=timezone.now)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="verified_students")
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [models.Index(fields=["faculty", "department", "status"]), models.Index(fields=["created_at"])]
        constraints = [models.CheckConstraint(condition=models.Q(admission_year__isnull=True) | models.Q(admission_year__gte=1950), name="student_admission_year_valid"), models.UniqueConstraint(Lower("matric_number"), name="uniq_student_matric_case_insensitive")]
    def __str__(self): return f"{self.matric_number} — {self.last_name}, {self.first_name}"
    @property
    def full_name(self): return " ".join(x for x in [self.first_name, self.middle_name, self.last_name] if x)

class StudentStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="status_history")
    previous_status = models.CharField(max_length=16, choices=StudentStatus.choices, blank=True)
    new_status = models.CharField(max_length=16, choices=StudentStatus.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    reason = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-changed_at"]

class StudentDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="documents")
    document_type = models.CharField(max_length=80)
    file = models.FileField(upload_to="students/documents/%Y/%m/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="verified_student_documents")
