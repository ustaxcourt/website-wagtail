from django.test import RequestFactory, TestCase, override_settings
from wagtail.models import Collection, Locale, Page, Site

from home.management.commands.pages.rules_and_guidance.petitioners_guidance import (
    PetitionersGuidancePageInitializer,
)
from home.models.pages.enhanced_standard import EnhancedStandardPage
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.snippets.navigation import NavigationRibbon


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
class HeadingWithLinkBlockRenderTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        self.home_page = Page(title="Home", slug="home-heading-with-link-test")
        root_page.add_child(instance=self.home_page)
        Site.objects.get_or_create(
            hostname="localhost",
            defaults={
                "root_page": self.home_page,
                "is_default_site": True,
            },
        )

    def serve(self, page):
        request = self.factory.get(page.url)
        request.site = Site.objects.get(is_default_site=True)
        return page.serve(request).render().content.decode()

    def test_heading_with_link_renders_wrapper_heading_and_link(self):
        """The template, not the stored value, supplies the layout class,
        and the link sits outside the heading element."""
        page = EnhancedStandardPage(
            title="Heading With Link Test Page",
            slug="heading-with-link-test-page",
            body=[
                {
                    "type": "heading_with_link",
                    "value": {
                        "text": "Get Started",
                        "level": "h3",
                        "link_text": "View detailed timeline",
                        "url": [
                            {
                                "type": "external_url",
                                "value": "https://example.com/timeline",
                            }
                        ],
                    },
                }
            ],
        )
        self.home_page.add_child(instance=page)

        content = self.serve(page)

        self.assertIn('<div class="heading-with-link">', content)
        self.assertIn("<h3>Get Started</h3>", content)
        self.assertIn(
            '(<a href="https://example.com/timeline">View detailed timeline</a>)',
            content,
        )

    def test_petitioners_guidance_initializer_uses_heading_with_link(self):
        if not Collection.objects.exists():
            Collection.add_root(name="Root")
        NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")
        PetitionersGuidancePageInitializer().create_page_info(self.home_page)
        page = PetitionerExperiencePage.objects.get(slug="petitioners-guidance")

        content = self.serve(page)

        self.assertIn('<div class="heading-with-link">', content)
        self.assertIn("<h2>Get Started</h2>", content)
        self.assertIn(">View detailed timeline</a>)", content)
        self.assertNotIn("get-started-row", content)
