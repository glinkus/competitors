from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from modules.analysis.models import Website, Page
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse
from django.core.validators import URLValidator

class AnalyseView(TemplateView):
    template_name = "modules/analysis/analyse.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        url = request.POST.get("url")
        print("Entered URL: ", url)

        validate = URLValidator()
        try:
            validate(url)
        except:
            # Redirect or show an error message if invalid URL
            return redirect("/analysis/analyse?error=invalid_url")
        
        website, created = Website.objects.get_or_create(start_url=url)
        website.last_visited = timezone.now().date()
        website.save()

        Page.objects.filter(website=website).update(visited=False)

        page = Page.objects.create(
            website=website,
            url=url,
            visited=False,
            page_title="",
        )

        # 5. Start the Scrapy crawler
        process = CrawlerProcess(get_project_settings())
        process.crawl("full_site_spider", website_id=website.id, website_name=website.start_url)
        process.start(stop_after_crawl=False)

        return redirect("/analysis/analyse")  # redirect after triggering the crawl

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
