from django.db import models

class ScrapedURL(models.Model):
    url = models.URLField(unique=True)
    visited = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    #parent = models.UrlField(null=True)

    def _str_(self):
        return f"{self.url} - {'Visited' if self.visited else 'To be visited'}"