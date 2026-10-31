import pytest
from django.db import IntegrityError, transaction
from .models import Faculty, Department

@pytest.mark.django_db
def test_department_is_attached_to_faculty():
    faculty = Faculty.objects.create(name="Science", code="SCI")
    department = Department.objects.create(faculty=faculty, name="Computer Science", code="CSC")
    assert department.faculty == faculty
