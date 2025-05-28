from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from core.uauth.models import *
from core.uauth.views.login_view import LoginView
from core.uauth.views.register_view import RegisterView
from core.uauth.views.email_verification_view import EmailVerificationView, VerificationSentView
from core.uauth.views.logout_view import LogoutView

login_view_instance = LoginView()
register_view_instance = RegisterView()
email_verification_instance = EmailVerificationView()
verification_sent_instance = VerificationSentView()

def logout_view(request):
    return LogoutView.as_view()(request)

def login_page(request):
    if request.method == "POST":
        return login_view_instance.post(request)
    return login_view_instance.get(request)

def register_page(request):
    if request.method == 'POST':
        return register_view_instance.post(request)
    return register_view_instance.get(request)

def send_verification_email(request, user, profile):
    return email_verification_instance.send_verification_email(request, user, profile)

def verification_sent(request, token):
    return verification_sent_instance.get(request, token)

def verify_email(request, token):
    return email_verification_instance.get(request, token)
