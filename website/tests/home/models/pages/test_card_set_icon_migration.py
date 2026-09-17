"""
Tests for the 0141 data migration that renames the old 'card' block 'icon'
field to 'numbered_icon' on pre-existing EnhancedStandardPage content saved
before WAG-1338 reshaped the Card Set block. Also covers dropping legacy
icon values that have no equivalent in the narrowed numbered_icon choices,
and reconciling existing page revision snapshots (wagtailcore_revision), not
just the live page row.

Unlike most StreamField data migrations in this codebase, 0141 can't use
`apps.get_model(...)` + `page.body` the normal way, since migration 0140
(which it depends on) already swapped in the new block definitions - reading
`page.body` through the historical model would silently drop the old 'icon'
key via StructBlock.to_python() before the migration code ever saw it. So it
reads/writes the raw StreamField JSON directly via SQL instead, and these
tests set up that raw legacy JSON the same way (bypassing the StreamField
descriptor) to simulate real pre-WAG-1338 production content.
"""

import importlib
import json

from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import TestCase, override_settings
from wagtail.models import Locale, Page, Revision, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage

migration_module = importlib.import_module(
    "home.migrations.0141_migrate_card_block_icon_field_pe"
)


class FakeSchemaEditor:
    """The migration only uses schema_editor.connection, so a real
    RunPython invocation's schema_editor isn't needed for these tests -
    the test DB's own connection (inside the test's transaction) is used
    directly, same as production migrations use the real connection."""

    def __init__(self, db_connection):
        self.connection = db_connection


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
class MigrateCardIconFieldTest(TestCase):
    def setUp(self):
        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-card-icon-migration-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.home_page = home_page

    def _create_page_with_raw_body(self, slug, raw_body_list):
        """Creates a real page via the ORM (so it has a valid page tree
        row), then overwrites its `body` column directly with raw JSON,
        bypassing the StreamField descriptor - simulating real legacy
        production data saved before the new block schema existed."""
        page = EnhancedStandardPage(title=slug, slug=slug, body=[])
        self.home_page.add_child(instance=page)

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE home_enhancedstandardpage SET body = %s WHERE page_ptr_id = %s",
                [json.dumps(raw_body_list), page.id],
            )
        return page

    def test_renames_icon_to_numbered_icon_and_sets_center_alignment(self):
        page = self._create_page_with_raw_body(
            "old-schema-card-page",
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "icon": "fa-solid fa-check",
                            "title": "More trial location options",
                            "description": "desc",
                            "color": "green",
                        },
                    ],
                    "id": "abc",
                }
            ],
        )

        migration_module.migrate_card_icon_field(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        card = page.body[0].value[0]
        self.assertEqual(card["numbered_icon"], "fa-solid fa-check")
        self.assertEqual(card["numbered_icon_alignment"], "center")
        self.assertEqual(card["title"], "More trial location options")
        self.assertEqual(card["color"], "green")

    def test_leaves_new_schema_cards_untouched(self):
        page = self._create_page_with_raw_body(
            "new-schema-card-page",
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "color": "white",
                            "numbered_icon": "fa-solid fa-1",
                            "numbered_icon_alignment": "left",
                            "title": "Already migrated",
                            "description": "desc",
                        },
                    ],
                    "id": "abc",
                }
            ],
        )

        migration_module.migrate_card_icon_field(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        card = page.body[0].value[0]
        self.assertEqual(card["numbered_icon"], "fa-solid fa-1")
        self.assertEqual(card["numbered_icon_alignment"], "left")

    def test_finds_card_blocks_nested_inside_card_tiles_default_content(self):
        page = self._create_page_with_raw_body(
            "nested-card-page",
            [
                {
                    "type": "card_tiles",
                    "value": {
                        "tiles": [],
                        "default_content": [
                            {
                                "type": "card",
                                "value": [
                                    {
                                        "icon": "fa-solid fa-exclamation",
                                        "title": "Nested card",
                                        "description": "desc",
                                        "color": "yellow",
                                    },
                                ],
                                "id": "nested1",
                            }
                        ],
                        "show_back_button": False,
                        "back_button_text": "",
                    },
                    "id": "ct1",
                }
            ],
        )

        migration_module.migrate_card_icon_field(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        nested_card = page.body[0].value["default_content"][0].value[0]
        self.assertEqual(nested_card["numbered_icon"], "fa-solid fa-exclamation")
        self.assertEqual(nested_card["numbered_icon_alignment"], "center")

    def test_is_idempotent(self):
        page = self._create_page_with_raw_body(
            "idempotent-card-page",
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "icon": "fa-solid fa-check",
                            "title": "Once",
                            "description": "desc",
                            "color": "green",
                        },
                    ],
                    "id": "abc",
                }
            ],
        )

        migration_module.migrate_card_icon_field(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )
        migration_module.migrate_card_icon_field(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        card = page.body[0].value[0]
        self.assertEqual(card["numbered_icon"], "fa-solid fa-check")
        self.assertEqual(card["numbered_icon_alignment"], "center")

    def test_drops_unmappable_legacy_icon_instead_of_writing_invalid_value(self):
        """A legacy icon like 'book' has no equivalent in the narrowed
        numbered_icon choices (None/One/Two/Three/Check/Exclamation). Writing
        it into numbered_icon anyway would store an invalid choice value, so
        the migration must drop it instead of copying it over."""
        page = self._create_page_with_raw_body(
            "unmappable-icon-page",
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "icon": "fa-solid fa-book",
                            "title": "Legacy decorative icon",
                            "description": "desc",
                            "color": "white",
                        },
                    ],
                    "id": "abc",
                }
            ],
        )

        migration_module.migrate_card_icon_field(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        # Read the raw stored JSON directly, bypassing the StreamField
        # descriptor: a StructValue always exposes every defined sub-field
        # with its default, so it can't distinguish "numbered_icon was never
        # set" from "numbered_icon was set to an invalid value" - only the
        # raw dict can confirm the migration actually dropped the key
        # instead of writing 'fa-solid fa-book' into it.
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT body FROM home_enhancedstandardpage WHERE page_ptr_id = %s",
                [page.id],
            )
            raw_body = cursor.fetchone()[0]
        card = json.loads(raw_body)[0]["value"][0]
        self.assertNotIn("icon", card)
        self.assertNotIn("numbered_icon", card)
        self.assertEqual(card["title"], "Legacy decorative icon")

        # Reading through the StreamField descriptor still works and simply
        # defaults the now-unset field, rather than raising or rendering a
        # stale/invalid value.
        page.refresh_from_db()
        rendered_card = page.body[0].value[0]
        self.assertEqual(rendered_card["numbered_icon"], "")

    def _create_legacy_revision(self, page, raw_body_list):
        """Creates a Revision row shaped like a real pre-WAG-1338 snapshot:
        Revision.content is a plain JSONField (no StructBlock parsing), so
        unlike the page table this can be built directly through the ORM
        while still keeping 'body' double-JSON-encoded, matching how Wagtail
        actually stores it."""
        return Revision.objects.create(
            content_type=ContentType.objects.get_for_model(EnhancedStandardPage),
            base_content_type=ContentType.objects.get_for_model(Page),
            object_id=str(page.id),
            object_str=page.title,
            content={
                "pk": page.id,
                "title": page.title,
                "body": json.dumps(raw_body_list),
            },
        )

    def test_updates_revision_content_snapshot(self):
        """Reverting to, previewing, or approving an old revision after this
        migration should not restore a copy of 'body' with the pre-migration
        'icon' key still intact - the revision snapshot needs the same
        rename applied to it as the live page row."""
        page = self._create_page_with_raw_body(
            "revision-icon-page",
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "icon": "fa-solid fa-check",
                            "title": "Live row",
                            "description": "desc",
                            "color": "green",
                        },
                    ],
                    "id": "abc",
                }
            ],
        )
        revision = self._create_legacy_revision(
            page,
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "icon": "fa-solid fa-exclamation",
                            "title": "Old revision snapshot",
                            "description": "desc",
                            "color": "yellow",
                        },
                    ],
                    "id": "abc",
                }
            ],
        )

        migration_module.migrate_card_icon_field(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        revision.refresh_from_db()
        migrated_body = json.loads(revision.content["body"])
        card = migrated_body[0]["value"][0]
        self.assertNotIn("icon", card)
        self.assertEqual(card["numbered_icon"], "fa-solid fa-exclamation")
        self.assertEqual(card["numbered_icon_alignment"], "center")
        self.assertEqual(card["title"], "Old revision snapshot")

    def test_leaves_revisions_without_a_body_field_untouched(self):
        """A revision for a snippet or other non-page model has no 'body'
        field at all; the migration must skip it rather than error."""
        page = self._create_page_with_raw_body(
            "revision-no-body-page",
            [{"type": "paragraph", "value": "<p>Unrelated.</p>"}],
        )
        revision = Revision.objects.create(
            content_type=ContentType.objects.get_for_model(EnhancedStandardPage),
            base_content_type=ContentType.objects.get_for_model(Page),
            object_id=str(page.id),
            object_str=page.title,
            content={"pk": page.id, "title": "some card icon text but no body key"},
        )

        # Should not raise despite matching the LIKE '%card%' pattern loosely.
        migration_module.migrate_card_icon_field(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        revision.refresh_from_db()
        self.assertNotIn("body", revision.content)

    def test_skips_pages_without_any_card_block(self):
        page = self._create_page_with_raw_body(
            "no-card-page",
            [{"type": "paragraph", "value": "<p>Nothing to migrate here.</p>"}],
        )

        # Should not raise, and should leave the page's body untouched.
        migration_module.migrate_card_icon_field(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        self.assertEqual(page.body[0].block_type, "paragraph")
