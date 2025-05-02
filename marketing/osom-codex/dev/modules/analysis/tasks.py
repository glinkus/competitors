import shlex
import subprocess
import os
from time import sleep
from celery import shared_task, chain
from modules.analysis.models import Page, Website, ExtractedKeyword, SEORecommendation, OverallAnalysis, PageAnalysis
from modules.analysis.utils.keyword_extraction import KeywordExtraction
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict, Counter
import json
import re
import nltk
import warnings
from pytrends.request import TrendReq
import pandas as pd
from nltk.corpus import stopwords
from transformers import pipeline
import textstat
from modules.analysis.utils.page_seo_analysis import PageSEOAnalysis
from modules.analysis.utils.seo_insights import SEOInsights
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from statistics import mean
from google import genai
from google.genai import types
import google.generativeai as genai_model

nltk.download('stopwords')


@shared_task
def run_one_page_spider(website_id, website_name):
    env = os.environ.copy()
    env['SCRAPY_SETTINGS_MODULE'] = 'competitors_scraper.settings'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.join(BASE_DIR, 'competitors_scraper')
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    output_file = os.path.join(log_dir, f'spider_output_{website_id}.txt')

    env['PYTHONPATH'] = BASE_DIR + os.pathsep + env.get('PYTHONPATH', '')

    while True:
        website = Website.objects.filter(id=website_id).first()
        if not website or not website.crawling_in_progress:
            print(f"Scraping manually stopped for website ID {website_id}")
            return "Scraping stopped by user."
        
        unvisited_pages = list(
            Page.objects.filter(website_id=website_id, visited=False)
            .values_list("url", flat=True)
        )
        if not unvisited_pages:
            w = Website.objects.filter(id=website_id).first()
            if w:
                w.crawling_in_progress = False
                w.crawling_finished = True
                w.scraping_stopped = False
                w.save()
                analyze_top_keywords_trends.delay(website_id)
                generate_target_audience.apply_async(args=[website_id], countdown=0)
                positioning_insights.apply_async(args=[website_id], countdown=15)
                generate_website_insight.apply_async(args=[website_id], countdown=60)
            else:
                raise Exception(f"Website with id {website_id} not found.")
            return "No more unvisited pages found."

        for page_url in unvisited_pages:
            cmd = (
                f"scrapy crawl one_page_spider -a page_url={page_url} "
                f"-a website_id={website_id} -a website_name='{website_name}'"
            )
            args = shlex.split(cmd)
            with open(output_file, "a") as f:
                result = subprocess.run(
                    args,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    env=env,
                    cwd=project_root
                )
                if result.returncode != 0:
                    raise Exception(f"Spider failed for URL {page_url}. See log: {output_file}")
                
                w = Website.objects.filter(id=website_id).first()
                if w and not w.favicon_url:
                    get_icon(page_url, website_id)
                    print(f"Saved favicon for: {page_url}")

                analyze_keywords.delay(page_url)
                classify_page.apply_async(args=[page_url], countdown=0)
                text_read_analysis.apply_async(args=[page_url], countdown=20)
                run_seo_analysis.apply_async(args=[page_url], countdown=40)
            sleep(50)

            website = Website.objects.filter(id=website_id).first()
            if not website or not website.crawling_in_progress:
                print(f"Scraping manually stopped for website ID {website_id}")
                return "Scraping stopped by user."
 
@shared_task
def run_seo_analysis(page_url):
    page = Page.objects.get(url=page_url)

    page_seo_analysis = PageSEOAnalysis(page_url)
    analysis = page_seo_analysis.analyze()

    page_analysis = PageAnalysis.objects.get(page=page)
    structured_data = json.loads(page_analysis.structured_data)
    total_word_count = structured_data.get("wordcount")

    if analysis:
        seo_insights = SEOInsights(
            content=page_analysis.content,
            url=page.url,
            overall_metrics=analysis,
            internal_links=page_analysis.internal_links,
            external_links=page_analysis.external_links,
            warnings=page_analysis.warnings,
            total_word_count=total_word_count
        )

        try:
            seo_insights.run_analysis()
        except Exception as e:
            print(f"Error running SEO Insights analysis: {e}")
    else:
        print(f"No analysis data found for page: {page.url}")
        return {"error": "No analysis data found."}

@shared_task
def analyze_keywords(page_url):
    page = Page.objects.get(url=page_url)
    extractor = KeywordExtraction()
    keywords = extractor.extract_keywords(page)


    ExtractedKeyword.objects.filter(page=page).delete()

    extracted_keywords_objs = [
        ExtractedKeyword(page=page, keyword=keyword, score=score)
        for keyword, score in keywords
    ]

    ExtractedKeyword.objects.bulk_create(extracted_keywords_objs)

    return {"stored_keywords_count": len(keywords), "page": page.url}

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    text = text.lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = [word for word in text.split() if word not in stop_words]
    return ' '.join(tokens)

@shared_task
def analyze_top_keywords_trends(website_id, top_n=10):
    keywords = ExtractedKeyword.objects.filter(page__website_id=website_id)

    keyword_counter = defaultdict(list)
    for kw in keywords:
        keyword_counter[kw.keyword].append(kw.score)

    keyword_summary = sorted(
        [(kw, len(scores), sum(scores) / len(scores)) for kw, scores in keyword_counter.items()],
        key=lambda x: (-x[1], -x[2])
    )

    top_keywords = [kw for kw, _, _ in keyword_summary[:top_n]]
    if not top_keywords:
        return {"message": "No keywords to enrich."}

    try:
        pytrends = TrendReq()
    except Exception as e:
        print(f"Error initializing pytrends: {e}")
        return {"message": "Failed to initialize pytrends."}
    # pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://172.167.161.8:8080'], retries=2, backoff_factor=0.1, requests_args={'verify':False})

    ExtractedKeyword.objects.filter(
        page__website_id=website_id,
        keyword__in=top_keywords
    ).update(
        trend_score=None,
        interest_over_time=None,
        interest_by_region=None,
        related_terms=None,
    )

    # Split into 5
    for i in range(0, len(top_keywords), 5):
        chunk = top_keywords[i:i+5]
        pytrends.build_payload(chunk, timeframe='today 3-m')

        for keyword in chunk:
            keyword_objs = ExtractedKeyword.objects.filter(page__website_id=website_id, keyword=keyword)
            if not keyword_objs.exists():
                continue

            main_obj = keyword_objs.first()

            df_time = pytrends.interest_over_time()
            if not df_time.empty and keyword in df_time:
                interest_data = {
                    date.strftime("%Y-%m-%d"): int(val)
                    for date, val in df_time[keyword].items()
                }
                trend_score = int(df_time[keyword].mean())
            else:
                interest_data = {}
                trend_score = 0

            related_terms = []
            try:
                related = pytrends.related_queries()
                if related and keyword in related and related[keyword].get("top") is not None:
                    related_terms = related[keyword]["top"].to_dict(orient="records")
            except Exception:
                pass

            try:
                df_region = pytrends.interest_by_region(
                    resolution='COUNTRY',
                    inc_low_vol=False,
                    inc_geo_code=False
                )
                df_region = df_region[df_region[keyword] > 0]
                region_data = df_region[keyword].to_dict()
            except Exception as e:
                print(f"Error fetching interest by region: {e}")
                region_data = {}

            main_obj.trend_score = trend_score
            main_obj.interest_over_time = interest_data
            main_obj.related_terms = related_terms
            main_obj.interest_by_region = region_data
            main_obj.trends_analyzed = True
            main_obj.save()
        sleep(60)

    return {"top_keywords_enriched": top_keywords}

@shared_task
def classify_page(page_url):
    classifier = pipeline(
        "zero-shot-classification",
        model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
        device=-1
    )

    page = Page.objects.get(url=page_url)
    structured_text = page.structured_text
    full_text = ' '.join(structured_text.values())

    if len(full_text.split()) < 25:
        return {f"skipped {page.url}": "Text too short for reliable classification."}

    page_analysis, created = PageAnalysis.objects.get_or_create(page=page)

    # Tone Classification
    tone_labels = ["technical", "emotional", "neutral"]
    try:
        tone_result = classifier(full_text, tone_labels, multi_label=True)
        page_analysis.text_types = {
            label: round(score * 100, 2)
            for label, score in zip(tone_result["labels"], tone_result["scores"])
        }
    except Exception as e:
        return {"error": f"Tone classification failed: {str(e)}"}

    # Positioning Classification
    positioning_labels = [
        "Innovative",
        "Traditional", 
        "Technical",
        "User-focused", 
        "Sustainable", 
        "Cost-efficient"
    ]
    try:
        positioning_result = classifier(full_text, positioning_labels, multi_label=True)
        page_analysis.positioning_classification = {
            label: round(score * 100, 2)
            for label, score in zip(positioning_result["labels"], positioning_result["scores"])
        }
    except Exception as e:
        return {"error": f"Positioning classification failed: {str(e)}"}

    # Page Type Classification
    type_labels = [
        "Product", 
        "Service", 
        "Blog", 
        "Case Study",
        "Contact", 
        "Careers", 
        "Landing Page"
    ]
    try:
        type_result = classifier(full_text, type_labels, multi_label=False)
        page_analysis.label = type_result["labels"][0]
        print(type_result)
    except Exception as e:
        return {"error": f"Page type classification failed: {str(e)}"}

    page_analysis.save()

    return f"{page.url} classified successfully."

def get_icon(page_url, website_id):
    page = Page.objects.get(url=page_url)
    raw_html = page.raw_html
    website = Website.objects.get(id=website_id)

    if website.favicon_url:
        return

    soup = BeautifulSoup(raw_html, "html.parser")
    icon_selectors = [
        'link[rel="icon"]',
        'link[rel="shortcut icon"]',
        'link[rel="apple-touch-icon"]',
        'link[rel="apple-touch-icon-precomposed"]',
    ]

    for selector in icon_selectors:
        tag = soup.select_one(selector)
        if tag and tag.get("href"):
            icon = urljoin(page.url, tag["href"])
            website.favicon_url = icon
            website.save()
            break

@shared_task
def text_read_analysis(page_url):
    page = Page.objects.get(url=page_url)
    structured_text = page.structured_text
    full_text = ' '.join(structured_text.values())
    
    word_count = len(full_text.split())
    if word_count < 25:
        return {"skipped": "Text too short for reliable readability analysis."}
    try:
        reading_score = textstat.flesch_reading_ease(full_text)
        reading_time = round(word_count / 200, 2)
    except Exception as e:
        return {"error in text analysis": str(e)}

    page_analysis, created = PageAnalysis.objects.get_or_create(page=page)
    page_analysis.text_readability = reading_score
    page_analysis.text_reading_time = reading_time
    page_analysis.save()

    return {
        "text_readability": reading_score,
        "reading_time": reading_time,
        "word_count": word_count
    }

@shared_task
def generate_website_insight(website_id):
    website = Website.objects.get(id=website_id)
    pages = Page.objects.filter(website=website)
    pages_analysis = PageAnalysis.objects.filter(page__in=pages)

    if not pages.exists():
        return "No pages to analyze."

    keywords_by_page = defaultdict(list)
    keywords = ExtractedKeyword.objects.filter(page__in=pages).order_by('-score')
    recommendations = SEORecommendation.objects.filter(page__in=pages)

    keyword_count_by_page = defaultdict(int)
    for kw in keywords:
        if keyword_count_by_page[kw.page_id] < 7:
            keywords_by_page[kw.page_id].append(kw.keyword)
            keyword_count_by_page[kw.page_id] += 1
            
    summaries = []
    count = 0
    for page in pages_analysis:
        count += 1
        if count < 20:
            summaries.append({
                "url": page.page.url,
                "readability": page.text_readability,
                "reading_time": page.text_reading_time,
                "tones": page.text_types,
                "seo_score": page.seo_score,
                "seo_score_details": page.seo_score_details,
                "linking_analysis": page.linking_analysis,
                "warnings": page.warnings,
                "content": page.content,
            })
        else:
            summaries.append({
                "url": page.page.url,
                "readability": page.text_readability,
                "reading_time": page.text_reading_time,
                "tones": page.text_types,
                "seo_score": page.seo_score,
                "seo_score_details": page.seo_score_details,
                "linking_analysis": page.linking_analysis,
                "warnings": page.warnings,
            })
        if count > 40: 
            break
        
    recommendations_list = list(recommendations.values_list('actions', flat=True))

    summaries.append({
        "keywords": dict(keywords_by_page),
    })
    
    client = genai.Client(api_key="AIzaSyCzvpa1Lb9dzp7-13T3C2HpDG9V7MVVsZM")

    max_tokens = 200000

    prompt = build_prompt(summaries, recommendations_list)
    while client.models.count_tokens(model="gemini-2.5-flash-preview-04-17", contents=prompt).total_tokens > max_tokens and summaries:
        summaries.pop()
        prompt = build_prompt(summaries, recommendations_list, truncated=True)

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=6024),
            response_mime_type='application/json',
            )
    )

    try:
        data = clean_json_response(response.text)
        OverallAnalysis.objects.update_or_create(
            website=website,
             defaults={
                "technology": data.get("Technology_stack"),
                "technology_summary": data.get("Technology_summary"),
                "backend_stack": data.get("Backend_stack"),
                "usp": data.get("Key_offerings_or_UVP"),
                "social_media": data.get("Social_medias"),
                "seo": data.get("SEO"),
                "recommendations": data.get("Recommendations"),
                "positioning_weaknesses": data.get("Positioning_weaknesses"),
                "partners": data.get("Partners"),
            }
        )
        print("Successfully generated insights.")
    except Exception as e:
        print("Error parsing insight:", e)
        return "Insight generation failed"

    return "Insight generated successfully"

def build_prompt(summaries, recommendations_list, truncated=False):
    note = "\n\nNote: The input data was truncated to fit within model limits." if truncated else ""
    return (
        "You are analyzing a **competitor's website** based on structured data extracted from multiple pages.\n\n"
        "The data includes: page URL, readability, estimated reading time, tone scores (technical/emotional/neutral), "
        "SEO score and analysis, content, warnings, and SEO recommendations. A summary of keywords and suggestions is also provided.\n\n"
        "Your task is to write an **executive summary** of the competitor's website performance. "
        "This should include clear insights that could be used for strategic benchmarking.\n\n"
        "The output MUST be returned in JSON format with the following **keys**:\n"
        "\n"
        "**Key_offerings_or_UVP**: What is the company's core offering? What sets them apart? Answer in at least 5 sentences\n"
        "**Technology_stack**: Return a **JSON object**, where keys are **customer-facing technologies or services** (e.g., 'Augmented Reality', 'AI-powered chatbots', '3D Visualizations'), and values are brief 1-2 sentence explanations of their purpose or how they’re used by the company.\n"
        "**Technology_summary**: Write a 2-sentence analytical conclusion summarizing the company’s technology positioning and innovation level based on their public offerings.\n"
        "**Backend_stack**: Return a **JSON object**, where keys are backend/internal technologies (e.g., Python, Django, MySQL, React, AWS, NGINX, etc.), and values are brief explanations of how they are used (e.g., hosting, databases, frameworks, etc.). Only include technologies inferred or detected from the content, warnings, metadata or structured data.\n"
        "**SEO**: Summary of SEO strengths and weaknesses (no recommendations). Answer in at least 5 sentences\n"
        "**Content**: Summary of content strengths and weaknesses (no recommendations). Answer in at least 5 sentences\n"
        "**Social_medias**: Any social links or emails found in content. Give exact links.\n"
        "**Partners**: Mentions of any collaborators, clients, or third-party partners found in the content.\n"
        "**Recommendations**: High-quality wide and overall suggestions based on overall weaknesses, seo_score_details and recommendations list. Answer in at least 5 sentences\n\n"
        "**Positioning_weaknesses**: Describe any unclear messaging, conflicting tones, or lack of focus in their offering. Answer in at least 5 sentences\n\n"
        "Do NOT include raw page titles or URLs. Avoid generic marketing speak. Give results in ordinary human language but broad spectrum. Be analytical.\n\n"
        "Return only the JSON object with exactly the specified keys. Do not add commentary, titles, or additional formatting.\n\n"
        f"Website Pages JSON:\n{json.dumps(summaries, ensure_ascii=False)}\n\n"
        f"Recommendations list JSON:\n{json.dumps(recommendations_list, ensure_ascii=False)}"
        f"{note}"
    )

def clean_json_response(text):
    cleaned = text.strip().strip("```json").strip("```").strip()
    return json.loads(cleaned)

@shared_task
def generate_target_audience(website_id):
    try:
        website = Website.objects.get(id=website_id)
        pages = Page.objects.filter(website=website)
        pages_analysis = PageAnalysis.objects.filter(page__in=pages)

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

        content_list = []
        for i, page in enumerate(pages_analysis):
            if i >= 50:
                break
            content_list.append({"content": page.content})


        prompt = (
            "I am analyzing the pages of a competitor's company website. "
            f"Based on these keywords: {', '.join(top_keywords)}, and based on content from the pages: {content_list}, "
            "identify the target audience the company is focusing on. "
            "Respond ONLY in JSON format using the following structure and present at least 4 audience segments:\n"
            "{\n"
            '  "Company Target Audience": {\n'
            '    "Audience Segment 1": "Short explanation",\n'
            '    "Audience Segment 2": "Short explanation"\n'
            "  }\n"
            "}\n"
            "Example:\n"
            "{\n"
            '  "Company Target Audience": {\n'
            '    "Tech Companies": "Businesses looking for advanced 3D solutions and data processing platforms.",\n'
            '    "Designers": "Individual designers and design teams working with 3D modeling and visualization."\n'
            "  }\n"
            "}"
        )

        model = genai_model.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        cleaned = response.text.strip().strip("```json").strip("```").strip()
        parsed = json.loads(cleaned)

        if "Company Target Audience" in parsed:
            parsed = parsed["Company Target Audience"]

        website.target_audience = parsed
        website.save()

        print("Successfully generated target audience.")
    except Exception as e:
        print(f"Error generating target audience: {e}")
    
@shared_task
def positioning_insights(website_id):
    try:
        website = Website.objects.get(id=website_id)
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

        keyword_summary = sorted(
            keyword_summary, key=lambda x: (-x["count"], -x["avg_score"])
        )[:10]

        page_titles = list(
            website.pages.values_list("page_title", flat=True)
            .exclude(page_title__isnull=True)
        )

        descriptions = list(
            PageAnalysis.objects.filter(page__website=website)
            .exclude(description__isnull=True)
            .values_list("description", flat=True)
        )

        audience_data = website.target_audience or {}
        audience_segments = [f"{k}: {v}" for k, v in audience_data.items()]

        prompt = (
            "You are an expert in branding and digital positioning. Analyze the data extracted from a competitors company’s website "
            "and generate a brief summary describing the company’s positioning and communication. Your answer should clearly highlight: "
            "What the company does (its product or service focus), its unique value proposition or market differentiation."
            "Be professional in tone, and avoid generic buzzwords. Use only the content provided. Write at least 6 sentences in detail.\n\n"
            f"Website url: {website.start_url}\n"
            f"Top keywords: {', '.join([kw['keyword'] for kw in keyword_summary])}.\n"
            f"Target Audience Segments: {', '.join(audience_segments)}\n"
            f"Page Titles: {', '.join(page_titles[:5])}\n"
            f"Descriptions: {' | '.join(descriptions[:5])}\n"
        )

        model = genai_model.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        website.positioning_insights = response_text
        website.save()

        print("Successfully generated positioning insights.")

    except Exception as e:
        print(f"Error generating positioning insights: {e}")

