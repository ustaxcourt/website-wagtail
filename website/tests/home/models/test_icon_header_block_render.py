from django.test import RequestFactory, TestCase, override_settings
from wagtail.models import Locale, Page, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.management.commands.pages.rules_and_guidance.petitioners_prepare_to_file import (
    PetitionersPrepareToFilePageInitializer,
)
from home.models.snippets.navigation import NavigationRibbon, NavigationRibbonLink


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
        self.assertIn('<h2 class="icon-header">', content)

    def test_prepare_to_file_initializer_generates_printable_checklist(self):
        NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")
        PetitionersPrepareToFilePageInitializer().create_page_info(self.home_page)
        page = PetitionerExperiencePage.objects.get(slug="petitioners-prepare-to-file")

        request = self.factory.get(page.url)
        request.site = Site.objects.get(is_default_site=True)
        content = page.serve(request).render().content.decode()

        self.assertIn("Pre-Filing Checklist", content)
        self.assertIn("printable-section__button", content)
        self.assertIn("Have these items ready before you begin your petition.", content)
        self.assertIn("A copy of the IRS Notice (if you received one).", content)
        self.assertIn("Corporate Disclosure Statement", content)
        self.assertIn("PLEASE NOTE:", content)
        self.assertIn("Here are the electronic filing instructions", content)
        self.assertEqual(page.slug, "petitioners-prepare-to-file")

    def test_navigation_ribbon_marks_current_page(self):
        ribbon = NavigationRibbon.objects.create(name="Petitioner Experience Ribbon")
        page = PetitionerExperiencePage(
            title="Ribbon Active State Test Page",
            slug="ribbon-active-state-test-page",
            introductory_text="Prepare to file",
            navigation_ribbon=ribbon,
            body=[],
        )
        self.home_page.add_child(instance=page)
        NavigationRibbonLink.objects.create(
            navigation_ribbon=ribbon,
            title="Current Page",
            icon="fa-solid fa-file",
            url=page.url,
        )

        request = self.factory.get(page.url)
        request.site = Site.objects.get(is_default_site=True)
        content = page.serve(request).render().content.decode()

        self.assertIn('class="current-page"', content)
        self.assertIn('aria-current="page"', content)
