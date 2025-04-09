import json
import google.generativeai as genai
from dotenv import load_dotenv
from modules.analysis.models import Page, SEORecommendation
load_dotenv()

EXPECTED_RECOMMENDATION_KEYS = {
    "entity_optimization_strategy",
    "content_strategy_across_platforms",
    "credibility_building_actions",
    "conversational_optimization",
    "cross_platform_presence_improvement",
}

class SEOInsights():
    def __init__(self, content, url, overall_metrics, internal_links, external_links, warnings, total_word_count):
        self.content = content
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.page = Page.objects.filter(url=url).first()
        self.overall_metrics = overall_metrics
        self.internal_links = internal_links
        self.external_links = external_links
        self.warnings = warnings
        self.total_word_count = total_word_count
        

    def _links_prompt(self) -> str:
        prompt = f"""
                    You are an SEO expert. Analyze the quality of links on a web page based on the information below.
                    Evaluate internal and external links, anchor text quality, and provide a score with detailed feedback.

                    Your analysis should include:

                    1. **Internal Linking**
                    - Are internal links relevant and helpful?
                    - Do they guide users to important or related pages?
                    - Is there a good distribution of internal links across the content?

                    2. **External Linking**
                    - Are external links pointing to authoritative and relevant sources?
                    - Are there any broken or suspicious external links?
                    - Are links unnecessarily pointing to competing domains?

                    3. **Anchor Text Quality**
                    - Is the anchor text descriptive and keyword-relevant?
                    - Are generic anchors like “click here” or “read more” overused?

                    4. **Link Optimization Issues**
                    - Are there missing `title` attributes on important links?
                    - Is there overlinking or underlinking?
                    - Are links placed naturally in the content flow?

                    Data to analyze:
                    - Page URL: {self.page}
                    - Internal links: {self.internal_links} (List of URL + anchor text)
                    - External links: {self.external_links} (List of URL + anchor text)
                    - Warnings: {self.warnings} (e.g. generic anchors, missing titles)
                    - Word count: {self.total_word_count}

                    Based on your analysis, return your response in **JSON** with the following format:

                    ```json
                    {{
                    "internal_linking_score": 0-100,
                    "external_linking_score": 0-100,
                    "anchor_text_score": 0-100,
                    "linking_recommendations": [
                        "Improve anchor text on internal links.",
                        "Remove broken external links.",
                        "Add links to related product pages."
                    ],
                    "overall_linking_score": 0-100
                    }}
                    """
        return prompt


    def _seo_score_prompt(self) -> str:
        prompt = f"""
                    Analyze the following website page based on SEO best practices. Consider:

                    1. Entity optimization (e.g. brand mentions, schema, topic relevance)
                    2. Content quality and structure (e.g. title, meta description, heading usage, readability)
                    3. Technical signals (e.g. image alt tags, canonical URLs, OG tags)
                    4. Trust and credibility (e.g. N-E-E-A-T-T signals, clarity, tone)
                    5. Platform presence (e.g. external links, social metadata)

                    Based on your analysis, return:
                    - An overall **SEO score (0–100)** based on these criteria
                    - Key weaknesses and strengths
                    - Specific actionable recommendations

                    Additional context:
                    SEO score should be lower if there are warnings, missing metadata, multiple H1s, etc.

                    Website Metrics:
                    {json.dumps(self.overall_metrics, indent=2)}

                    Content:
                    {json.dumps(self.content, indent=2)}

                    Respond ONLY in JSON with this structure:
                    {{
                    "seo_score": 85,
                    "strengths": [...],
                    "weaknesses": [...],
                    "recommendations": [...]
                    }}
                    """
        return prompt

    
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

                    For each category, return:
                    - A list of concrete and actionable items under the key `"actions"`.

                    Only use this format, MUST MATCH EXACTLY:
                    ```json
                    {{
                    "entity_optimization_strategy": {{
                        "actions": [...]
                    }},
                    "content_strategy_across_platforms": {{
                        "actions": [...]
                    }},
                    "credibility_building_actions": {{
                        "actions": [...]
                    }},
                    "conversational_optimization": {{
                        "actions": [...]
                    }},
                    "cross_platform_presence_improvement": {{
                        "actions": [...]
                    }}
                    }}

                    Only return your output in JSON format without any additional explanations.
                    """
        return prompt
    
    def run_analysis(self):
        # Analyze the content
        self.analyze()
        # Analyze the links
        self.analyze_links()
        # Analyze the SEO score
        self.analyze_score()

    def analyze(self):
        prompt = self._final_recommendations_prompt()
        response = self.model.generate_content(prompt)
        content = response.text

        if content.startswith("```json"):
            content = content.strip("```json").strip("```").strip()

        try:
            recommendations = json.loads(content)
        except Exception as e:
            return {
                "error": f"Failed to parse JSON: {str(e)}",
                "raw_response": content
            }

        if not self.validate_recommendations_structure(recommendations):
            print("Invalid recommendation structure. Skipping DB save.")
            return {
                "error": "Invalid structure",
                "raw_response": content
            }

        for category, data in recommendations.items():
            actions = data.get("actions")
            rationale = data.get("rationale", "")

            if actions:
                SEORecommendation.objects.create(
                    page=self.page,
                    category=category,
                    actions=actions,
                    rationale=rationale,
                )
            else:
                print(f"Skipping category '{category}' due to missing actions")

        print("Successfully did recommendations")
        return recommendations
    
    def analyze_links(self):
        prompt = self._links_prompt()
        response = self.model.generate_content(prompt)
        content = response.text.strip()

        if content.startswith("```json"):
            content = content.strip("```json").strip("```").strip()

        try:
            link_scores = json.loads(content)
        except Exception as e:
            print("❌ Failed to parse link analysis JSON:", e)
            return {}
        if self.page.linking_analysis != link_scores:
            self.page.linking_analysis = link_scores
            self.page.save()
        print("Successfully did link analysis")
        return link_scores


    def analyze_score(self):
        prompt = self._seo_score_prompt()
        response = self.model.generate_content(prompt)
        content = response.text.strip()

        if content.startswith("```json"):
            content = content.strip("```json").strip("```").strip()

        try:
            score_data = json.loads(content)
        except Exception as e:
            print("❌ Failed to parse SEO score JSON:", e)
            return {}
        
        self.page.seo_score = score_data.get("seo_score", None)
        self.page.seo_score_details = score_data
        self.page.save()
        print("Successfully did SEO score analysis")
        return score_data

    def validate_recommendations_structure(self, data: dict) -> bool:
        if not isinstance(data, dict):
            return False

        if set(data.keys()) != EXPECTED_RECOMMENDATION_KEYS:
            print(f"Unexpected keys: {set(data.keys())}")
            return False
        
        for key in EXPECTED_RECOMMENDATION_KEYS:
            category = data.get(key)
            if not isinstance(category, dict):
                print(f"Category '{key}' is not a dict.")
                return False
            if "actions" not in category:
                print(f"'actions' missing in '{key}'.")
                return False
            if not isinstance(category["actions"], list):
                print(f"'actions' in '{key}' is not a list.")
                return False
            if not all(isinstance(action, str) for action in category["actions"]):
                print(f"Not all actions in '{key}' are strings.")
                return False

        return True

