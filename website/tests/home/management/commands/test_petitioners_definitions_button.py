from django.test import TestCase
from wagtail.models import Locale, Page

from home.management.commands.pages.rules_and_guidance import (
    PetitionersDefinitionsButtonUpdater,
    rules_and_guidance_pages_to_initialize,
)
from home.management.commands.update_pages import pages_to_update
from home.models import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript


class TestPetitionersDefinitionsButtonUpdater(TestCase):
    def setUp(self):
        Locale.objects.get_or_create(language_code="en")
        root_page = Page.add_root(title="Root", slug="root")
        self.home_page = root_page.add_child(instance=Page(title="Home", slug="home"))
        self.pages = {}
        for slug in PetitionersDefinitionsButtonUpdater.PAGE_SLUGS:
            page = self.home_page.add_child(
                instance=PetitionerExperiencePage(
                    title=slug,
                    slug=slug,
                    show_floating_definitions_button=False,
                )
            )
            page.save_revision().publish()
            self.pages[slug] = page

    def test_registered_only_in_update_pages(self):
        self.assertIn(PetitionersDefinitionsButtonUpdater, pages_to_update)
        self.assertNotIn(
            PetitionersDefinitionsButtonUpdater,
            rules_and_guidance_pages_to_initialize,
        )

    def test_run_enables_and_publishes_all_target_pages(self):
        PetitionersDefinitionsButtonUpdater().run()

        for slug in PetitionersDefinitionsButtonUpdater.PAGE_SLUGS:
            with self.subTest(slug=slug):
                page = PetitionerExperiencePage.objects.get(slug=slug)
                self.assertTrue(page.show_floating_definitions_button)
                self.assertTrue(page.live)

        script = ExecuteScript.objects.get(
            command_name=PetitionersDefinitionsButtonUpdater.COMMAND_NAME
        )
        self.assertEqual(script.execution_status, "SUCCESS")

    def test_run_skips_without_recording_when_a_target_page_is_missing(self):
        Page.objects.get(slug="petitioners-timeline").delete()

        PetitionersDefinitionsButtonUpdater().run()

        self.assertFalse(
            ExecuteScript.objects.filter(
                command_name=PetitionersDefinitionsButtonUpdater.COMMAND_NAME
            ).exists()
        )
        for slug in PetitionersDefinitionsButtonUpdater.PAGE_SLUGS[:-1]:
            page = PetitionerExperiencePage.objects.get(slug=slug)
            self.assertFalse(page.show_floating_definitions_button)

    def test_update_does_not_create_new_revisions_when_all_buttons_are_on(self):
        for page in self.pages.values():
            page.show_floating_definitions_button = True
            page.save_revision().publish()
        revision_counts = {
            slug: Page.objects.get(slug=slug).revisions.count()
            for slug in PetitionersDefinitionsButtonUpdater.PAGE_SLUGS
        }

        PetitionersDefinitionsButtonUpdater().update()

        self.assertEqual(
            {
                slug: Page.objects.get(slug=slug).revisions.count()
                for slug in PetitionersDefinitionsButtonUpdater.PAGE_SLUGS
            },
            revision_counts,
        )
