from django.db import transaction
from rest_framework import serializers
from apps.accounts.models import User, Role
from apps.academics.models import Faculty, Department, AcademicProgramme
from .models import Student, StudentStatus, StudentStatusHistory
from apps.audit.models import AuditLog

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    faculty_name = serializers.CharField(source="faculty.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    class Meta:
        model = Student
        fields = ("id", "user", "matric_number", "first_name", "middle_name", "last_name", "full_name", "email", "phone_number", "faculty", "faculty_name", "department", "department_name", "programme", "academic_level", "admission_year", "current_session", "status", "photograph", "emergency_contact_name", "emergency_contact_phone", "registration_channel", "submitted_at", "verified_at", "rejection_reason", "created_at", "updated_at")
        read_only_fields = ("id", "user", "status", "registration_channel", "submitted_at", "verified_at", "rejection_reason", "created_at", "updated_at")
    def validate(self, attrs):
        faculty = attrs.get("faculty", getattr(self.instance, "faculty", None))
        department = attrs.get("department", getattr(self.instance, "department", None))
        if faculty and department and department.faculty_id != faculty.id:
            raise serializers.ValidationError({"department": "Selected department does not belong to the selected faculty."})
        programme = attrs.get("programme", getattr(self.instance, "programme", None))
        if programme and department and programme.department_id != department.id:
            raise serializers.ValidationError({"programme": "Selected programme does not belong to the selected department."})
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            role = request.user.role
            if role == Role.FACULTY_ADMIN and faculty and faculty.id != request.user.faculty_id:
                raise serializers.ValidationError({"faculty": "You may only manage students within your assigned faculty."})
            if role == Role.DEPARTMENT_ADMIN and department and department.id != request.user.department_id:
                raise serializers.ValidationError({"department": "You may only manage students within your assigned department."})
        return attrs

class PublicRegistrationSerializer(serializers.Serializer):
    matric_number = serializers.CharField(max_length=40)
    first_name = serializers.CharField(max_length=100)
    middle_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=30, required=False, allow_blank=True)
    faculty = serializers.PrimaryKeyRelatedField(queryset=Faculty.objects.filter(is_active=True))
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.filter(is_active=True))
    programme = serializers.PrimaryKeyRelatedField(queryset=AcademicProgramme.objects.filter(is_active=True), required=False, allow_null=True)
    academic_level = serializers.CharField(max_length=20, required=False, allow_blank=True)
    admission_year = serializers.IntegerField(required=False, allow_null=True, min_value=1950, max_value=2100)
    password = serializers.CharField(write_only=True, min_length=12, trim_whitespace=False)
    def validate(self, attrs):
        if Student.objects.filter(matric_number__iexact=attrs["matric_number"]).exists():
            raise serializers.ValidationError({"matric_number": "A student record with this matriculation number already exists."})
        if User.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "An account with this email already exists."})
        department = attrs["department"]
        if department.faculty_id != attrs["faculty"].id:
            raise serializers.ValidationError({"department": "Department is invalid for the selected faculty."})
        programme = attrs.get("programme")
        if programme and programme.department_id != department.id:
            raise serializers.ValidationError({"programme": "Programme is invalid for the selected department."})
        return attrs
    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data["email"].lower()
        user = User(email=email, username=email, first_name=validated_data["first_name"], last_name=validated_data["last_name"], role=Role.STUDENT, is_active=False)
        user.set_password(password)
        user.save()
        validated_data["email"] = email
        student = Student.objects.create(user=user, registration_channel="SELF", status=StudentStatus.PENDING, **validated_data)
        StudentStatusHistory.objects.create(student=student, previous_status="", new_status=StudentStatus.PENDING, reason="Self-registration submitted for verification")
        AuditLog.objects.create(actor=user, action="STUDENT_SELF_REGISTERED", object_type="Student", object_id=str(student.id), metadata={"registration_channel": "SELF"})
        return student

class StudentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=StudentStatus.choices)
    reason = serializers.CharField(required=False, allow_blank=True)
    def validate_status(self, value):
        if value == StudentStatus.PENDING: raise serializers.ValidationError("A verified record cannot be returned to pending through this action.")
        return value
