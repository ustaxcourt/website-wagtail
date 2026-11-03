from unittest import mock

from django.test import TestCase
from wagtail.models import Locale, Page, Site

from home.management.commands.pages.rules_and_guidance import (
    PetitionersHelpRulesLinkUpdater,
    rules_and_guidance_pages_to_initialize,
)
from home.management.commands.pages.rules_and_guidance.side_card_seed_data import (
    add_helpful_links_side_card,
)
from home.management.commands.update_pages import pages_to_update
from home.models import NavigationRibbon, SideCard
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript


class TestPetitionersHelpRulesLink(TestCase):
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

        self.rules_page = Page(title="Rules", slug="rules")
        home_page.add_child(instance=self.rules_page)
        home_page.add_child(
            instance=Page(title="DAWSON User Guides", slug="dawson-user-guides")
        )
        home_page.add_child(
            instance=Page(title="Training", slug="dawson-faqs-training-and-support")
        )

        ribbon = NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")
        self.help_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title="Frequently Asked Questions",
                slug="petitioners-help",
                navigation_ribbon=ribbon,
            )
        )

    def link_texts(self):
        card = SideCard.objects.get(page=self.help_page, header_title="Helpful Links")
        return [link.value["text"] for link in card.links]

    def seed_card_without_rules_link(self):
        """Mimic an environment seeded before WAG-1465."""
        self.rules_page.slug = "rules-hidden"
        self.rules_page.save()
        add_helpful_links_side_card(None, self.help_page)
        self.rules_page.slug = "rules"
        self.rules_page.save()

    def test_registered_only_in_update_pages(self):
        self.assertIn(PetitionersHelpRulesLinkUpdater, pages_to_update)
        self.assertNotIn(
            PetitionersHelpRulesLinkUpdater, rules_and_guidance_pages_to_initialize
        )

    def test_seed_puts_rules_link_under_training_video(self):
        add_helpful_links_side_card(None, self.help_page)

        self.assertEqual(
            self.link_texts(),
            [
                "DAWSON Petitioner Electronic Filing Instructions",
                "DAWSON Petitioner Training Video",
                "Tax Court Rules",
            ],
        )

    def test_run_appends_rules_link_to_existing_card_and_records_success(self):
        self.seed_card_without_rules_link()
        self.assertNotIn("Tax Court Rules", self.link_texts())

        PetitionersHelpRulesLinkUpdater().run()

        self.assertEqual(self.link_texts()[-1], "Tax Court Rules")
        card = SideCard.objects.get(page=self.help_page, header_title="Helpful Links")
        self.assertEqual(card.links[-1].value["url"][0].value.pk, self.rules_page.pk)
        script = ExecuteScript.objects.get(
            command_name=PetitionersHelpRulesLinkUpdater.COMMAND_NAME
        )
        self.assertEqual(script.execution_status, "SUCCESS")

    def test_update_does_not_duplicate_existing_rules_link(self):
        add_helpful_links_side_card(None, self.help_page)

        PetitionersHelpRulesLinkUpdater().update()

        self.assertEqual(self.link_texts().count("Tax Court Rules"), 1)

    def test_run_only_executes_once(self):
        self.seed_card_without_rules_link()
        PetitionersHelpRulesLinkUpdater().run()

        self.assertEqual(PetitionersHelpRulesLinkUpdater().run(), 0)
        self.assertEqual(
            ExecuteScript.objects.filter(
                command_name=PetitionersHelpRulesLinkUpdater.COMMAND_NAME
            ).count(),
            1,
        )

    def script_rows(self):
        return ExecuteScript.objects.filter(
            command_name=PetitionersHelpRulesLinkUpdater.COMMAND_NAME
        )

    def test_run_skips_without_recording_when_card_missing_then_retries(self):
        """A missing card is not recorded as run, so a later deploy adds the link."""
        self.assertEqual(PetitionersHelpRulesLinkUpdater().run(), 0)
        self.assertFalse(self.script_rows().exists())

        self.seed_card_without_rules_link()
        PetitionersHelpRulesLinkUpdater().run()

        self.assertEqual(self.link_texts()[-1], "Tax Court Rules")
        self.assertEqual(self.script_rows().get().execution_status, "SUCCESS")

    def test_run_skips_without_recording_when_card_renamed(self):
        self.seed_card_without_rules_link()
        SideCard.objects.filter(page=self.help_page).update(
            header_title="Helpful Resources"
        )

        self.assertEqual(PetitionersHelpRulesLinkUpdater().run(), 0)

        self.assertFalse(self.script_rows().exists())

    def test_run_records_success_log_when_link_already_present(self):
        add_helpful_links_side_card(None, self.help_page)

        PetitionersHelpRulesLinkUpdater().run()

        script = self.script_rows().get()
        self.assertEqual(script.execution_status, "SUCCESS")
        self.assertIn("already", script.execution_log)

    def test_run_rolls_back_card_when_publish_fails(self):
        """A publish failure leaves the card unchanged and records FAILURE."""
        self.seed_card_without_rules_link()
        links_before = self.link_texts()

        with mock.patch(
            "wagtail.models.Revision.publish", side_effect=RuntimeError("boom")
        ):
            with self.assertRaises(RuntimeError):
                PetitionersHelpRulesLinkUpdater().run()

        self.assertEqual(self.link_texts(), links_before)
        script = self.script_rows().get()
        self.assertEqual(script.execution_status, "FAILURE")
        self.assertIn("boom", script.execution_log)
