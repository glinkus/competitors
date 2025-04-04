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