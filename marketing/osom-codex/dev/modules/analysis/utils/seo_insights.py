import json
import google.generativeai as genai
from dotenv import load_dotenv
from modules.analysis.models import Page, SEORecommendation
load_dotenv()

class SEO_Insights():
    def __init__(self, content, url):
        self.content = content
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.page = Page.objects.filter(url=url).first()

    def _final_recommendations_prompt(self) -> str:
        prompt = f"""
                    Based on the complete SEO analysis provided below, please generate strategic recommendations for improving the site's SEO performance. 
                    Address the following aspects:
                    1. Entity optimization strategy.
                    2. Content strategy across platforms.
                    3. Credibility building actions.
                    4. Conversational optimization.
                    5. Cross-platform presence improvement.

                    Analysis Results:
                    {json.dumps(self.content, indent=2)}

                    Only return your output in JSON format without any additional explanations.
                    """
        return prompt
    
    def _platform_evaluation_prompt(self) -> str:
        return f"""
                Evaluate this company's presence across various platforms. Focus on:
                1. Search engines (Google, Bing)
                2. Knowledge graphs (e.g., Google Knowledge Panel, Wikidata)
                3. AI platforms (ChatGPT, Bard, Gemini)
                4. Social platforms (LinkedIn, Twitter, YouTube, etc.)
                5. Industry-specific platforms or directories

                Data to analyze:
                {json.dumps(self.content, indent=2)}

                Only return your output in JSON format without any additional explanations.
                """



    def analyze(self):
        prompt = self._final_recommendations_prompt()
        response = self.model.generate_content(prompt)
        content = response.text

        if content.startswith("```json"):
            content = content.strip("```json").strip("```").strip()

        try:
            recommendations = json.loads(content)
        except Exception as e:
            recommendations = {
                "error": f"Failed to parse JSON: {str(e)}",
                "raw_response": content
            }


        # print(response)
        # print("Parsed recommendations:", json.dumps(recommendations, indent=2))
        # print("--------------------------------\n", recommendations)

        raw_data = recommendations
        for category, data in raw_data.items():
            actions = data.get("actions") or data.get("tactics") or data.get("improvement")
            rationale = data.get("rationale") or data.get("focus") or ""

            if actions:
                SEORecommendation.objects.create(
                    page=self.page,
                    category=category,
                    actions=actions,
                    rationale=rationale,
                )
            else:
                print(f"⚠️ Skipping category '{category}' due to missing actions")


        return recommendations
    
    def analyze_platform_presence(self):
        prompt = self._platform_evaluation_prompt()
        response = self.model.generate_content(prompt)
        content = response.text

        if content.startswith("```json"):
            content = content.strip("```json").strip("```").strip()

        try:
            evaluation = json.loads(content)
        except Exception as e:
            evaluation = {
                "error": f"Failed to parse JSON: {str(e)}",
                "raw_response": content
            }
        
        if isinstance(evaluation, dict):
            for key, value in evaluation.items():
                actions = value.get("actions") or value.get("tactics") or value.get("improvement")
                rationale = value.get("rationale") or value.get("focus") or ""
                if actions:
                    SEORecommendation.objects.create(
                        page=self.page,
                        category=f"platform_presence::{key}",
                        actions=actions,
                        rationale=rationale,
                    )


        return evaluation

