from modules.analysis.models import Website, Page
from django.views.generic import TemplateView
from django.utils import timezone
from django.shortcuts import redirect
from django.core.validators import URLValidator
from modules.analysis.tasks import run_one_page_spider

class ConfirmReanalyseView(TemplateView):
    def post(self, request):
        url = request.POST.get("url")
        validate = URLValidator()
        try:
            validate(url)
        except:
            return redirect(f"{reverse('modules.analysis:analyse')}?error=invalid_url")

        website = Website.objects.filter(start_url=url).first()
        if website:
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
            
            run_one_page_spider.delay(website_id=website.id, website_name=url)

        return redirect('modules.analysis:analyse')