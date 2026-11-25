import copy
import importlib
import json

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from wagtail.blocks.stream_block import StreamValue
from wagtail.models import Locale, Page, Revision, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage
from home.models.pages.petitioner_experience import PetitionerExperiencePage

migration = importlib.import_module(
    "home.migrations.0171_migrate_show_info_icon_to_bubble_content"
)


def _timeline(phases):
    return [{"type": "detailed_timeline", "value": {"phases": phases}}]


def _phase(**value):
    return {"type": "phase", "value": {"title": "t", **value}}


def test_checked_info_icon_becomes_info_and_unchecked_becomes_number():
    data = _timeline(
        [_phase(show_info_icon=False), _phase(show_info_icon=True), _phase()]
    )
    assert migration._convert_phases(data) is True
    values = [p["value"] for p in data[0]["value"]["phases"]]
    assert [v["bubble_content"] for v in values] == ["number", "info", "number"]
    assert all("show_info_icon" not in v for v in values)


def test_nested_timelines_are_converted():
    inner = _timeline([_phase(show_info_icon=True)])
    data = [{"type": "anchor", "value": {"body": inner}}]
    assert migration._convert_phases(data) is True
    assert inner[0]["value"]["phases"][0]["value"]["bubble_content"] == "info"


def test_already_migrated_data_is_unchanged_and_idempotent():
    data = _timeline([_phase(bubble_content="scale")])
    before = copy.deepcopy(data)
    assert migration._convert_phases(data) is False
    assert data == before


def test_existing_bubble_content_is_not_overwritten_but_old_key_removed():
    data = _timeline([_phase(bubble_content="user", show_info_icon=True)])
    assert migration._convert_phases(data) is True
    assert data[0]["value"]["phases"][0]["value"] == {
        "title": "t",
        "bubble_content": "user",
    }


def test_convert_stream_json_accepts_json_string_and_skips_unchanged():
    raw = '[{"type": "paragraph", "value": "x"}]'
    assert migration._convert_stream_json(raw) is None


# ---------------------------------------------------------------------------
# Database-backed coverage: persisted page bodies, revisions and re-runs.
# Follows tests/home/models/pages/test_section_header_link_url_backfill.py.
# ---------------------------------------------------------------------------
def _legacy_body():
    """A timeline in the pre-migration format (show_info_icon, no bubble_content)."""
    return [
        {
            "type": "detailed_timeline",
            "id": "10000000-0000-0000-0000-000000000000",
            "value": {
                "title": "Timeline",
                "introduction": "<p>Intro</p>",
                "phases": [
                    {
                        "type": "phase",
                        "id": "20000000-0000-0000-0000-000000000001",
                        "value": {
                            "title": "First",
                            "show_info_icon": False,
                            "instructions": "<p>One</p>",
                        },
                    },
                    {
                        "type": "phase",
                        "id": "20000000-0000-0000-0000-000000000002",
                        "value": {
                            "title": "Last",
                            "show_info_icon": True,
                            "instructions": "<p>Two</p>",
                        },
                    },
                ],
            },
        }
    ]


def _bubble_values(raw_body):
    if isinstance(raw_body, str):
        raw_body = json.loads(raw_body)
    return [
        (p["value"].get("bubble_content"), "show_info_icon" in p["value"])
        for p in raw_body[0]["value"]["phases"]
    ]


CONVERTED = [("number", False), ("info", False)]


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
class MigrateShowInfoIconToBubbleContentDbTest(TestCase):
    def setUp(self):
        Locale.objects.get_or_create(language_code="en")
        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")
        home_page = Page(title="Home", slug="home-bubble-content-migration-test")
        root_page.add_child(instance=home_page)
        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.enhanced = home_page.add_child(
            instance=EnhancedStandardPage(
                title="Enhanced", slug="bubble-enhanced", body=[]
            )
        )
        self.petitioner = home_page.add_child(
            instance=PetitionerExperiencePage(
                title="Petitioner", slug="bubble-petitioner", body=[]
            )
        )

    def _set_legacy_body(self, page, raw_body):
        stream_block = EnhancedStandardPage._meta.get_field("body").stream_block
        EnhancedStandardPage.objects.filter(pk=page.pk).update(
            body=StreamValue(stream_block, raw_body, is_lazy=True)
        )
        page.refresh_from_db()

    def _make_revision(self, page, raw_body):
        # Created directly: a real pre-migration revision simply exists with
        # the old content (save_revision() would re-validate it).
        content = page.serializable_data()
        content["body"] = json.dumps(raw_body)
        return Revision.objects.create(
            content=content,
            object_id=str(page.pk),
            content_type=page.content_type,
            base_content_type=ContentType.objects.get_for_model(Page),
        )

    def _run(self):
        migration.migrate_show_info_icon_to_bubble_content(
            apps=apps, schema_editor=None
        )

    def test_live_bodies_of_both_page_types_are_converted(self):
        for page in (self.enhanced, self.petitioner):
            self._set_legacy_body(page, _legacy_body())

        self._run()

        for page in (self.enhanced, self.petitioner):
            page.refresh_from_db()
            self.assertEqual(_bubble_values(page.body.raw_data), CONVERTED)

    def test_published_and_draft_revisions_are_converted(self):
        self._set_legacy_body(self.petitioner, _legacy_body())
        published = self._make_revision(self.petitioner, _legacy_body())
        draft = self._make_revision(self.petitioner, _legacy_body())
        PetitionerExperiencePage.objects.filter(pk=self.petitioner.pk).update(
            live_revision=published, latest_revision=draft
        )

        self._run()

        for revision in (published, draft):
            revision.refresh_from_db()
            self.assertEqual(_bubble_values(revision.content["body"]), CONVERTED)

    def test_second_run_leaves_persisted_data_unchanged(self):
        self._set_legacy_body(self.enhanced, _legacy_body())
        revision = self._make_revision(self.enhanced, _legacy_body())

        self._run()
        self.enhanced.refresh_from_db()
        revision.refresh_from_db()
        body_after_first = json.dumps(list(self.enhanced.body.raw_data))
        revision_after_first = revision.content["body"]

        self._run()
        self.enhanced.refresh_from_db()
        revision.refresh_from_db()

        self.assertEqual(
            json.dumps(list(self.enhanced.body.raw_data)), body_after_first
        )
        self.assertEqual(revision.content["body"], revision_after_first)
        self.assertEqual(_bubble_values(self.enhanced.body.raw_data), CONVERTED)

    def test_pages_without_a_timeline_are_untouched(self):
        raw = [{"type": "paragraph", "value": "<p>No timeline here</p>"}]
        self._set_legacy_body(self.enhanced, raw)
        revision = self._make_revision(self.enhanced, raw)

        self._run()

        self.enhanced.refresh_from_db()
        revision.refresh_from_db()
        self.assertEqual(list(self.enhanced.body.raw_data), raw)
        self.assertEqual(json.loads(revision.content["body"]), raw)
