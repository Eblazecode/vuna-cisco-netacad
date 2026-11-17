from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.academics.views import FacultyViewSet, DepartmentViewSet, AcademicProgrammeViewSet, AcademicSessionViewSet
from apps.academics.public_views import PublicAcademicStructureView
from apps.students.views import StudentViewSet, PublicRegistrationView

router = DefaultRouter()
router.register("faculties", FacultyViewSet)
router.register("departments", DepartmentViewSet)
router.register("academic-programmes", AcademicProgrammeViewSet)
router.register("academic-sessions", AcademicSessionViewSet)
router.register("students", StudentViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/public/academic-structure/", PublicAcademicStructureView.as_view(), name="public-academic-structure"),
    path("api/v1/registration/", PublicRegistrationView.as_view(), name="student-registration"),
    path("api/v1/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
