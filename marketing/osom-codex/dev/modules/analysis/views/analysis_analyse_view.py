from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.http import JsonResponse

from modules.analysis.models import Website, Page
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse
from django.core.validators import URLValidator
from modules.analysis.tasks import run_one_page_spider

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
            website.crawling_in_progress = True
            website.crawling_finished = False
            website.visited_count = 0
            website.save()

            Page.objects.filter(website=website).delete()
            Page.objects.all().delete()
            Page.objects.create(
            website=website,
            url=url,
            visited=False,
            page_title="",
            )
        else:
            website = Website.objects.create(start_url=url, last_visited=timezone.now().date(), crawling_in_progress=True)
            Page.objects.create(
            website=website,
            url=url,
            visited=False,
            page_title="",
            )

        run_one_page_spider.delay(website_id=website.id, website_name=website.start_url)

        return redirect(f"/analysis/analyse?website_id={website.id}")

    # def get(self, request, *args, **kwargs):
    #     websites = Website.objects.all().order_by('-last_visited')
    #     context = {
    #         'websites': websites,
    #     }
    #     return render(request, self.template_name, context)
    
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            website_id = request.GET.get('website_id')
            if website_id:
                try:
                    website = Website.objects.get(id=website_id)
                    data = {
                        'crawling_in_progress': website.crawling_in_progress,
                        'crawling_finished': website.crawling_finished,
                        'visited_count': website.visited_count,
                    }
                except Website.DoesNotExist:
                    data = {'error': 'Website not found'}
                return JsonResponse(data)
            return JsonResponse({'error': 'No website_id provided'})
        else:
            websites = Website.objects.all().order_by('-last_visited')
            context = {
                'websites': websites,
            }
            return render(request, self.template_name, context)


