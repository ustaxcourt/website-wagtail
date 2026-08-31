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
class HeroSectionRenderTest(TestCase):
    """Verify that an EnhancedStandardPage with a hero section renders without error."""

    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-hero-section-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.page = EnhancedStandardPage(
            title="Hero Section Test Page",
            slug="hero-section-test-page",
            body=[
                {
                    "type": "hero_section",
                    "value": {
                        "title": "File Your Petition with the United States Tax Court",
                        "introductory_text": "Challenge an IRS determination by filing a petition. This guide walks you through every step of the process, including what to expect after filing in the United States Tax Court.",
                        "callout_block": {
                            "heading": "Deadline for Filing",
                            "text": "<p>A document filed through DAWSON is timely if it is electronically filed by 11:59 p.m., Eastern time, on the day it is due.</p>",
                            "callout_type": "info",
                        },
                        "buttons": [
                            {
                                "type": "button",
                                "value": {
                                    "icon": None,
                                    "icon_location": "before",
                                    "text": "View Pre-Filing Checklist",
                                    "url": [
                                        {
                                            "type": "external_url",
                                            "value": "https://app.dawson.ustaxcourt.gov/login",
                                            "id": "c42bbb8d-7d14-438d-932f-34070579e21d",
                                        }
                                    ],
                                    "style": "inverted-primary",
                                    "button_hover": True,
                                },
                                "id": "fa0c132b-750d-4fbd-beec-b8fb30cbb8da",
                            },
                            {
                                "type": "button",
                                "value": {
                                    "icon": None,
                                    "icon_location": "after",
                                    "text": "File a Petition Online",
                                    "url": [
                                        {
                                            "type": "external_url",
                                            "value": "https://app.dawson.ustaxcourt.gov/login",
                                            "id": "3be11592-3f5f-4385-8429-66fcb19733fe",
                                        }
                                    ],
                                    "style": "primary",
                                    "button_hover": True,
                                },
                                "id": "8172c98a-29c9-4bd8-afcb-81136cee0238",
                            },
                        ],
                    },
                    "id": "101bd86b-439e-4370-8f0b-87375e583b39",
                }
            ],
        )
        home_page.add_child(instance=self.page)

    def test_hero_section_renders_without_variable_does_not_exist(self):
        """Page with a hero section in body must return HTTP 200."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        self.assertEqual(rendered.status_code, 200)

    def test_hero_section_content_appears_in_response(self):
        """Accordion title must appear in the rendered HTML."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        self.assertIn("File Your Petition with the United States Tax Court", content)
        self.assertIn(
            "Challenge an IRS determination by filing a petition. This guide walks you through every step of the process, including what to expect after filing in the United States Tax Court.",
            content,
        )
        self.assertIn("Deadline for Filing", content)
        self.assertIn(
            "A document filed through DAWSON is timely if it is electronically filed by 11:59 p.m., Eastern time, on the day it is due.",
            content,
        )
        self.assertIn("View Pre-Filing Checklist", content)
        self.assertIn("File a Petition Online", content)
