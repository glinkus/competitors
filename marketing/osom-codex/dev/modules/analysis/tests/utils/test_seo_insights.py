import json

import pytest
from modules.analysis.utils import seo_insights as seo_module

# Dummy classes to stub external dependencies
class DummyModel:
    def __init__(self, model_name):
        pass
    def generate_content(self, prompt):
        class Response:
            text = ''
        return Response()

class DummyPage:
    def __init__(self, url):
        self.url = url

class DummyPageAnalysis:
    def __init__(self):
        self.internal_links = None
        self.external_links = None
        self.cta_analysis = None
        self.linking_analysis = None
        self.seo_score = None
        self.seo_score_details = None
    def save(self):
        pass

@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Stub the AI model
    monkeypatch.setattr(seo_module.genai, "GenerativeModel", DummyModel)
    # Stub Page ORM manager
    class DummyQuerySet:
        def __init__(self, items):
            self._items = items
        def first(self):
            return self._items[0] if self._items else None

    class DummyPageManager:
        def filter(self, url):
            return DummyQuerySet([DummyPage(url)])
    monkeypatch.setattr(seo_module.Page, "objects", DummyPageManager())
    # Stub PageAnalysis ORM manager
    class DummyPAObjects:
        def get_or_create(self, page):
            return (DummyPageAnalysis(), True)
    monkeypatch.setattr(seo_module.PageAnalysis, "objects", DummyPAObjects())
    # Stub SEORecommendation ORM manager
    class DummyRecManager:
        def create(self, **kwargs):
            return None
    monkeypatch.setattr(seo_module.SEORecommendation, "objects", DummyRecManager())
    yield

def test_validate_recommendations_structure_valid():
    data = {k: {"actions": ["action1", "action2"]} for k in seo_module.EXPECTED_RECOMMENDATION_KEYS}
    insights = seo_module.SEOInsights("", "http://test", {}, [], [], [], 0)
    assert insights.validate_recommendations_structure(data)

def test_validate_recommendations_structure_invalid_keys():
    data = {"wrong_key": {"actions": []}}
    insights = seo_module.SEOInsights("", "http://test", {}, [], [], [], 0)
    assert not insights.validate_recommendations_structure(data)

def test_extract_ctas_filters_and_trims():
    insights = seo_module.SEOInsights("", "http://test", {}, [], [], [], 0)
    links = [
        {"url": "http://a", "anchor": "Go"},
        {"url": "http://b", "anchor": "  Start here  "},
        {"url": None,     "anchor": "Test action"},
    ]
    ctas = insights.extract_ctas(links)
    assert ctas == {"http://b": "Start here"}

def test_cta_analysis_prompt_contains_expected_keys():
    insights = seo_module.SEOInsights("", "http://test", {}, [], [], [], 0)
    prompt = insights.cta_analysis_prompt({"https://ex": "Click me"}, "https://ex-page", 42)
    assert '"cta_score"' in prompt
    assert '"summary"' in prompt

def test_links_prompt_contains_json_structure():
    insights = seo_module.SEOInsights("", "http://test", {}, [], [], [], 0)
    prompt = insights._links_prompt()
    assert "internal_linking_score" in prompt
    assert "competitor_weaknesses" in prompt

def test_seo_score_prompt_contains_keys():
    insights = seo_module.SEOInsights("", "http://test", {"a":1}, [], [], [], 100)
    prompt = insights._seo_score_prompt()
    assert '"seo_score"' in prompt
    assert "recommendations" in prompt

def test_final_recommendations_prompt_structure():
    insights = seo_module.SEOInsights("{}", "http://test", {}, [], [], [], 0)
    prompt = insights._final_recommendations_prompt()
    for key in seo_module.EXPECTED_RECOMMENDATION_KEYS:
        assert f'"{key}"' in prompt

def test_analyze_ctas_parses_and_saves(monkeypatch):
    insights = seo_module.SEOInsights("", "http://test", {}, [], [], [], 0)
    # prepare page_analysis links
    insights.page_analysis.internal_links = [{"url":"http://a","anchor":"Action"}]
    insights.page_analysis.external_links = []
    # override model response
    class Response: text = '{"cta":{"http://a":"Action"},"cta_score":50,"summary":"ok"}'
    insights.model.generate_content = lambda prompt: Response()
    result = insights.analyze_ctas()
    assert result == {"cta":{"http://a":"Action"},"cta_score":50,"summary":"ok"}
    assert insights.page_analysis.cta_analysis == result

def test_analyze_recommendations_parses_and_returns(monkeypatch):
    insights = seo_module.SEOInsights("{}", "http://test", {}, [], [], [], 0)
    data = {k:{"actions":["x"]} for k in seo_module.EXPECTED_RECOMMENDATION_KEYS}
    payload = "```json\n" + json.dumps(data) + "\n```"
    class Response: text = payload
    insights.model.generate_content = lambda prompt: Response()
    result = insights.analyze_recommendations()
    assert result == data

def test_analyze_links_parses_and_saves(monkeypatch):
    insights = seo_module.SEOInsights("", "http://test", {}, [], [], [], 0)
    sample = {"internal_linking_score":10}
    payload = "```json\n" + json.dumps(sample) + "\n```"
    class Response: text = payload
    insights.model.generate_content = lambda prompt: Response()
    result = insights.analyze_links()
    assert result == sample
    assert insights.page_analysis.linking_analysis == sample

def test_analyze_score_parses_and_saves(monkeypatch):
    insights = seo_module.SEOInsights("", "http://test", {}, [], [], [], 0)
    sample = {"seo_score":75,"foo":["bar"]}
    payload = "```json\n" + json.dumps(sample) + "\n```"
    class Response: text = payload
    insights.model.generate_content = lambda prompt: Response()
    result = insights.analyze_score()
    assert result == sample
    assert insights.page_analysis.seo_score == 75
    assert insights.page_analysis.seo_score_details == sample
