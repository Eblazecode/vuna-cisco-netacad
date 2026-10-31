from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserMeSerializer, UserProvisionSerializer
from .permissions import IsAcademyAdmin
from .models import User

class MeView(generics.RetrieveAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self): return self.request.user

class UserProvisionView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by("last_name", "first_name")
    serializer_class = UserProvisionSerializer
    permission_classes = [IsAcademyAdmin]
