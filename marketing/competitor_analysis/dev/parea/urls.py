from django.contrib.auth import views as auth_views
from django.urls import path
from core.uauth.views import views as uauth_views

app_name = "parea"

urlpatterns = [
    path("", uauth_views.login_page, name="index"), 
    
    
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]