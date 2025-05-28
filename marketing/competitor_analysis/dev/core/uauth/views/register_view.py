from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View
from core.uauth.models import UserProfile
from core.uauth.views.email_verification_view import EmailVerificationView

class RegisterView(View):
    template_name = 'core/uauth/register.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        user = User.objects.filter(username=username)
        
        if user.exists():
            messages.info(request, "Username already taken!")
            return redirect('/register/')
        
        if User.objects.filter(email=email).exists():
            messages.info(request, "Email address already in use!")
            return redirect('/register/')
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long!")
            return redirect('/register/')
            
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email
        )
        
        user.set_password(password)
        user.save()
        
        profile = UserProfile.objects.create(user=user)
        
        email_view = EmailVerificationView()
        success = email_view.send_verification_email(request, user, profile)
        
        if success:
            messages.info(request, "Account created successfully! Please check your email to verify your account before logging in.")
        else:
            messages.warning(request, "Account created but we couldn't send the verification email automatically. Please use the verification link provided.")
        
        return redirect('/login/')
