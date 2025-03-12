from urllib.parse import urljoin
import scrapy
from twisted.internet import threads
from scrapy import signals
from competitors_scraper.items import PageItem
from modules.analysis.models import Page
from modules.analysis.models import Website
from django.conf import settings
from django.utils import timezone

class FullSiteSpider(scrapy.Spider):
    name = "full_site_spider"

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "SCRAPY_IGNORE_SIGNALS": True,
        "EXTENSIONS": {
            "scrapy.extensions.telnet.TelnetConsole": None,
        },
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }

    def __init__(self, website_id=None, website_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.website_id = website_id
        self.visited_links = set()
        self.urls = set()
        self.website_name = website_name
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
            u = list(unvisited_pages.values_list("url", flat=True))
            self.urls = set(u)
            self.logger.info("Urls from database: %s", len(u))
            print(self.urls)
            print("Scrapy is using database:", settings.DATABASES['default']['NAME'])
        threads.deferToThread(fetch_urls).addCallback(lambda _: self.schedule_initial_request())

    def schedule_initial_request(self):
        for url in self.urls:         
            if(url not in self.visited_links):
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
                self.visited_links.add(url)
                # Enqueue the request directly via the scheduler
                self.crawler.engine.slot.scheduler.enqueue_request(req)
            else:
                self.urls.remove(url)
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
    
    def update_page_sync(self, page, response):
        page.visited = True
        page.page_title = response.css("title::text").get() or ""
        page.last_visit = timezone.now().date()
        page.save()

    def get_page_sync(self, website_id, url):
        return Page.objects.get(website_id=website_id, url=url)

    def parse(self, response):
        url = response.url
        if url in self.visited_links:
            return
        self.logger.info(f"--- Crawled URL --- {url}")
        print(f"--- Crawled URL --- {url}")
        self.visited_links.add(url)
        d = threads.deferToThread(self.get_page_sync, self.website_id, url)
        d.addCallback(lambda page: self.update_page_sync(page, response))
        # Add an error callback to catch if the page does not exist.
        d.addErrback(lambda failure: failure.trap(Page.DoesNotExist))
        links = response.css("a::attr(href)").getall()
        for link in links:
            absolute_link = urljoin(url, link)

            if (absolute_link.startswith(self.website_name)
                    and absolute_link not in self.visited_links
                    and absolute_link not in self.urls):
                self.urls.add(absolute_link)
                print(f"Added new page to local storage: {absolute_link}")
                item = PageItem()
                item["url"] = absolute_link
                item["website"] = self.website_instance
                item["page_title"] = ""
                yield item
