# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.og/en/latest/topics/items.html

import scrapy
from scrapy.contrib.djangoitem import DjangoItem
from modules.analysis.models import ScrapedURL

class ScrapedItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    text = scrapy.Field()
    headings = scrapy.Field()
class ScrapedURLItem(DjangoItem):
    django_model = ScrapedURL
