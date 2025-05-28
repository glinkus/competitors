import json
import google.generativeai as genai
from dotenv import load_dotenv
from modules.analysis.models import Page, SEORecommendation, PageAnalysis
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
        self.page_analysis, created = PageAnalysis.objects.get_or_create(page=self.page)
        self.overall_metrics = overall_metrics
        self.internal_links = internal_links
        self.external_links = external_links
        self.warnings = warnings
        self.total_word_count = total_word_count
        

    def _links_prompt(self) -> str:
        prompt = f"""
        You are an SEO strategist analyzing a **competitor's webpage** to uncover link-related strengths, weaknesses, and strategic patterns. Use the data below to evaluate link quality, extract meaning from where they link to, and identify weaknesses you could exploit.

        Analyze the following areas:

        1. **Internal Linking Quality**
        - Do internal links cover a diverse set of strategic pages (e.g. product pages, conversion points, blogs)?
        - Is the internal link structure deep or shallow?
        - Are any important sections or high-value pages missing internal references?

        2. **External Linking Quality**
        - Are outbound links pointing to authoritative and industry-relevant sources?
        - Are any links potentially risky (low authority, outdated, broken)?
        - Is there an overuse of outbound linking, or lack of it (which may indicate a "closed-off" strategy)?

        3. **Anchor Text Relevance**
        - Are anchor texts meaningful and keyword-relevant?
        - Are vague or generic phrases like “read more” overused?
        - Are there signs of unnatural linking patterns?

        4. **Link Optimization Signals**
        - Are `title` attributes or descriptive `alt` texts missing?
        - Are links evenly distributed through content or bunched together?
        - Are there image or icon-based links with missing metadata?

        5. **Contextual Understanding of Links**
        - Provide a short **summary of what content the internal links lead to** (e.g. “product categories”, “case studies”, “company blog”, etc.).
        - Provide a **summary of what kinds of external sources** are linked (e.g. “documentation sites”, “competitor tools”, “news media”, etc.).
        - What can you infer about this website's **content strategy** or **authority-building tactics** based on this?

        6. **Competitive Opportunity Analysis**
        - What weaknesses in their link strategy reduce their SEO effectiveness or user experience?
        - How could you structure your own linking better to outshine this competitor?

        ---  

        **Data to analyze**:
        - Page URL: {self.page}
        - Internal Links: {self.internal_links} (List of URLs + anchor texts)
        - External Links: {self.external_links} (List of URLs + anchor texts)
        - Warnings: {self.warnings} (e.g. generic anchors, missing titles)
        - Word Count: {self.total_word_count}

        ---  

        Must return your analysis as **JSON** using the structure below:

        ```json
        {{
        "internal_linking_score": 0-100,
        "external_linking_score": 0-100,
        "anchor_text_score": 0-100,
        "overall_linking_score": 0-100,

        "internal_link_targets_summary": "Links mostly lead to blog posts and outdated case studies.",
        "external_link_targets_summary": "Links point to low-authority partners and one competitor site.",
        "linking_strategy_observation": "The website seems to favor minimal outbound linking, likely aiming to retain SEO juice but missing opportunities to build authority.",

        "linking_recommendations": [
            "Improve anchor text on internal links.",
            "Add internal links to underlinked service pages.",
            "Include outbound links to credible industry sources."
        ],

        "competitor_weaknesses": [
            "No internal links to high-converting pages like Contact or Pricing.",
            "Overuse of generic anchor text such as 'read more'.",
            "Lack of outbound links suggests missed authority-building opportunities."
        ],

        "exploitation_opportunities": [
            "Target and optimize for keywords where their anchor text is vague.",
            "Create clearer, structured navigation that links to every strategic area.",
            "Build links from third-party sites they are not leveraging."
        ]
        }}
        ```
        overall_linking_score, anchor_text_score, external_linking_score, and internal_linking_score should be between 0 and 100.
        The higher the score, the better the linking strategy. 100 means most optimal linking strategy. The lower the score, the worse the linking strategy.
        """
        return prompt

    def cta_analysis_prompt(self, ctas: dict, page_url: str, word_count: int) -> str:
        return f"""
            You are analyzing a **competitor's web page** for its **Call-To-Action (CTA)** strategy. You have been provided with structured data containing CTA links and their visible anchor text.
            Your task is to evaluate the effectiveness of the CTA usage on the page, both in terms of user engagement and conversion optimization.
            ### Data:
            - Page URL: {page_url}
            - Word count: {word_count}
            - CTAs on the page:
            {json.dumps(ctas, indent=2)}

            ### Instructions:
            1. Identify how well the CTAs are distributed across the page.
            2. Evaluate the diversity and persuasiveness of the anchor text.
            3. Determine whether the CTAs serve different funnel stages (e.g., awareness, consideration, action).
            4. Comment on the tone and specificity of the anchor phrases (e.g., “Learn more” vs. “Start your free trial”).
            5. Point out if any opportunities for stronger CTAs were missed.

            ### Output:
            Must return ONLY a **JSON** object with the following keys:

            ```json
            {{
            "cta": {{
                "https://example.com/signup": "Start your free trial",
                "https://example.com/contact": "Get in Touch"
            }},
            "cta_score": 0-100,
            "summary": "In-depth written analysis of CTA usage, structure, persuasiveness, and UX impact."
            }}
            ```
            cta_score should be a score from 0 to 100, where 100 indicates an optimal CTA strategy.
            Do not return explanations, markdown, or additional formatting.
            Only return the JSON object.
            """

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
        # Analyze the CTAs
        self.analyze_ctas()
        # Analyze the content
        self.analyze_recommendations()
        # Analyze the links
        self.analyze_links()
        # Analyze the SEO score
        self.analyze_score()
    
    def analyze_ctas(self):
        internal_links = self.page_analysis.internal_links or []
        external_links = self.page_analysis.external_links or []
        
        if isinstance(internal_links, str):
            internal_links = json.loads(internal_links)
        if isinstance(external_links, str):
            external_links = json.loads(external_links)
            
        ctas = self.extract_ctas(internal_links + external_links)

        if not ctas:
            print("❗ No CTAs found for analysis.")
            return None

        prompt = self.cta_analysis_prompt(ctas, self.page.url, self.total_word_count)
        response = self.model.generate_content(prompt)
        content = response.text.strip("```json").strip("```").strip()

        try:
            cta_data = json.loads(content)
            if not all(k in cta_data for k in ["cta", "cta_score", "summary"]):
                raise ValueError("Missing required keys in CTA response")
            self.page_analysis.cta_analysis = cta_data
            self.page_analysis.save()
            print("Successfully saved CTA analysis.")
            return cta_data
        except Exception as e:
            print("Failed to parse or save CTA analysis:", e)
            print("Raw output:", content)
            return None

    def analyze_recommendations(self):
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
            print("Failed to parse link analysis JSON:", e)
            return {}
            
        if self.page_analysis.linking_analysis != link_scores:
            self.page_analysis.linking_analysis = link_scores
            self.page_analysis.save()
            
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
        
        self.page_analysis.seo_score = score_data.get("seo_score", None)
        self.page_analysis.seo_score_details = score_data
        self.page_analysis.save()
        
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
    
    def extract_ctas(self, links):
        ctas = {}
        for link in links:
            anchor = (link.get("anchor") or "").strip()
            url = link.get("url")
            if url and anchor and len(anchor) > 2:
                ctas[url] = anchor
        return ctas


