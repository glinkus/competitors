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

    def __str__(self):
        return self.page_title or self.url


class ExtractedKeyword(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='extracted_keywords')
    keyword = models.CharField(max_length=100)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.keyword


