from urllib.parse import urljoin

import scrapy
import asyncio
from modules.analysis.models import ScrapedURL
from competitors_scraper.items import ScrapedUrlItem
from django.conf import settings
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync

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
            'scrapy.extensions.telnet.TelnetConsole': None,
        },
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unvisited_links = set()
        self.visited_links = set()
        self.urls = set()

    @sync_to_async
    def fetch_urls(self):
        return ScrapedURL.objects.all().values("url")
    
    
    async def call_fetch_urls(self):
        # This is the synchronous function that calls the asynchronous function
        self.urls = await self.fetch_urls()
    @async_to_sync
    async def call_url(self):
        return await self.call_fetch_urls
    
    def start_requests(self):
        #self.call_fetch_urls()
        #print(f"Urls from database: {urls}")
        #self.logger.info(f"Using seed URL: {seed_url}")
        #urls = ScrapedURL.objects.all().values("url")
        self.call_url()
        print(f"Urls from database: {len(self.urls)}")
        print("Scrapy is using database:", settings.DATABASES['default']['NAME'])
        yield scrapy.Request(
            self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "handle_httpstatus_all": True,
            },
            callback=self.parse,
            dont_filter=True,
       )

    def parse(self, response):
        print("Parse-------------------------------------------------------------")
        url = response.url
        print(f"\n--- Crawled URL ---\n{url}\n")

        #self.visited_links.add(url)

        links = response.css("a::attr(href)").getall()
        for link in links:
            absolute_link = urljoin(url, link)
            print(f"Absolute link: {absolute_link}")
            if absolute_link.startswith(self.start_urls[0]) and absolute_link not in self.visited_links:
                #self.unvisited_links.append(absolute_link)
                print(f"Added new page to local storage: {absolute_link}")
                item = ScrapedUrlItem()
                item["url"] = absolute_link
                yield item
