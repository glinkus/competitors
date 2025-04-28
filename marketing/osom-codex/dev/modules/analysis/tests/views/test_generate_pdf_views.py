import os
from datetime import datetime, timezone as dt_tz
from django.test import TestCase, RequestFactory
from django.http import Http404
from django.conf import settings
from modules.analysis.models import Website
from modules.analysis.views.analysis_generate_pdf_view import GeneratePDFView
from unittest.mock import patch, MagicMock

class GeneratePDFViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.website = Website.objects.create(start_url='http://example.com')

    @patch('modules.analysis.views.analysis_generate_pdf_view.timezone.now')
    @patch('modules.analysis.views.analysis_generate_pdf_view.CSS')
    @patch('modules.analysis.views.analysis_generate_pdf_view.HTML')
    @patch('modules.analysis.views.analysis_generate_pdf_view.render_to_string')
    @patch('modules.analysis.views.analysis_generate_pdf_view.OverviewView')
    def test_generate_pdf_success(self, mock_ovvw_cls, mock_render, mock_HTML_cls, mock_CSS_cls, mock_now):
        # Prepare fake overview context
        fake_ctx = {
            "website": self.website,
            "meta_title": "Title",
            "meta_description": "Desc",
            "seo_score": 80,
            "keyword_summary": [],
            "target_audience": "Anyone",
            "avg_ttfb": 100,
            "avg_fcp": 200,
            "avg_lcp": 300,
            "avg_loaded": 400,
            "positioning_insights": "Insights",
            "partners": [],
            "usp": "USP",
            "seo_details": {},
            "positioning_weaknesses": [],
            "social_links": [],
            "recommendations": [],
        }
        # Stub OverviewView.get_context_data
        ovvw_inst = MagicMock()
        ovvw_inst.get_context_data.return_value = fake_ctx
        mock_ovvw_cls.return_value = ovvw_inst
        # Stub render_to_string
        mock_render.return_value = '<html>PDF</html>'
        # Stub HTML().write_pdf
        html_inst = MagicMock(); html_inst.write_pdf.return_value = b'%PDF-DUMMY%'
        mock_HTML_cls.return_value = html_inst
        # Stub CSS()
        mock_CSS_cls.return_value = object()

        # make now() deterministic
        fake_now = datetime(2025,4,28,12,0,0, tzinfo=dt_tz.utc)
        mock_now.return_value = fake_now

        # Perform request
        request = self.factory.get('/', HTTP_HOST='testserver')
        response = GeneratePDFView.as_view()(request, website_id=self.website.id)

        # Assertions on response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(f'website_overview_{self.website.id}.pdf', response['Content-Disposition'])
        self.assertEqual(response.content, b'%PDF-DUMMY%')

        # Verify OverviewView called correctly
        mock_ovvw_cls.assert_called_once_with()
        ovvw_inst.get_context_data.assert_called_once_with(website_id=self.website.id)

        # now is controlled
        mock_render.assert_called_once_with(
            'modules/analysis/overview_pdf.html',
            {
                "website_url": self.website.start_url,
                "meta_title": "Title",
                "meta_description": "Desc",
                "seo_score": 80,
                "keyword_summary": [],
                "target_audience": "Anyone",
                "avg_ttfb": 100,
                "avg_fcp": 200,
                "avg_lcp": 300,
                "avg_loaded": 400,
                "positioning_insights": "Insights",
                "partners": [],
                "usp": "USP",
                "seo_details": {},
                "positioning_weaknesses": [],
                "social_links": [],
                "recommendations": [],
                "now": fake_now
            }
        )

        # Verify HTML and CSS usage
        base_url = request.build_absolute_uri('/')
        mock_HTML_cls.assert_called_once_with(string='<html>PDF</html>', base_url=base_url)
        expected_css = os.path.join(settings.BASE_DIR, 'rarea','css','pdf.css')
        mock_CSS_cls.assert_called_once_with(filename=expected_css)

    def test_generate_pdf_not_found(self):
        # invalid ID should raise Http404
        request = self.factory.get('/', HTTP_HOST='testserver')
        with self.assertRaises(Http404):
            GeneratePDFView.as_view()(request, website_id=9999)
