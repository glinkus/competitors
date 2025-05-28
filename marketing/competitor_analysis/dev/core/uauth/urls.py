from django.urls import path
from core.uauth.views.login_view import LoginView
from core.uauth.views.register_view import RegisterView
from core.uauth.views.email_verification_view import EmailVerificationView, VerificationSentView
from core.uauth.views.logout_view import LogoutView

app_name = 'core.uauth'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/<uuid:token>/', EmailVerificationView.as_view(), name='verify_email'),
    path('verification-sent/<uuid:token>/', VerificationSentView.as_view(), name='verification_sent'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
