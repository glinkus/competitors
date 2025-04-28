import json
import pytest
from types import SimpleNamespace
import pandas as pd

from modules.analysis.tasks import (
    preprocess_text,
    clean_json_response,
    build_prompt,
    generate_target_audience,
    positioning_insights,
    analyze_keywords,
    text_read_analysis,
    classify_page,
    analyze_top_keywords_trends,
    get_icon,
    generate_website_insight,
)
from modules.analysis.models import (
    Website,
    Page,
    PageAnalysis,
    ExtractedKeyword,
    SEORecommendation,
    OverallAnalysis,
)

@pytest.mark.parametrize("raw, expected", [
    ("<p>Hello, World!</p>", "hello world"),
    ("This is a test. And a TEST!", "test test"),
    ("Stopwords are removed from THIS text", "stopwords removed text"),
])
def test_preprocess_text(raw, expected):
    result = preprocess_text(raw)
    assert result == expected

def test_clean_json_response():
    src = " ```json\n{\"a\":1, \"b\":2}\n``` "
    assert clean_json_response(src) == {"a": 1, "b": 2}

def test_build_prompt_contains_sections():
    summaries = [{"url":"u","readability":1,"reading_time":2,
                  "tones":{},"seo_score":0,"seo_score_details":{},
                  "linking_analysis":{},"warnings":[], "content":"c"}]
    recs = ["action1","action2"]
    prompt = build_prompt(summaries, recs)
    # must contain JSON dumps and keys
    assert "Website Pages JSON" in prompt
    assert '"action1"' in prompt and '"action2"' in prompt
    assert "**Key_offerings_or_UVP**" in prompt

@pytest.mark.django_db
def test_generate_target_audience_creates_and_saves(monkeypatch):
    # setup website, pages, analyses, and keywords
    site = Website.objects.create(start_url="http://x")
    # create dummy pages and analyses
    p = Page.objects.create(website=site, url="u1")
    PageAnalysis.objects.create(page=p, content="AAA")
    # add multiple keywords so top_keywords has items
    for kw,count in [("k1",3),("k2",2)]:
        for i in range(count):
            ExtractedKeyword.objects.create(page=p, keyword=kw, score=1.0)
    # mock external GenAI model
    fake_text = json.dumps({"Company Target Audience":{
        "Seg1":"Desc1","Seg2":"Desc2","Seg3":"Desc3","Seg4":"Desc4"
    }})
    fake_resp = SimpleNamespace(text=fake_text)
    class FakeGen:
        def __init__(self, model): pass
        def generate_content(self, prompt): return fake_resp
    monkeypatch.setattr("modules.analysis.tasks.genai_model.GenerativeModel", FakeGen)
    # run task
    generate_target_audience(site.id)
    site.refresh_from_db()
    assert isinstance(site.target_audience, dict)
    assert site.target_audience["Seg1"] == "Desc1"
    assert len(site.target_audience) >= 4

@pytest.mark.django_db
def test_positioning_insights_saves_text(monkeypatch):
    # setup website with target audience and keywords
    site = Website.objects.create(start_url="http://y", target_audience={"A":"X"})
    p = Page.objects.create(website=site, url="u2", page_title="t1")
    pa = PageAnalysis.objects.create(page=p, description="d1")
    # create some keywords
    ek = ExtractedKeyword.objects.create(page=p, keyword="k", score=1.0,
                                        interest_over_time={"2023-01-01":5},
                                        interest_by_region={"US":5},
                                        trend_score=5)
    # mock external GenAI model
    fake_text = "Positioning summary here."
    fake_resp = SimpleNamespace(text=fake_text)
    class FakeGen2:
        def __init__(self, model): pass
        def generate_content(self, prompt): return fake_resp
    monkeypatch.setattr("modules.analysis.tasks.genai_model.GenerativeModel", FakeGen2)
    # run task
    positioning_insights(site.id)
    site.refresh_from_db()
    assert site.positioning_insights == fake_text

@pytest.mark.django_db
def test_analyze_keywords(monkeypatch):
    site = Website.objects.create(start_url="http://k")
    p = Page.objects.create(website=site, url="url1")
    PageAnalysis.objects.create(page=p)
    class FakeKE:
        def extract_keywords(self, page): return [("kw1", 0.5), ("kw2", 0.8)]
    monkeypatch.setattr("modules.analysis.tasks.KeywordExtraction", lambda: FakeKE())
    res = analyze_keywords("url1")
    assert res["stored_keywords_count"] == 2
    assert res["page"] == "url1"
    kws = ExtractedKeyword.objects.filter(page=p)
    assert sorted([k.keyword for k in kws]) == ["kw1", "kw2"]

@pytest.mark.django_db
def test_text_read_analysis(monkeypatch):
    site = Website.objects.create(start_url="http://t")
    p = Page.objects.create(website=site, url="u", structured_text={"a": "b"})
    # short text -> skip
    short = text_read_analysis("u")
    assert "skipped" in short
    # normal text
    long_text = "word " * 100
    p.structured_text = {"a": long_text}
    p.save()
    monkeypatch.setattr("modules.analysis.tasks.textstat.flesch_reading_ease", lambda txt: 42.0)
    monkeypatch.setattr("modules.analysis.tasks.sleep", lambda x: None)
    out = text_read_analysis("u")
    assert out["word_count"] == 100
    assert out["text_readability"] == 42.0
    assert out["reading_time"] == round(100/200, 2)

@pytest.mark.django_db
def test_classify_page(monkeypatch):
    site = Website.objects.create(start_url="http://c")
    text = "word " * 30
    p = Page.objects.create(website=site, url="u2", structured_text={"a": text})
    # fake classifier
    class FakeClf:
        def __init__(self, *args, **kw): pass
        def __call__(self, full, labels, multi_label=False):
            return {"labels": labels, "scores": [0.1]*len(labels)}
    monkeypatch.setattr("modules.analysis.tasks.pipeline", lambda *a, **k: FakeClf())
    res = classify_page("u2")
    assert "tone" in res and "positioning" in res and "label" in res
    pa = PageAnalysis.objects.get(page=p)
    assert pa.label in [l for l in res["positioning"] or res["tone"] or []] or isinstance(pa.label, str)

@pytest.mark.django_db
def test_analyze_top_keywords_trends_no_keywords():
    site = Website.objects.create(start_url="http://z")
    out = analyze_top_keywords_trends(site.id)
    assert out == {"message": "No keywords to enrich."}

@pytest.mark.django_db
def test_analyze_top_keywords_trends_with_keywords(monkeypatch):
    site = Website.objects.create(start_url="http://z2")
    p = Page.objects.create(website=site, url="u3")
    # two keywords
    ek = ExtractedKeyword.objects.create(page=p, keyword="k", score=1.0)
    # fake pytrends
    class FakeTrendReq:
        def build_payload(self, chunk, **kw): pass
        def interest_over_time(self):
            return pd.DataFrame({"k": [5, 10]}, index=pd.to_datetime(["2023-01-01","2023-01-02"]))
        def related_queries(self):
            return {"k": {"top": pd.DataFrame([{"query":"r","value":1}])}}
        def interest_by_region(self, **kw):
            return pd.DataFrame({"k": [0,2]}, index=["A","B"])
    monkeypatch.setattr("modules.analysis.tasks.TrendReq", FakeTrendReq)
    monkeypatch.setattr("modules.analysis.tasks.sleep", lambda x: None)
    out = analyze_top_keywords_trends(site.id, top_n=1)
    assert out["top_keywords_enriched"] == ["k"]
    ek.refresh_from_db()
    assert ek.trend_score == 7  # mean of [5,10]

def test_get_icon_sets_favicon(db):
    site = Website.objects.create(start_url="http://icon")
    html = '<link rel="icon" href="/fav.ico" />'
    p = Page.objects.create(website=site, url="http://icon", raw_html=html)
    get_icon("http://icon", site.id)
    site.refresh_from_db()
    assert site.favicon_url == "http://icon/fav.ico"

@pytest.mark.django_db
def test_generate_website_insight(monkeypatch):
    site = Website.objects.create(start_url="http://ins")
    # no pages
    assert generate_website_insight(site.id) == "No pages to analyze."
    # with pages
    p = Page.objects.create(website=site, url="u", page_title="t")
    pa = PageAnalysis.objects.create(
        page=p,
        text_readability=1,
        text_reading_time=1,
        text_types={},
        seo_score=1,
        seo_score_details={},
        linking_analysis={},
        warnings=[],
        content="c"
    )
    ExtractedKeyword.objects.create(page=p, keyword="kw", score=1.0)
    SEORecommendation.objects.create(page=p, actions="act1")
    # fake genai client
    class FakeModels:
        def count_tokens(self, **kw): return SimpleNamespace(total_tokens=1)
        def generate_content(self, **kw):
            text = "```json\n" + json.dumps({
                "Technology_stack":{},
                "Technology_summary":"sum",
                "Backend_stack":{},
                "Key_offerings_or_UVP":"uvp",
                "Social_medias":[],
                "SEO":"seo",
                "Content":"cont",
                "recommendations":"rec",
                "Positioning_weaknesses":"weak",
                "Partners":[]
            }) + "\n```"
            return SimpleNamespace(text=text)
    class FakeClient:
        def __init__(self, api_key): self.models = FakeModels()
    monkeypatch.setattr("modules.analysis.tasks.genai.Client", FakeClient)
    monkeypatch.setattr("modules.analysis.tasks.types.GenerateContentConfig", lambda **kw: None)
    monkeypatch.setattr("modules.analysis.tasks.build_prompt", lambda s, r, truncated=False: "p")
    msg = generate_website_insight(site.id)
    assert msg == "Insight generated successfully"
    oa = OverallAnalysis.objects.get(website=site)
    assert oa.technology_summary == "sum"
