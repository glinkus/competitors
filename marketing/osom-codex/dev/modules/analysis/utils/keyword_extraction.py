from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from collections import defaultdict
from modules.analysis.models import Page, ExtractedKeyword
import torch

class KeywordExtraction:

    _instance = None

    IMPORTANCE_WEIGHTS = {
        'title': 15.0,
        'h1': 9.0,
        'h2': 7.0,
        'h3': 5.0,
        'h4': 2.0,
        'h5': 1.5,
        'h6': 1.0,
        'alt': 3.0,
        'p': 1.0,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KeywordExtraction, cls).__new__(cls)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            cls._instance.model = SentenceTransformer('distiluse-base-multilingual-cased', device=device)
            cls._instance.kw_extractor = KeyBERT(model=cls._instance.model)
        return cls._instance

    def extract_keywords(self, page: Page, top_n=15):
        structured_text = page.structured_text
        keyword_scores = defaultdict(float)

        for tag, text in structured_text.items():
            weight = self.IMPORTANCE_WEIGHTS.get(tag, 1.0)
            if text:
                keywords = self.kw_extractor.extract_keywords(
                    text,
                    keyphrase_ngram_range=(1, 3),
                    stop_words=None,
                    top_n=top_n
                )
                for keyword, score in keywords:
                    keyword_scores[keyword] += score * weight

        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_n]