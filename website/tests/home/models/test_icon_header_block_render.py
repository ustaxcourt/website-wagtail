from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from wagtail.documents.models import Document
from wagtail.models import Collection, Locale, Page, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.management.commands.pages.rules_and_guidance.petitioners_prepare_to_file import (
    PetitionersPrepareToFilePageInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_guidance import (
    PetitionersGuidancePageInitializer,
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
        if Collection.get_first_root_node() is None:
            Collection.add_root(name="Root")

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
                        "icon": "file",
                        "text": "How to File",
                    },
                }
            ],
        )

        content = self.render_page(page)

        self.assertIn('class="icon-header__icon material-symbols-outlined"', content)
        self.assertIn("file", content)
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
                        "icon": "check",
                        "text": "Pre-Filing Checklist",
                    },
                }
            ],
        )

        content = self.render_page(page)

        self.assertIn('class="icon-header__icon material-symbols-outlined"', content)
        self.assertIn("check", content)
        self.assertIn("Pre-Filing Checklist", content)
        self.assertIn('<h2 class="icon-header">', content)

    def test_section_header_owns_layout_markup(self):
        page = EnhancedStandardPage(
            title="Section Header Test Page",
            slug="section-header-test-page",
            body=[
                {
                    "type": "section_header",
                    "value": {
                        "heading": "Get Started",
                        "link_text": "View detailed timeline",
                        "link_url": "https://example.com/petitioners-timeline",
                    },
                }
            ],
        )

        self.assertNotIn("get-started-row", str(page.body.raw_data))

        content = self.render_page(page)

        self.assertIn('<div class="get-started-row">', content)
        self.assertIn("<h2>Get Started</h2>", content)
        self.assertIn('href="https://example.com/petitioners-timeline"', content)
        self.assertIn("View detailed timeline", content)

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

    def test_petitioners_guidance_initializer_generates_how_to_file_cards(self):
        NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")
        document = Document.objects.create(
            collection=Collection.get_first_root_node(),
            title="How to File test document",
            file=SimpleUploadedFile(
                "how-to-file.svg",
                b'<svg xmlns="http://www.w3.org/2000/svg"></svg>',
                content_type="image/svg+xml",
            ),
        )
        with patch.object(
            PetitionersGuidancePageInitializer,
            "load_document_from_documents_dir",
            return_value=document,
        ):
            PetitionersGuidancePageInitializer().create_page_info(self.home_page)
        page = PetitionerExperiencePage.objects.get(slug="petitioners-guidance")

        how_to_file_cards = next(
            block
            for block in page.body.raw_data
            if block["type"] == "card"
            and block["value"][0]["value"]["title"] == "Electronic Filing - Recommended"
        )

        self.assertEqual(len(how_to_file_cards["value"]), 2)
        self.assertNotIn("class=", str(how_to_file_cards))

        request = self.factory.get(page.url)
        request.site = Site.objects.get(is_default_site=True)
        content = page.serve(request).render().content.decode()

        self.assertEqual(content.count('class="info-card dark-primary"'), 2)
        for expected_text in (
            "Electronic Filing - Recommended",
            "Mail Your Petition",
            "Petition Form",
            "Petition Kit",
            "NOTE FOR Petitioners who file by mail:",
        ):
            self.assertTrue(
                expected_text in content,
                f"Rendered How to File section is missing: {expected_text}",
            )

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
