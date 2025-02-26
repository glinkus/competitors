import scrapy
from scrapy_playwright.page import PageCoroutine

class PlaywrightSpider(scrapy.Spider):
    name = "playwright_spider"
    start_urls = ["https://indeform.com"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},  # Run headless mode
        "DOWNLOAD_HANDLERS": {"http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                              "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"},
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
    }

    async def parse(self, response):
        title = response.css("title::text").get()
        url = response.url
        text = " ".join(response.css("p::text, div::text, span::text").getall()).strip()
        headings = response.css("h1::text, h2::text, h3::text, div.title::text").getall()

        print("\n--- Scraped Data ---")
        print(f"Title: {title}")
        print(f"URL: {url}")
        print(f"Headings: {headings if headings else 'No headings found'}")
        print(f"Text: {text if text else 'No text found'}")
        print("--- End of Scraped Data ---\n")

        yield {"title": title, "url": url, "headings": headings, "text": text}
