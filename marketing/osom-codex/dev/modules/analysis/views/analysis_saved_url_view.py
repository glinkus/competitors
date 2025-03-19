from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from modules.analysis.models import Website

class URLView(TemplateView):
    template_name = "modules/analysis/saved_urls.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        website_id = kwargs.get('website_id')
        website = get_object_or_404(Website, id=website_id)
        pages = website.pages.all()
        context['website'] = website
        context['pages'] = pages
        return context
