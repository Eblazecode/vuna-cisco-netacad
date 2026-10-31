from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Role

class RolePermission(BasePermission):
    """Explicit role allow-list. Object-level scope must still be enforced in querysets."""
    allowed_roles = set()
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_superuser or user.role in self.allowed_roles))

class IsAcademyAdmin(RolePermission):
    allowed_roles = {Role.SUPER_ADMIN, Role.ACADEMY_DIRECTOR, Role.ACADEMY_COORDINATOR}

class CanManageStudents(RolePermission):
    allowed_roles = {Role.SUPER_ADMIN, Role.ACADEMY_DIRECTOR, Role.ACADEMY_COORDINATOR,
                     Role.FACULTY_ADMIN, Role.DEPARTMENT_ADMIN}

class IsReadOnlyAuditor(RolePermission):
    allowed_roles = {Role.AUDITOR}
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.method in SAFE_METHODS

class CanViewStudents(RolePermission):
    allowed_roles = CanManageStudents.allowed_roles | {Role.AUDITOR, Role.UNIVERSITY_MANAGEMENT}
