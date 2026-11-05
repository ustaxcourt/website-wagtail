"""
Tests for the 0165 data migration that converts legacy "section_header"
Link URL values (plain URL strings from the old URLBlock) into the new
PageSelectorBlock stream format
([{"type": "external_url", "value": <url>, ...}]).

Both the live page row and its revisions are converted so the admin
editor's draft/preview state stays usable with the new block schema.

Legacy data is injected with a queryset update() (as a lazy StreamValue)
because the new block schema can no longer validate/convert the old string
format - which is exactly why the migration operates on raw stream data.
"""

import importlib
import json

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from wagtail.blocks.stream_block import StreamValue
from wagtail.models import Locale, Page, Revision, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage

backfill_module = importlib.import_module(
    "home.migrations.0165_alter_enhancedstandardpage_body"
)

LEGACY_URL = "https://example.com/petitioners-timeline"


def _legacy_section_header(link_text="View detailed timeline", link_url=LEGACY_URL):
    return {
        "type": "section_header",
        "value": {
            "heading": "Get Started",
            "style": "default",
            "link_text": link_text,
            "link_url": link_url,
        },
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
class ConvertSectionHeaderLinkUrlTest(TestCase):
    def setUp(self):
        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-section-header-backfill-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.page = EnhancedStandardPage(
            title="Section Header Backfill Test Page",
            slug="section-header-backfill-test-page",
            body=[],
        )
        home_page.add_child(instance=self.page)

    def _set_legacy_body(self, raw_body):
        """Write legacy-format raw stream data directly to the page row."""
        stream_block = EnhancedStandardPage._meta.get_field("body").stream_block
        EnhancedStandardPage.objects.filter(pk=self.page.pk).update(
            body=StreamValue(stream_block, raw_body, is_lazy=True)
        )
        self.page.refresh_from_db()

    def test_backfill_converts_live_page_link_url_to_stream_format(self):
        self._set_legacy_body([_legacy_section_header()])

        backfill_module.convert_section_header_link_urls(apps=apps, schema_editor=None)

        self.page.refresh_from_db()
        link_url = self.page.body.raw_data[0]["value"]["link_url"]
        self.assertIsInstance(link_url, list)
        self.assertEqual(len(link_url), 1)
        self.assertEqual(link_url[0]["type"], "external_url")
        self.assertEqual(link_url[0]["value"], LEGACY_URL)
        self.assertIn("id", link_url[0])

    def test_backfill_converts_revision_content(self):
        self._set_legacy_body([_legacy_section_header()])
        # Create the revision row directly - save_revision() runs full_clean,
        # which the legacy string format can no longer pass; a real
        # pre-migration revision row simply exists with the old content.
        revision = Revision.objects.create(
            content=self.page.serializable_data(),
            object_id=str(self.page.pk),
            content_type=self.page.content_type,
            base_content_type=ContentType.objects.get_for_model(Page),
        )

        backfill_module.convert_section_header_link_urls(apps=apps, schema_editor=None)

        revision.refresh_from_db()
        body = revision.content["body"]
        if isinstance(body, str):
            body = json.loads(body)
        link_url = body[0]["value"]["link_url"]
        self.assertIsInstance(link_url, list)
        self.assertEqual(link_url[0]["type"], "external_url")
        self.assertEqual(link_url[0]["value"], LEGACY_URL)

    def test_backfill_converts_empty_legacy_link_url_to_empty_stream(self):
        self._set_legacy_body([_legacy_section_header(link_text="", link_url="")])

        backfill_module.convert_section_header_link_urls(apps=apps, schema_editor=None)

        self.page.refresh_from_db()
        self.assertEqual(self.page.body.raw_data[0]["value"]["link_url"], [])

    def test_backfill_converts_section_headers_nested_in_card_tiles(self):
        self._set_legacy_body(
            [
                {
                    "type": "card_tiles",
                    "value": {
                        "tiles": [
                            {
                                "type": "item",
                                "value": {
                                    "icon": 1,
                                    "icon_direction": "top",
                                    "card_header": "Anchor Tile",
                                    "link": [
                                        {
                                            "type": "anchor_page",
                                            "value": {
                                                "breadcrumb_title": "Anchor Tile",
                                                "body": [
                                                    _legacy_section_header(
                                                        link_text="Nested link"
                                                    )
                                                ],
                                            },
                                        }
                                    ],
                                    "card_hover": True,
                                },
                            }
                        ],
                        "default_content": [],
                        "show_back_button": False,
                        "back_button_text": "",
                    },
                }
            ]
        )

        backfill_module.convert_section_header_link_urls(apps=apps, schema_editor=None)

        self.page.refresh_from_db()
        anchor_body = self.page.body.raw_data[0]["value"]["tiles"][0]["value"]["link"][
            0
        ]["value"]["body"]
        link_url = anchor_body[0]["value"]["link_url"]
        self.assertIsInstance(link_url, list)
        self.assertEqual(link_url[0]["type"], "external_url")
        self.assertEqual(link_url[0]["value"], LEGACY_URL)

    def test_backfill_is_idempotent(self):
        self._set_legacy_body([_legacy_section_header()])

        backfill_module.convert_section_header_link_urls(apps=apps, schema_editor=None)
        self.page.refresh_from_db()
        first_link_url = self.page.body.raw_data[0]["value"]["link_url"]

        backfill_module.convert_section_header_link_urls(apps=apps, schema_editor=None)
        self.page.refresh_from_db()

        self.assertEqual(
            self.page.body.raw_data[0]["value"]["link_url"], first_link_url
        )

    def test_backfill_skips_pages_without_legacy_data(self):
        self._set_legacy_body(
            [
                {
                    "type": "section_header",
                    "value": {
                        "heading": "Get Started",
                        "style": "default",
                        "link_text": "View detailed timeline",
                        "link_url": [{"type": "external_url", "value": LEGACY_URL}],
                    },
                }
            ]
        )
        before = list(self.page.body.raw_data)

        backfill_module.convert_section_header_link_urls(apps=apps, schema_editor=None)

        self.page.refresh_from_db()
        self.assertEqual(list(self.page.body.raw_data), before)
