from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from modules.analysis.models import Website, Page, ExtractedKeyword, SEORecommendation
from collections import defaultdict
import json

class URLView(TemplateView):
    template_name = "modules/analysis/website_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        website_id = kwargs.get('website_id')
        website = get_object_or_404(Website, id=website_id)
        pages = website.pages.all()

        keywords_by_page = defaultdict(list)
        all_keywords = ExtractedKeyword.objects.filter(page__in=pages)

        keyword_scores = defaultdict(list)
        for kw in all_keywords:
            keyword_scores[(kw.page_id, kw.keyword)].append(kw.score)

        for kw in all_keywords:
            avg_score = sum(keyword_scores[(kw.page_id, kw.keyword)]) / len(keyword_scores[(kw.page_id, kw.keyword)])

            trend_keys = list(kw.interest_over_time.keys()) if kw.interest_over_time else []
            trend_values = list(kw.interest_over_time.values()) if kw.interest_over_time else []

            keywords_by_page[kw.page_id].append({
                "keyword": kw.keyword,
                "score": round(avg_score, 2),
                "trend_keys": json.dumps(trend_keys),
                "trend_values": json.dumps(trend_values),
                "interest_by_region": kw.interest_by_region if kw.interest_by_region else {},
                "trend_score": kw.trend_score if kw.trend_score else 0,
            })

        # Serialize SEO metadata
        pages_json = {
            page.id: {
                "seo_score": page.seo_score,
                "seo_score_details": page.seo_score_details,
                "linking_analysis": page.linking_analysis,
                "warnings": page.warnings,
            }
            for page in pages
        }

        # Serialize recommendations
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
            "keywords_by_page": json.dumps(keywords_by_page),
            "pages_json": json.dumps(pages_json),
            "recommendations_json": json.dumps(recommendations_json),
        })
        return context

