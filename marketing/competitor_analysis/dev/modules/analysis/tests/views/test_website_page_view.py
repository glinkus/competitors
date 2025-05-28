import json
from django.test import TestCase, RequestFactory
from modules.analysis.models import Website, Page, PageAnalysis, LoadingTime, ExtractedKeyword, SEORecommendation
from modules.analysis.views.analysis_website_page_view import URLView

class URLViewTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.website = Website.objects.create(start_url='http://site.test')

    def test_format_time(self):
        view = URLView()
        self.assertEqual(view.format_time(1.25), "1min 15s")
        self.assertEqual(view.format_time(0.3), "18.0s")

    # integration test
    def test_get_context_data_full(self):
        page = Page.objects.create(
            website=self.website,
            url="http://site.test/page",
            page_title="Title"
        )
        analysis = PageAnalysis.objects.create(
            page=page,
            text_reading_time=0.5,
            text_readability=4.2,
            seo_score=77,
            description="desc",
            seo_score_details="det",
            linking_analysis="link",
            warnings="warn",
            cta_analysis="cta",
            text_types={"technical": 2, "emotional": 3},
            positioning_classification={"pos1": 5}
        )
        LoadingTime.objects.create(
            page=page,
            time_to_first_byte=0.1,
            first_contentful_paint=0.2,
            largest_contentful_paint=0.3,
            fully_loaded=0.4
        )
        ExtractedKeyword.objects.create(
            page=page,
            keyword="kw1",
            score=1.0,
            trend_score=0,
            interest_over_time={},
            interest_by_region={}
        )
        SEORecommendation.objects.create(
            page=page,
            category="cat",
            rationale="rat",
            actions="act"
        )
        req = self.rf.get('/')
        req.user = type("U", (), {"is_authenticated": True})()
        view = URLView()
        view.request = req

        ctx = view.get_context_data(website_id=self.website.id)

        self.assertEqual(ctx["website"], self.website)
        self.assertEqual(list(ctx["pages"]), [page])

        self.assertIn("Other", ctx["label_groups"])
        self.assertEqual(ctx["label_groups"]["Other"], [page])
        self.assertEqual(ctx["keywords_by_page"], {page.id: ["kw1"]})
        pages_json = json.loads(ctx["pages_json"])
        pj = pages_json[str(page.id)]
        self.assertEqual(pj["seo_score"], 77)
        self.assertEqual(pj["seo_score_details"], "det")
        self.assertEqual(pj["linking_analysis"], "link")
        self.assertEqual(pj["warnings"], "warn")
        self.assertEqual(pj["cta_analysis"], "cta")
        self.assertEqual(pj["meta_title"], "Title")
        self.assertEqual(pj["meta_description"], "desc")
        self.assertEqual(pj["text_reading_time"], "30.0s")
        self.assertEqual(pj["text_readability"], 4.2)
        self.assertListEqual(pj["tone_labels"], ["technical", "emotional"])
        self.assertListEqual(pj["tone_data"], [2, 3])
        self.assertListEqual(pj["positioning_labels"], ["pos1"])
        self.assertListEqual(pj["positioning_data"], [5])

        self.assertEqual(pj["time_to_first_byte"], 0.1)
        self.assertEqual(pj["first_contentful_paint"], 0.2)
        self.assertEqual(pj["largest_contentful_paint"], 0.3)
        self.assertEqual(pj["fully_loaded"], 0.4)

        recs = json.loads(ctx["recommendations_json"])
        rec_list = recs[str(page.id)]
        self.assertEqual(len(rec_list), 1)
        self.assertEqual(rec_list[0], {
            "category": "cat",
            "rationale": "rat",
            "actions": "act"
        })

    # integration test
    def test_get_context_data_empty(self):
        page = Page.objects.create(
            website=self.website,
            url="x",
            page_title="X"
        )
        PageAnalysis.objects.create(
            page=page,
            text_reading_time=0,
            text_readability=0,
            seo_score=0,
            description=""
        )
        req = self.rf.get('/')
        req.user = type("U", (), {"is_authenticated": True})()
        view = URLView()
        view.request = req

        ctx = view.get_context_data(website_id=self.website.id)

        self.assertIn(page, ctx["pages"])
        pj = json.loads(ctx["pages_json"])
        self.assertIn(str(page.id), pj)
        self.assertEqual(pj[str(page.id)]["meta_title"], "X")
        self.assertEqual(pj[str(page.id)]["meta_description"], "")
        self.assertEqual(ctx["keywords_by_page"], {})
        self.assertEqual(json.loads(ctx["recommendations_json"]), {})
