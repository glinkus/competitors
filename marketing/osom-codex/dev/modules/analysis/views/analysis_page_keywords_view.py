from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from modules.analysis.models import Page, ExtractedKeyword

class PageKeywordsView(TemplateView):
    template_name = "modules/analysis/page_keywords.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_id = kwargs.get('page_id')
        page = get_object_or_404(Page, id=page_id)
        keywords = ExtractedKeyword.objects.filter(page=page).order_by('-score')

        context['page'] = page
        context['keywords'] = keywords
        return context