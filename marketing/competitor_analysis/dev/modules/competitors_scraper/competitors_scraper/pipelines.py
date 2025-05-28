# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from modules.analysis.models import Page
import logging
from asgiref.sync import sync_to_async

@sync_to_async
class PagePipeline:
    def process_item(self, item, spider):
        logging.info("Processing item")
        try:
            item.save()
            logging.info(f"Saved URL: {item['url']}")
        except Exception as e:
            logging.error(f"Error saving item: {e}")
        
        return item
