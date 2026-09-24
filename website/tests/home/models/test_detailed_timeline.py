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
class DetailedTimelineRenderTest(TestCase):
    """Verify that an EnhancedStandardPage with a detailed timeline renders without error."""

    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-detailed-timeline-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.page = EnhancedStandardPage(
            title="Detailed Timeline Test Page",
            slug="detailed-timeline-test-page",
            body=[
                {
                    "type": "detailed_timeline",
                    "value": {
                        "title": "United States Tax Court Case Timeline",
                        "introduction": '<p data-block-key="lamyb">Please note: The timeline of every court case is different. This is a general timeline to help you<br/>understand the lifecycle of a case and should not be used for planning purposes.</p>',
                        "phases": [
                            {
                                "type": "phase",
                                "value": {
                                    "title": "Receive an IRS Notice",
                                    "date_range": "Day 0",
                                },
                                "id": "b4941d41-ab20-4e73-9ea6-66e6a22001fb",
                            },
                            {
                                "type": "phase",
                                "value": {
                                    "title": "File Your Petition",
                                    "date_range": "Day 0-Deadline",
                                },
                                "id": "36557146-a5db-462b-9955-a436cd87d486",
                            },
                            {
                                "type": "phase",
                                "value": {
                                    "title": "IRS Files Answer",
                                    "date_range": "Up To 60 Days After the Petition is Filed",
                                },
                                "id": "96ce579b-89c6-4b01-9013-e33a079314dc",
                            },
                            {
                                "type": "phase",
                                "value": {
                                    "title": "Trial Date is Scheduled",
                                    "date_range": "6-13 Months",
                                },
                                "id": "c711466a-53f8-4deb-aa63-a0edb2b05cb2",
                            },
                            {
                                "type": "phase",
                                "value": {
                                    "title": "Discovery & Discussion",
                                    "date_range": "4-12 Months",
                                },
                                "id": "90c53c79-43a6-45d7-b384-a067bc4355e3",
                            },
                            {
                                "type": "phase",
                                "value": {
                                    "title": "Trial Preparation",
                                    "date_range": "2-4 Months Before Trial",
                                },
                                "id": "92fbd6bf-b338-4993-a5e7-ddffe874c42b",
                            },
                            {
                                "type": "phase",
                                "value": {
                                    "title": "Trial",
                                    "date_range": "12-24+ Months After Filing",
                                },
                                "id": "49330a63-e33a-4028-9104-32063c7541c0",
                            },
                            {
                                "type": "phase",
                                "value": {
                                    "title": "Decision",
                                    "date_range": "6-12+ Months After Trial",
                                },
                                "id": "6c4a7579-026c-444a-ae78-41d71ce33e7a",
                            },
                        ],
                    },
                    "id": "b050e963-8231-4c33-817c-101d50838d56",
                }
            ],
        )
        home_page.add_child(instance=self.page)

    def test_detailed_timeline_renders_without_variable_does_not_exist(self):
        """Page with a detailed timeline in body must return HTTP 200."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        self.assertEqual(rendered.status_code, 200)

    def test_detailed_timeline_content_appears_in_response(self):
        """Accordion title must appear in the rendered HTML."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        self.assertIn("United States Tax Court Case Timeline", content)
        self.assertIn("Please note:", content)
        self.assertIn("Receive an IRS Notice", content)
        self.assertIn("Day 0", content)
        self.assertIn("File Your Petition", content)
        self.assertIn("Day 0-Deadline", content)
        self.assertIn("IRS Files Answer", content)
        self.assertIn("Up To 60 Days After the Petition is Filed", content)
        self.assertIn("Trial Date is Scheduled", content)
        self.assertIn("6-13 Months", content)
        self.assertIn("Discovery &amp; Discussion", content)
        self.assertIn("4-12 Months", content)
        self.assertIn("Trial Preparation", content)
        self.assertIn("2-4 Months Before Trial", content)
        self.assertIn("Trial", content)
        self.assertIn("12-24+ Months After Filing", content)
        self.assertIn("Decision", content)
        self.assertIn("6-12+ Months After Trial", content)
