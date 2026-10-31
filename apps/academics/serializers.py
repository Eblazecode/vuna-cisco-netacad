from rest_framework import serializers
from .models import Faculty, Department, AcademicProgramme, AcademicSession

class FacultySerializer(serializers.ModelSerializer):
    class Meta: model = Faculty; fields = "__all__"; read_only_fields = ("id", "created_at", "updated_at")
class DepartmentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.name", read_only=True)
    class Meta: model = Department; fields = "__all__"; read_only_fields = ("id", "created_at", "updated_at")
class AcademicProgrammeSerializer(serializers.ModelSerializer):
    class Meta: model = AcademicProgramme; fields = "__all__"; read_only_fields = ("id", "created_at", "updated_at")
class AcademicSessionSerializer(serializers.ModelSerializer):
    class Meta: model = AcademicSession; fields = "__all__"; read_only_fields = ("id", "created_at", "updated_at")
