from django.urls import path
from .views.analysis_analyse_view import AnalyseView, stop_scraping, continue_scraping
from .views.analysis_website_page_view import URLView
from .views.analysis_overview_view import OverviewView, website_insight_status, target_audience_status, technology_status
from .views.analysis_landing_view import LandingView
from .views.analysis_compare_view import CompareView
from .views.analysis_generate_pdf_view import GeneratePDFView
from .views.analysis_confirm_view import ConfirmReanalyseView

app_name = "modules.analysis" 

urlpatterns = [
    path('', LandingView.as_view(), name='analysis'),
    path('analyse/', AnalyseView.as_view(), name='analyse'),
    path('analyse/website_page/<int:website_id>/', URLView.as_view(), name='website_page'),
    path('analyse/overview/<int:website_id>/', OverviewView.as_view(), name='overview'),
    path('api/website/<int:website_id>/insight-status/', website_insight_status, name='website-insight-status'),
    path("api/website/target-audience-status/<int:website_id>/", target_audience_status, name="target_audience_status"),
    path('stop-scraping/<int:website_id>/', stop_scraping, name='stop_scraping'),
    path('continue-scraping/<int:website_id>/', continue_scraping, name='continue-scraping'),
    path('analyse/compare/', CompareView.as_view(), name='compare'),
    path("api/technology-status/<int:website_id>/", technology_status, name="technology_status"),
    path('analyse/overview/pdf/<int:website_id>/', GeneratePDFView.as_view(), name='generate_pdf'),
    path('analyse/confirm/', ConfirmReanalyseView.as_view(), name='analyse_confirm'),
]