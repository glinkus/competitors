import shlex
import subprocess
import os
from time import sleep
from celery import shared_task
from modules.analysis.models import Page, Website, ExtractedKeyword, SEORecommendation
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
import google.generativeai as genai

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

                analyze_page.delay(page_url)
                sleep(5)
                classify_text.delay(page_url)
                sleep(5)
                text_read_analysis.delay(page_url)
                sleep(5)
                run_seo_analysis.delay(page_url)
            website = Website.objects.filter(id=website_id).first()
            if not website or not website.crawling_in_progress:
                print(f"Scraping manually stopped for website ID {website_id}")
                return "Scraping stopped by user."

        sleep(5)


@shared_task
def run_seo_analysis(page_url):
    page = Page.objects.get(url=page_url)

    page_seo_analysis = PageSEOAnalysis(page_url)
    analysis = page_seo_analysis.analyze()

    total_word_count = page.structured_data.get("wordcount")

    if analysis:
        seo_insights = SEOInsights(
            content=page.content,
            url=page.url,
            overall_metrics=analysis,
            internal_links=page.internal_links,
            external_links=page.external_links,
            warnings=page.warnings,
            total_word_count=total_word_count
        )
        
        try:
            seo_insights.run_analysis()
        except Exception as e:
            print(f"Error running SEO Insights analysis: {e}")


@shared_task
def analyze_page(page_url):
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
def extract_keywords_for_website(website_id, top_n=20):
    pages = Page.objects.filter(website_id=website_id)

    documents = []
    page_ids = []

    for page in pages:
        structured_text = page.structured_text
        full_text = ' '.join(structured_text.values())
        preprocessed = preprocess_text(full_text)
        documents.append(preprocessed)
        page_ids.append(page.id)

    vectorizer = TfidfVectorizer(
        max_df=0.85,
        ngram_range=(1, 3),
        stop_words='english',
    )

    tfidf_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()

    ExtractedKeyword.objects.filter(page__website_id=website_id).delete()

    keyword_objects = []

    for doc_idx, page_id in enumerate(page_ids):
        tfidf_scores = tfidf_matrix[doc_idx].toarray().flatten()
        top_indices = tfidf_scores.argsort()[::-1][:top_n]

        for idx in top_indices:
            keyword = feature_names[idx]
            score = tfidf_scores[idx]

            keyword_objects.append(
                ExtractedKeyword(
                    page_id=page_id,
                    keyword=keyword,
                    score=score
                )
            )

    ExtractedKeyword.objects.bulk_create(keyword_objects)

    return {
        "website_id": website_id,
        "pages_processed": len(page_ids),
        "total_keywords_extracted": len(keyword_objects)
    }

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

    geo = 'LT'
    pytrends = TrendReq()
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
        pytrends.build_payload(chunk, timeframe='today 3-m', geo=geo)

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
            main_obj.save()
        sleep(60)

    return {"top_keywords_enriched": top_keywords}

@shared_task
def classify_text(page_url):
    classifier = pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
            device=-1 
        )

    page = Page.objects.get(url=page_url)
    structured_text = page.structured_text
    full_text = ' '.join(structured_text.values())

    candidate_labels = [
        "technical",
        "emotional",
        "neutral"
    ]
    if len(full_text.split()) < 25:
        return {f"skipped {page.url}": "Text too short for reliable classification."}
    try:
        result = classifier(full_text, candidate_labels, multi_label=True)
    except Exception as e:
        return {f"error in text classification analyzing {page.url}: {str(e)}"}

    tone_classification = {label: round(score * 100, 2) for label, score in zip(result["labels"], result["scores"])}
    page.text_types = tone_classification
    page.save()

    return {"tone_classification": tone_classification}

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

    Page.objects.filter(id=page.id).update(
        text_readability=reading_score,
        text_reading_time=reading_time
        )

    return {
        "text_readability": reading_score,
        "reading_time": reading_time,
        "word_count": word_count
    }

@shared_task
def generate_website_insight(website_id):
    website = Website.objects.get(id=website_id)
    pages = Page.objects.filter(website=website).exclude(text_readability__isnull=True)

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
    for page in pages:
        summaries.append({
            "url": page.url,
            "readability": page.text_readability,
            "reading_time": page.text_reading_time,
            "tones": page.text_types,
            "seo_score": page.seo_score,
            "seo_score_details": page.seo_score_details,
            "linking_analysis": page.linking_analysis,
            "warnings": page.warnings,
        })
        
    recommendations_list = list(recommendations.values_list('actions', flat=True))
    
    summaries.append({
        "keywords": dict(keywords_by_page),
        "recommendations": recommendations_list
    })
    prompt = (
        "You are analyzing a company's website based on the data extracted from its pages. "
        "Each page contains a title, URL, readability score, reading time (in minutes), tone classification "
        "(technical, emotional, neutral), SEO score, and a list of SEO-related warnings, seo recommendations and other recommendations .\n\n"
        "Given this data for all pages in JSON format below, write a concise executive summary of the entire website's content and SEO performance. "
        "Identify tone trends, content clarity, SEO health, recurring weaknesses, and provide improvement suggestions. "
        "Be clear, professional, and do not include the raw URLs or page titles directly. Focus on aggregated insight. \n\n"
        f"Website Pages JSON:\n{json.dumps(summaries, ensure_ascii=False)}"
    )

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    print(f"Insight response: {response}")
    website.insight_text = response.text.strip()
    website.save()

    return "Insight generated successfully"

@shared_task
def generate_target_audience(website_id):
    try:
        website = Website.objects.get(id=website_id)
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

        print(f"Top keywords for target audience: {top_keywords}")

        prompt = (
            "I am analyzing the pages of a competitor's company website. "
            f"Based on these keywords: {', '.join(top_keywords)}, "
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

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        cleaned = response.text.strip().strip("```json").strip("```").strip()
        parsed = json.loads(cleaned)

        if "Company Target Audience" in parsed:
            parsed = parsed["Company Target Audience"]

        website.target_audience = parsed
        website.save()

    except Exception as e:
        print(f"Error generating target audience: {e}")
