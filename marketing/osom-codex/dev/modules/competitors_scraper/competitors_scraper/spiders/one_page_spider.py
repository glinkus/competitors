from urllib.parse import urlparse, urlunparse, urljoin
import tldextract
import scrapy
from twisted.internet import threads
from scrapy import signals
from competitors_scraper.items import PageItem
from modules.analysis.models import Page, Website
from django.conf import settings
from django.utils import timezone
from django.db import close_old_connections

def normalize_url(url):
    parsed = urlparse(url)
    scheme = 'https'
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip('/') or '/'
    return urlunparse((scheme, netloc, path, '', '', ''))

# def domain_matches(url, base_keyword):
#     extracted = tldextract.extract(url)
#     return base_keyword in extracted.domain

class OnePageSpider(scrapy.Spider):
    name = "one_page_spider"

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "DOWNLOAD_DELAY": 1,
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
        },
        "PLAYWRIGHT_CONTEXTsp": {
            "default": {"viewport": {"width": 1280, "height": 720}},
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    def __init__(self, page_url=None, website_id=None, website_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if page_url is None:
            raise ValueError("A page URL must be provided as the 'page_url' argument")
        self.page_url = normalize_url(page_url)
        self.website_id = website_id
        self.website_name = normalize_url(website_name) if website_name else ""

        self.website_instance = None
        self.urls = set()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider

    def spider_opened(self):
        def fetch_urls():
            unvisited_pages = Page.objects.filter(
                visited=False,
                website=self.website_id
            )
            self.website_instance = Website.objects.get(id=self.website_id)
            u = [normalize_url(u) for u in unvisited_pages.values_list("url", flat=True)]
            self.urls = set(u)
            self.logger.info(f"Initial URLs from DB: {self.urls}")
            # extracted = tldextract.extract(self.website_name)
            # self.base_keyword = extracted.domain
            # self.logger.info(f"Extracted domain: {self.base_keyword}")

        threads.deferToThread(fetch_urls).addCallback(lambda _: self.start_requests())
        
    def start_requests(self):
        yield scrapy.Request(
            self.page_url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "handle_httpstatus_all": True,
                "playwright_page_coroutines": [
                    lambda page: page.route("**/*.{png,jpg,jpeg,webm,woff,woff2,ttf,css,mp4}", lambda route: route.abort()),
                    lambda page: page.wait_for_load_state("networkidle")
                ]

            },
            callback=self.parse,
            dont_filter=True,
        )

    def extract_structured_text(self, response):
        elements = {
            'title': 'title::text',
            'h1': 'h1::text',
            'h2': 'h2::text',
            'h3': 'h3::text',
            'h4': 'h4::text',
            'h5': 'h5::text',
            'h6': 'h6::text',
            'alt': 'img::attr(alt)',
            'p': 'p ::text',
            'li': 'li::text'
        }
        
        structured = {}
        for tag, selector in elements.items():
            texts = response.css(selector).getall()
            if texts:
                joined = " ".join(text.strip() for text in texts if text.strip())
                structured[tag] = joined
        if 'p' in structured and 'li' in structured:
            structured['p'] = structured['p'] + " " + structured['li']
            del structured['li']
        return structured


    def update_page_sync(self, page, response):
        close_old_connections()
        page.visited = True
        page.page_title = response.css("title::text").get() or ""
        page.last_visit = timezone.now().date()
        structured = self.extract_structured_text(response)
        page.structured_text = structured

        page.save()

        website = page.website
        website.visited_count += 1
        website.save()

    def save_page_sync(self, website_id, url):
        norm_url = normalize_url(url)
        page, created = Page.objects.get_or_create(website_id=website_id, url=norm_url)
        return page

        
    
    def get_page_sync(self, website_id, url):
        norm_url = normalize_url(url)
        return Page.objects.filter(website_id=website_id, url=norm_url).first()
    
    

    def parse(self, response):
        url = normalize_url(response.url)
        self.logger.info(f"--- Crawling URL --- {url}")

        d = threads.deferToThread(self.get_page_sync, self.website_id, url)
        def update_if_exists(page):
            if page is not None:
                threads.deferToThread(self.update_page_sync, page, response)
            else:
                self.logger.info(f"No Page record found for URL: {url}")
        d.addCallback(update_if_exists)
        d.addErrback(lambda failure: failure.trap(Page.DoesNotExist))

        content_type = response.headers.get("Content-Type", b"").decode("utf-8")
        if "text/html" not in content_type.lower():
            self.logger.info(f"Skipping non-HTML content for URL {url} with content type: {content_type}")
            self.logger.info("Finished processing single page. Closing spider.")
            self.crawler.engine.close_spider(self, reason="finished")
            return
        links = response.css("a::attr(href)").getall()
        self.logger.info(f"Found {len(links)} links on the page.")
        for link in links:
            absolute_link = normalize_url(urljoin(url, link))
            self.logger.info(f"Checking link: {absolute_link}")
            original_link = urlparse(url).netloc
            founded_link = urlparse(absolute_link).netloc

            if original_link == founded_link and absolute_link != url and absolute_link not in self.urls:
                    self.logger.info(f"Found internal link: {absolute_link}")
                    self.urls.add(absolute_link)
                    try:
                        threads.deferToThread(self.save_page_sync, self.website_id, absolute_link)
                    except Exception as e:
                        self.logger.error(f"Error saving page: {e}")
                    

        self.logger.info("Finished processing single page. Closing spider.")
        self.crawler.engine.close_spider(self, reason="finished")

        