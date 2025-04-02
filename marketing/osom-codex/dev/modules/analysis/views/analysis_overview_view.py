from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from modules.analysis.models import Page, Website
from statistics import median


class OverviewView(TemplateView):
    template_name = "modules/analysis/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        website_id = kwargs.get('website_id')
        website = get_object_or_404(Website, id=website_id)

        pages = Page.objects.filter(website_id=website_id).exclude(text_types__isnull=True)
        median_tones, most_technical_url, least_technical_url = self.calculate_median_tones(pages)

        context.update({
            "website": website,
            "median_tones": median_tones,
            "tone_labels": list(median_tones.keys()),
            "tone_data": list(median_tones.values()),
            "most_technical_url": most_technical_url,
            "least_technical_url": least_technical_url,
        })
        return context

    def calculate_median_tones(self, pages):
        tone_scores = {}
        technical_scores = []

        for page in pages:
            if not page.text_types:
                continue

            for tone, score in page.text_types.items():
                tone_scores.setdefault(tone, []).append(score)

            technical_score = page.text_types.get("technical")
            if technical_score is not None:
                technical_scores.append((technical_score, page.url))

        median_tones = {
            tone: round(median(scores), 2)
            for tone, scores in tone_scores.items()
        }

        most_technical_url = None
        least_technical_url = None

        if technical_scores:
            most_technical_url = max(technical_scores, key=lambda x: x[0])[1]
            least_technical_url = min(technical_scores, key=lambda x: x[0])[1]

        return median_tones, most_technical_url, least_technical_url
