from django.test import TestCase, override_settings
from wagtail.models import Collection, Locale, Page, Site

from home.management.commands.pages.rules_and_guidance import (
    DawsonTroubleshootFileUploads,
)
from home.management.commands.pages.rules_and_guidance.dawson_troubleshoot_file_uploads import (
    PAGE_SLUG,
    HIDE_TITLE_COMMAND_NAME,
    RESTORE_BODY_COMMAND_NAME,
    REMOVE_RESOURCES_COMMAND_NAME,
)
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript

LEGACY_RESOURCE_CARDS = [
    {
        "type": "quick_access_tiles",
        "value": {
            "tiles_hover_enabled": True,
            "icon_position": "desktop_top_mobile_left",
            "tiles": [
                {
                    "type": "item",
                    "value": {
                        "title": "Adobe Convert files to PDFs User Guide",
                        "description": "",
                        "icon": {"svg_file": None},
                        "content_alignment": "left",
                        "link": [
                            {
                                "type": "external_url",
                                "value": "https://helpx.adobe.com/acrobat/desktop/create-documents/create-pdfs/convert-to-pdf.html",
                            }
                        ],
                    },
                }
            ],
        },
    }
]


class TestTroubleshootFileUploadsInitializer(TestCase):
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

    def get_page(self):
        return PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)

    def test_new_page_is_created_without_resource_cards(self):
        DawsonTroubleshootFileUploads().run()

        page = self.get_page()
        self.assertFalse(page.resource_cards)
        self.assertFalse(page.has_resource_tiles)
        self.assertEqual(len(page.body[0].value["phases"]), 6)

    def test_existing_page_resource_cards_are_removed_once(self):
        DawsonTroubleshootFileUploads().run()
        page = self.get_page()
        page.resource_cards = LEGACY_RESOURCE_CARDS
        page.save_revision().publish()
        ExecuteScript.objects.filter(
            command_name=REMOVE_RESOURCES_COMMAND_NAME
        ).delete()

        DawsonTroubleshootFileUploads().run()

        page = self.get_page()
        self.assertFalse(page.resource_cards)
        self.assertFalse(page.get_latest_revision_as_object().resource_cards)
        script = ExecuteScript.objects.get(command_name=REMOVE_RESOURCES_COMMAND_NAME)
        self.assertEqual(script.execution_status, "SUCCESS")
        self.assertEqual(len(page.body[0].value["phases"]), 6)

    def test_removal_without_resource_cards_creates_no_revision(self):
        DawsonTroubleshootFileUploads().run()
        ExecuteScript.objects.filter(
            command_name=REMOVE_RESOURCES_COMMAND_NAME
        ).delete()
        revisions_before = self.get_page().revisions.count()

        DawsonTroubleshootFileUploads().run()

        self.assertEqual(self.get_page().revisions.count(), revisions_before)

    def test_run_executes_only_once(self):
        DawsonTroubleshootFileUploads().run()

        self.assertEqual(DawsonTroubleshootFileUploads().run(), 0)
        self.assertEqual(
            ExecuteScript.objects.filter(
                command_name=REMOVE_RESOURCES_COMMAND_NAME
            ).count(),
            1,
        )

    def test_missing_page_is_skipped_without_error(self):
        DawsonTroubleshootFileUploads().remove_resource_cards()
        DawsonTroubleshootFileUploads().hide_timeline_title()

        self.assertFalse(Page.objects.filter(slug=PAGE_SLUG).exists())

    def test_new_page_hides_the_timeline_title(self):
        DawsonTroubleshootFileUploads().run()

        self.assertFalse(self.get_page().body[0].value["show_title"])

    def test_existing_page_timeline_title_is_hidden_once(self):
        DawsonTroubleshootFileUploads().run()
        page = self.get_page()
        body = page.body.get_prep_value()
        body[0]["value"]["show_title"] = True
        page.body = body
        page.save_revision().publish()
        ExecuteScript.objects.filter(command_name=HIDE_TITLE_COMMAND_NAME).delete()

        DawsonTroubleshootFileUploads().run()

        page = self.get_page()
        self.assertFalse(page.body[0].value["show_title"])
        self.assertFalse(
            page.get_latest_revision_as_object().body[0].value["show_title"]
        )
        self.assertEqual(len(page.body[0].value["phases"]), 6)

    def test_existing_page_with_empty_body_gets_restored_once(self):
        DawsonTroubleshootFileUploads().run()
        page = self.get_page()
        page.body = []
        page.save_revision().publish()
        ExecuteScript.objects.filter(command_name=RESTORE_BODY_COMMAND_NAME).delete()

        DawsonTroubleshootFileUploads().run()

        page = self.get_page()
        self.assertEqual(len(page.body), 1)
        self.assertEqual(page.body[0].block_type, "detailed_timeline")
        self.assertEqual(len(page.body[0].value["phases"]), 6)
        self.assertFalse(page.body[0].value["show_title"])
        self.assertFalse(page.resource_cards)
        script = ExecuteScript.objects.get(command_name=RESTORE_BODY_COMMAND_NAME)
        self.assertEqual(script.execution_status, "SUCCESS")
        revision_count = page.revisions.count()

        DawsonTroubleshootFileUploads().run()

        page.refresh_from_db()
        self.assertEqual(len(page.body), 1)
        self.assertEqual(page.revisions.count(), revision_count)

    def test_existing_nonempty_body_is_not_overwritten_by_restore(self):
        DawsonTroubleshootFileUploads().run()
        page = self.get_page()
        body_before = page.body.get_prep_value()
        revision_count = page.revisions.count()
        ExecuteScript.objects.filter(command_name=RESTORE_BODY_COMMAND_NAME).delete()

        DawsonTroubleshootFileUploads().run()

        page.refresh_from_db()
        self.assertEqual(page.body.get_prep_value(), body_before)
        self.assertEqual(page.revisions.count(), revision_count)

    def test_run_defers_updates_while_page_has_unpublished_changes(self):
        DawsonTroubleshootFileUploads().run()
        page = self.get_page()
        draft_body = page.body.get_prep_value()
        draft_body[0]["value"]["introduction"] = "<p>Pending editorial draft.</p>"
        page.body = []
        page.save_revision().publish()
        page.body = draft_body
        page.save_revision()
        page.refresh_from_db()
        self.assertTrue(page.has_unpublished_changes)

        pending_commands = [
            REMOVE_RESOURCES_COMMAND_NAME,
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
class TestTroubleshootFileUploadsPageLayout(TestCase):
    def setUp(self):
        TestTroubleshootFileUploadsInitializer.setUp(self)
        DawsonTroubleshootFileUploads().run()
        self.page = PetitionerExperiencePage.objects.get(slug=PAGE_SLUG)

    def render(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_page_has_no_resources_column_and_content_spans_full_width(self):
        html = self.render()

        self.assertNotIn("petitioner-resources-heading", html)
        self.assertNotIn("petitioner-resource-rail", html)
        self.assertNotIn("side-card-rail", html)
        self.assertNotIn("desktop:grid-col-8", html)
        self.assertRegex(html, r"grid-col-12\s+side-card-main")

    def test_timeline_controls_are_unchanged(self):
        html = self.render()

        self.assertIn("detailed-timeline-expand-button", html)
        self.assertNotIn(f"<h2>{self.page.title}</h2>", html)
        self.assertIn("detailed-timeline-print-button", html)
        self.assertIn(f'data-print-title="{self.page.title}"', html)
        self.assertEqual(html.count('class="detailed-timeline-accordion-block"'), 6)
        self.assertEqual(html.count("detailed-timeline-accordion-header-button"), 6)
