from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from modules.analysis.models import Page, ExtractedKeyword, Website
from collections import Counter
from modules.analysis.tasks import analyze_page

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
    
    def post(self, request, *args, **kwargs):
        # Get the website instance
        website = get_object_or_404(Website, id=kwargs.get('website_id'))
        
        # Optionally clear existing extracted keywords for a fresh recalculation
        ExtractedKeyword.objects.filter(page__website=website).delete()

        # Retrieve all pages for the website
        pages = website.pages.all()
        
        # Option 1: Loop and trigger each analyze_page task individually.
        for page in pages:
            analyze_page.delay(page.url)
        
        # Option 2 (alternative): Use a Celery group to run tasks concurrently.
        # tasks = group(analyze_page.s(page.url) for page in pages)
        # tasks.apply_async()
        
        # Redirect back to the keywords page
        return redirect(reverse('modules.analysis:website_keywords', kwargs={'website_id': website.id}))