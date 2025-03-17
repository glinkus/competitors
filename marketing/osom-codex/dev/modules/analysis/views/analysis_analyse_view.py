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
from modules.analysis.tasks import run_spider

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
        
        website_qs = Website.objects.filter(start_url=url)
        if website_qs.exists():
            website = website_qs.first()
            website.last_visited = timezone.now().date()
            website.save()
            Page.objects.filter(website=website).delete()
            Page.objects.create(
            website=website,
            url=url,
            visited=False,
            page_title="",
            )
        else:
            website = Website.objects.create(start_url=url, last_visited=timezone.now().date())
            Page.objects.create(
            website=website,
            url=url,
            visited=False,
            page_title="",
            )

        run_spider.delay(website_id=website.id, website_name=website.start_url)

        return redirect("/analysis/analyse")

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
