from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from modules.analysis.models import Page, ExtractedKeyword, Website
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from transformers import pipeline

class OverviewView(TemplateView):
    template_name = "modules/analysis/overview.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        website_id = kwargs.get('website_id')
        website = get_object_or_404(Website, id=website_id)

        pages = Page.objects.filter(website_id=website_id).exclude(text_types__isnull=True)
        average_tones = self.calculate_average_tones(pages)

        context.update({
            "website": website,
            "average_tones": average_tones,
        })
        return context
    
    def calculate_average_tones(self, pages):
        tone_totals = {}
        tone_counts = {}

        for page in pages:
            if not page.text_types:
                continue

            for tone, score in page.text_types.items():
                tone_totals[tone] = tone_totals.get(tone, 0) + score
                tone_counts[tone] = tone_counts.get(tone, 0) + 1

        average_tones = {
            tone: round(tone_totals[tone] / tone_counts[tone], 2)
            for tone in tone_totals
        }

        return average_tones

