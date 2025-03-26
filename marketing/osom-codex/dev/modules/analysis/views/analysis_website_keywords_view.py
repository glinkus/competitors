from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from modules.analysis.models import Page, ExtractedKeyword, Website
from collections import Counter

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
            keyword_summary.append({
                'keyword': keyword,
                'count': count,
                'avg_score': round(avg_score, 2),
            })

        keyword_summary = sorted(
            [item for item in keyword_summary if item['count'] > 0],
            key=lambda x: (-x['avg_score'], -x['count'])
        )

        context.update({
            'website': website,
            'keyword_summary': keyword_summary[:],
        })
        return context