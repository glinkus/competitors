from collections import defaultdict
from modules.analysis.models import Page, ExtractedKeyword
import yake
import re

class KeywordExtraction:
    _instance = None

    IMPORTANCE_WEIGHTS = {
        'title': 12.0,
        'h1': 10.0,
        'h2': 8.0,
        'h3': 5.0,
        'h4': 2.0,
        'h5': 1.5,
        'h6': 1.0,
        'alt': 3.0,
        'p': 1.0,
    }

    # List of terms or patterns you want to exclude (e.g., university names)
    DEFAULT_FILTER_PATTERNS = [r'\buniversity\b']  # using word boundaries to filter the word "university"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KeywordExtraction, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialization for YAKE does not require heavy models.
        pass

    def _filter_keyword(self, keyword, filter_patterns):
        for pattern in filter_patterns:
            if re.search(pattern, keyword, re.IGNORECASE):
                return True
        return False

    def extract_keywords(self, page: Page, top_n=15, language="en", filter_patterns=None):
        if filter_patterns is None:
            filter_patterns = self.DEFAULT_FILTER_PATTERNS

        structured_text = page.structured_text
        keyword_scores = defaultdict(float)

        # Iterate over each HTML tag and its associated text.
        for tag, text in structured_text.items():
            weight = self.IMPORTANCE_WEIGHTS.get(tag, 1.0)
            if text:
                # Initialize YAKE with additional parameters.
                kw_extractor = yake.KeywordExtractor(
                    lan=language, 
                    n=3, 
                    dedupLim=0.8,   # adjust deduplication threshold
                    dedupFunc='seqm', 
                    top=top_n
                )
                # Extract keywords from the current text block.
                keywords = kw_extractor.extract_keywords(text)
                for keyword, score in keywords:
                    # Skip the keyword if it matches any undesired patterns.
                    if self._filter_keyword(keyword, filter_patterns):
                        continue
                    # The lower the score, the more relevant the keyword.
                    # We invert the score and multiply by the tag weight.
                    keyword_scores[keyword] += weight / (score + 1e-8)

        # Sort keywords by aggregated scores in descending order.
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_n]


















# from keybert import KeyBERT
# from sentence_transformers import SentenceTransformer
# from collections import defaultdict
# from modules.analysis.models import Page, ExtractedKeyword
# import torch

# class KeywordExtraction:
#     _instance = None

#     IMPORTANCE_WEIGHTS = {
#         'title': 15.0,
#         'h1': 9.0,
#         'h2': 7.0,
#         'h3': 5.0,
#         'h4': 2.0,
#         'h5': 1.5,
#         'h6': 1.0,
#         'alt': 3.0,
#         'p': 1.0,
#     }

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(KeywordExtraction, cls).__new__(cls)
#         return cls._instance

#     def __init__(self):
#         # Initialize only if not already set
#         if not hasattr(self, "kw_extractor"):
#             device = "cuda" if torch.cuda.is_available() else "cpu"
#             self.model = SentenceTransformer('distiluse-base-multilingual-cased', device=device)
#             self.kw_extractor = KeyBERT(model=self.model)

#     def extract_keywords(self, page: Page, top_n=15):
#         structured_text = page.structured_text
#         keyword_scores = defaultdict(float)

#         for tag, text in structured_text.items():
#             weight = self.IMPORTANCE_WEIGHTS.get(tag, 1.0)
#             if text:
#                 keywords = self.kw_extractor.extract_keywords(
#                     text,
#                     keyphrase_ngram_range=(1, 3),
#                     stop_words=None,
#                     top_n=top_n
#                 )
#                 for keyword, score in keywords:
#                     keyword_scores[keyword] += score * weight

#         sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
#         return sorted_keywords[:top_n]
