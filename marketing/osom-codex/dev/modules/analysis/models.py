from django.db import models


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

    def __str__(self):
        return self.page_title or self.url


class Importance(models.TextChoices):
    TITLE = 'title', 'Title'
    H1 = 'h1', 'H1'
    H2 = 'h2', 'H2'
    H3 = 'h3', 'H3'
    H4 = 'h4', 'H4'
    H5 = 'h5', 'H5'
    H6 = 'h6', 'H6'
    ALT = 'alt', 'Alt'
    P = 'p', 'Paragraph'


IMPORTANCE_WEIGHTS = {
    Importance.TITLE: 15.0,
    Importance.H1: 9.0,
    Importance.H2: 7.0,
    Importance.H3: 5.0,
    Importance.H4: 2.0,
    Importance.H5: 1.5,
    Importance.H6: 1.0,
    Importance.ALT: 3.0,
    Importance.P: 1.0,
}


class Keyword(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='keywords')
    html_element = models.CharField(max_length=10, choices=Importance.choices)
    word = models.CharField(max_length=100)

    @property
    def importance_weight(self):
        return IMPORTANCE_WEIGHTS.get(self.html_element, 1.0)

    def __str__(self):
        return f'{self.word} ({self.html_element})'


# class ScrapedURL(models.Model):
#     url = models.URLField(unique=True)
#     visited = models.BooleanField(default=False)
#     created_at = models.DateField(auto_now_add=True)
#     #parent = models.UrlField(null=True)

#     def _str_(self):
#         return f"{self.url} - {'Visited' if self.visited else 'To be visited'}"

