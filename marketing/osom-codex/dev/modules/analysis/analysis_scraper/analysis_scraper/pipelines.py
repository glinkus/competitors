import sys
import os
import django
from asgiref.sync import sync_to_async

DJANGO_PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.append(DJANGO_PROJECT_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
from modules.analysis.models import ScrapedURL

class SaveLinksPipeline:
    @sync_to_async
    def process_item(self, item, spider):
        url = item.get("url")

        print(f"Url from pipeline: {url}")
        if url:
            obj, created = ScrapedURL.objects.get_or_create(url=url)
            if created:
                print(f"Added new URL: {url}")
            else:
                print(f"URL already exists: {url}")

        return item