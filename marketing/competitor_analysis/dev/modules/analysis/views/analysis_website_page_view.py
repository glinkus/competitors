from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from modules.analysis.models import Website, Page, ExtractedKeyword, SEORecommendation, PageAnalysis
from collections import defaultdict
import json
from django.contrib.auth.mixins import LoginRequiredMixin

class URLView(LoginRequiredMixin, TemplateView):
    template_name = "modules/analysis/website_page.html"

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
        label_groups = defaultdict(list)

        for page in pages:
            label = getattr(page.analysis, 'label', None) or 'Other'
            label_groups[label].append(page)

            loading_time = getattr(page, 'loading_time', None)
            reading_time = self.format_time(page.analysis.text_reading_time) if page.analysis.text_reading_time else None
            pages_json[page.id] = {
                "seo_score": page.analysis.seo_score,
                "seo_score_details": page.analysis.seo_score_details,
                "linking_analysis": page.analysis.linking_analysis,
                "warnings": page.analysis.warnings,
                "cta_analysis": page.analysis.cta_analysis, 
                "meta_title": page.page_title,
                "meta_description": page.analysis.description,
                "text_reading_time": reading_time,
                "text_readability": page.analysis.text_readability,
                "tone_labels": list(page.analysis.text_types.keys()),
                "tone_data": list(page.analysis.text_types.values()),
                "positioning_labels": list(page.analysis.positioning_classification.keys()),
                "positioning_data": list(page.analysis.positioning_classification.values()),
            }
            if loading_time:
                pages_json[page.id].update({
                    "time_to_first_byte": loading_time.time_to_first_byte,
                    "first_contentful_paint": loading_time.first_contentful_paint,
                    "largest_contentful_paint": loading_time.largest_contentful_paint,
                    "fully_loaded": loading_time.fully_loaded,
                })

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
            "label_groups": dict(label_groups),
            "keywords_by_page": dict(keywords_by_page),
            "pages_json": json.dumps(pages_json),
            "recommendations_json": json.dumps(recommendations_json),
        })
        return context
    
    def format_time(self, mins):
        total_seconds = int(round(mins * 60))
        if mins >= 1:
            minutes = int(mins // 1)
            total_seconds = int(total_seconds % 60)
            return f"{minutes}min {total_seconds}s"
        else:
            return f"{round(mins * 60, 1)}s"
