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

        target_audience = website.target_audience
        if target_audience is None:
            target_audience = self.target_audience(website_id)

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
    
    def target_audience(self, website_id):
        website = get_object_or_404(Website, id=website_id)
        keywords = ExtractedKeyword.objects.filter(page__website=website)
        keyword_counter = Counter()
        keyword_scores = {}

        for kw in keywords:
            keyword_counter[kw.keyword] += 1
            keyword_scores.setdefault(kw.keyword, []).append(kw.score)

        sorted_keywords = sorted(
            keyword_counter.items(),
            key=lambda item: (-item[1], -sum(keyword_scores[item[0]]) / len(keyword_scores[item[0]]))
        )

        top_keywords = [kw for kw, _ in sorted_keywords[:20]]

        prompt = (
            "Atlieku konkurentų įmonės svetainės puslapių analizę. "
            f"Pagal šiuos raktinius žodžius: {', '.join(top_keywords)}, "
            "nurodyk, į kokią auditoriją orientuojasi įmonė. "
            "Atsakyk TIK JSON formatu, naudodamas šią struktūrą:\n"
            "{\n"
            "  \"Į ką orientuojasi įmonė\": {\n"
            "    \"Auditorijos segmentas 1\": \"Trumpas paaiškinimas\",\n"
            "    \"Auditorijos segmentas 2\": \"Trumpas paaiškinimas\"\n"
            "  }\n"
            "}\n"
            "Pavyzdys:\n"
            "{\n"
            "  \"Į ką orientuojasi įmonė\": {\n"
            "    \"Technologijų įmonės\": \"Įmonės, ieškančios pažangių 3D sprendimų ir duomenų apdorojimo platformų.\",\n"
            "    \"Dizaineriai\": \"Individualūs dizaineriai ir dizaino komandos, dirbančios su 3D modeliavimu ir vizualizacija.\"\n"
            "  }\n"
            "}"
        )


        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        insight = response.text
        parsed_audience = self.extract_json(insight, website_id)

        return parsed_audience
    
    def extract_json(self, response, website_id):
        website = get_object_or_404(Website, id=website_id)
        try:
            cleaned = response.strip().strip("```json").strip("```").strip()
            parsed = json.loads(cleaned)

            if "Į ką orientuojasi įmonė" in parsed:
                parsed = parsed["Į ką orientuojasi įmonė"]

            if not isinstance(parsed, dict):
                raise ValueError("Expected a flat dictionary after unwrapping.")

            website.target_audience = parsed
            website.save()
            return parsed

        except json.JSONDecodeError as e:
            raise ValueError(f"Model response could not be parsed as JSON: {e}\nRaw output: {response}") from e


