from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from modules.analysis.models import Page, ExtractedKeyword, Website, OverallAnalysis, PageAnalysis, LoadingTime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
import ast
from statistics import mean

class CompareView(LoginRequiredMixin, TemplateView):
    template_name = "modules/analysis/compare.html"

    def get(self, request, *args, **kwargs):
        ids = request.GET.get('ids', '')
        id_list = [int(i) for i in ids.split(',') if i.isdigit()]
        sites = Website.objects.filter(id__in=id_list).select_related('overall_analysis')

        comparison = []
        for site in sites:
            pages = Page.objects.filter(website=site, loading_time__isnull=False)
            page_analyses = PageAnalysis.objects.filter(page__website=site)

            metrics = pages.aggregate(
                avg_ttfb=Avg('loading_time__time_to_first_byte'),
                avg_fcp=Avg('loading_time__first_contentful_paint'),
                avg_loaded=Avg('loading_time__fully_loaded'),
            )

            seo_score = page_analyses.aggregate(avg_score=Avg('seo_score'))['avg_score'] or 0
            readability, reading_time = self.average(page_analyses)

            # keywords summary
            keywords = ExtractedKeyword.objects.filter(page__website=site)
            keyword_data = keywords.values('keyword').annotate(
                count=Count('id'),
                avg_score=Avg('score'),
                trend_score=Avg('trend_score')
            ).order_by('-count', '-avg_score')[:5]

            overall = getattr(site, 'overall_analysis', None)
            technology = list((overall.technology or {}).keys()) if overall else []
            backend_stack = list((overall.backend_stack or {}).keys()) if overall else []
            partners = []
            if overall and overall.partners:
                try:
                    partners = ast.literal_eval(overall.partners)
                except Exception:
                    partners = []

            social_links = []
            if overall and overall.social_media:
                try:
                    parsed = ast.literal_eval(overall.social_media)
                    if isinstance(parsed, dict):
                        social_links = [link.strip() for link in parsed.values() if isinstance(link, str)]
                    elif isinstance(parsed, list):
                        social_links = [link.strip() for link in parsed if isinstance(link, str)]
                except (ValueError, SyntaxError):
                    social_links = []

            comparison.append({
                'site': site,
                'pages_crawled': pages.count(),
                'avg_ttfb': metrics['avg_ttfb'] or 0,
                'avg_fcp': metrics['avg_fcp'] or 0,
                'avg_loaded': metrics['avg_loaded'] or 0,
                'seo_score': seo_score,
                'avg_readability': readability,
                'avg_reading_time': reading_time,
                'keywords': list(keyword_data),
                'technology': technology,
                'backend_stack': backend_stack,
                'partners': partners,
                'usp': overall.usp if overall else None,
                'social_media': social_links,
            })

        return self.render_to_response({
            'comparison': comparison
        })
    def average(self, pages):
        readability_scores = []
        reading_times = []

        for page in pages:
            if not page.text_readability or not page.text_reading_time:
                continue

            readability_scores.append((page.text_readability, page.page.url))
            reading_times.append((page.text_reading_time, page.page.url))

        avg_readability = round(mean(score for score, _ in readability_scores), 2)

        avg_reading_time_val = mean(time for time, _ in reading_times)
        avg_reading_time = self.format_time(avg_reading_time_val)

        return avg_readability, avg_reading_time
    
    def format_time(self, mins):
        total_seconds = int(round(mins * 60))
        if mins >= 1:
            minutes = int(mins // 1)
            total_seconds = int(total_seconds % 60)
            return f"{minutes}min {total_seconds}s"
        else:
            return f"{round(mins * 60, 1)}s"