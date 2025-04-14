from django.urls import path

from .views.analysis_analyse_view import AnalyseView
from .views.analysis_website_page_view import URLView
from .views.analysis_page_keywords_view import PageKeywordsView
from .views.analysis_website_keywords_view import WebsiteKeywordsView
from .views.analysis_insights_view import InsightsView
from .views.analysis_overview_view import OverviewView
from .views.analysis_landing_view import LandingView

app_name = "modules.analysis" 

urlpatterns = [
    path('', LandingView.as_view(), name='analysis'),
    path('analyse/', AnalyseView.as_view(), name='analyse'),
    path('analyse/website_page/<int:website_id>/', URLView.as_view(), name='website_page'),
    path('website-keywords/<int:website_id>/', WebsiteKeywordsView.as_view(), name='website_keywords'),
    path('insights/<int:website_id>/', InsightsView.as_view(), name='insights'),
    path('overview/<int:website_id>/', OverviewView.as_view(), name='overview'),
]