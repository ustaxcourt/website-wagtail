from django.test import TestCase, override_settings
from wagtail.models import Collection, Locale, Page, Site

from home.management.commands.pages.rules_and_guidance import (
    DawsonTroubleshootFileUploads,
)
from home.management.commands.pages.rules_and_guidance.dawson_troubleshoot_file_uploads import (
    PAGE_SLUG,
    HIDE_TITLE_COMMAND_NAME,
    RESTORE_BODY_COMMAND_NAME,
    RESOURCES_COMMAND_NAME,
    troubleshoot_file_uploads_resources,
)
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript

EXPECTED_RESOURCES = [
    (
        "Adobe Convert files to PDFs User Guide",
        "https://helpx.adobe.com/acrobat/desktop/create-documents/create-pdfs/convert-to-pdf.html",
    ),
    (
        "Adobe Combine files into one PDF User Guide",
        "https://helpx.adobe.com/acrobat/desktop/edit-documents/combine-files/combine-files.html",
    ),
    (
        "Adobe Remove passwords from PDF User Guide",
        "https://helpx.adobe.com/acrobat/desktop/protect-documents/protect-with-passwords/remove-passwords-from-pdfs.html",
    ),
]


def resource_tiles(page):
    return page.resource_cards[0].value["tiles"]


class TestTroubleshootFileUploadsResourceCards(TestCase):
    def setUp(self):
        Locale.objects.get_or_create(language_code="en")
        if not Collection.objects.exists():
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
        home_page.add_child(
            instance=Page(title="DAWSON User Guides", slug="dawson-user-guides")
        )

    def test_resources_match_the_requirements(self):
        self.assertEqual(troubleshoot_file_uploads_resources, EXPECTED_RESOURCES)

    def test_new_page_is_created_with_resource_cards(self):
        DawsonTroubleshootFileUploads().run()

        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        tiles = resource_tiles(page)
        self.assertEqual(
            [(tile["title"], tile["link"][0].value) for tile in tiles],
            EXPECTED_RESOURCES,
        )
        for tile in tiles:
            self.assertEqual(tile["icon"]["svg_file"].title, "PDF_icon.svg")
            self.assertEqual(tile["link"][0].block_type, "external_url")

    def test_existing_page_gets_resource_cards_once(self):
        DawsonTroubleshootFileUploads().run()
        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        page.resource_cards = []
        page.save_revision().publish()
        ExecuteScript.objects.filter(command_name=RESOURCES_COMMAND_NAME).delete()

        DawsonTroubleshootFileUploads().run()

        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        self.assertEqual(len(resource_tiles(page)), 3)
        self.assertEqual(
            len(page.get_latest_revision_as_object().resource_cards[0].value["tiles"]),
            3,
        )
        script = ExecuteScript.objects.get(command_name=RESOURCES_COMMAND_NAME)
        self.assertEqual(script.execution_status, "SUCCESS")

    def test_existing_resource_cards_are_not_overwritten(self):
        DawsonTroubleshootFileUploads().run()
        ExecuteScript.objects.filter(command_name=RESOURCES_COMMAND_NAME).delete()
        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        tiles_before = [tile["title"] for tile in resource_tiles(page)]
        revisions_before = page.revisions.count()

        DawsonTroubleshootFileUploads().run()

        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        self.assertEqual([tile["title"] for tile in resource_tiles(page)], tiles_before)
        self.assertEqual(page.revisions.count(), revisions_before)

    def test_resource_update_runs_only_once(self):
        DawsonTroubleshootFileUploads().run()

        self.assertEqual(DawsonTroubleshootFileUploads().run(), 0)
        self.assertEqual(
            ExecuteScript.objects.filter(command_name=RESOURCES_COMMAND_NAME).count(),
            1,
        )

    def test_missing_page_is_skipped_without_error(self):
        DawsonTroubleshootFileUploads().add_resource_cards()
        DawsonTroubleshootFileUploads().hide_timeline_title()

        self.assertFalse(Page.objects.filter(slug=PAGE_SLUG).exists())

    def test_new_page_hides_the_timeline_title(self):
        DawsonTroubleshootFileUploads().run()

        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        self.assertFalse(page.body[0].value["show_title"])

    def test_existing_page_timeline_title_is_hidden_once(self):
        DawsonTroubleshootFileUploads().run()
        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        body = page.body.get_prep_value()
        body[0]["value"]["show_title"] = True
        page.body = body
        page.save_revision().publish()
        ExecuteScript.objects.filter(command_name=HIDE_TITLE_COMMAND_NAME).delete()

        DawsonTroubleshootFileUploads().run()

        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        self.assertFalse(page.body[0].value["show_title"])
        self.assertFalse(
            page.get_latest_revision_as_object().body[0].value["show_title"]
        )
        self.assertEqual(len(page.body[0].value["phases"]), 6)

    def test_existing_page_with_empty_body_gets_restored_once(self):
        DawsonTroubleshootFileUploads().run()
        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        page.body = []
        page.save_revision().publish()
        ExecuteScript.objects.filter(command_name=RESTORE_BODY_COMMAND_NAME).delete()

        DawsonTroubleshootFileUploads().run()

        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        self.assertEqual(len(page.body), 1)
        self.assertEqual(page.body[0].block_type, "detailed_timeline")
        self.assertEqual(len(page.body[0].value["phases"]), 6)
        self.assertFalse(page.body[0].value["show_title"])
        self.assertEqual(len(resource_tiles(page)), 3)
        script = ExecuteScript.objects.get(command_name=RESTORE_BODY_COMMAND_NAME)
        self.assertEqual(script.execution_status, "SUCCESS")
        revision_count = page.revisions.count()

        DawsonTroubleshootFileUploads().run()

        page.refresh_from_db()
        self.assertEqual(len(page.body), 1)
        self.assertEqual(page.revisions.count(), revision_count)

    def test_existing_nonempty_body_is_not_overwritten_by_restore(self):
        DawsonTroubleshootFileUploads().run()
        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        body_before = page.body.get_prep_value()
        revision_count = page.revisions.count()
        ExecuteScript.objects.filter(command_name=RESTORE_BODY_COMMAND_NAME).delete()

        DawsonTroubleshootFileUploads().run()

        page.refresh_from_db()
        self.assertEqual(page.body.get_prep_value(), body_before)
        self.assertEqual(page.revisions.count(), revision_count)

    def test_run_defers_updates_while_page_has_unpublished_changes(self):
        DawsonTroubleshootFileUploads().run()
        page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)
        draft_body = page.body.get_prep_value()
        draft_body[0]["value"]["introduction"] = "<p>Pending editorial draft.</p>"
        page.body = []
        page.save_revision().publish()
        page.body = draft_body
        page.save_revision()
        page.refresh_from_db()
        self.assertTrue(page.has_unpublished_changes)

        pending_commands = [
            RESOURCES_COMMAND_NAME,
            RESTORE_BODY_COMMAND_NAME,
            HIDE_TITLE_COMMAND_NAME,
        ]
        ExecuteScript.objects.filter(command_name__in=pending_commands).delete()
        DawsonTroubleshootFileUploads().run()

        page.refresh_from_db()
        self.assertFalse(page.body)
        self.assertEqual(
            str(page.get_latest_revision_as_object().body[0].value["introduction"]),
            "<p>Pending editorial draft.</p>",
        )
        self.assertFalse(
            ExecuteScript.objects.filter(command_name__in=pending_commands).exists()
        )


@override_settings(GITHUB_SHA="0123456789")
class TestTroubleshootFileUploadsResourcesColumn(TestCase):
    def setUp(self):
        TestTroubleshootFileUploadsResourceCards.setUp(self)
        DawsonTroubleshootFileUploads().run()
        self.page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)

    def render(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_resources_column_renders_cards_with_links_after_timeline(self):
        html = self.render()

        self.assertIn('id="petitioner-resources-heading"', html)
        self.assertIn(">Resources</h2>", html)
        for title, url in EXPECTED_RESOURCES:
            self.assertIn(title, html)
            self.assertIn(f'href="{url}"', html)
        # Source order puts the Resources column after the timeline for tablet/mobile.
        self.assertLess(
            html.index("detailed-timeline-phases-block"),
            html.index("petitioner-resources-heading"),
        )

    def test_timeline_controls_are_unchanged(self):
        html = self.render()

        self.assertIn("detailed-timeline-expand-button", html)
        self.assertNotIn(f"<h2>{self.page.title}</h2>", html)
        self.assertIn("detailed-timeline-print-button", html)
        self.assertIn(f'data-print-title="{self.page.title}"', html)
        self.assertEqual(html.count('class="detailed-timeline-accordion-block"'), 6)
        self.assertEqual(html.count("detailed-timeline-accordion-header-button"), 6)

    def test_page_without_resource_cards_has_no_resources_column(self):
        self.page.resource_cards = []
        self.page.save_revision().publish()
        html = self.render()

        self.assertNotIn("petitioner-resources-heading", html)
        self.assertNotIn("petitioner-resource-rail", html)
        self.assertIn("side-card-layout", html)
