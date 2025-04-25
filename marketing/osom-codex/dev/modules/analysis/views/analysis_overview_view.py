from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from modules.analysis.models import Page, Website, ExtractedKeyword, LoadingTime, OverallAnalysis, PageAnalysis
from statistics import median, mean
from collections import Counter
import google.generativeai as genai
from django.shortcuts import get_object_or_404, redirect
import json
from modules.analysis.utils.page_seo_analysis import PageSEOAnalysis
from modules.analysis.tasks import generate_website_insight
from django.http import JsonResponse
from modules.analysis.tasks import generate_target_audience, positioning_insights, analyze_top_keywords_trends
import ast


def website_insight_status(request, website_id):
    website = Website.objects.filter(id=website_id).first()
    overall_analysis = OverallAnalysis.objects.filter(website=website).first()

    if website and overall_analysis:
        try:
            tech_data = overall_analysis.technology if overall_analysis.technology else {}
        except Exception as e:
            return JsonResponse({"ready": False, "error": str(e)})

        return JsonResponse({
            "ready": True,
            "technology": tech_data,
            "technology_summary": overall_analysis.technology_summary,
            "backend_stack": overall_analysis.backend_stack,
        })

    return JsonResponse({"ready": False})

def target_audience_status(request, website_id):
    website = Website.objects.filter(id=website_id).first()
    if website and website.target_audience:
        return JsonResponse({"ready": True, "audience": website.target_audience})
    return JsonResponse({"ready": False})

def technology_status(request, website_id):
    website = Website.objects.get(id=website_id)
    if hasattr(website, "overall_analysis") and website.overall_analysis.technology:
        try:
            tech = json.loads(website.overall_analysis.technology)
            return JsonResponse({"ready": True, "technology": tech})
        except Exception:
            return JsonResponse({"ready": False})
    return JsonResponse({"ready": False})

class OverviewView(TemplateView):
    template_name = "modules/analysis/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        website_id = kwargs.get('website_id')
        website = get_object_or_404(Website, id=website_id)

        pages = Page.objects.filter(website_id=website_id, analysis__isnull=False).select_related("analysis")
        page_analyses = [page.analysis for page in pages if page.analysis]

        median_tones = self.calculate_median_tones(page_analyses)

        pages_stats = [a for a in page_analyses if a.text_reading_time is not None and a.text_readability is not None]
        stats = self.average(pages_stats)
        reading_labels = [a.page.url for a in pages_stats]
        reading_values = [round(a.text_reading_time * 60, 1) for a in pages_stats]
        readability_values = [round(a.text_readability, 2) for a in pages_stats]
        seo_score = self.calculate_seo_score(website_id=website_id)

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
                # 'trends_analyzed': trend_obj.trends_analyzed if trend_obj else False,
            })
        top_keywords = sorted(
            keyword_summary, key=lambda x: (-x["count"], -x["avg_score"])
        )[:10]

        # if any(not kw.get("trends_analyzed", True) for kw in top_keywords):
        #     print()# analyze_top_keywords_trends.delay(website.id)

        context["keyword_summary"] = top_keywords

        per_page_tones = []
        for a in pages_stats:
            tone_data = {
                "technical": a.text_types.get("technical", 0),
                "emotional": a.text_types.get("emotional", 0),
                "neutral": a.text_types.get("neutral", 0)
            }
            per_page_tones.append(tone_data)

        insights = OverallAnalysis.objects.filter(website=website).first()
        if (
            insights is None or
            not insights.partners or
            not insights.positioning_weaknesses or
            not insights.recommendations or
            not insights.seo or
            not insights.social_media or
            not insights.technology or
            not insights.usp
        ):
            generate_website_insight.delay(website_id)
        if website.positioning_insights is None:
            positioning_insights.delay(website_id)
        target_audience = website.target_audience
        if target_audience is None:
            generate_target_audience.apply_async(args=[website_id], countdown=10)

        pages = Page.objects.filter(website_id=website_id)
        speed_metrics, avg_metrics = self.get_loading_time(website_id)

        overall_analysis = OverallAnalysis.objects.filter(website=website).first()

        partners = []
        if overall_analysis and overall_analysis.partners:
            try:
                parsed = ast.literal_eval(overall_analysis.partners)
                if isinstance(parsed, list):
                    partners = [p.strip("'\"") for p in parsed if isinstance(p, str)]
            except (ValueError, SyntaxError):
                partners = []
        
        social_links = []
        if overall_analysis and overall_analysis.social_media:
            try:
                parsed = ast.literal_eval(overall_analysis.social_media)
                if isinstance(parsed, dict):
                    social_links = [link.strip() for link in parsed.values() if isinstance(link, str)]
                elif isinstance(parsed, list):
                    social_links = [link.strip() for link in parsed if isinstance(link, str)]
            except (ValueError, SyntaxError):
                social_links = []
        starting_page = pages.filter(url=website.start_url).first()

        context.update({
            "website": website,
            "median_tones": median_tones,
            "tone_labels": list(median_tones.keys()),
            "tone_data": list(median_tones.values()),
            **stats,
            "target_audience": target_audience,
            "reading_labels": reading_labels,
            "reading_values": reading_values,
            "readability_values": readability_values,
            "per_page_tones": per_page_tones,	
            "load_labels": speed_metrics["labels"],
            "load_ttfb": speed_metrics["ttfb"],
            "load_fcp": speed_metrics["fcp"],
            "load_lcp": speed_metrics["lcp"],
            "load_loaded": speed_metrics["loaded"],
            "overall_analysis": overall_analysis,
            "seo_score": seo_score,
            "positioning_insights": website.positioning_insights,
            "partners": partners,
            "usp": overall_analysis.usp,
            "seo_details": overall_analysis.seo,
            "positioning_weaknesses": overall_analysis.positioning_weaknesses,
            "social_links": social_links,
            "recommendations": overall_analysis.recommendations,
            "meta_title": starting_page.page_title,
            "meta_description": starting_page.analysis.description,
            **avg_metrics
        })
        return context


    def calculate_seo_score(self, website_id):
        all_pages = Page.objects.filter(website_id=website_id).select_related("analysis")
        pages = [page.analysis for page in all_pages if page.analysis.seo_score is not None]
        total_score = 0
        for page in pages:
            if page.seo_score is not None:
                total_score += page.seo_score
        return round(total_score / len(pages), 0) if pages else 0

    def format_time(self, mins):
        total_seconds = int(round(mins * 60))
        if mins >= 1:
            minutes = int(mins // 1)
            total_seconds = int(total_seconds % 60)
            return f"{minutes}min {total_seconds}s"
        else:
            return f"{round(mins * 60, 1)}s"
    
    def get_loading_time(self, website_id):
        pages = Page.objects.filter(website_id=website_id)
        loading_times = LoadingTime.objects.filter(page__in=pages).select_related('page')

        speed_metrics = {
            "labels": [],
            "ttfb": [],
            "fcp": [],
            "lcp": [],
            "loaded": [],
        }

        for loading_time in loading_times:
            speed_metrics["labels"].append(loading_time.page.url)
            speed_metrics["ttfb"].append(round(loading_time.time_to_first_byte or 0, 1))
            speed_metrics["fcp"].append(round(loading_time.first_contentful_paint or 0, 1))
            speed_metrics["lcp"].append(round(loading_time.largest_contentful_paint or 0, 1))
            speed_metrics["loaded"].append(round(loading_time.fully_loaded or 0, 1))

        avg_metrics = {
            "avg_ttfb": round(mean(speed_metrics["ttfb"]), 0) if speed_metrics["ttfb"] else None,
            "avg_fcp": round(mean(speed_metrics["fcp"]), 0) if speed_metrics["fcp"] else None,
            "avg_lcp": round(mean(speed_metrics["lcp"]), 0) if speed_metrics["lcp"] else None,
            "avg_loaded": round(mean(speed_metrics["loaded"]), 0) if speed_metrics["loaded"] else None,
        }
        
        return speed_metrics, avg_metrics


    def average(self, pages):
        readability_scores = []
        reading_times = []

        for page in pages:
            readability_scores.append((page.text_readability, page.page.url))
            reading_times.append((page.text_reading_time, page.page.url))

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
                technical_scores.append((technical_score, page.page.url))

        median_tones = {
            tone: round(median(scores), 2)
            for tone, scores in tone_scores.items()
        }

        return median_tones
    


