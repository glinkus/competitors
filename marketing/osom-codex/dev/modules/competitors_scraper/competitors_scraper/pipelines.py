# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from modules.analysis.models import Page
import logging
from asgiref.sync import sync_to_async
# class SaveLinksPipeline:
#     def process_item(self, item, spider):
#         url = item.get("url")

#         print(f"Url from pipeline: {url}")
#         if url:
#             obj, created = ScrapedURL.objects.get_or_create(url=url)
#             if created:
#                 print(f"Added new URL: {url}")
#             else:
#                 print(f"URL already exists: {url}")

#         return item
@sync_to_async
class PagePipeline:
    def process_item(self, item, spider):
        try:
            item.save()
            logging.info(f"Saved URL: {item['url']}")
        except Exception as e:
            logging.error(f"Error saving item: {e}")
        
        return item
