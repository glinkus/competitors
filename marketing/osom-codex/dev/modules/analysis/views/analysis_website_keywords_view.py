from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from modules.analysis.models import Page, ExtractedKeyword, Website
from collections import Counter
from modules.analysis.tasks import analyze_page
from modules.analysis.tasks import analyze_top_keywords_trends
import json

class WebsiteKeywordsView(TemplateView):
    template_name = "modules/analysis/website_keywords.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        website = get_object_or_404(Website, id=kwargs.get('website_id'))

        keywords = ExtractedKeyword.objects.filter(page__website=website)
        keyword_counter = Counter()
        keyword_scores = {}

        for kw in keywords:
            keyword_counter[kw.keyword] += 1
            keyword_scores.setdefault(kw.keyword, []).append(kw.score)

        keyword_summary = []
        for keyword, count in keyword_counter.items():
            avg_score = sum(keyword_scores[keyword]) / len(keyword_scores[keyword])

            trend_obj = ExtractedKeyword.objects.filter(
                    page__website=website,
                    keyword=keyword,
                    interest_over_time__isnull=False
                ).exclude(interest_over_time={}).first()

            if trend_obj and trend_obj.interest_over_time:
                trend_keys = list(trend_obj.interest_over_time.keys())
                trend_values = list(trend_obj.interest_over_time.values())
            else:
                trend_keys = []
                trend_values = []

            keyword_summary.append({
                'keyword': keyword,
                'count': count,
                'avg_score': round(avg_score, 2),
                'trend_keys': json.dumps(trend_keys),
                'trend_values': json.dumps(trend_values),
                'interest_by_region': trend_obj.interest_by_region if trend_obj else {},
                'trend_score': trend_obj.trend_score if trend_obj else 0,	
            })

        keyword_summary = sorted(
            [item for item in keyword_summary if item['count'] > 0],
            key=lambda x: ( -x['count'], -x['avg_score'])
        )

        context.update({
            'website': website,
            'keyword_summary': keyword_summary[:10],
        })
        return context
    
    def post(self, request, *args, **kwargs):
        website = get_object_or_404(Website, id=kwargs.get('website_id'))

        if 'recalculate' in request.POST:
            analyze_top_keywords_trends.delay(website.id)
        else:
            ExtractedKeyword.objects.filter(page__website=website).delete()
            for page in website.pages.all():
                analyze_page.delay(page.url)

        return redirect(reverse('modules.analysis:website_keywords', kwargs={'website_id': website.id}))