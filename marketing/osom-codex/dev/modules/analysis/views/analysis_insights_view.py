import google.generativeai as genai
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from modules.analysis.models import Website, ExtractedKeyword
from collections import Counter

genai.configure(api_key="your-api-key")  # Or use os.getenv("GEMINI_API_KEY")

class InsightsView(TemplateView):
    template_name = "modules/analysis/insights.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        website = get_object_or_404(Website, id=kwargs.get('website_id'))

        keywords = ExtractedKeyword.objects.filter(page__website=website)
        keyword_counter = Counter()
        keyword_scores = {}

        for kw in keywords:
            keyword_counter[kw.keyword] += 1
            keyword_scores.setdefault(kw.keyword, []).append(kw.score)

        sorted_keywords = sorted(
            keyword_counter.items(),
            key=lambda item: (-item[1], -sum(keyword_scores[item[0]]) / len(keyword_scores[item[0]]))
        )

        top_keywords = [kw for kw, _ in sorted_keywords[:20]]

        prompt = (
            f"Aiškink, kaip konkurentai komunikuoja ir save pozicionuoja, "
            f"pagal šiuos raktinius žodžius: {', '.join(top_keywords)}. "
            f"Pasakyk ar auditorija labiau tech, ar paprasti žmonės."
        )

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        context.update({
            "website": website,
            "keywords": top_keywords,
            "insight": response.text,
        })
        return context
