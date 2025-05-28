from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.views import View
from core.uauth.models import UserProfile

class EmailVerificationView(View):
    def send_verification_email(self, request, user, profile):
        verification_link = request.build_absolute_uri(
            reverse('core.uauth:verify_email', kwargs={'token': profile.verification_token})
        )
        
        subject = 'Verify your email address'
        html_message = render_to_string('core/uauth/email/verification_email.html', {
            'user': user,
            'verification_link': verification_link,
        })
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False

    def get(self, request, token):
        try:
            profile = UserProfile.objects.get(verification_token=token)
            if not profile.email_verified:
                profile.email_verified = True
                profile.save()
                messages.success(request, "Your email has been verified successfully! You can now log in.")
            else:
                messages.info(request, "Your email has already been verified.")
            return redirect('/login/')
        except UserProfile.DoesNotExist:
            messages.error(request, "Invalid verification link. Try new one.")
            return redirect('/register/')

class VerificationSentView(View):
    template_name = 'core/uauth/verification_sent.html'
    
    def get(self, request, token):
        try:
            profile = UserProfile.objects.get(verification_token=token)
            verification_link = request.build_absolute_uri(
                reverse('core.uauth:verify_email', kwargs={'token': profile.verification_token})
            )
            return render(request, self.template_name, {
                'verification_link': verification_link,
                'user': profile.user
            })
        except UserProfile.DoesNotExist:
            messages.error(request, "Invalid verification token.")
            return redirect('core.uauth:register')
