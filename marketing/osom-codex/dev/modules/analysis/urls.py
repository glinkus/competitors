from django.urls import path

from . import views
from .views.analysis_saved_url_view import URLView

app_name = "modules.analysis" 

urlpatterns = [
    path("analyse", views.AnalyseView.as_view(), name="analyse"),
    path('analyse/saved-urls/<int:website_id>/', URLView.as_view(), name='saved_urls'),
]