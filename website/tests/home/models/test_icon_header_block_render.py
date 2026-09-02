from django.test import RequestFactory, TestCase, override_settings
from wagtail.models import Locale, Page, Site

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
class IconHeaderBlockRenderTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        self.home_page = Page(title="Home", slug="home-icon-header-test")
        root_page.add_child(instance=self.home_page)
        Site.objects.get_or_create(
            hostname="localhost",
            defaults={
                "root_page": self.home_page,
                "is_default_site": True,
            },
        )

    def render_page(self, page):
        self.home_page.add_child(instance=page)
        request = self.factory.get(page.url)
        request.site = Site.objects.get(is_default_site=True)
        response = page.serve(request)
        return response.render().content.decode()

    def test_icon_header_renders_on_enhanced_standard_page(self):
        page = EnhancedStandardPage(
            title="Icon Header Test Page",
            slug="icon-header-test-page",
            body=[
                {
                    "type": "icon_header",
                    "value": {
                        "icon": "fa-solid fa-file",
                        "text": "How to File",
                    },
                }
            ],
        )

        content = self.render_page(page)

        self.assertIn('class="icon-header"', content)
        self.assertIn('class="fa-solid fa-file"', content)
        self.assertIn("How to File", content)

    def test_icon_header_renders_on_petitioner_experience_page(self):
        ribbon = NavigationRibbon(name="Icon Header Test Ribbon")
        ribbon.save()
        page = PetitionerExperiencePage(
            title="Petitioner Experience Test Page",
            slug="petitioner-experience-test-page",
            introductory_text="Prepare to file",
            navigation_ribbon=ribbon,
            body=[
                {
                    "type": "icon_header",
                    "value": {
                        "icon": "fa-solid fa-check",
                        "text": "Pre-Filing Checklist",
                    },
                }
            ],
        )

        content = self.render_page(page)

        self.assertIn('class="icon-header"', content)
        self.assertIn('class="fa-solid fa-check"', content)
        self.assertIn("Pre-Filing Checklist", content)
