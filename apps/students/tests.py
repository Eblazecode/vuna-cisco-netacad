import pytest
from rest_framework.test import APIClient
from apps.accounts.models import User, Role
from apps.academics.models import Faculty, Department
from .models import Student, StudentStatus

@pytest.mark.django_db
def test_public_registration_creates_pending_inactive_student():
    faculty = Faculty.objects.create(name="Science", code="SCI")
    department = Department.objects.create(faculty=faculty, name="Computer Science", code="CSC")
    client = APIClient()
    response = client.post("/api/v1/registration/", {
        "matric_number": "VU/CSC/26/0001", "first_name": "Ada", "last_name": "Okafor",
        "email": "ada@example.edu", "faculty": str(faculty.id), "department": str(department.id),
        "password": "A-very-strong-test-password-2026"
    }, format="json")
    assert response.status_code == 201
    student = Student.objects.get(matric_number="VU/CSC/26/0001")
    assert student.status == StudentStatus.PENDING
    assert student.user.is_active is False

@pytest.mark.django_db
def test_student_matric_number_is_unique():
    faculty = Faculty.objects.create(name="Science", code="SCI")
    department = Department.objects.create(faculty=faculty, name="Computer Science", code="CSC")
    Student.objects.create(matric_number="VU/1", first_name="A", last_name="B", email="a@x.com", faculty=faculty, department=department)
    with pytest.raises(Exception):
        Student.objects.create(matric_number="VU/1", first_name="C", last_name="D", email="c@x.com", faculty=faculty, department=department)
