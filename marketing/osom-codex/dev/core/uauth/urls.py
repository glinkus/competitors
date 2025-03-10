from django.contrib.auth import views as auth_views
from django.urls import path

app_name = "core.uauth"

urlpatterns = [
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("login", auth_views.LoginView.as_view(template_name="core/uauth/login.html"), name="login"),	
    path("register", auth_views.LoginView.as_view(template_name="core/uauth/register.html"), name="register"),
]
