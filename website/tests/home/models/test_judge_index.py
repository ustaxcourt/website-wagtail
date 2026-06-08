"""
Unit tests for JudgeIndex page and related models.
Covers _build_judge_groups(), page rendering, routes, and PrivateSeminarDisclosure.
"""

import datetime

from django.test import TestCase, RequestFactory, override_settings
from wagtail.models import Locale, Page, Site

from home.models.pages.judge_index import (
    JudgeIndex,
    TYPE_ORDER,
    FILTER_KEYS,
    FILTER_LABELS,
    SECTION_LABELS_SINGULAR,
    SECTION_LABELS_PLURAL,
)
from home.models.snippets.judges import (
    JudgeProfile,
    JudgeCollection,
    JudgeRole,
    PrivateSeminarDisclosure,
)


OVERRIDE = dict(
    GITHUB_SHA="test1234567",
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)


def _make_judge(first, last, title, display_name=""):
    """Create a JudgeProfile, bypassing DraftStateMixin workflow."""
    judge = JudgeProfile(
        first_name=first,
        last_name=last,
        title=title,
        display_name=display_name or f"{first} {last}",
    )
    # Use save() directly; the model's save() handles auto-collection membership.
    judge.save()
    return judge


@override_settings(**OVERRIDE)
class JudgeIndexSetUpMixin(TestCase):
    """Shared setUp for JudgeIndex tests."""

    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-judge-index-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        self.judge_index = JudgeIndex(
            title="Judge Information",
            slug="judge-information",
            intro_text="<p>See the Judge&#x27;s biography by clicking on the cards.</p>",
        )
        home_page.add_child(instance=self.judge_index)

        # Create judges — JudgeProfile.save() auto-adds them to their collection.
        self.judge_smith = _make_judge("Jane", "Smith", "Judge")
        self.judge_jones = _make_judge("Bob", "Jones", "Judge")
        self.sstj = _make_judge("Alice", "Anderson", "Senior Special Trial Judge")

        # Ensure collections exist (they are auto-created by save())
        self.judges_collection = JudgeCollection.objects.get(name="Judges")
        self.sstj_collection = JudgeCollection.objects.get(
            name="Senior Special Trial Judges"
        )

        # Create a Chief Judge role pointing to smith
        self.chief_role = JudgeRole(role_name="Chief Judge", judge=self.judge_smith)
        self.chief_role.save()

        # Create a disclosure for smith
        self.disclosure = PrivateSeminarDisclosure.objects.create(
            judge=self.judge_smith,
            program_provider="ACME Legal",
            program_title="Tax Law Seminar",
            date=datetime.date(2024, 6, 15),
            location="Washington, DC",
        )

    def _get_request(self, path="/"):
        request = self.factory.get(path)
        request.site = Site.objects.get(is_default_site=True)
        return request


@override_settings(**OVERRIDE)
class BuildJudgeGroupsTest(JudgeIndexSetUpMixin):
    """Tests for JudgeIndex._build_judge_groups()."""

    def _groups_by_type(self):
        groups = self.judge_index._build_judge_groups()
        return {g["type"]: g for g in groups}

    def test_empty_collections_excluded(self):
        """Collections with no judges should not appear in groups."""
        by_type = self._groups_by_type()
        # Only Judge and Senior Special Trial Judge collections are populated
        self.assertIn("Judge", by_type)
        self.assertIn("Senior Special Trial Judge", by_type)
        # Senior Judge and Special Trial Judge have no members
        self.assertNotIn("Senior Judge", by_type)
        self.assertNotIn("Special Trial Judge", by_type)

    def test_groups_in_type_order(self):
        """Groups must follow TYPE_ORDER ordering."""
        groups = self.judge_index._build_judge_groups()
        types_returned = [g["type"] for g in groups]
        # Filter TYPE_ORDER to only populated types and compare order
        populated = [t for t in TYPE_ORDER if t in types_returned]
        self.assertEqual(types_returned, populated)

    def test_group_keys_present(self):
        """Each group must have the required keys."""
        for group in self.judge_index._build_judge_groups():
            for key in ("type", "label", "filter_key", "filter_label", "judges"):
                self.assertIn(
                    key, group, f"Missing key '{key}' in group {group['type']}"
                )

    def test_filter_key_matches_constants(self):
        by_type = self._groups_by_type()
        for judge_type, group in by_type.items():
            self.assertEqual(group["filter_key"], FILTER_KEYS[judge_type])

    def test_filter_label_matches_constants(self):
        by_type = self._groups_by_type()
        for judge_type, group in by_type.items():
            self.assertEqual(group["filter_label"], FILTER_LABELS[judge_type])

    def test_section_label_plural_when_multiple_judges(self):
        """Judges collection has 2 judges → plural section label."""
        by_type = self._groups_by_type()
        self.assertEqual(by_type["Judge"]["label"], SECTION_LABELS_PLURAL["Judge"])

    def test_section_label_singular_when_one_judge(self):
        """SSTJ collection has 1 judge → singular section label."""
        by_type = self._groups_by_type()
        self.assertEqual(
            by_type["Senior Special Trial Judge"]["label"],
            SECTION_LABELS_SINGULAR["Senior Special Trial Judge"],
        )

    def test_role_label_uses_role_name_when_role_exists(self):
        """Judge with a JudgeRole should have role_label = role.role_name."""
        by_type = self._groups_by_type()
        judges_group = by_type["Judge"]
        smith_entry = next(
            (e for e in judges_group["judges"] if e["judge"].id == self.judge_smith.id),
            None,
        )
        self.assertIsNotNone(smith_entry, "Smith not found in judges group")
        self.assertEqual(smith_entry["role_label"], "Chief Judge")

    def test_role_label_falls_back_to_title_when_no_role(self):
        """Judge without a JudgeRole should have role_label = judge.title."""
        by_type = self._groups_by_type()
        judges_group = by_type["Judge"]
        jones_entry = next(
            (e for e in judges_group["judges"] if e["judge"].id == self.judge_jones.id),
            None,
        )
        self.assertIsNotNone(jones_entry, "Jones not found in judges group")
        self.assertEqual(jones_entry["role_label"], self.judge_jones.title)

    def test_chief_judge_ordered_first(self):
        """Chief Judge (smith) must appear first in the Judges group."""
        by_type = self._groups_by_type()
        judges_group = by_type["Judge"]
        first_judge = judges_group["judges"][0]["judge"]
        self.assertEqual(first_judge.id, self.judge_smith.id)


@override_settings(**OVERRIDE)
class JudgeIndexRenderTest(JudgeIndexSetUpMixin):
    """Tests for JudgeIndex main page rendering."""

    def test_page_renders_200(self):
        request = self._get_request(self.judge_index.url)
        response = self.judge_index.serve(request)
        rendered = response.render()
        self.assertEqual(rendered.status_code, 200)

    def test_page_title_in_html(self):
        request = self._get_request(self.judge_index.url)
        response = self.judge_index.serve(request)
        rendered = response.render()
        self.assertIn("Judge Information", rendered.content.decode())

    def test_intro_text_in_html(self):
        request = self._get_request(self.judge_index.url)
        response = self.judge_index.serve(request)
        rendered = response.render()
        self.assertIn("biography", rendered.content.decode())

    def test_judge_display_name_in_html(self):
        request = self._get_request(self.judge_index.url)
        response = self.judge_index.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        self.assertIn("Smith", content)

    def test_filter_buttons_in_html(self):
        request = self._get_request(self.judge_index.url)
        response = self.judge_index.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        # All Judges filter button should appear
        self.assertIn("All Judges", content)

    def test_section_headers_in_html(self):
        request = self._get_request(self.judge_index.url)
        response = self.judge_index.serve(request)
        rendered = response.render()
        content = rendered.content.decode()
        self.assertIn("Biographies", content)


@override_settings(**OVERRIDE)
class JudgeDetailRouteTest(JudgeIndexSetUpMixin):
    """Tests for the judge_detail routable route."""

    def test_valid_judge_returns_200(self):
        path = f"{self.judge_index.url}{self.judge_smith.id}/smith/"
        request = self._get_request(path)
        response = self.judge_index.judge_detail(
            request, id=str(self.judge_smith.id), last_name="smith"
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_judge_id_returns_404(self):
        from django.http import Http404

        request = self._get_request("/judge-information/99999/nobody/")
        with self.assertRaises(Http404):
            self.judge_index.judge_detail(request, id="99999", last_name="nobody")

    def test_wrong_last_name_returns_404(self):
        from django.http import Http404

        request = self._get_request(
            f"/judge-information/{self.judge_smith.id}/wrongname/"
        )
        with self.assertRaises(Http404):
            self.judge_index.judge_detail(
                request, id=str(self.judge_smith.id), last_name="wrongname"
            )


@override_settings(**OVERRIDE)
class PrivateSeminarDisclosuresRouteTest(JudgeIndexSetUpMixin):
    """Tests for the private_seminar_disclosures routable route."""

    def test_route_returns_200(self):
        request = self._get_request(
            f"{self.judge_index.url}private-seminar-disclosures/"
        )
        response = self.judge_index.private_seminar_disclosures(request)
        self.assertEqual(response.status_code, 200)

    def test_shows_disclosure_data(self):
        request = self._get_request(
            f"{self.judge_index.url}private-seminar-disclosures/"
        )
        response = self.judge_index.private_seminar_disclosures(request)
        content = response.content.decode()
        self.assertIn("Tax Law Seminar", content)
        self.assertIn("ACME Legal", content)

    def test_empty_state_message_when_no_disclosures(self):
        PrivateSeminarDisclosure.objects.all().delete()
        request = self._get_request(
            f"{self.judge_index.url}private-seminar-disclosures/"
        )
        response = self.judge_index.private_seminar_disclosures(request)
        content = response.content.decode()
        self.assertIn("No seminar disclosures have been filed", content)

    def test_year_filter_returns_matching_disclosures(self):
        request = self._get_request(
            f"{self.judge_index.url}private-seminar-disclosures/?year=2024"
        )
        response = self.judge_index.private_seminar_disclosures(request)
        content = response.content.decode()
        self.assertIn("Tax Law Seminar", content)

    def test_year_filter_excludes_non_matching(self):
        request = self._get_request(
            f"{self.judge_index.url}private-seminar-disclosures/?year=1990"
        )
        response = self.judge_index.private_seminar_disclosures(request)
        content = response.content.decode()
        self.assertNotIn("Tax Law Seminar", content)

    def test_invalid_year_param_ignored(self):
        request = self._get_request(
            f"{self.judge_index.url}private-seminar-disclosures/?year=notayear"
        )
        # Should not raise; should show all disclosures
        response = self.judge_index.private_seminar_disclosures(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Tax Law Seminar", content)


@override_settings(**OVERRIDE)
class PrivateSeminarDisclosureModelTest(JudgeIndexSetUpMixin):
    """Tests for PrivateSeminarDisclosure model."""

    def test_str_format(self):
        expected = "Jane Smith — Tax Law Seminar (2024-06-15)"
        self.assertEqual(str(self.disclosure), expected)

    def test_meta_ordering(self):
        # The Meta.ordering is ["-date", "judge__last_name"]
        self.assertEqual(
            PrivateSeminarDisclosure._meta.ordering,
            ["-date", "judge__last_name"],
        )


@override_settings(**OVERRIDE)
class SeedBottomTilesRevisionTest(JudgeIndexSetUpMixin):
    """Regression tests for the dev-web bug where _seed_bottom_tiles wrote
    to the model via .save() but never created a Wagtail revision. The
    public page rendered the tiles correctly (reads model fields directly)
    but the admin editor read the last revision (which pre-dated the
    seeding) and showed the bottom_tiles StreamField empty. Fix is to call
    save_revision().publish() after the model save so the admin and the
    public page stay in sync.
    """

    # A minimal, valid bottom_tiles StreamField payload. We bypass
    # _build_bottom_tiles_data() because in production it loads SVG icons via
    # Wagtail Documents (requires the Documents collection + media files),
    # neither of which are set up in this lightweight unit-test environment.
    # The behavior under test is the revision lifecycle, not tile content.
    _FAKE_TILES = [
        {
            "type": "quick_access_tiles",
            "value": {
                "tiles_hover_enabled": True,
                "icon_position": "desktop_top_mobile_left",
                "tiles": [],
            },
        }
    ]

    def _seed(self):
        from unittest.mock import patch
        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        # The seeder looks up the page by slug, so make this instance's slug
        # match what the initializer expects.
        self.judge_index.slug = "judges"
        self.judge_index.save()

        page = Page.objects.get(pk=self.judge_index.pk)
        initializer = JudgesPageInitializer()
        with patch.object(
            initializer, "_build_bottom_tiles_data", return_value=self._FAKE_TILES
        ):
            initializer._seed_bottom_tiles(page)

    def test_seed_creates_a_published_revision_with_bottom_tiles(self):
        # Sanity-check the starting state — no bottom_tiles on the model
        # and no revisions in history (treebeard add_child does not create one).
        self.judge_index.refresh_from_db()
        self.assertFalse(bool(self.judge_index.bottom_tiles))
        self.assertIsNone(self.judge_index.latest_revision)

        self._seed()

        # Model fields are populated.
        self.judge_index.refresh_from_db()
        self.assertTrue(bool(self.judge_index.bottom_tiles))
        # A revision was created and published so the admin editor sees
        # the same content as the public page.
        self.assertIsNotNone(self.judge_index.latest_revision)
        revision_obj = self.judge_index.latest_revision.as_object()
        self.assertTrue(bool(revision_obj.bottom_tiles))

    def test_seed_with_stale_existing_revision_updates_admin_state(self):
        # Reproduce the dev-web shape: page already has a revision capturing
        # an empty bottom_tiles state (the "before 1246 deploy" snapshot).
        # The seeder must overwrite that revision so the admin reflects the
        # seeded tiles.
        self.judge_index.slug = "judges"
        self.judge_index.save()
        stale = self.judge_index.save_revision()
        stale.publish()
        self.judge_index.refresh_from_db()
        self.assertFalse(
            bool(self.judge_index.latest_revision.as_object().bottom_tiles)
        )

        self._seed()

        self.judge_index.refresh_from_db()
        latest = self.judge_index.latest_revision.as_object()
        self.assertTrue(bool(latest.bottom_tiles))
        self.assertNotEqual(self.judge_index.latest_revision_id, stale.id)

    def test_seed_skips_when_bottom_tiles_already_populated(self):
        # Belt-and-suspenders: confirm that admin-customized bottom_tiles are
        # preserved across deploys. If bottom_tiles is non-empty, the seed
        # short-circuits and does NOT create a new revision.
        self.judge_index.slug = "judges"
        self.judge_index.bottom_tiles = [
            {
                "type": "quick_access_tiles",
                "value": {
                    "tiles_hover_enabled": True,
                    "icon_position": "desktop_top_mobile_left",
                    "tiles": [],
                },
            }
        ]
        self.judge_index.save()
        marker_rev = self.judge_index.save_revision()
        marker_rev.publish()
        self.judge_index.refresh_from_db()
        existing_rev_id = self.judge_index.latest_revision_id

        self._seed()

        self.judge_index.refresh_from_db()
        # No new revision should have been created.
        self.assertEqual(self.judge_index.latest_revision_id, existing_rev_id)

    def test_seed_bottom_tiles_skips_when_page_is_not_a_judge_index(self):
        # Pass a plain Page (not backed by a JudgeIndex row) to _seed_bottom_tiles.
        # The JudgeIndex.DoesNotExist branch should fire and return without error.
        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        # The home_page from setUp is a plain Page — it has no JudgeIndex row.
        plain_page = Page.objects.get(slug="home-judge-index-test")
        initializer = JudgesPageInitializer()
        # Should return silently without creating any revision on judge_index.
        initializer._seed_bottom_tiles(plain_page)

        self.judge_index.refresh_from_db()
        self.assertIsNone(self.judge_index.latest_revision)


@override_settings(**OVERRIDE)
class JudgesPageInitializerUpdateTest(JudgeIndexSetUpMixin):
    """Tests for JudgesPageInitializer.update() — specifically the title-correction
    branch (WAG-1246) that uses save_revision().publish() instead of a plain save()
    so the Wagtail admin editor stays in sync with the live page model.
    """

    def setUp(self):
        super().setUp()
        self.judge_index.slug = "judges"
        self.judge_index.save()

    def _run_update(self):
        from unittest.mock import patch
        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        initializer = JudgesPageInitializer()
        with (
            patch.object(initializer, "update_judge_roles_and_profiles"),
            patch.object(initializer, "_seed_seminar_disclosures"),
            patch.object(initializer, "_seed_bottom_tiles"),
        ):
            initializer.update()

    def test_update_corrects_stale_title_and_publishes_revision(self):
        # Reproduce the pre-1246 dev-web state: page exists but has the old title.
        self.judge_index.title = "Judges"
        self.judge_index.seo_title = "Judges"
        self.judge_index.save()
        self.assertIsNone(self.judge_index.latest_revision)

        self._run_update()

        self.judge_index.refresh_from_db()
        self.assertEqual(self.judge_index.title, "Judge Information")
        self.assertEqual(self.judge_index.seo_title, "Judge Information")
        # save_revision().publish() must have been called so the admin shows
        # the corrected title, not the stale pre-fix revision.
        self.assertIsNotNone(self.judge_index.latest_revision)
        rev_obj = self.judge_index.latest_revision.as_object()
        self.assertEqual(rev_obj.title, "Judge Information")

    def test_update_skips_title_correction_when_already_correct(self):
        # Title is already "Judge Information" — no revision should be created.
        self.assertIsNone(self.judge_index.latest_revision)

        self._run_update()

        self.judge_index.refresh_from_db()
        self.assertEqual(self.judge_index.title, "Judge Information")
        self.assertIsNone(self.judge_index.latest_revision)

    def test_update_is_noop_when_page_slug_not_found(self):
        # The initializer slug "judges" doesn't match any page.
        self.judge_index.slug = "not-judges"
        self.judge_index.save()

        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        # Should return silently without raising.
        JudgesPageInitializer().update()
