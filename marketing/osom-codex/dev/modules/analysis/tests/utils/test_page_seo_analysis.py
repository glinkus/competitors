import pytest
import json
import re
from modules.analysis.utils import page_seo_analysis

class DummyWebsite:
    def __init__(self, start_url):
        self.start_url = start_url

class DummyPage:
    def __init__(self, url, raw_html, start_url):
        self.url = url
        self.raw_html = raw_html
        self.website = DummyWebsite(start_url)
    def save(self): pass

class FakePageQS:
    def __init__(self, page): self.page = page
    def filter(self, **kwargs): return self
    def first(self): return self.page

class DummyPageAnalysis:
    def __init__(self, page):
        self.page = page
        self.description = None
        self.content_hash = None
        self.warnings = None
        self.links = None
        self.content = None
        self.internal_links = None
        self.external_links = None
        self.structured_data = None
    def save(self): pass

class DummyPageAnalysisManager:
    def get_or_create(self, page): return (DummyPageAnalysis(page), True)

@pytest.fixture(autouse=True)
def patch_models(monkeypatch):
    monkeypatch.setattr(page_seo_analysis, 'Page', DummyPage)
    monkeypatch.setattr(page_seo_analysis, 'PageAnalysis', DummyPageAnalysis)
    monkeypatch.setattr(page_seo_analysis.PageAnalysis, 'objects', DummyPageAnalysisManager(), raising=False)

def make_analyzer(monkeypatch, html, url="http://example.com/path"):
    dummy = DummyPage(url, html, "http://example.com")
    monkeypatch.setattr(page_seo_analysis.Page, 'objects', FakePageQS(dummy), raising=False)
    return page_seo_analysis.PageSEOAnalysis(url)

def test_validate_title_variations(monkeypatch):
    a = make_analyzer(monkeypatch, "<html></html>")
    a.warnings = []
    a.title = ""
    a.validate_title()
    assert "Title is missing." in a.warnings
    a.warnings.clear(); a.title = "short"
    a.validate_title()
    assert any("too short" in w for w in a.warnings)
    a.warnings.clear(); a.title = "x" * 80
    a.validate_title()
    assert any("too long" in w for w in a.warnings)

def test_validate_description_variations(monkeypatch):
    a = make_analyzer(monkeypatch, "<html></html>")
    a.warnings = []
    a.description = ""
    a.validate_description()
    assert "Description is missing." in a.warnings
    a.warnings.clear(); a.description = "a" * 20
    a.validate_description()
    assert any("too short" in w for w in a.warnings)
    a.warnings.clear(); a.description = "a" * 300
    a.validate_description()
    assert any("too long" in w for w in a.warnings)

def test_validate_og_missing(monkeypatch):
    html = "<html><head><!-- no og --></head></html>"
    a = make_analyzer(monkeypatch, html, url="http://site")
    a.warnings = []
    a.validate_og(html)
    assert any("Missing og:title" in w for w in a.warnings)
    assert any("Missing og:description" in w for w in a.warnings)
    assert any("Missing og:image" in w for w in a.warnings)

def test_analyze_headings_and_additional(monkeypatch):
    html = """
    <html><head>
      <title>My Title</title>
      <meta name="description" content="desc">
    </head><body>
      <h1>H1</h1><h2>H2a</h2><h2>H2b</h2>
    </body></html>
    """
    a = make_analyzer(monkeypatch, html)
    a.headings = {}; a.additional_info = {}
    a.analyze_headings(); a.analyze_additional_tags()
    assert a.headings["h1"] == ["H1"]
    assert set(a.headings["h2"]) == {"H2a", "H2b"}
    assert a.additional_info["title"] == ["My Title"]
    assert a.additional_info["meta_desc"] == ["desc"]

def test_analyze_a_tags_and_links(monkeypatch):
    html = """
    <html><body>
      <a href="/foo"         >foo</a>
      <a href="/bar" title="" >read more</a>
      <a href="http://ex.com/img.png">img.png link</a>
      <a href="http://external.com">external</a>
    </body></html>
    """
    a = make_analyzer(monkeypatch, html)
    a.warnings = []; a.links = []
    a.analyze_a_tags(html)
    assert any("Anchor missing title" in w for w in a.warnings)
    assert any("generic text" in w for w in a.warnings)
    assert all(not l.endswith("img.png") for l in a.links)
    assert any(e["url"].startswith("http://external.com") for e in a.external_links)
    assert any(i["url"].endswith("/foo") for i in a.internal_links)

def test_normalize_url_cases(monkeypatch):
    a = make_analyzer(monkeypatch, "")
    assert a.normalize_url("http://x.com") == "http://x.com"
    a.url = "http://ex.com/page?x=1"
    assert a.normalize_url("?y=2") == "http://ex.com/page?y=2"

def test_verify_img_tags(monkeypatch):
    html = '<html><body><img src="a.jpg"><img data-src="b.png" alt="ok"></body></html>'
    a = make_analyzer(monkeypatch, html)
    a.warnings = []
    a.verify_img_tags(html)
    assert any("missing alt tag: a.jpg" in w for w in a.warnings)

def test_verify_h1_tags(monkeypatch):
    a = make_analyzer(monkeypatch, "<html><body></body></html>")
    a.warnings = []; a.verify_h1_tags("")
    assert "Missing h1 tag" in a.warnings
    a = make_analyzer(monkeypatch, "<h1>one</h1><h1>two</h1>")
    a.warnings = []; a.verify_h1_tags("")
    assert "Multiple h1 tags was found" in a.warnings

def test_process_text_counts(monkeypatch):
    a = make_analyzer(monkeypatch, "")
    text = "Hello world world"
    a.process_text(text)
    assert a.total_word_count == 3
    assert a.wordcount["world"] == 2
    assert ("hello world") in a.bigrams

def test_full_analyze_short_circuit(monkeypatch):
    a = make_analyzer(monkeypatch, "")
    a.page.raw_html = ""
    a.raw_html = ""
    res = a.analyze()
    assert res is False
