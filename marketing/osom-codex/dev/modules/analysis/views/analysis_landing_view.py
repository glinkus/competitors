from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from modules.analysis.models import Page, ExtractedKeyword

class LandingView(TemplateView):
    template_name = "modules/analysis/landing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
