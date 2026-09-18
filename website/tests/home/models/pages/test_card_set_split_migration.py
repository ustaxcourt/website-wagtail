"""
Tests for the 0142 data migration that splits any 'card' StreamField block
with more than 3 cards into consecutive blocks of at most 3, on pre-existing
EnhancedStandardPage content saved before WAG-1338 capped the Card Set at
`max_num=3`.

Without this, an already-published oversized card set (e.g. the "Case
Procedure Information" page, seeded years before this cap existed) would
keep rendering fine - Wagtail only enforces `max_num` on save - but fail
validation the next time an editor opened and saved that page.
"""

import importlib
import json

from django.db import connection
from django.test import TestCase, override_settings
from wagtail.models import Locale, Page, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage

migration_module = importlib.import_module(
    "home.migrations.0145_split_oversized_card_sets_pe"
)


class FakeSchemaEditor:
    """The migration only uses schema_editor.connection, so a real
    RunPython invocation's schema_editor isn't needed for these tests -
    the test DB's own connection (inside the test's transaction) is used
    directly, same as production migrations use the real connection."""

    def __init__(self, db_connection):
        self.connection = db_connection


def _card(title):
    return {
        "color": "green",
        "numbered_icon": "fa-solid fa-check",
        "numbered_icon_alignment": "center",
        "title_icon": None,
        "title_icon_alt_text": "",
        "subtitle": "",
        "title": title,
        "description": "desc",
        "buttons": [],
    }


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
class SplitOversizedCardSetsTest(TestCase):
    def setUp(self):
        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-card-split-migration-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.home_page = home_page

    def _create_page_with_raw_body(self, slug, raw_body_list):
        page = EnhancedStandardPage(title=slug, slug=slug, body=[])
        self.home_page.add_child(instance=page)

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE home_enhancedstandardpage SET body = %s WHERE page_ptr_id = %s",
                [json.dumps(raw_body_list), page.id],
            )
        return page

    def test_splits_four_cards_into_three_and_one(self):
        page = self._create_page_with_raw_body(
            "four-card-page",
            [
                {
                    "type": "card",
                    "value": [
                        _card("One"),
                        _card("Two"),
                        _card("Three"),
                        _card("Four"),
                    ],
                    "id": "original-id",
                }
            ],
        )

        migration_module.split_oversized_card_sets(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        card_blocks = [block for block in page.body if block.block_type == "card"]
        self.assertEqual(len(card_blocks), 2)
        self.assertEqual(len(card_blocks[0].value), 3)
        self.assertEqual(len(card_blocks[1].value), 1)
        self.assertEqual(
            [card["title"] for card in card_blocks[0].value],
            ["One", "Two", "Three"],
        )
        self.assertEqual(card_blocks[1].value[0]["title"], "Four")

    def test_first_chunk_keeps_original_id_second_chunk_gets_a_new_one(self):
        page = self._create_page_with_raw_body(
            "id-preservation-page",
            [
                {
                    "type": "card",
                    "value": [
                        _card("One"),
                        _card("Two"),
                        _card("Three"),
                        _card("Four"),
                    ],
                    "id": "original-id",
                }
            ],
        )

        migration_module.split_oversized_card_sets(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        raw = page.body.raw_data
        card_blocks = [block for block in raw if block["type"] == "card"]
        self.assertEqual(card_blocks[0]["id"], "original-id")
        self.assertNotEqual(card_blocks[1]["id"], "original-id")

    def test_splits_seven_cards_into_three_three_one(self):
        page = self._create_page_with_raw_body(
            "seven-card-page",
            [
                {
                    "type": "card",
                    "value": [_card(str(i)) for i in range(7)],
                    "id": "abc",
                }
            ],
        )

        migration_module.split_oversized_card_sets(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        card_blocks = [block for block in page.body if block.block_type == "card"]
        self.assertEqual([len(block.value) for block in card_blocks], [3, 3, 1])

    def test_leaves_conforming_card_sets_untouched(self):
        page = self._create_page_with_raw_body(
            "three-card-page",
            [
                {
                    "type": "card",
                    "value": [_card("One"), _card("Two"), _card("Three")],
                    "id": "abc",
                }
            ],
        )

        migration_module.split_oversized_card_sets(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        card_blocks = [block for block in page.body if block.block_type == "card"]
        self.assertEqual(len(card_blocks), 1)
        self.assertEqual(len(card_blocks[0].value), 3)

    def test_finds_oversized_card_blocks_nested_inside_card_tiles_default_content(
        self,
    ):
        page = self._create_page_with_raw_body(
            "nested-oversized-page",
            [
                {
                    "type": "card_tiles",
                    "value": {
                        "tiles": [],
                        "default_content": [
                            {
                                "type": "card",
                                "value": [
                                    _card("One"),
                                    _card("Two"),
                                    _card("Three"),
                                    _card("Four"),
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

        migration_module.split_oversized_card_sets(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        default_content = page.body[0].value["default_content"]
        card_blocks = [block for block in default_content if block.block_type == "card"]
        self.assertEqual(len(card_blocks), 2)
        self.assertEqual(len(card_blocks[0].value), 3)
        self.assertEqual(len(card_blocks[1].value), 1)

    def test_is_idempotent(self):
        page = self._create_page_with_raw_body(
            "idempotent-split-page",
            [
                {
                    "type": "card",
                    "value": [
                        _card("One"),
                        _card("Two"),
                        _card("Three"),
                        _card("Four"),
                    ],
                    "id": "abc",
                }
            ],
        )

        migration_module.split_oversized_card_sets(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )
        migration_module.split_oversized_card_sets(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        card_blocks = [block for block in page.body if block.block_type == "card"]
        self.assertEqual([len(block.value) for block in card_blocks], [3, 1])

    def test_skips_pages_without_any_card_block(self):
        page = self._create_page_with_raw_body(
            "no-card-page",
            [{"type": "paragraph", "value": "<p>Nothing to migrate here.</p>"}],
        )

        migration_module.split_oversized_card_sets(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        self.assertEqual(page.body[0].block_type, "paragraph")
