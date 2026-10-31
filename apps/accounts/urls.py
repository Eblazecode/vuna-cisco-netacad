from django.urls import path
from .views import MeView, UserProvisionView
urlpatterns = [path("me/", MeView.as_view()), path("users/", UserProvisionView.as_view())]
