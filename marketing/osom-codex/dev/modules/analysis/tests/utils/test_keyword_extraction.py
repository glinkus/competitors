import pytest
from modules.analysis.utils.keyword_extraction import KeywordExtraction

@pytest.fixture(autouse=True)
def patch_models(monkeypatch):
    monkeypatch.setattr('modules.analysis.utils.keyword_extraction.SentenceTransformer', lambda *args, **kwargs: None)
    monkeypatch.setattr('modules.analysis.utils.keyword_extraction.KeyBERT', lambda *args, **kwargs: None)

def test_singleton():
    ke1 = KeywordExtraction()
    ke2 = KeywordExtraction()
    assert ke1 is ke2

def test_preprocess_text():
    ke = KeywordExtraction()
    text = "<p>Hello, WORLD! This is a test.</p>"
    cleaned = ke.preprocess_text(text)
    assert "hello" in cleaned
    assert "world" in cleaned
    assert "test" in cleaned
    assert "this" not in cleaned
    assert '<' not in cleaned and '>' not in cleaned and ',' not in cleaned

def test_extract_keywords_tfidf():
    ke = KeywordExtraction()
    docs = ["alpha beta beta", "beta gamma gamma"]
    keywords = ke.extract_keywords_tfidf(docs, top_n=2)
    assert isinstance(keywords, list) and len(keywords) == 2
    assert all(isinstance(lst, list) and len(lst) == 2 for lst in keywords)
    assert "beta" in keywords[0]
    assert "gamma" in keywords[1] or "beta" in keywords[1]

class DummyPage:
    def __init__(self, structured_text):
        self.structured_text = structured_text

def test_extract_keywords_single_tag():
    ke = KeywordExtraction()
    page = DummyPage({'title': "apple banana apple", 'p': None})
    result = ke.extract_keywords(page, top_n=2)
    assert isinstance(result, list) and len(result) == 2
    keys = [kw for kw, score in result]
    assert keys[0] == "apple"
    assert keys[1] == "banana apple"

def test_extract_keywords_empty():
    ke = KeywordExtraction()
    page = DummyPage({})
    result = ke.extract_keywords(page)
    assert result == []
