from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from modules.analysis.models import Website, Page, ExtractedKeyword, SEORecommendation
from collections import defaultdict
import json

class URLView(TemplateView):
    template_name = "modules/analysis/saved_urls.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        website_id = kwargs.get('website_id')
        website = get_object_or_404(Website, id=website_id)
        pages = website.pages.all()

        keywords_by_page = defaultdict(list)
        keywords = ExtractedKeyword.objects.filter(page__in=pages)
        for kw in keywords:
            keywords_by_page[kw.page_id].append(kw.keyword)

        pages_json = {}
        for page in pages:
            pages_json[page.id] = {
                "seo_score": page.seo_score,
                "seo_score_details": page.seo_score_details,
                "linking_analysis": page.linking_analysis,
                "warnings": page.warnings,
            }

        recommendations = SEORecommendation.objects.filter(page__in=pages)
        recommendations_json = defaultdict(list)
        for rec in recommendations:
            recommendations_json[rec.page_id].append({
                "category": rec.category,
                "rationale": rec.rationale,
                "actions": rec.actions,
            })

        context.update({
            "website": website,
            "pages": pages,
            "keywords_by_page": dict(keywords_by_page),
            "pages_json": json.dumps(pages_json),
            "recommendations_json": json.dumps(recommendations_json),
        })
        return context
