from django.test import TestCase
from wagtail.models import Locale, Page, Site

from home.management.commands.pages.rules_and_guidance import (
    DawsonHowToEfilePetition,
    DawsonHowToMergePdfs,
    DawsonTroubleshootFileUploads,
    DawsonHowToSearchForACase,
    DawsonHowToSearchForAnOrder,
    DawsonHowToSearchForAnOpinion,
    DawsonHowToUpdateContactInfo,
    DawsonHowToViewDashboard,
    rules_and_guidance_pages_to_initialize,
)
from home.management.commands.update_pages import pages_to_update
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript

# (initializer, slug, ExecuteScript command name)
DAWSON_PAGES = [
    (
        DawsonHowToEfilePetition,
        "dawson-how-to-e-file-a-petition",
        "WAG-1450: How to e-file a Petition",
    ),
    (
        DawsonHowToMergePdfs,
        "dawson-how-to-merge-pdfs",
        "WAG-1450: How to merge PDFs",
    ),
    (
        DawsonTroubleshootFileUploads,
        "dawson-troubleshoot-file-uploads",
        "WAG-1450: How to troubleshoot file upload errors",
    ),
    (
        DawsonHowToSearchForACase,
        "dawson-how-to-search-for-a-case",
        "WAG-1450: How to search for a case",
    ),
    (
        DawsonHowToSearchForAnOrder,
        "dawson-how-to-search-for-an-order",
        "WAG-1450: How to search for an order",
    ),
    (
        DawsonHowToSearchForAnOpinion,
        "dawson-how-to-search-for-an-opinion",
        "WAG-1450: How to search for an opinion",
    ),
    (
        DawsonHowToUpdateContactInfo,
        "dawson-how-to-update-contact-info",
        "WAG-1450: How to update contact information",
    ),
    (
        DawsonHowToViewDashboard,
        "dawson-how-to-view-dashboard",
        "WAG-1450: How to view the DAWSON dashboard",
    ),
]


class TestDawsonUserGuidePages(TestCase):
    def setUp(self):
        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.user_guides_page = Page(
            title="DAWSON User Guides", slug="dawson-user-guides"
        )
        home_page.add_child(instance=self.user_guides_page)

        # PetitionerExperiencePage requires a navigation ribbon.
        NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")

    def test_registered_only_in_update_pages(self):
        for initializer, _, _ in DAWSON_PAGES:
            with self.subTest(initializer=initializer.__name__):
                self.assertIn(initializer, pages_to_update)
                self.assertNotIn(initializer, rules_and_guidance_pages_to_initialize)

    def test_command_names_are_unique(self):
        command_names = [command_name for _, _, command_name in DAWSON_PAGES]
        self.assertEqual(len(command_names), len(set(command_names)))

    def test_run_creates_page_with_breadcrumb_and_records_success(self):
        for initializer, slug, command_name in DAWSON_PAGES:
            with self.subTest(initializer=initializer.__name__):
                initializer().run()

                page = PetitionerExperiencePage.objects.get(slug=slug)
                self.assertTrue(page.live)
                self.assertEqual(page.breadcrumb_page_url, self.user_guides_page.url)

                script = ExecuteScript.objects.get(command_name=command_name)
                self.assertEqual(script.execution_status, "SUCCESS")

    def test_run_raises_without_recording_when_user_guides_page_missing(self):
        self.user_guides_page.delete()

        for initializer, slug, command_name in DAWSON_PAGES:
            with self.subTest(initializer=initializer.__name__):
                with self.assertRaises(Exception):
                    initializer().run()

                # Nothing is recorded, so the next deploy retries.
                self.assertFalse(Page.objects.filter(slug=slug).exists())
                self.assertFalse(
                    ExecuteScript.objects.filter(command_name=command_name).exists()
                )

    def test_run_only_executes_once(self):
        for initializer, slug, command_name in DAWSON_PAGES:
            with self.subTest(initializer=initializer.__name__):
                initializer().run()
                Page.objects.get(slug=slug).delete()

                # Second run is skipped by ExecuteScript, so the page is not recreated.
                self.assertEqual(initializer().run(), 0)
                self.assertFalse(Page.objects.filter(slug=slug).exists())
                self.assertEqual(
                    ExecuteScript.objects.filter(command_name=command_name).count(), 1
                )
