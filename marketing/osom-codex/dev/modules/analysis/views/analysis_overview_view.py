from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from modules.analysis.models import Page, Website, ExtractedKeyword
from statistics import median, mean
from collections import Counter
import google.generativeai as genai
from django.shortcuts import get_object_or_404, redirect
import json
from modules.analysis.utils.page_seo_analysis import PageSEOAnalysis
from modules.analysis.tasks import generate_website_insight
from django.http import JsonResponse
from modules.analysis.tasks import generate_target_audience

def website_insight_status(request, website_id):
    website = Website.objects.filter(id=website_id).first()
    if website and website.insight_text:
        return JsonResponse({
            "ready": True,
            "insight": website.insight_text
        })
    return JsonResponse({"ready": False})

def target_audience_status(request, website_id):
    website = Website.objects.filter(id=website_id).first()
    if website and website.target_audience:
        return JsonResponse({"ready": True, "audience": website.target_audience})
    return JsonResponse({"ready": False})

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
        reading_labels = [page.url for page in pages_stats]
        reading_values = [round(page.text_reading_time * 60, 1) for page in pages_stats]
        readability_values = [round(page.text_readability, 2) for page in pages_stats]

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


        context["keyword_summary"] = sorted(
            keyword_summary, key=lambda x: (-x["count"], -x["avg_score"])
        )[:10]

        per_page_tones = []
        for page in pages_stats:
            tone_data = {
                "technical": page.text_types.get("technical", 0),
                "emotional": page.text_types.get("emotional", 0),
                "neutral": page.text_types.get("neutral", 0)
            }
            per_page_tones.append(tone_data)

        if website.insight_text is None:
            generate_website_insight.delay(website_id)

        target_audience = website.target_audience
        if target_audience is None:
            generate_target_audience.apply_async(args=[website_id], countdown=10)

        
        pages = Page.objects.filter(website_id=website_id)

        context.update({
            "website": website,
            "median_tones": median_tones,
            "tone_labels": list(median_tones.keys()),
            "tone_data": list(median_tones.values()),
            "most_technical_url": most_technical_url,
            "least_technical_url": least_technical_url,
            **stats,
            "target_audience": target_audience,
            "reading_labels": reading_labels,
            "reading_values": reading_values,
            "readability_values": readability_values,
            "per_page_tones": per_page_tones,	
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
    


