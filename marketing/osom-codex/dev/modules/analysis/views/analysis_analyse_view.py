from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from modules.analysis.models import Website, Page
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class AnalyseView(TemplateView):
    template_name = "modules/analysis/analyse.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        url = request.POST.get('url')
        if not url:
            return redirect('/analyse')  # or wherever you want to redirect

        # 1. Retrieve or create a Website entry
        website, created = Website.objects.get_or_create(start_url=url)
        # 2. Update last_visited if Website already exists
        website.last_visited = timezone.now().date()
        website.save()

        # 3. Mark all existing Page entries for this Website as unvisited
        Page.objects.filter(website=website).update(visited=False)

        # 4. Create a new Page entry
        page = Page.objects.create(
            website=website,
            url=url,
            visited=False,
            page_title="",  # or something relevant, if known
        )

        # 5. Start the Scrapy crawler
        process = CrawlerProcess(get_project_settings())
        process.crawl("full_site_spider")  # spider name in full_site_spider.py
        process.start(stop_after_crawl=False)

        return redirect('/analyse')  # redirect after triggering the crawl

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

