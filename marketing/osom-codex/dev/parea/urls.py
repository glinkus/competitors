from django.contrib.auth import views as auth_views
from django.urls import path
from core.uauth.views import views as uauth_views

app_name = "parea"

# urlpatterns = [
#     path(
#         "",
#         auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name="parea/index.html"),
#         name="index",
#     ),
# ]
urlpatterns = [
    path("", uauth_views.login_page, name="index"),
]