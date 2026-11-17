from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AcademicProgramme, Department, Faculty


class PublicAcademicStructureView(APIView):
    """Expose only active academic reference data needed by public registration."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        faculties = Faculty.objects.filter(is_active=True).order_by("name").values("id", "name", "code")
        departments = Department.objects.filter(
            is_active=True, faculty__is_active=True
        ).order_by("name").values("id", "name", "code", "faculty_id")
        programmes = AcademicProgramme.objects.filter(
            is_active=True, department__is_active=True, department__faculty__is_active=True
        ).order_by("name").values("id", "name", "code", "department_id")
        return Response({
            "faculties": list(faculties),
            "departments": list(departments),
            "programmes": list(programmes),
        })
