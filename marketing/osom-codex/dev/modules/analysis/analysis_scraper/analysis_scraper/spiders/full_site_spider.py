from urllib.parse import urljoin

import scrapy
import sys
import os
import django
from asgiref.sync import sync_to_async
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import defer

DJANGO_PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
sys.path.append(DJANGO_PROJECT_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
from modules.analysis.models import ScrapedURL

class FullSiteSpider(scrapy.Spider):
    name = "full_site_spider"
    start_urls = ["https://www.indeform.com"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "EXTENSIONS": {
            'scrapy.extensions.telnet.TelnetConsole': None,
        },
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unvisited_links = set()
        self.visited_links = set()
    
    async def call_Fetch_unvisited_links(self):
        return await self.get_unvisited_links()

    async def get_unvisited_links(self):
        return [obj.url for obj in ScrapedURL.objects.all()]

    # def start_requests(self):
    #     seed_url = self.start_urls[0]
    #     self.logger.info(f"Using seed URL: {seed_url}")
    #     yield scrapy.Request(
    #         seed_url,
    #         meta={
    #             "playwright": True,
    #             "playwright_include_page": True,
    #             "handle_httpstatus_all": True,
    #         },
    #         callback=self.parse,
    #         dont_filter=True,
    #     )



    # @inlineCallbacks
    # def start_requests(self):
    #     # Convert the coroutine into a Deferred.
    #     self.unvisited_links = yield defer.ensureDeferred(self.call_Fetch_unvisited_links())
    #     self.logger.info(f"Unvisited: {self.unvisited_links}")

    #     if self.unvisited_links:
    #         for url in self.unvisited_links:
    #             yield scrapy.Request(
    #                 url,
    #                 meta={
    #                 "playwright": True,
    #                 "playwright_include_page": True,
    #                 "handle_httpstatus_all": True,
    #                 },
    #                 callback=self.parse,
    #                 dont_filter=True,
    #                 )
    #     else:
    #         yield scrapy.Request(
    #             url=self.start_urls[0],
    #             meta={
    #                 "playwright": True,
    #                 "playwright_include_page": True,
    #                 "handle_httpstatus_all": True,
    #             },
    #             callback=self.parse,
    #             dont_filter=True,
    #         )

    #     return defer.returnValue(None)

    def parse(self, response):
        print("Parse-------------------------------------------------------------")
        url = response.url
        print(f"\n--- Crawled URL ---\n{url}\n")

        self.visited_links.add(url)

        links = response.css("a::attr(href)").getall()
        for link in links:
            absolute_link = urljoin(url, link)

            if absolute_link.startswith(self.start_urls[0]) and absolute_link not in self.visited_links:
                self.unvisited_links.add(absolute_link)
                print(f"Added new page to local storage: {absolute_link}")
                yield {"url": absolute_link}
