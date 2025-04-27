from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views import View
from core.uauth.models import UserProfile
from core.uauth.views.email_verification_view import EmailVerificationView

class LoginView(View):
    template_name = 'core/uauth/login.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        is_email = '@' in username_or_email
        
        if is_email:
            if not User.objects.filter(email=username_or_email).exists():
                messages.error(request, 'No account found with this email')
                return redirect('/login/')
            user_obj = User.objects.get(email=username_or_email)
            username = user_obj.username
        else:
            if not User.objects.filter(username=username_or_email).exists():
                messages.error(request, 'Invalid Username')
                return redirect('/login/')
            username = username_or_email
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            try:
                profile = UserProfile.objects.get(user=user)
                if not profile.email_verified:
                    messages.warning(request, "Please verify your email address before logging in.")
                    email_view = EmailVerificationView()
                    email_view.send_verification_email(request, user, profile)
                    messages.info(request, "A new verification email has been sent to your email address.")
                    return redirect('/login/')
                
                login(request, user)
                return redirect('/analysis/')
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
                messages.warning(request, "Please verify your email address before logging in.")
                email_view = EmailVerificationView()
                email_view.send_verification_email(request, user, profile)
                return redirect('/login/')
