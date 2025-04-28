from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from modules.analysis.views.analysis_compare_view import CompareView
from modules.analysis.models import (
    Website, Page, LoadingTime, PageAnalysis, ExtractedKeyword, OverallAnalysis
)

class CompareViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="u", password="p")

    def _get_response(self, query):
        req = self.factory.get('/', query)
        req.user = self.user
        return CompareView.as_view()(req)

    def test_no_ids_yields_empty_comparison(self):
        resp = self._get_response({'ids': ''})
        # no sites => comparison should be empty list
        self.assertIn('comparison', resp.context_data)
        self.assertEqual(resp.context_data['comparison'], [])

    def test_invalid_ids_ignored(self):
        resp = self._get_response({'ids': 'a,!,123x'})
        self.assertEqual(resp.context_data['comparison'], [])

    def test_full_aggregation_and_parsing(self):
        # prepare one website
        site = Website.objects.create(start_url='https://ex.com', last_visited='2025-01-01')
        # two pages with loading times
        p1 = Page.objects.create(website=site, url='u1')
        p2 = Page.objects.create(website=site, url='u2')
        LoadingTime.objects.create(page=p1, time_to_first_byte=1, first_contentful_paint=2, fully_loaded=3)
        LoadingTime.objects.create(page=p2, time_to_first_byte=3, first_contentful_paint=4, fully_loaded=5)
        # page analyses with readability/time and seo
        PageAnalysis.objects.create(page=p1, seo_score=80, text_readability=0.5, text_reading_time=1.2)
        PageAnalysis.objects.create(page=p2, seo_score=60, text_readability=0.7, text_reading_time=0.8)
        # keywords: kw1 twice, kw2 once
        ExtractedKeyword.objects.create(page=p1, keyword='kw1', score=0.9, trend_score=0.1)
        ExtractedKeyword.objects.create(page=p2, keyword='kw1', score=0.7, trend_score=0.3)
        ExtractedKeyword.objects.create(page=p1, keyword='kw2', score=1.0, trend_score=0.5)
        # overall analysis with various fields
        OverallAnalysis.objects.create(
            website=site,
            technology={'React':1,'Django':1},
            backend_stack={'Python':1},
            partners="['pA','pB']",
            social_media="{'fb':'fb.com','tw':'tw.com'}",
            usp='UniqueVal'
        )
        # call view
        resp = self._get_response({'ids': str(site.id)})
        comp = resp.context_data['comparison'][0]

        # basic site and counts
        self.assertEqual(comp['site'], site)
        self.assertEqual(comp['pages_crawled'], 2)
        # averages of loading times
        self.assertAlmostEqual(comp['avg_ttfb'], (1+3)/2)
        self.assertAlmostEqual(comp['avg_fcp'], (2+4)/2)
        self.assertAlmostEqual(comp['avg_loaded'], (3+5)/2)
        # seo score avg
        self.assertEqual(comp['seo_score'], (80+60)/2)
        # avg_readability rounded to 2 decimals, reading time formatted
        self.assertEqual(comp['avg_readability'], round((0.5+0.7)/2,2))
        self.assertIn('min', comp['avg_reading_time'])  # formats as "1min Xs" or "Xs"

        # keywords summary: first entry is kw1 with count=2
        kd = comp['keywords'][0]
        self.assertEqual(kd['keyword'], 'kw1')
        self.assertEqual(kd['count'], 2)
        self.assertAlmostEqual(kd['avg_score'], (0.9+0.7)/2)
        # tech/backend parsing
        self.assertCountEqual(comp['technology'], ['React','Django'])
        self.assertEqual(comp['backend_stack'], ['Python'])
        # partners and social media
        self.assertEqual(comp['partners'], ['pA','pB'])
        self.assertCountEqual(comp['social_media'], ['fb.com','tw.com'])
        self.assertEqual(comp['usp'], 'UniqueVal')

    def test_partners_and_social_media_error_fallthrough(self):
        # create site + overall with bad strings
        site = Website.objects.create(start_url='https://ex2.com', last_visited='2025-01-02')
        OverallAnalysis.objects.create(
            website=site,
            technology=None, backend_stack=None,
            partners="not a list", social_media="bad{}string",
            usp=None
        )
        # one dummy page & loading/pageanalysis to avoid average() crash
        p = Page.objects.create(website=site, url='u')
        LoadingTime.objects.create(page=p, time_to_first_byte=1, first_contentful_paint=1, fully_loaded=1)
        PageAnalysis.objects.create(page=p, seo_score=50, text_readability=1.0, text_reading_time=0.5)
        resp = self._get_response({'ids': str(site.id)})
        comp = resp.context_data['comparison'][0]
        # invalid partners/social -> empty list
        self.assertEqual(comp['partners'], [])
        self.assertEqual(comp['social_media'], [])
        # technology/backend default to empty
        self.assertEqual(comp['technology'], [])
        self.assertEqual(comp['backend_stack'], [])
        # usp was None
        self.assertIsNone(comp['usp'])
