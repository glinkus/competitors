from urllib.parse import urljoin
import scrapy
from twisted.internet import threads
from scrapy import signals
from modules.analysis.models import ScrapedURL
from competitors_scraper.items import ScrapedUrlItem
from django.conf import settings

class FullSiteSpider(scrapy.Spider):
    name = "full_site_spider"
    start_urls = ["https://indeform.com"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "EXTENSIONS": {
            "scrapy.extensions.telnet.TelnetConsole": None,
        },
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visited_links = set()
        self.urls = set()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider

    def spider_opened(self):
        # Run the Django ORM call in a separate thread.
        def fetch_urls():
            urls = list(ScrapedURL.objects.all().values_list("url", flat=True))
            self.urls = urls
            self.logger.info("Urls from database: %s", len(urls))
            print(self.urls)
            print("Scrapy is using database:", settings.DATABASES['default']['NAME'])
        threads.deferToThread(fetch_urls).addCallback(lambda _: self.schedule_initial_request())

    def schedule_initial_request(self):
        for url in self.urls:         
            req = scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "handle_httpstatus_all": True,
                },
                callback=self.parse,
                dont_filter=True,
            )
            # Enqueue the request directly via the scheduler
            self.crawler.engine.slot.scheduler.enqueue_request(req)
        # req = scrapy.Request(
        #     self.start_urls[0],
        #     meta={
        #         "playwright": True,
        #         "playwright_include_page": True,
        #         "handle_httpstatus_all": True,
        #     },
        #     callback=self.parse,
        #     dont_filter=True,
        # )
        # # Enqueue the request directly via the scheduler
        # self.crawler.engine.slot.scheduler.enqueue_request(req)

    def start_requests(self):
        # Return an empty iterable since we schedule the initial request in spider_opened.
        return iter([])

    def parse(self, response):
        self.logger.info("Parse ----------------------------------------------------")
        url = response.url
        self.logger.info(f"--- Crawled URL --- {url}")

        links = response.cs
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",s("a::attr(href)").getall()
        for link in links:
            absolute_link = urljoin(url, link)
            self.logger.debug(f"Absolute link: {absolute_link}")
            if absolute_link.startswith(self.start_urls[0]) and absolute_link not in self.visited_links:
                print(f"Added new page to local storage: {absolute_link}")
                item = ScrapedUrlItem()
                item["url"] = absolute_link
                yield item
