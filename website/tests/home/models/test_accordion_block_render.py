"""
Regression test for WAG-1259: VariableDoesNotExist when an Accordion Block is
rendered inside a Card Tiles default content (or any page that uses enhanced_body.html
called with the `only` keyword).

The bug was caused by `accordion_block.html` using `block.value|default:self`,
where `self` is not in the template context when the template is rendered via
`{% include "accordion_block.html" with block=block ... %}`.
"""

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
class AccordionBlockRenderTest(TestCase):
    """Verify that an EnhancedStandardPage with an accordion block renders without error."""

    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-accordion-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.page = EnhancedStandardPage(
            title="Accordion Test Page",
            slug="accordion-test-page",
            body=[
                {
                    "type": "accordion",
                    "value": {
                        "title": "Test Accordion",
                        "description": [
                            {
                                "type": "prose",
                                "value": "<p>Accordion body content</p>",
                            }
                        ],
                        "default_to_open": False,
                    },
                }
            ],
        )
        home_page.add_child(instance=self.page)

    def test_accordion_block_renders_without_variable_does_not_exist(self):
        """Page with an accordion block in body must return HTTP 200."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        self.assertEqual(rendered.status_code, 200)

    def test_accordion_block_content_appears_in_response(self):
        """Accordion title must appear in the rendered HTML."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        self.assertIn("Test Accordion", content)
        self.assertIn("accordion-block", content)


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
class AccordionBlockInCardTilesDefaultContentRenderTest(TestCase):
    """
    Verify that an accordion block inside a Card Tiles default_content renders
    without VariableDoesNotExist. This is the exact scenario reported in WAG-1259.
    """

    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-ct-accordion-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.page = EnhancedStandardPage(
            title="Card Tiles Accordion Test Page",
            slug="card-tiles-accordion-test-page",
            body=[
                {
                    "type": "card_tiles",
                    "value": {
                        "tiles": [
                            {
                                "icon": 1,
                                "icon_direction": "top",
                                "card_header": "Test Card",
                                "link": [
                                    {
                                        "type": "external_url",
                                        "value": "https://example.com",
                                    }
                                ],
                                "card_hover": True,
                            }
                        ],
                        "default_content": [
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "Default Content Accordion",
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": "<p>Inside accordion</p>",
                                        }
                                    ],
                                    "default_to_open": False,
                                },
                            }
                        ],
                    },
                }
            ],
        )
        home_page.add_child(instance=self.page)

    def test_accordion_in_card_tiles_default_content_renders_without_error(self):
        """Page with an accordion in card tiles default_content must return HTTP 200."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        self.assertEqual(rendered.status_code, 200)

    def test_accordion_in_card_tiles_content_appears_in_response(self):
        """Accordion title must appear in the rendered HTML."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        self.assertIn("Default Content Accordion", content)
