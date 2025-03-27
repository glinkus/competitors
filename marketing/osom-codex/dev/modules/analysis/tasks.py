import shlex
import subprocess
import os
from time import sleep
from celery import shared_task
from modules.analysis.models import Page, Website, ExtractedKeyword
from modules.analysis.utils.keyword_extraction import KeywordExtraction


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
        unvisited_pages = list(
            Page.objects.filter(website_id=website_id, visited=False)
            .values_list("url", flat=True)
        )
        if not unvisited_pages:
            w = Website.objects.filter(id=website_id).first()
            if w:
                w.crawling_finished = True
                w.save()
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
                
                analyze_page.delay(page_url)
        sleep(5)

        # web = Website.objects.filter(id=website_id).first()
        # if web:
        #     web.crawling_finished = True
        #     web.save()
        # else:
        #     raise Exception(f"Website with id {website_id} not found.")
        # return "Scraped one page"
    
@shared_task
def analyze_page(page_url):
    page = Page.objects.get(url=page_url)
    extractor = KeywordExtraction()
    keywords = extractor.extract_keywords(page)

    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # project_root = os.path.join(BASE_DIR, 'competitors_scraper')
    # log_dir = os.path.join(project_root, 'logs')
    # os.makedirs(log_dir, exist_ok=True)
    # file_path = os.path.join(log_dir, f'keywords_{page.id}.txt')


    # with open(file_path, "w", encoding="utf-8") as f:
    #     for keyword, score in keywords:
    #         f.write(f"{keyword}: {score}\n")

    ExtractedKeyword.objects.filter(page=page).delete()

    extracted_keywords_objs = [
        ExtractedKeyword(page=page, keyword=keyword, score=score)
        for keyword, score in keywords
    ]

    ExtractedKeyword.objects.bulk_create(extracted_keywords_objs)

    return {"stored_keywords_count": len(keywords), "page": page.url}