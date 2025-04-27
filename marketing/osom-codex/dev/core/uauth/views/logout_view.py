from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.views import View

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('core.uauth:login')
