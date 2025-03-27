from django.urls import path

from . import views
from .views.analysis_saved_url_view import URLView
from .views.analysis_page_keywords_view import PageKeywordsView
from .views.analysis_website_keywords_view import WebsiteKeywordsView

app_name = "modules.analysis" 

urlpatterns = [
    path("analyse", views.AnalyseView.as_view(), name="analyse"),
    path('analyse/saved-urls/<int:website_id>/', URLView.as_view(), name='saved_urls'),
    path('analyse/saved-urls/<int:website_id>/<int:page_id>/keywords/', PageKeywordsView.as_view(), name='page_keywords'),
    path('analyse/website-keywords/<int:website_id>/', WebsiteKeywordsView.as_view(), name='website_keywords'),
    
]