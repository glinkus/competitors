import json
from datetime import datetime
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.http import JsonResponse
from modules.analysis.models import Website, OverallAnalysis, Page, PageAnalysis, ExtractedKeyword, LoadingTime
from modules.analysis.views.analysis_overview_view import website_insight_status, target_audience_status, technology_status, OverviewView
from unittest.mock import patch

class OverviewViewTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.website = Website.objects.create(start_url='http://ex.com')

    # integration test
    def test_website_insight_status_variants(self):
        req = self.rf.get('/')
        resp = website_insight_status(req, website_id=9999)
        data = json.loads(resp.content)
        self.assertEqual(data, {"ready": False})

        resp = website_insight_status(req, website_id=self.website.id)
        data = json.loads(resp.content)
        self.assertEqual(data, {"ready": False})

        tech = {'foo': 'bar'}
        OverallAnalysis.objects.create(
            website=self.website,
            technology=json.dumps(tech),
            technology_summary='sum',
            backend_stack='stk'
        )
        resp = website_insight_status(req, website_id=self.website.id)
        data = json.loads(resp.content)
        self.assertTrue(data.pop("ready"))
        self.assertEqual(data, {
            "technology": json.dumps(tech),
            "technology_summary": 'sum',
            "backend_stack": 'stk'
        })

    # integration test
    def test_target_audience_status(self):
        req = self.rf.get('/')
        resp = target_audience_status(req, website_id=self.website.id)
        self.assertEqual(json.loads(resp.content), {"ready": False})
        self.website.target_audience = 'millennials'
        self.website.save()
        resp = target_audience_status(req, website_id=self.website.id)
        self.assertEqual(json.loads(resp.content), {
            "ready": True, "audience": 'millennials'
        })

    # integration test
    def test_technology_status(self):
        req = self.rf.get('/')
        resp = technology_status(req, website_id=self.website.id)
        self.assertEqual(json.loads(resp.content), {"ready": False})

        OverallAnalysis.objects.create(website=self.website, technology='notjson')
        resp = technology_status(req, website_id=self.website.id)
        self.assertEqual(json.loads(resp.content), {"ready": False})

        OverallAnalysis.objects.filter(website=self.website).update(
            technology=json.dumps({"x": 1})
        )
        resp = technology_status(req, website_id=self.website.id)
        data = json.loads(resp.content)
        self.assertTrue(data.pop("ready"))
        self.assertEqual(data, {"technology": {"x": 1}})

    def test_utility_methods(self):
        view = OverviewView()
        self.assertEqual(view.format_time(1.5), "1min 30s")
        self.assertEqual(view.format_time(0.2), "12.0s")
        self.assertEqual(view.calculate_seo_score(12345), 0)

        p1 = Page.objects.create(website=self.website, url='a', page_title='t')
        PageAnalysis.objects.create(
            page=p1, text_reading_time=1.0, text_readability=2.0,
            seo_score=80, description='d'
        )
        p2 = Page.objects.create(website=self.website, url='b', page_title='t2')
        PageAnalysis.objects.create(
            page=p2, text_reading_time=3.0, text_readability=6.0,
            seo_score=40, description='d2'
        )
        self.assertEqual(view.calculate_seo_score(self.website.id), 60)

        LoadingTime.objects.create(
            page=p1, time_to_first_byte=0.1,
            first_contentful_paint=0.2,
            largest_contentful_paint=0.3,
            fully_loaded=0.4
        )
        lm, avg = view.get_loading_time(self.website.id)
        self.assertEqual(lm["labels"], ['a'])
        self.assertEqual(avg["avg_ttfb"], 0.0)
        stats = view.average([p1.analysis, p2.analysis])
        self.assertIn('avg_readability', stats)
        p1.analysis.text_types = {'tech':1, 'emo':2}
        p2.analysis.text_types = {'tech':3, 'emo':0}
        med = view.calculate_median_tones([p1.analysis, p2.analysis])
        self.assertEqual(med, {'tech':2.0, 'emo':1.0})

    # integration test
    def test_get_context_data_full(self):
        page = Page.objects.create(
            website=self.website,
            url=self.website.start_url,
            page_title='PT'
        )
        analysis = PageAnalysis.objects.create(
            page=page,
            text_reading_time=0.5,
            text_readability=4.5,
            seo_score=90,
            description='descr'
        )
        ExtractedKeyword.objects.create(
            page=page,
            keyword='kw',
            score=1.0,
            interest_over_time={'k':2},
            interest_by_region={'r':3},
            trend_score=5
        )
        LoadingTime.objects.create(
            page=page,
            time_to_first_byte=0.1,
            first_contentful_paint=0.2,
            largest_contentful_paint=0.3,
            fully_loaded=0.4
        )
        OverallAnalysis.objects.create(
            website=self.website,
            partners="['p1']",
            positioning_weaknesses="['pw']",
            recommendations="['r1']",
            seo="{'a':1}",
            social_media="['s1']",
            technology="{'t':1}",
            usp='UP!',
            technology_summary='tsum',
            backend_stack='bstk'
        )
        self.website.positioning_insights = 'done'
        self.website.target_audience = 'done'
        self.website.save()
        req = self.rf.get('/')
        req.user = type('u', (), {'is_authenticated': True})()
        view = OverviewView()
        view.request = req
        with patch('modules.analysis.views.analysis_overview_view.generate_website_insight') as m1, \
             patch('modules.analysis.views.analysis_overview_view.positioning_insights') as m2, \
             patch('modules.analysis.views.analysis_overview_view.generate_target_audience') as m3:
            ctx = view.get_context_data(website_id=self.website.id)
            m1.delay.assert_not_called()
            m2.delay.assert_not_called()
            m3.apply_async.assert_not_called()

        self.assertEqual(ctx['website'], self.website)
        self.assertEqual(ctx['seo_score'], 90)
        self.assertEqual(ctx['median_tones'], {})
        self.assertIn('30.0s', ctx['avg_reading_time'])
        self.assertEqual(ctx['partners'], ['p1'])
        self.assertEqual(ctx['social_links'], ['s1'])
        self.assertEqual(ctx['recommendations'], "['r1']")
        self.assertEqual(ctx['usp'], 'UP!')
        self.assertEqual(ctx['meta_title'], 'PT')
        self.assertEqual(ctx['meta_description'], 'descr')
