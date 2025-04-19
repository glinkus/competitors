from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from modules.analysis.models import Page, ExtractedKeyword, Website
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg


class CompareView(LoginRequiredMixin, TemplateView):
    template_name = "modules/analysis/compare.html"

    def get(self, request, *args, **kwargs):
        ids = request.GET.get('ids','')
        id_list = [int(i) for i in ids.split(',') if i.isdigit()]
        sites = list(Website.objects.filter(id__in=id_list))

        comparison = []
        for site in sites:
            pages = Page.objects.filter(website=site, loading_time__isnull=False)
            metrics = pages.aggregate(
                avg_ttfb=Avg('loading_time__time_to_first_byte'),
                avg_fcp=Avg('loading_time__first_contentful_paint'),
                avg_loaded=Avg('loading_time__fully_loaded'),
            )
            comparison.append({
                'site': site,
                'pages_crawled': pages.count(),
                'avg_ttfb': metrics['avg_ttfb'] or 0,
                'avg_fcp': metrics['avg_fcp'] or 0,
                'avg_loaded': metrics['avg_loaded'] or 0,
                'seo_score': site.pages.aggregate(avg_score=Avg('seo_score'))['avg_score'] or 0,
            })

        return self.render_to_response({
            'comparison': comparison
        })