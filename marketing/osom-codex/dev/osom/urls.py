from django.urls import path, include

urlpatterns = [
    # ...other URL patterns...
    path('analysis/', include('modules.analysis.urls')),
    # ...other URL patterns...
]
