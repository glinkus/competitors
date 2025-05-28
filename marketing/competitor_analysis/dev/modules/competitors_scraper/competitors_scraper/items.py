# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from modules.analysis.models import Website
from modules.analysis.models import Page
from scrapy_djangoitem import DjangoItem

class CompetitorsScraperItem(scrapy.Item):
    pass

class WebsiteItem(DjangoItem):
    django_model = Website

class PageItem(DjangoItem):
    django_model = Page