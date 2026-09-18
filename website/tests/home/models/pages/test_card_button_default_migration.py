"""
Tests for the 0149 data migration that strips the phantom Button entry that
ListBlock's default-value behavior injects into any 'card' whose raw data
omits the 'buttons' key entirely.

Card's 'buttons' field (home/models/pages/enhanced_standard.py) is a
ListBlock(ButtonBlock(), ...). Wagtail's ListBlock.__init__ falls back to
`[self.child_block.get_default()]` whenever no explicit `default` is passed,
so any card built without a 'buttons' key - every card defined before this
field existed, e.g. in
home/management/commands/pages/rules_and_guidance/case_procedure_page.py -
got a single Button with a required-but-blank 'text' and an empty required
'url' baked into its stored JSON the moment it passed through the current
StructBlock/ListBlock schema, instead of an empty list. That phantom button
renders as nothing on the public site, but fails full_clean() the moment an
editor opens the page in Wagtail admin, since 'text' and 'url' are both
required.

home/models/pages/enhanced_standard.py now passes `default=[]` so this can't
happen to newly-created cards, but pages already constructed under the old
default (or resaved while it was in effect) need their stored JSON repaired
directly - hence this migration and these tests.

Each ListBlock/StreamBlock entry round-trips through the current schema as
{"type": "item", "value": {...}, "id": "..."} (confirmed against a real
locally-created page), not a bare dict - these fixtures mirror that shape,
unlike 0141's fixtures which model much older, pre-wrapper legacy data.
"""

import importlib
import json

from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import TestCase, override_settings
from wagtail.models import Locale, Page, Revision, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage

migration_module = importlib.import_module(
    "home.migrations.0146_strip_phantom_card_button_pe"
)


class FakeSchemaEditor:
    """The migration only uses schema_editor.connection, so a real
    RunPython invocation's schema_editor isn't needed for these tests -
    the test DB's own connection (inside the test's transaction) is used
    directly, same as production migrations use the real connection."""

    def __init__(self, db_connection):
        self.connection = db_connection


def _phantom_button(button_id="btn-1"):
    return {
        "type": "item",
        "value": {
            "icon": None,
            "icon_location": "before",
            "text": None,
            "url": [],
            "style": "primary",
            "button_hover": True,
        },
        "id": button_id,
    }


def _real_button(button_id="btn-1"):
    return {
        "type": "item",
        "value": {
            "icon": None,
            "icon_location": "before",
            "text": "Download Form 4",
            "url": [{"type": "external_url", "value": "https://example.com/form4.pdf"}],
            "style": "primary",
            "button_hover": True,
        },
        "id": button_id,
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
class StripPhantomCardButtonTest(TestCase):
    def setUp(self):
        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-card-button-migration-test")
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

    def test_strips_phantom_button_with_blank_text_and_empty_url(self):
        page = self._create_page_with_raw_body(
            "phantom-button-page",
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "type": "item",
                            "value": {
                                "color": "green",
                                "numbered_icon": "fa-solid fa-check",
                                "numbered_icon_alignment": "center",
                                "title": "More trial location options",
                                "description": "desc",
                                "buttons": [_phantom_button()],
                            },
                            "id": "card-1",
                        }
                    ],
                    "id": "cards",
                }
            ],
        )

        migration_module.strip_phantom_card_button(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        card = page.body[0].value[0]
        self.assertEqual(list(card["buttons"]), [])
        self.assertEqual(card["title"], "More trial location options")
        self.assertTrue(page.full_clean() is None)

    def test_leaves_real_buttons_untouched(self):
        page = self._create_page_with_raw_body(
            "real-button-page",
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "type": "item",
                            "value": {
                                "color": "white",
                                "numbered_icon": "",
                                "numbered_icon_alignment": "left",
                                "title": "Statement of Taxpayer ID",
                                "description": "desc",
                                "buttons": [_real_button()],
                            },
                            "id": "card-1",
                        }
                    ],
                    "id": "cards",
                }
            ],
        )

        migration_module.strip_phantom_card_button(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        card = page.body[0].value[0]
        buttons = list(card["buttons"])
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0]["text"], "Download Form 4")

    def test_leaves_cards_with_no_buttons_key_untouched(self):
        page = self._create_page_with_raw_body(
            "no-buttons-key-page",
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "type": "item",
                            "value": {
                                "color": "white",
                                "title": "No buttons field at all",
                                "description": "desc",
                            },
                            "id": "card-1",
                        }
                    ],
                    "id": "cards",
                }
            ],
        )

        migration_module.strip_phantom_card_button(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        self.assertEqual(page.body[0].value[0]["title"], "No buttons field at all")

    def test_is_idempotent(self):
        page = self._create_page_with_raw_body(
            "idempotent-button-page",
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "type": "item",
                            "value": {
                                "color": "green",
                                "title": "Once",
                                "description": "desc",
                                "buttons": [_phantom_button()],
                            },
                            "id": "card-1",
                        }
                    ],
                    "id": "cards",
                }
            ],
        )

        migration_module.strip_phantom_card_button(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )
        migration_module.strip_phantom_card_button(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        page.refresh_from_db()
        card = page.body[0].value[0]
        self.assertEqual(list(card["buttons"]), [])

    def _create_legacy_revision(self, page, raw_body_list):
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
        page = self._create_page_with_raw_body(
            "revision-button-page",
            [
                {
                    "type": "card",
                    "value": [
                        {
                            "type": "item",
                            "value": {
                                "color": "green",
                                "title": "Live row",
                                "description": "desc",
                                "buttons": [_phantom_button()],
                            },
                            "id": "card-1",
                        }
                    ],
                    "id": "cards",
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
                            "type": "item",
                            "value": {
                                "color": "yellow",
                                "title": "Old revision snapshot",
                                "description": "desc",
                                "buttons": [_phantom_button(button_id="btn-rev")],
                            },
                            "id": "card-1",
                        }
                    ],
                    "id": "cards",
                }
            ],
        )

        migration_module.strip_phantom_card_button(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        revision.refresh_from_db()
        migrated_body = json.loads(revision.content["body"])
        card = migrated_body[0]["value"][0]["value"]
        self.assertEqual(card["buttons"], [])
        self.assertEqual(card["title"], "Old revision snapshot")

    def test_leaves_revisions_without_a_body_field_untouched(self):
        page = self._create_page_with_raw_body(
            "revision-no-body-button-page",
            [{"type": "paragraph", "value": "<p>Unrelated.</p>"}],
        )
        revision = Revision.objects.create(
            content_type=ContentType.objects.get_for_model(EnhancedStandardPage),
            base_content_type=ContentType.objects.get_for_model(Page),
            object_id=str(page.id),
            object_str=page.title,
            content={"pk": page.id, "title": "some buttons text but no body key"},
        )

        migration_module.strip_phantom_card_button(
            apps=None, schema_editor=FakeSchemaEditor(connection)
        )

        revision.refresh_from_db()
        self.assertNotIn("body", revision.content)
