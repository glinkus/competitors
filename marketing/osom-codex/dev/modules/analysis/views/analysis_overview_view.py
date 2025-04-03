from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from modules.analysis.models import Page, Website
from statistics import median, mean

class OverviewView(TemplateView):
    template_name = "modules/analysis/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        website_id = kwargs.get('website_id')
        website = get_object_or_404(Website, id=website_id)

        pages = Page.objects.filter(website_id=website_id).exclude(text_types__isnull=True)
        median_tones, most_technical_url, least_technical_url = self.calculate_median_tones(pages)

        pages_stats = Page.objects.filter(website_id=website_id).exclude(text_reading_time__isnull=True, text_readability__isnull=True)
        stats = self.average(pages_stats)

        context.update({
            "website": website,
            "median_tones": median_tones,
            "tone_labels": list(median_tones.keys()),
            "tone_data": list(median_tones.values()),
            "most_technical_url": most_technical_url,
            "least_technical_url": least_technical_url,
            **stats,  # includes all readability stats
        })
        return context

    def format_time(self, seconds):
        if seconds >= 60:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}min {secs}s"
        else:
            return f"{int(seconds)}s"

    def average(self, pages):
        readability_scores = []
        reading_times = []

        for page in pages:
            readability_scores.append((page.text_readability, page.url))
            reading_times.append((page.text_reading_time, page.url))

        avg_readability = round(mean(score for score, _ in readability_scores), 2)
        avg_reading_time_val = mean(time for time, _ in reading_times)
        avg_reading_time = self.format_time(avg_reading_time_val)

        highest_read_page = max(readability_scores, key=lambda x: x[0])[1]
        lowest_read_page = min(readability_scores, key=lambda x: x[0])[1]
        longest_page = max(reading_times, key=lambda x: x[0])[1]
        shortest_page = min(reading_times, key=lambda x: x[0])[1]

        return {
            "avg_readability": avg_readability,
            "avg_reading_time": avg_reading_time,
            "highest_readability_url": highest_read_page,
            "lowest_readability_url": lowest_read_page,
            "longest_reading_url": longest_page,
            "shortest_reading_url": shortest_page,
        }


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
