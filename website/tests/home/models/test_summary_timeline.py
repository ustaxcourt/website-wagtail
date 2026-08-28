from django.test import TestCase, RequestFactory, override_settings
from wagtail.models import Locale, Page, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage


@override_settings(
    GITHUB_SHA="test1234567",
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class SummaryTimelineRenderTest(TestCase):
    """Verify that an EnhancedStandardPage with a summary timeline renders without error."""

    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-summary-timeline-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.page = EnhancedStandardPage(
            title="Summary Timeline Test Page",
            slug="summary-timeline-test-page",
            body=[
                {
                    "type": "summary_timeline",
                    "value": {
                        "title": "TYPICAL CASE TIMELINE",
                        "phases": [
                            {
                                "type": "item",
                                "value": {
                                    "title": "File Petition",
                                    "date_range": "Day 0-Deadline",
                                },
                                "id": "7186dc9c-8000-478e-8368-3f504b939fed",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "title": "IRS Answer",
                                    "date_range": "~60 days",
                                },
                                "id": "0378cb50-e6a7-40c8-949b-52277d0a6146",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "title": "Pre-Trial",
                                    "date_range": "2-12 months",
                                },
                                "id": "7d41def7-3871-4ac3-a6f0-e25c96edd1f7",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "title": "Trial",
                                    "date_range": "12-24+ months",
                                },
                                "id": "51600c9e-dd3d-4794-8a10-2d1f49c4c7b3",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "title": "Decision",
                                    "date_range": "6-12+ months",
                                },
                                "id": "5bb39ad2-5435-4e59-a201-5787dde81ef6",
                            },
                        ],
                    },
                    "id": "055229e4-ab8a-458b-a226-8783d8412579",
                }
            ],
        )
        home_page.add_child(instance=self.page)

    def test_summary_timeline_renders_without_variable_does_not_exist(self):
        """Page with a summary timeline in body must return HTTP 200."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        self.assertEqual(rendered.status_code, 200)

    def test_summary_timeline_content_appears_in_response(self):
        """Accordion title must appear in the rendered HTML."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        self.assertIn("TYPICAL CASE TIMELINE", content)
        self.assertIn("File Petition", content)
        self.assertIn("Day 0-Deadline", content)
        self.assertIn("IRS Answer", content)
        self.assertIn("~60 days", content)
        self.assertIn("Pre-Trial", content)
        self.assertIn("2-12 months", content)
        self.assertIn("Trial", content)
        self.assertIn("12-24+ months", content)
        self.assertIn("Decision", content)
        self.assertIn("6-12+ months", content)
