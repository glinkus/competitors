from django.contrib.auth import views as auth_views
from django.urls import path
from .views.views import login_page, register_page

app_name = "core.uauth"

urlpatterns = [
    path("login/", login_page, name="login"),
    path("register/", register_page, name="register"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
