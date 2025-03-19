from urllib.parse import urlparse, urlunparse, urljoin
import tldextract
import scrapy
from twisted.internet import threads
from scrapy import signals
from competitors_scraper.items import PageItem
from modules.analysis.models import Page, Website
from django.conf import settings
from django.utils import timezone
from asgiref.sync import sync_to_async
from django.db import close_old_connections

def normalize_url(url):
    parsed = urlparse(url)
    scheme = 'https'
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip('/') or '/'
    return urlunparse((scheme, netloc, path, '', '', ''))

def domain_matches(url, base_keyword):
    extracted = tldextract.extract(url)
    return base_keyword in extracted.domain

class FullSiteSpider(scrapy.Spider):
    name = "full_site_spider"
    custom_settings = {
        "CONCURRENT_REQUESTS": 100,
        
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 10,
        "PLAYWRIGHT_CONTEXTS": {"default": {"viewport": {"width": 1280, "height": 720}}},

        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 0.5,
        "AUTOTHROTTLE_MAX_DELAY": 3,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 5,

        "SCHEDULER_PRIORITY_QUEUE": "scrapy.pqueues.DownloaderAwarePriorityQueue",

        "SCHEDULER_DISK_QUEUE": "scrapy.squeues.PickleFifoDiskQueue",
        "SCHEDULER_MEMORY_QUEUE": "scrapy.squeues.FifoMemoryQueue", 

        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "ASYNCIO_EVENT_LOOP": "uvloop.Loop"

    }
    # custom_settings = {
    #     # "PLAYWRIGHT_BROWSER_TYPE": "chromium",
    #     # "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    #     # "CONCURRENT_REQUESTS": 5,
    #     # "DOWNLOAD_DELAY": 1, 
    #     # "DOWNLOAD_HANDLERS": {
    #     #     "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    #     #     "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
    #     # },
    #     # "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    #     # "SCRAPY_IGNORE_SIGNALS": True,  # Helps avoid signal errors when not running in main thread
    #     # "EXTENSIONS": {
    #     #     "scrapy.extensions.telnet.TelnetConsole": None,
    #     # },
    #     # "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    #     "PLAYWRIGHT_BROWSER_TYPE": "chromium",
    #     "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    #     "CONCURRENT_REQUESTS": 1000,
    #     "DOWNLOAD_DELAY": 1, 
    #     "DOWNLOAD_HANDLERS": {
    #         "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    #         "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
    #     },
    #     "PLAYWRIGHT_CONTEXTS": {
    #         "default": {"viewport": {"width": 1280, "height": 720}},
    #         "javaScriptEnabled": True,
    #     },
    #     "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    # }

    def __init__(self, website_id=None, website_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.website_id = website_id
        self.website_name = normalize_url(website_name) if website_name else ""
        self.visited_links = set()
        self.urls = set()
        self.website_instance = None

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
            
            extracted = tldextract.extract(self.website_name)
            self.base_keyword = extracted.domain

            # with open("/home/gustas/indeform_praktika/marketing/osom-codex/dev/modules/competitors_scraper/competitors_scraper/spiders/log.txt", "a") as log_file:
            #     log_file.write(f"Extracted domain: {self.base_keyword}\n")
            # print("Extracted domain:", self.base_keyword)
            # print("URLs from DB:", self.urls)
            # print("Scrapy is using database:", settings.DATABASES['default']['NAME'])

        threads.deferToThread(fetch_urls).addCallback(lambda _: self.schedule_initial_request())

    def schedule_initial_request(self):
        for url in self.urls:
            req = scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "handle_httpstatus_all": True,
                    "playwright_page_coroutines": [
                        lambda page: page.wait_for_load_state("networkidle"),  # Ensures JS has fully loaded
                        lambda page: page.route("**/*.{png,jpg,jpeg,webm,woff,woff2,ttf,css,mp4}", lambda route: route.abort())
                    ]
                },
                callback=self.parse,
                dont_filter=True,
            )
            self.crawler.engine.slot.scheduler.enqueue_request(req)

    def start_requests(self):
        return iter([])

    def update_page_sync(self, page, response):
        close_old_connections()
        page.visited = True
        page.page_title = response.css("title::text").get() or ""
        page.last_visit = timezone.now().date()
        page.save()

        website = page.website
        website.visited_count += 1
        website.save()
    

    def get_page_sync(self, website_id, url):
        norm_url = normalize_url(url)
        return Page.objects.filter(website_id=website_id, url=norm_url).first()

    def parse(self, response):
        url = normalize_url(response.url)
        # count = 0
        # for u in self.urls:
        #     count += 1
        #     with open("/home/gustas/indeform_praktika/marketing/osom-codex/dev/modules/competitors_scraper/competitors_scraper/spiders/log.txt", "a") as log_file:
        #         log_file.write(f"URLS: {u}, Number: {count}\n")
    
        # count = 0
        # for u in self.visited_links:
        #     count += 1
        #     with open("/home/gustas/indeform_praktika/marketing/osom-codex/dev/modules/competitors_scraper/competitors_scraper/spiders/log.txt", "a") as log_file:
        #         log_file.write(f"Visited set:: {u}, count: {count}\n")
        #     print(f"Visited set:: {u}, count: {count}")
        
        # for count, u in enumerate(self.urls, 1):
        #     self.logger.info(f"Discovered URL #{count}: {u}")
        # for count, u in enumerate(self.visited_links, 1):
        #     self.logger.info(f"Visited URL #{count}: {u}")
        

        print(f"--- Crawling URL --- {url}")
        with open("/home/gustas/indeform_praktika/marketing/osom-codex/dev/modules/competitors_scraper/competitors_scraper/spiders/log.txt", "a") as log_file:
            log_file.write(f"--- Crawling URL --- {url}\n")

        if url in self.visited_links:
            return
        self.visited_links.add(url)

        with open("/home/gustas/indeform_praktika/marketing/osom-codex/dev/modules/competitors_scraper/competitors_scraper/spiders/log.txt", "a") as log_file:
            log_file.write(f"--- Crawled URL --- {url}\n")

        print(f"--- Crawled URL --- {url}")
        # Update the Page record in a thread
        d = threads.deferToThread(self.get_page_sync, self.website_id, url)
        def update_if_exists(page):
            if page is not None:
                threads.deferToThread(self.update_page_sync, page, response)

        d.addCallback(update_if_exists)
        d.addErrback(lambda failure: failure.trap(Page.DoesNotExist))
        
        links = response.css("a::attr(href)").getall()
        new_request_generated = False
        for link in links:
            absolute_link = normalize_url(urljoin(url, link))
            if domain_matches(absolute_link, self.base_keyword) and absolute_link not in self.visited_links:
                if absolute_link not in self.urls:
                    # Record it as discovered (for DB/pipeline purposes)
                    self.urls.add(absolute_link)
                    item = PageItem()
                    item["url"] = absolute_link
                    item["website"] = self.website_instance
                    item["page_title"] = ""
                    yield item
                # Always schedule if not visited yet.
                new_request_generated = True
                yield scrapy.Request(
                    absolute_link,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "handle_httpstatus_all": True,
                    },
                    callback=self.parse,
                    dont_filter=True,
                )
                # self.logger.info(f"New request generated: {absolute_link}")

        # self.logger.info(f"Visited set size: {len(self.visited_links)}, Discovered set size: {len(self.urls)}")
        # with open("/home/gustas/indeform_praktika/marketing/osom-codex/dev/modules/competitors_scraper/competitors_scraper/spiders/log.txt", "a") as log_file:
        #     log_file.write(f"self.visited_links length: {len(self.visited_links)}\n self.urls length: {len(self.urls)}\n")
        if not new_request_generated and self.visited_links == self.urls:
            def finish_crawl():
                website = Website.objects.get(id=self.website_id)
                website.crawling_in_progress = False
                website.crawling_finished = True
                website.visited_count = len(self.visited_links)
                website.save()
            threads.deferToThread(finish_crawl)
            self.logger.info("No new links found. All links have been visited. Closing spider.")
            self.crawler.engine.close_spider(self, reason="finished")
