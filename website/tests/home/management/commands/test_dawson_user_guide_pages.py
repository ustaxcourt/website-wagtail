from django.test import TestCase
from django.template.loader import render_to_string
from taggit.models import Tag
from wagtail.models import Collection, Locale, Page, Site
from wagtail.images import get_image_model

from home.management.commands.pages.rules_and_guidance import (
    DawsonHowToEfilePetition,
    DawsonHowToPayFilingFee,
    DawsonTroubleshootFileUploads,
    DawsonHowToSearchForACase,
    DawsonHowToSearchForAnOrder,
    DawsonHowToSearchForAnOpinion,
    DawsonHowToUpdateContactInfo,
    DawsonHowToViewDashboard,
    rules_and_guidance_pages_to_initialize,
)
from home.management.commands.pages.rules_and_guidance.dawson_how_to_search_for_an_opinion import (
    IMAGE_ALT,
    IMAGE_TITLE,
    CONTENT_SCRIPT_NAME,
)
from home.management.commands.update_pages import pages_to_update
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript
from home.utils.document_collection_and_tag_assignment import get_tags_for_document
from search.dawson_client import get_environment_specific_dawson_url

# (initializer, slug, ExecuteScript command name)
DAWSON_PAGES = [
    (
        DawsonHowToEfilePetition,
        "dawson-how-to-e-file-a-petition",
        "WAG-1450: Populate e-file Petition guide timeline and instructions",
    ),
    (
        DawsonHowToPayFilingFee,
        "dawson-how-to-pay-filing-fee",
        "WAG-1450: How to pay the filing fee",
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
        "WAG-1446: Populate How to search for an opinion user guide",
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
        if not Collection.objects.exists():
            Collection.add_root(name="Root")

        if Collection.get_first_root_node() is None:
            Collection.add_root(name="Root")
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

        # Most DAWSON pages attach this navigation ribbon.
        NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")
        for filename in DawsonHowToEfilePetition.DOCUMENT_FILENAMES.values():
            for tag_name in get_tags_for_document(filename):
                Tag.objects.get_or_create(name=tag_name)

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
                self.assertEqual(
                    page.breadcrumb_title,
                    "DAWSON User Guides & Electronic Filing Instructions",
                )
                self.assertTrue(page.show_floating_definitions_button)

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

    def test_opinion_guide_has_its_timeline_and_controls(self):
        DawsonHowToSearchForAnOpinion().run()

        page = PetitionerExperiencePage.objects.get(
            slug="dawson-how-to-search-for-an-opinion"
        )
        timeline = page.body[0]
        self.assertEqual(timeline.block_type, "detailed_timeline")
        self.assertEqual(timeline.value["print_button_text"], "Print")
        self.assertFalse(timeline.value["show_title"])
        self.assertEqual(
            [phase.value["title"] for phase in timeline.value["phases"]],
            [
                "Access Opinion Search",
                "Search by Keyword, Phrase, Judge, Date, or Opinion Type",
                "Search by Docket Number or Case Title/Petitioner Name",
                "Review Search Results",
                "Tips and Tricks",
            ],
        )
        self.assertEqual(
            [phase.value["bubble_content"] for phase in timeline.value["phases"]],
            ["number", "number", "number", "number", "info"],
        )

        html = render_to_string(
            "detailed_timeline.html", {"block": timeline, "page": page}
        )
        self.assertIn("Expand All", html)
        self.assertIn("Print", html)
        self.assertIn(
            f'href="{get_environment_specific_dawson_url()}/todays-opinions"',
            html,
        )
        self.assertIn(
            f'href="{get_environment_specific_dawson_url()}"',
            html,
        )
        self.assertIn(
            "written determination of a judge on the issues tried and submitted "
            "to the Court for decision",
            html,
        )
        self.assertIn("Premium Tax Credit", html)
        self.assertIn("OR ( | )", html)
        self.assertIn("AND ( + )", html)
        self.assertIn("5,000 matches", html)
        self.assertIn("Search by Judge, Date or Opinion Type", html)
        self.assertIn("To search opinions by docket number:", html)
        self.assertIn("To search opinions by case title or petitioner name:", html)
        self.assertNotIn("<strong>NOT</strong>", html)
        self.assertTrue(get_image_model().objects.filter(title=IMAGE_TITLE).exists())

        phases = {
            phase["value"]["title"]: phase["value"]["instructions"]
            for phase in page.body.get_prep_value()[0]["value"]["phases"]
        }
        image_marker = f'alt="{IMAGE_ALT}"'
        # Only the one available screenshot is placed, under Review Search Results.
        self.assertEqual(
            [phases[title].count(image_marker) for title in phases],
            [0, 0, 0, 1, 0],
        )

        # The image closes out Review Search Results, after both paragraphs.
        review = phases["Review Search Results"]
        self.assertLess(review.index("next 100 results."), review.index(image_marker))
        self.assertFalse(page.resource_cards)

    def test_existing_guide_content_update_matches_expanded_design(self):
        DawsonHowToSearchForAnOpinion().run()

        page = PetitionerExperiencePage.objects.get(
            slug="dawson-how-to-search-for-an-opinion"
        )
        body = page.body.get_prep_value()
        timeline = body[0]["value"]
        timeline["introduction"] = "<p>Outdated introduction.</p>"
        timeline["phases"][1]["value"]["title"] = "Outdated search phase"
        page.body = body
        page.save_revision().publish()
        ExecuteScript.objects.filter(command_name=CONTENT_SCRIPT_NAME).delete()

        DawsonHowToSearchForAnOpinion().run()

        page.refresh_from_db()
        timeline = page.body[0].value
        self.assertIn("written determination of a judge", str(timeline["introduction"]))
        self.assertEqual(
            timeline["phases"][1].value["title"],
            "Search by Keyword, Phrase, Judge, Date, or Opinion Type",
        )
        html = render_to_string(
            "detailed_timeline.html", {"block": page.body[0], "page": page}
        )
        self.assertIn("Refine Your Search Using Connectors", html)
        self.assertIn("To search by opinion type:", html)
        self.assertNotIn("Outdated", html)
        self.assertEqual(html.count(f'alt="{IMAGE_ALT}"'), 1)

    def test_existing_blank_opinion_guide_gets_populated(self):
        home_page = Page.objects.get(slug="home")
        home_page.add_child(
            instance=PetitionerExperiencePage(
                title="How to search for an opinion",
                slug="dawson-how-to-search-for-an-opinion",
            )
        )

        DawsonHowToSearchForAnOpinion().run()

        page = PetitionerExperiencePage.objects.get(
            slug="dawson-how-to-search-for-an-opinion"
        )
        self.assertEqual(len(page.body), 1)
        self.assertEqual(page.body[0].block_type, "detailed_timeline")
        self.assertTrue(page.live)
