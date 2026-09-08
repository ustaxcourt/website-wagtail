"""
Tests for the 0137 data migration that renames the old 'card' block 'icon'
field to 'numbered_icon' on pre-existing EnhancedStandardPage content saved
before WAG-1338 reshaped the Card Set block.

Unlike most StreamField data migrations in this codebase, 0137 can't use
`apps.get_model(...)` + `page.body` the normal way, since migration 0136
(which it depends on) already swapped in the new block definitions - reading
`page.body` through the historical model would silently drop the old 'icon'
key via StructBlock.to_python() before the migration code ever saw it. So it
reads/writes the raw StreamField JSON directly via SQL instead, and these
tests set up that raw legacy JSON the same way (bypassing the StreamField
descriptor) to simulate real pre-WAG-1338 production content.
"""

import importlib
import json

from django.db import connection
from django.test import TestCase, override_settings
from wagtail.models import Locale, Page, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage

migration_module = importlib.import_module(
    "home.migrations.0137_migrate_card_block_icon_field"
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
