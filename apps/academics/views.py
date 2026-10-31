from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsAcademyAdmin
from .models import Faculty, Department, AcademicProgramme, AcademicSession
from .serializers import FacultySerializer, DepartmentSerializer, AcademicProgrammeSerializer, AcademicSessionSerializer

class ScopedAdminViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAcademyAdmin]
class FacultyViewSet(ScopedAdminViewSet): queryset = Faculty.objects.all(); serializer_class = FacultySerializer
class DepartmentViewSet(ScopedAdminViewSet): queryset = Department.objects.select_related("faculty").all(); serializer_class = DepartmentSerializer
class AcademicProgrammeViewSet(ScopedAdminViewSet): queryset = AcademicProgramme.objects.select_related("department").all(); serializer_class = AcademicProgrammeSerializer
class AcademicSessionViewSet(ScopedAdminViewSet): queryset = AcademicSession.objects.all(); serializer_class = AcademicSessionSerializer
