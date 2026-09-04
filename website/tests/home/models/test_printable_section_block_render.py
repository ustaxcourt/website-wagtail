"""
Regression tests for the printable_section block, covering both top-level
rendering and rendering inside a Card Tiles default_content (which passes
its own `suffix` into enhanced_body.html and must not collide with a
top-level block's generated element ID).
"""

from django.test import TestCase, RequestFactory, override_settings
from wagtail.models import Locale, Page, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage

PRINTABLE_SECTION_BODY = [
    {
        "type": "heading",
        "value": {"text": "Section Heading", "level": "h3", "id": ""},
    },
    {
        "type": "list",
        "value": {
            "list_type": "unordered",
            "items": [{"text": "<p>List item one</p>"}],
        },
    },
    {
        "type": "paragraph",
        "value": "<p>Printable paragraph content</p>",
    },
]


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
class PrintableSectionBlockRenderTest(TestCase):
    """Verify that an EnhancedStandardPage with a printable_section block renders without error."""

    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-printable-section-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.page = EnhancedStandardPage(
            title="Printable Section Test Page",
            slug="printable-section-test-page",
            body=[
                {
                    "type": "printable_section",
                    "value": {
                        "title": "Test Printable Section",
                        "intro": "<p>Intro text</p>",
                        "body": PRINTABLE_SECTION_BODY,
                    },
                }
            ],
        )
        home_page.add_child(instance=self.page)

    def test_printable_section_block_renders_without_error(self):
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        self.assertEqual(rendered.status_code, 200)

    def test_printable_section_block_content_appears_in_response(self):
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        self.assertIn("Test Printable Section", content)
        self.assertIn("Section Heading", content)
        self.assertIn("List item one", content)
        self.assertIn("Printable paragraph content", content)
        self.assertIn('id="printable-section-0-prt"', content)
        # The paragraph body child must not be wrapped in a <p>, since the
        # RichTextBlock value already renders its own block-level markup.
        self.assertNotIn(
            "<p><p>Printable paragraph content</p></p>",
            content,
        )


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
class PrintableSectionInCardTilesDefaultContentRenderTest(TestCase):
    """
    Verify a printable_section inside Card Tiles default_content renders with
    an ID distinct from a top-level printable_section at the same block_index,
    so both blocks' Print buttons initialize correctly.
    """

    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-ct-printable-section-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.page = EnhancedStandardPage(
            title="Card Tiles Printable Section Test Page",
            slug="card-tiles-printable-section-test-page",
            body=[
                {
                    "type": "printable_section",
                    "value": {
                        "title": "Top Level Printable Section",
                        "intro": "",
                        "body": PRINTABLE_SECTION_BODY,
                    },
                },
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
                                "type": "printable_section",
                                "value": {
                                    "title": "Default Content Printable Section",
                                    "intro": "",
                                    "body": PRINTABLE_SECTION_BODY,
                                },
                            }
                        ],
                    },
                },
            ],
        )
        home_page.add_child(instance=self.page)

    def test_printable_section_in_card_tiles_default_content_renders_without_error(
        self,
    ):
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        self.assertEqual(rendered.status_code, 200)

    def test_printable_section_ids_do_not_collide(self):
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        self.assertIn("Top Level Printable Section", content)
        self.assertIn("Default Content Printable Section", content)
        # Both blocks are index 0 within their own loop, so without a
        # distinct suffix they would generate the same element ID.
        self.assertIn('id="printable-section-0-prt"', content)
        self.assertIn('id="printable-section-0-default-content"', content)
