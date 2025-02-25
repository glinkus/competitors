from django.contrib.auth import views as auth_views
from django.urls import path

app_name = "core.uauth"

urlpatterns = [
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
]
