"""
Regression test for WAG-1259: VariableDoesNotExist when a Callout Block is
rendered inside a Card Tiles page (or any page that uses enhanced_body.html).

The bug was caused by `callout_block.html` using `block.value|default:self`,
where `self` is not in the template context when the template is rendered via
`{% include "callout_block.html" with block=block %}`.
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
class CalloutBlockRenderTest(TestCase):
    """Verify that an EnhancedStandardPage with a callout block renders without error."""

    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        # Create a home page to attach the test page to
        home_page = Page(title="Home", slug="home")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.page = EnhancedStandardPage(
            title="Callout Test Page",
            slug="callout-test-page",
            body=[
                {
                    "type": "callout",
                    "value": {
                        "heading": "QA Test",
                        "text": "<p>Testing</p>",
                        "callout_type": "info",
                    },
                }
            ],
        )
        home_page.add_child(instance=self.page)

    def test_callout_block_renders_without_variable_does_not_exist(self):
        """Page with a callout block in body must return HTTP 200."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        # Calling .render_to_response() triggers template rendering
        rendered = response.render()
        self.assertEqual(rendered.status_code, 200)

    def test_callout_block_content_appears_in_response(self):
        """Callout heading and text must appear in the rendered HTML."""
        request = self.factory.get(self.page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = self.page.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        self.assertIn("QA Test", content)
        self.assertIn("styled-callout", content)
