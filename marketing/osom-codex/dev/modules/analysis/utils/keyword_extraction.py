# from collections import defaultdict
# from modules.analysis.models import Page, ExtractedKeyword
# import yake
# import re
# import spacy

# class KeywordExtraction:
#     _instance = None

#     IMPORTANCE_WEIGHTS = {
#         'title': 13.0,
#         'h1': 10.0,
#         'h2': 8.0,
#         'h3': 5.0,
#         'h4': 2.0,
#         'h5': 1.5,
#         'h6': 1.0,
#         'alt': 3.0,
#         'p': 1.0,
#     }

#     DEFAULT_FILTER_PATTERNS = [r'\buniversity\b']

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#         return cls._instance

#     def __init__(self, language_model='en_core_web_sm'):
#         self.nlp = spacy.load(language_model)

#     def _filter_keyword(self, keyword, filter_patterns, named_entities):
#         keyword_lower = keyword.lower()

#         # Filter by regex patterns
#         for pattern in filter_patterns:
#             if re.search(pattern, keyword_lower, re.IGNORECASE):
#                 return True

#         # Filter if keyword matches any unwanted named entities
#         if keyword_lower in named_entities:
#             return True

#         return False

#     def get_named_entities(self, text):
#         doc = self.nlp(text)
#         # Adjust labels as needed (ORG: organizations, GPE: locations, PERSON: names)
#         unwanted_labels = {'ORG', 'GPE', 'PERSON'}
#         return {ent.text.lower() for ent in doc.ents if ent.label_ in unwanted_labels}

#     def extract_keywords(self, page: Page, top_n=15, language="en", filter_patterns=None):
#         if filter_patterns is None:
#             filter_patterns = self.DEFAULT_FILTER_PATTERNS

#         structured_text = page.structured_text
#         keyword_scores = defaultdict(float)

#         for tag, text in structured_text.items():
#             weight = self.IMPORTANCE_WEIGHTS.get(tag, 1.0)
#             if text:
#                 kw_extractor = yake.KeywordExtractor(
#                     lan=language,
#                     n=3,
#                     dedupLim=0.8,
#                     dedupFunc='seqm',
#                     top=top_n
#                 )
#                 keywords = kw_extractor.extract_keywords(text)

#                 named_entities = self.get_named_entities(text)

#                 for keyword, score in keywords:
#                     if self._filter_keyword(keyword, filter_patterns, named_entities):
#                         continue

#                     keyword_scores[keyword] += weight / (score + 1e-8)

#         sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
#         return sorted_keywords[:top_n]



















# from keybert import KeyBERT
# from sentence_transformers import SentenceTransformer
# from collections import defaultdict
# from modules.analysis.models import Page, ExtractedKeyword
# import torch
# import re
# import nltk
# from nltk.corpus import stopwords

# nltk.download('stopwords')

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
#         if not hasattr(self, "kw_extractor"):
#             device = "cuda" if torch.cuda.is_available() else "cpu"
#             self.model = SentenceTransformer('distiluse-base-multilingual-cased', device=device)
#             self.kw_extractor = KeyBERT(model=self.model)
#             self.stop_words = set(stopwords.words('english'))

#     def preprocess_text(self, text):
#         text = text.lower()
#         text = re.sub(r'<[^>]+>', ' ', text)
#         text = re.sub(r'[^\w\s]', ' ', text)
#         text = re.sub(r'\s+', ' ', text).strip()
#         tokens = [word for word in text.split() if word not in self.stop_words]
#         return ' '.join(tokens)

#     def extract_keywords(self, page: Page, top_n=15):
#         structured_text = page.structured_text
#         keyword_scores = defaultdict(float)

#         for tag, text in structured_text.items():
#             weight = self.IMPORTANCE_WEIGHTS.get(tag, 1.0)
#             if text:
#                 preprocessed_text = self.preprocess_text(text)
#                 if preprocessed_text:
#                     keywords = self.kw_extractor.extract_keywords(
#                         preprocessed_text,
#                         keyphrase_ngram_range=(1, 3),
#                         stop_words='english',
#                         top_n=top_n
#                     )
#                     for keyword, score in keywords:
#                         keyword_scores[keyword] += score * weight

#         sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
#         return sorted_keywords[:top_n]


from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from modules.analysis.models import Page, ExtractedKeyword
import torch
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

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
        return cls._instance

    def __init__(self):
        if not hasattr(self, "kw_extractor"):
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = SentenceTransformer('distiluse-base-multilingual-cased', device=device)
            self.kw_extractor = KeyBERT(model=self.model)
            self.stop_words = set(stopwords.words('english'))
            self.vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 3),
                max_df=1.0,
                min_df=1
            )

    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        tokens = [word for word in text.split() if word not in self.stop_words]
        return ' '.join(tokens)

    def extract_keywords_tfidf(self, documents, top_n=15):
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        feature_array = self.vectorizer.get_feature_names_out()
        keywords = []
        for doc_idx in range(tfidf_matrix.shape[0]):
            tfidf_sorting = tfidf_matrix[doc_idx].toarray().flatten().argsort()[::-1]
            top_keywords = [feature_array[i] for i in tfidf_sorting[:top_n]]
            keywords.append(top_keywords)
        return keywords

    def extract_keywords(self, page: Page, top_n=15):
        structured_text = page.structured_text
        texts = []
        tag_weights = []

        for tag, text in structured_text.items():
            if text:
                preprocessed_text = self.preprocess_text(text)
                if preprocessed_text:
                    texts.append(preprocessed_text)
                    tag_weights.append(self.IMPORTANCE_WEIGHTS.get(tag, 1.0))

        tfidf_keywords_list = self.extract_keywords_tfidf(texts, top_n=top_n)
        keyword_scores = defaultdict(float)

        for keywords, weight in zip(tfidf_keywords_list, tag_weights, strict=False):
            for rank, keyword in enumerate(keywords):
                keyword_scores[keyword] += (top_n - rank) * weight

        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_n]