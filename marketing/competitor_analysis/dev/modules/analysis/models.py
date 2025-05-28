from django.db import models
from django.db.models import JSONField

class Website(models.Model):
    start_url = models.URLField(max_length=500, unique=True)
    last_visited = models.DateField(auto_now_add=True)
    crawling_in_progress = models.BooleanField(default=False)
    crawling_finished = models.BooleanField(default=False)
    visited_count = models.IntegerField(default=0)
    target_audience = JSONField(null=True, blank=True)
    favicon_url = models.URLField(null=True, blank=True)
    scraping_stopped = models.BooleanField(default=False)
    positioning_insights = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.start_url

class OverallAnalysis(models.Model):
    website = models.OneToOneField(Website, on_delete=models.CASCADE, related_name="overall_analysis")

    technology = models.JSONField(null=True, blank=True)
    technology_summary = models.TextField(null=True, blank=True)
    backend_stack = models.JSONField(null=True, blank=True)
    usp = models.TextField(null=True, blank=True)
    social_media = models.TextField(null=True, blank=True)
    seo = models.TextField(null=True, blank=True)
    recommendations = models.TextField(null=True, blank=True)
    partners = models.TextField(null=True, blank=True)
    positioning_weaknesses = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.website.start_url


class Page(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='pages')
    url = models.URLField(max_length=500, unique=True)
    visited = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    page_title = models.CharField(max_length=255)
    raw_html = models.TextField(null=True, blank=True)
    last_visit = models.DateField(null=True, blank=True)
    structured_text = JSONField(default=dict)

    def __str__(self):
        return self.page_title or self.url
    
class PageAnalysis(models.Model):
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name="analysis")

    cta_analysis = models.JSONField(null=True, blank=True)
    linking_analysis = models.JSONField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    content_hash = models.CharField(max_length=42, blank=True, null=True)
    warnings = JSONField(default=dict, null=True, blank=True)
    content = JSONField(default=dict, null=True, blank=True)
    internal_links = JSONField(default=list, null=True, blank=True)
    external_links = JSONField(default=list, null=True, blank=True)
    links = JSONField(default=dict, null=True, blank=True)
    structured_data = JSONField(default=dict, null=True, blank=True)
    seo_score = models.FloatField(null=True, blank=True)
    seo_score_details = models.JSONField(null=True, blank=True)
    text_types = JSONField(default=dict, null=True, blank=True)
    positioning_classification = JSONField(default=dict, null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    text_readability = models.FloatField(null=True, blank=True)
    text_reading_time = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.description

class LoadingTime(models.Model):
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name="loading_time")

    page_speed_score = models.FloatField(null=True, blank=True)
    time_to_first_byte = models.FloatField(null=True, blank=True)
    first_contentful_paint = models.FloatField(null=True, blank=True)
    fully_loaded = models.FloatField(null=True, blank=True)
    largest_contentful_paint = models.FloatField(null=True, blank=True)

class SEORecommendation(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)

    category = models.CharField(max_length=100)
    actions = models.JSONField()
    rationale = models.TextField()


class ExtractedKeyword(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='extracted_keywords')
    
    keyword = models.CharField(max_length=100)
    score = models.FloatField()
    trend_score = models.IntegerField(null=True, blank=True)
    interest_over_time = JSONField(null=True, blank=True)
    interest_by_region = JSONField(null=True, blank=True)
    related_terms = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    trends_analyzed = models.BooleanField(default=False)

    def __str__(self):
        return self.keyword
