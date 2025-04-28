from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
from unittest.mock import patch
import json

from modules.analysis.views.analysis_analyse_view import AnalyseView, stop_scraping, continue_scraping
from modules.analysis.models import Website, Page


class AnalyseViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="pass")
        self.default_date = timezone.now().date()
        # enable client usage for non-AJAX test
        self.client.login(username="tester", password="pass")

    def _login_request(self, req):
        req.user = self.user
        return req

    def test_normalize_url(self):
        v = AnalyseView()
        # trailing slash removal, lowercasing, enforce https
        self.assertEqual(
            v.normalize_url("http://Example.COM/foo/"),
            "https://example.com/foo"
        )
        # root path default
        self.assertEqual(
            v.normalize_url("example.com"),
            "https://example.com/"
        )

    def test_delete_existing_website(self):
        site = Website.objects.create(
            start_url="https://a.com", last_visited=self.default_date
        )
        req = self.factory.post("/", {"delete_website_id": site.id})
        resp = AnalyseView.as_view()(self._login_request(req))
        self.assertIsInstance(resp, JsonResponse)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content), {"deleted": True})
        self.assertFalse(Website.objects.filter(id=site.id).exists())

    def test_delete_nonexistent_website(self):
        req = self.factory.post("/", {"delete_website_id": 999})
        resp = AnalyseView.as_view()(self._login_request(req))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(json.loads(resp.content), {"error": "Website not found"})

    def test_post_invalid_url_redirects(self):
        req = self.factory.post("/", {"url": "nota valid url"})
        resp = AnalyseView.as_view()(self._login_request(req))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("error=invalid_url", resp.url)

    def test_post_creates_new_website_and_page(self):
        url = "http://new.com/path/"
        req = self.factory.post("/", {"url": url})
        resp = AnalyseView.as_view()(self._login_request(req))
        self.assertEqual(resp.status_code, 302)
        site = Website.objects.get(start_url="https://new.com/path")
        self.assertTrue(site.crawling_in_progress)
        pages = Page.objects.filter(website=site)
        self.assertEqual(pages.count(), 1)
        self.assertEqual(pages.first().url, site.start_url)

    def test_post_reuses_existing_website_and_resets(self):
        base = "https://reuse.com/"
        site = Website.objects.create(
            start_url=base, last_visited=self.default_date, visited_count=5,
            crawling_in_progress=False, crawling_finished=True
        )
        Page.objects.create(website=site, url=base, visited=True)
        req = self.factory.post("/", {"url": base})
        resp = AnalyseView.as_view()(self._login_request(req))
        site.refresh_from_db()
        self.assertTrue(site.crawling_in_progress)
        self.assertFalse(site.crawling_finished)
        self.assertEqual(Page.objects.filter(website=site).count(), 1)
        self.assertEqual(resp.status_code, 302)

    def test_get_ajax_without_website_id(self):
        req = self.factory.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        resp = AnalyseView.as_view()(self._login_request(req))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content), {"error": "No website_id provided"})

    def test_get_ajax_with_bad_website_id(self):
        req = self.factory.get("/", {"website_id": 999}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        resp = AnalyseView.as_view()(self._login_request(req))
        self.assertEqual(json.loads(resp.content), {"error": "Website not found"})

    def test_get_ajax_with_good_website_id(self):
        site = Website.objects.create(start_url="https://x.com", last_visited=self.default_date)
        # create some pages with unique URLs
        for idx, visited in enumerate((True, False, True), start=1):
            Page.objects.create(website=site, url=f"{site.start_url}?{idx}", visited=visited)
        req = self.factory.get("/", {"website_id": site.id}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        resp = AnalyseView.as_view()(self._login_request(req))
        data = json.loads(resp.content)
        self.assertEqual(data["visited_count"], 2)
        self.assertFalse(data["crawling_finished"])
        self.assertTrue(isinstance(data["crawling_in_progress"], bool))

    def test_get_non_ajax_renders(self):
        Website.objects.create(start_url="https://y.com", last_visited=self.default_date)
        resp = self.client.get(reverse('modules.analysis:analyse'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("websites", resp.context)
        self.assertTrue(len(resp.context["websites"]) >= 1)


class ScrapingControlTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = Website.objects.create(
            start_url="https://ctrl.com", last_visited=timezone.now().date(),
            crawling_in_progress=True, scraping_stopped=False
        )

    def test_stop_scraping_success(self):
        req = self.factory.post("/", {})
        resp = stop_scraping(req, website_id=self.site.id)
        self.site.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(json.loads(resp.content)["stopped"])
        self.assertFalse(self.site.crawling_in_progress)
        self.assertTrue(self.site.scraping_stopped)

    def test_stop_scraping_already_stopped(self):
        self.site.crawling_in_progress = False
        self.site.save()
        req = self.factory.post("/", {})
        resp = stop_scraping(req, website_id=self.site.id)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content)["error"], "Invalid or already stopped")

    @patch("modules.analysis.views.analysis_analyse_view.run_one_page_spider")
    def test_continue_scraping_success(self, mock_spider):
        # mark site as stopped
        self.site.crawling_in_progress = False
        self.site.scraping_stopped = True
        self.site.save()
        req = self.factory.post("/", {})
        resp = continue_scraping(req, website_id=self.site.id)
        self.site.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(json.loads(resp.content)["continued"])
        self.assertTrue(self.site.crawling_in_progress)
        mock_spider.delay.assert_called_once_with(
            website_id=self.site.id, website_name=self.site.start_url
        )

    def test_continue_scraping_invalid(self):
        # still in progress
        self.site.crawling_in_progress = True
        self.site.save()
        req = self.factory.post("/", {})
        resp = continue_scraping(req, website_id=self.site.id)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content)["error"], "Unable to continue")
