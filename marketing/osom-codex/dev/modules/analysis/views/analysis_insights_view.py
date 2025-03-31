import google.generativeai as genai
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from modules.analysis.models import Website, ExtractedKeyword, KeywordInsight
from collections import Counter
import markdown

genai.configure(api_key="AIzaSyCzvpa1Lb9dzp7-13T3C2HpDG9V7MVVsZM")

class InsightsView(TemplateView):
    template_name = "modules/analysis/insights.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        website = get_object_or_404(Website, id=kwargs.get('website_id'))

        try:
            insight = website.insight.insight_text
        except KeywordInsight.DoesNotExist:
            insight = self._generate_insight(website)

        context.update({
            "website": website,
            "insight": markdown.markdown(insight, extensions=["extra"]),
        })
        return context

    def post(self, request, *args, **kwargs):
        website = get_object_or_404(Website, id=kwargs.get('website_id'))

        # Delete existing insight if present
        KeywordInsight.objects.filter(website=website).delete()

        # Regenerate and store
        new_insight = self._generate_insight(website)

        return redirect(reverse("modules.analysis:insights", kwargs={"website_id": website.id}))

    def _generate_insight(self, website):
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
            f"Aiškink, kaip konkurentų įmonė komunikuoja ir save pozicionuoja, "
            f"pagal šiuos raktinius žodžius: {', '.join(top_keywords)}. "
            f"Nepateik raktinių žodžių, užklausos rezultate. "
            f"Pasakyk į kokią auditoriją orientuojasi įmonė."
        )

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        insight = response.text

        KeywordInsight.objects.create(website=website, insight_text=insight)

        return insight
