from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.http import JsonResponse
from urllib.parse import urlparse, urlunparse, urljoin

from modules.analysis.models import Website, Page
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse
from django.core.validators import URLValidator
from modules.analysis.tasks import run_one_page_spider
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

genai.configure(api_key=settings.GENAI_API_KEY)

@require_POST
def stop_scraping(request, website_id):
    website = Website.objects.filter(id=website_id).first()
    if website and website.crawling_in_progress:
        website.crawling_in_progress = False
        website.scraping_stopped = True
        website.save()
        return JsonResponse({'stopped': True})
    return JsonResponse({'error': 'Invalid or already stopped'}, status=400)

@require_POST
def continue_scraping(request, website_id):
    website = Website.objects.filter(id=website_id).first()
    if website and not website.crawling_in_progress:
        website.crawling_in_progress = True
        website.scraping_stopped = False
        website.save()
        run_one_page_spider.delay(website_id=website.id, website_name=website.start_url)
        return JsonResponse({'continued': True})
    return JsonResponse({'error': 'Unable to continue'}, status=400)

class AnalyseView(LoginRequiredMixin, TemplateView):
    template_name = "modules/analysis/analyse.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get("delete_website_id"):
            website_id = request.POST.get("delete_website_id")
            try:
                website = Website.objects.get(id=website_id)
                website.delete()
                return JsonResponse({'deleted': True})
            except Website.DoesNotExist:
                return JsonResponse({'error': 'Website not found'}, status=404)

        u = request.POST.get("url")
        url = self.normalize_url(u)
        print("Entered URL: ", url)

        validate = URLValidator()
        try:
            validate(url)
        except:
            return redirect(f"{reverse('modules.analysis:analyse')}?error=invalid_url")
        
        website_qs = Website.objects.filter(start_url=url)
        if website_qs.exists():
            website = website_qs.first()
            website.last_visited = timezone.now().date()
            website.crawling_in_progress = True
            website.crawling_finished = False
            website.visited_count = 0
            website.save()

            Page.objects.filter(website=website).delete()
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

        return redirect(reverse('modules.analysis:analyse'))
    
    
    def get(self, request, *args, **kwargs):

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            website_id = request.GET.get('website_id')
            if website_id:
                try:
                    website = Website.objects.get(id=website_id)
                    visited_count = Page.objects.filter(website_id=website.id, visited=True).count()
                    data = {
                        'crawling_in_progress': website.crawling_in_progress,
                        'crawling_finished': website.crawling_finished,
                        'visited_count': visited_count,
                    }
                except Website.DoesNotExist:
                    data = {'error': 'Website not found'}
                print("Data: ", data)
                return JsonResponse(data)
            return JsonResponse({'error': 'No website_id provided'})
        else:
            websites = Website.objects.all().order_by('-last_visited')
            context = {
                'websites': websites,
            }
            return render(request, self.template_name, context)
        
    def normalize_url(self, url):
        if not urlparse(url).scheme:
            url = 'https://' + url
        parsed = urlparse(url)
        scheme = 'https'
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip('/') or '/'
        return urlunparse((scheme, netloc, path, '', '', '')) 


