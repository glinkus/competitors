# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from modules.analysis.models import ScrapedURL
from scrapy_djangoitem import DjangoItem

class CompetitorsScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ScrapedUrlItem(DjangoItem):
    django_model = ScrapedURL