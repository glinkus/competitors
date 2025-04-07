from modules.analysis.models import Page, Website
from urllib.parse import urlsplit
from collections import Counter
import lxml.html as lh
import hashlib
import re
import trafilatura
import json
from bs4 import BeautifulSoup
import os
from nltk.corpus import stopwords
import nltk

HEADING_TAGS_XPATHS = {
    "h1": "//h1",
    "h2": "//h2",
    "h3": "//h3",
    "h4": "//h4",
    "h5": "//h5",
    "h6": "//h6",
}

ADDITIONAL_TAGS_XPATHS = {
    "title": "//title/text()",
    "meta_desc": '//meta[@name="description"]/@content',
    "viewport": '//meta[@name="viewport"]/@content',
    "charset": "//meta[@charset]/@charset",
    "canonical": '//link[@rel="canonical"]/@href',
    "alt_href": '//link[@rel="alternate"]/@href',
    "alt_hreflang": '//link[@rel="alternate"]/@hreflang',
    "og_title": '//meta[@property="og:title"]/@content',
    "og_desc": '//meta[@property="og:description"]/@content',
    "og_url": '//meta[@property="og:url"]/@content',
    "og_image": '//meta[@property="og:image"]/@content',
}
GENERIC_ANCHORS = {
    "click here", "read more", "more", "here", "this", "link", "go", "see more",
    "continue", "details", "page", "article", "info", "information", "learn more",
    "check it out", "visit", "next", "submit", "buy now", "download", "watch", "view"
}

IMAGE_EXTENSIONS = {
    ".img", ".png",".jpg",".jpeg", ".gif", ".bmp", ".svg", ".webp", ".avif"
}
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

class PageSEOAnalysis():
    def __init__(self, url):
        self.url = url
        self.page = Page.objects.filter(url=url).first()
        self.website = self.page.website
        self.base_domain = urlsplit(self.website.start_url)
        self.raw_html = self.page.raw_html
        self.parsed_url = urlsplit(url)
        self.title: str = ""
        self.author: str = ""
        self.description: str = ""
        self.hostname: str = ""
        self.sitename: str
        self.date: str
        self.keywords = {}
        self.warnings = []
        self.links = []
        self.total_word_count = 0
        self.wordcount = Counter()
        self.bigrams = Counter()
        self.trigrams = Counter()
        self.stem_to_word = {}
        self.content: str = None
        self.content_hash: str = None
        self.headings = {}
        self.additional_info = {}
        

    def analyze_headings(self):
        try:
            dom = lh.fromstring(self.raw_html)
        except ValueError as e:
            dom = lh.fromstring(self.raw_html.encode('utf-8'))
        for tag, xpath in HEADING_TAGS_XPATHS.items():
            value = [heading.text_content() for heading in dom.xpath(xpath)]
            if value:
                self.headings.update({tag: value})
    
    def analyze_additional_tags(self):
        try:
            dom = lh.fromstring(self.raw_html)
        except ValueError as _:
            dom = lh.fromstring(self.raw_html.encode('utf-8'))
        for tag, xpath in ADDITIONAL_TAGS_XPATHS.items():
            value = dom.xpath(xpath)
            if value:
                self.additional_info.update({tag: value})

    def analyze(self, raw_html=None):
        if not raw_html:
            if not self.raw_html:
                self.warnings.append("No raw HTML available for analysis.")
                return False
            raw_html = self.raw_html

        self.content_hash = hashlib.sha1(raw_html.encode("utf-8")).hexdigest()
        if self.page.content_hash == self.content_hash:
            print("No changes detected in the content.")
            return False

        metadata = trafilatura.extract_metadata(
            filecontent=raw_html,
            default_url=self.url,
            extensive=True
        )
        metadata_dict = metadata.as_dict() if metadata else {}

        def get_meta_value(key):
            value = metadata_dict.get(key)
            return "" if value is None or value == "None" else value

        self.title = get_meta_value("title")
        self.author = get_meta_value("author")
        self.description = get_meta_value("description")
        self.hostname = get_meta_value("hostname")
        self.sitename = get_meta_value("sitename")
        self.date = get_meta_value("date")
        metadata_keywords = get_meta_value("keywords")
        
        if metadata_keywords and len(metadata_keywords) > 0:
            self.warnings.append("Keywords should be avoided as they are a spam indicator and no longer used by Search Engines")

        # Extract main content as JSON.
        content = trafilatura.extract(
            raw_html,
            include_links=True,
            include_formatting=False,
            include_tables=True,
            include_images=True,
            output_format="json"
        )
        self.content = json.loads(content) if content else None

        if self.content and "text" in self.content:
            self.process_text(self.content["text"])

        # Run various analyses.
        self.validate_title()
        self.validate_description()
        self.validate_og(raw_html)
        self.analyze_a_tags(raw_html)
        self.verify_img_tags(raw_html)
        self.verify_h1_tags(raw_html)
        self.analyze_headings()
        self.analyze_additional_tags()
    
        self.save_analysis_to_db()

        return True
    
    def validate_title(self):
        length = len(self.title)

        if length == 0:
            self.warnings.append("Title is missing.")
        elif length < 10:
            self.warnings.append("Title is too short. It should be between 50 to 60 characters long")
        elif length > 70:
            self.warnings.append("Title is too long. It should between 50 to 60 characters long")


    def validate_description(self):
        length = len(self.description)

        if length == 0:
            self.warnings.append("Description is missing.")
        elif length < 70:
            self.warnings.append("Description is too short. It is less than 70 characters. It should be around 150 characters.")
        elif length > 200:
            self.warnings.append("Description is too long. It is more than 200 characters. It should be around 150 characters.")
        
    def validate_og(self, raw_html):
        html_without_comments = re.sub(r"<!--.*?-->", r"", raw_html, flags=re.DOTALL)
        soup = BeautifulSoup(html_without_comments.lower(), "html.parser")

        og_title = soup.findAll("meta", attrs={"property": "og:title"})
        og_description = soup.findAll("meta", attrs={"property": "og:description"})
        og_image = soup.findAll("meta", attrs={"property": "og:image"})

        if len(og_title) == 0:
            self.warnings.append(f"Missing og:title on page: {self.url}")

        if len(og_description) == 0:
            self.warnings.append(f"Missing og:description on page: {self.url}")

        if len(og_image) == 0:
            self.warnings.append(f"Missing og:image on page: {self.url}")

    
    def analyze_a_tags(self, raw_html):
        html_without_comments = re.sub(r"<!--.*?-->", r"", raw_html, flags=re.DOTALL)
        soap = BeautifulSoup(html_without_comments, "html.parser")

        anchors = soap.find_all("a", href=True)
        for tag in anchors:
            tag_text = tag.text.lower().strip()
            tag_href = tag["href"]

            if len(tag.get("title", "")) == 0:
                self.warnings.append(f"Anchor missing title tag: {tag_href}")

            if tag_text in GENERIC_ANCHORS:
                self.warnings.append(f"Anchor text contains generic text: '{tag_text}'")

            if self.base_domain.netloc not in tag_href and ":" in tag_href:
                continue

            url = self.normalize_url(tag_href)
            url_filename, url_file_extension = os.path.splitext(url)
            if url_file_extension in IMAGE_EXTENSIONS:
                continue

            if "#" in url:
                url = url[: url.rindex("#")]

            self.links.append(url)
            
    def normalize_url(self, url):
        if ":" in url:
            return url

        relative_path = url
        domain = self.base_domain.netloc

        if domain[-1] == "/":
            domain = domain[:-1]

        if len(relative_path) > 0 and relative_path[0] == "?":
            if "?" in self.url:
                return f'{self.url[:self.url.index("?")]}{relative_path}'

            return f"{self.url}{relative_path}"

        if len(relative_path) > 0 and relative_path[0] != "/":
            relative_path = f"/{relative_path}"

        return f"{self.base_domain.scheme}://{domain}{relative_path}"
    
    def verify_img_tags(self, raw_html):
        html_without_comments = re.sub(r"<!--.*?-->", r"", raw_html, flags=re.DOTALL)
        soup = BeautifulSoup(html_without_comments.lower(), "html.parser")
        
        images = soup.find_all("img")
        for image in images:
            src = ""
            if "src" in image:
                src = image["src"]
            elif "data-src" in image:
                src = image["data-src"]
            else:
                src = image

            if len(image.get("alt", "")) == 0:
                self.warnings.append(f"Image missing alt tag: {src}")
    
    def verify_h1_tags(self, raw_html):
        html_without_comments = re.sub(r"<!--.*?-->", r"", raw_html, flags=re.DOTALL)
        soup = BeautifulSoup(html_without_comments, "html.parser")

        h1_tags = soup.find_all("h1")
        if len(h1_tags) == 0:
            self.warnings.append("Missing h1 tag")
        elif len(h1_tags) > 1:
            self.warnings.append("Multiple h1 tags was found")

    def word_list_freq_dist(self, wordlist):
        return dict(Counter(wordlist))


    def sort_freq_dist(self, freqdist, limit=1):
        aux = [
            (freqdist[key], self.stem_to_word[key])
            for key in freqdist
            if freqdist[key] >= limit
        ]
        aux.sort()
        aux.reverse()
        return aux

    def raw_tokenize(self, rawtext):
        token_regex = re.compile(r"(?u)\b\w\w+\b")
        return token_regex.findall(rawtext.lower())

    def tokenize(self, rawtext):
        token_regex = re.compile(r"(?u)\b\w\w+\b")
        return [
            word
            for word in token_regex.findall(rawtext.lower())
            if word not in set(stopwords.words('english'))
        ]

    def getngrams(self, D, n=2):
        return zip(*[D[i:] for i in range(n)])

    def process_text(self, page_text):
        tokens = self.tokenize(page_text)
        raw_tokens = self.raw_tokenize(page_text)
        self.total_word_count = len(raw_tokens)

        bigrams = self.getngrams(raw_tokens, 2)

        for ng in bigrams:
            vt = " ".join(ng)
            self.bigrams[vt] += 1

        trigrams = self.getngrams(raw_tokens, 3)

        for ng in trigrams:
            vt = " ".join(ng)
            self.trigrams[vt] += 1

        freq_dist = self.word_list_freq_dist(tokens)

        for word in freq_dist:
            cnt = freq_dist[word]

            if word not in self.stem_to_word:
                self.stem_to_word[word] = word

            if word in self.wordcount:
                self.wordcount[word] += cnt
            else:
                self.wordcount[word] = cnt

            if word in self.keywords:
                self.keywords[word] += cnt
            else:
                self.keywords[word] = cnt

    def save_analysis_to_db(self):
        self.page.raw_html = self.raw_html
        self.page.description = self.description
        self.page.content_hash = self.content_hash

        self.page.keywords = json.dumps(self.keywords)
        self.page.warnings = json.dumps(self.warnings)
        self.page.links = json.dumps(self.links)
        
        structured_data = {
            "total_word_count": self.total_word_count,
            "wordcount": dict(self.wordcount),
            "bigrams": dict(self.bigrams),
            "trigrams": dict(self.trigrams),
            "headings": self.headings,
            "additional_info": self.additional_info,
        }
        self.page.structured_data = json.dumps(structured_data)
        
        self.page.save()
