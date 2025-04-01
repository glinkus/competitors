from django.db import models
from django.db.models import JSONField

class Website(models.Model):
    start_url = models.URLField(max_length=500, unique=True)
    last_visited = models.DateField(auto_now_add=True)
    crawling_in_progress = models.BooleanField(default=False)
    crawling_finished = models.BooleanField(default=False)
    visited_count = models.IntegerField(default=0)

    def __str__(self):
        return self.start_url



class Page(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='pages')
    url = models.URLField(max_length=500, unique=True)
    visited = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    page_title = models.CharField(max_length=255)
    last_visit = models.DateField(null=True, blank=True)
    structured_text = JSONField(default=dict)
    text_types = JSONField(default=dict)

    def __str__(self):
        return self.page_title or self.url


class ExtractedKeyword(models.Model):
    keyword = models.CharField(max_length=100)
    score = models.FloatField()
    trend_score = models.IntegerField(null=True, blank=True)
    interest_over_time = JSONField(null=True, blank=True)
    interest_by_region = JSONField(null=True, blank=True)
    related_terms = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='extracted_keywords')

    def __str__(self):
        return self.keyword

class KeywordInsight(models.Model):
    website = models.OneToOneField(Website, on_delete=models.CASCADE, related_name="insight")
    insight_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insight for {self.website.start_url}"



