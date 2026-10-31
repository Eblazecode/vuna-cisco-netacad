import csv
import io
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from apps.accounts.models import Role
from apps.accounts.permissions import CanManageStudents, CanViewStudents
from apps.audit.models import AuditLog
from .models import Student, StudentStatus, StudentStatusHistory
from .serializers import StudentSerializer, PublicRegistrationSerializer, StudentStatusUpdateSerializer

class RegistrationThrottle(AnonRateThrottle): rate = "5/hour"
class PublicRegistrationView(CreateAPIView):
    serializer_class = PublicRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegistrationThrottle]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data); serializer.is_valid(raise_exception=True)
        student = serializer.save()
        return Response({"message": "Registration submitted for verification.", "student_id": str(student.id), "status": student.status}, status=status.HTTP_201_CREATED)

class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    queryset = Student.objects.select_related("faculty", "department", "programme", "current_session", "user").all()
    def get_permissions(self):
        read_actions = {"list", "retrieve", "export_csv"}
        if self.action in read_actions:
            return [IsAuthenticated(), CanViewStudents()]
        return [IsAuthenticated(), CanManageStudents()]
    def perform_create(self, serializer):
        student = serializer.save(registration_channel="ADMIN", status=StudentStatus.PENDING)
        StudentStatusHistory.objects.create(student=student, previous_status="", new_status=StudentStatus.PENDING, changed_by=self.request.user, reason="Administrator-assisted registration")
        AuditLog.objects.create(actor=self.request.user, action="STUDENT_ADMIN_REGISTERED", object_type="Student", object_id=str(student.id), metadata={"registration_channel": "ADMIN"})
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == Role.FACULTY_ADMIN:
            qs = qs.filter(faculty_id=getattr(user, "faculty_id", None))
        elif user.role == Role.DEPARTMENT_ADMIN:
            qs = qs.filter(department_id=getattr(user, "department_id", None))
        status_filter = self.request.query_params.get("status")
        faculty = self.request.query_params.get("faculty")
        department = self.request.query_params.get("department")
        q = self.request.query_params.get("q")
        if status_filter: qs = qs.filter(status=status_filter)
        if faculty: qs = qs.filter(faculty_id=faculty)
        if department: qs = qs.filter(department_id=department)
        if q:
            from django.db.models import Q
            qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(matric_number__icontains=q) | Q(email__icontains=q))
        return qs
    @action(detail=True, methods=["post"], url_path="status")
    @transaction.atomic
    def set_status(self, request, pk=None):
        student = self.get_object()
        serializer = StudentStatusUpdateSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]
        reason = serializer.validated_data.get("reason", "")
        previous = student.status
        student.status = new_status
        if new_status == StudentStatus.ACTIVE:
            student.verified_at = timezone.now(); student.verified_by = request.user
            if student.user_id:
                student.user.is_active = True; student.user.save(update_fields=["is_active"])
        elif new_status in {StudentStatus.REJECTED, StudentStatus.SUSPENDED} and student.user_id:
            student.user.is_active = False; student.user.save(update_fields=["is_active"])
        student.rejection_reason = reason if new_status == StudentStatus.REJECTED else ""
        student.save()
        StudentStatusHistory.objects.create(student=student, previous_status=previous, new_status=new_status, changed_by=request.user, reason=reason)
        AuditLog.objects.create(actor=request.user, action="STUDENT_STATUS_CHANGED", object_type="Student", object_id=str(student.id), metadata={"from": previous, "to": new_status, "reason": reason})
        return Response(StudentSerializer(student).data)
    @action(detail=False, methods=["post"], url_path="import.csv")
    def import_csv(self, request):
        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "Upload a CSV file using the file field."}, status=400)
        if upload.size > 5 * 1024 * 1024:
            return Response({"detail": "CSV file exceeds the 5 MB limit."}, status=400)
        try:
            text = upload.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            required = {"matric_number", "first_name", "last_name", "email", "faculty_code", "department_code"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                return Response({"detail": "CSV headers must include: " + ", ".join(sorted(required))}, status=400)
            from apps.academics.models import Faculty, Department
            created, errors = [], []
            for line, row in enumerate(reader, start=2):
                try:
                    faculty = Faculty.objects.get(code=row["faculty_code"].strip(), is_active=True)
                    department = Department.objects.get(code=row["department_code"].strip(), faculty=faculty, is_active=True)
                    if request.user.role == Role.FACULTY_ADMIN and faculty.id != request.user.faculty_id:
                        raise ValueError("Row is outside your assigned faculty scope")
                    if request.user.role == Role.DEPARTMENT_ADMIN and department.id != request.user.department_id:
                        raise ValueError("Row is outside your assigned department scope")
                    matric = row["matric_number"].strip()
                    if Student.objects.filter(matric_number__iexact=matric).exists():
                        raise ValueError("Duplicate matriculation number")
                    student = Student.objects.create(matric_number=matric, first_name=row["first_name"].strip(), last_name=row["last_name"].strip(), email=row["email"].strip().lower(), faculty=faculty, department=department, academic_level=row.get("academic_level", "").strip(), admission_year=int(row["admission_year"]) if row.get("admission_year", "").strip() else None, registration_channel="ADMIN", status=StudentStatus.PENDING)
                    StudentStatusHistory.objects.create(student=student, previous_status="", new_status=StudentStatus.PENDING, changed_by=request.user, reason="Bulk CSV import")
                    created.append(str(student.id))
                except Exception as exc:
                    errors.append({"row": line, "matric_number": row.get("matric_number", ""), "error": str(exc)})
            AuditLog.objects.create(actor=request.user, action="STUDENT_CSV_IMPORTED", object_type="Student", metadata={"created_count": len(created), "error_count": len(errors)})
            return Response({"created": len(created), "failed": len(errors), "errors": errors}, status=207 if errors else 201)
        except UnicodeDecodeError:
            return Response({"detail": "CSV must be UTF-8 encoded."}, status=400)

    @action(detail=False, methods=["get"], url_path="export.csv")
    def export_csv(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="vuna-students.csv"'
        writer = csv.writer(response)
        writer.writerow(["Matric Number", "First Name", "Last Name", "Email", "Faculty", "Department", "Status"])
        for s in self.filter_queryset(self.get_queryset()):
            writer.writerow([s.matric_number, s.first_name, s.last_name, s.email, s.faculty.name, s.department.name, s.status])
        return response
