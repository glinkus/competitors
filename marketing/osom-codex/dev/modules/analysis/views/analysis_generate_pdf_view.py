from weasyprint import HTML, CSS
import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from modules.analysis.models import Website
from modules.analysis.views.analysis_overview_view import OverviewView

class GeneratePDFView(TemplateView):
    def get(self, request, *args, **kwargs):
        website_id = kwargs.get('website_id')
        website = get_object_or_404(Website, id=website_id)

        overview_view = OverviewView()
        overview_view.request = request
        context = overview_view.get_context_data(website_id=website_id)

        pdf_context = {
            "website_url": context.get("website").start_url,
            "meta_title": context.get("meta_title"),
            "meta_description": context.get("meta_description"),
            "seo_score": context.get("seo_score"),
            "keyword_summary": context.get("keyword_summary"),
            "target_audience": context.get("target_audience"),
            "avg_ttfb": context.get("avg_ttfb"),
            "avg_fcp": context.get("avg_fcp"),
            "avg_lcp": context.get("avg_lcp"),
            "avg_loaded": context.get("avg_loaded"),
            "positioning_insights": context.get("positioning_insights"),
            "partners": context.get("partners"),
            "usp": context.get("usp"),
            "seo_details": context.get("seo_details"),
            "positioning_weaknesses": context.get("positioning_weaknesses"),
            "social_links": context.get("social_links"),
            "recommendations": context.get("recommendations"),
            "now": context.get("now") or timezone.now()
        }

        html_string = render_to_string('modules/analysis/overview_pdf.html', pdf_context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        css_path = os.path.join(settings.BASE_DIR, 'rarea', 'css', 'pdf.css')
        pdf_file = html.write_pdf(stylesheets=[CSS(filename=css_path)])

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="website_overview_{website_id}.pdf"'
        return response

