# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.og/en/latest/topics/items.html

import scrapy

class ScrapedItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    text = scrapy.Field()
    headings = scrapy.Field()

