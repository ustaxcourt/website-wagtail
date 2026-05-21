"""Tests for home/management/commands/backfill_live_revisions.py"""

import pytest
from io import StringIO
from django.core.management import call_command
from wagtail.models import Locale, Page


@pytest.fixture
def root_page(db):
    Locale.objects.get_or_create(language_code="en")
    return Page.add_root(title="Root", slug="root")


@pytest.mark.django_db
class TestBackfillLiveRevisions:
    def test_reports_no_backfill_needed_when_no_pages_exist(self):
        out = StringIO()
        call_command("backfill_live_revisions", stdout=out, stderr=StringIO())
        assert "No pages need backfill" in out.getvalue()

    def test_dry_run_does_not_create_live_revision(self, root_page):
        child = root_page.add_child(
            instance=Page(title="Dry Run Test", slug="dry-run-backfill-test", live=True)
        )
        Page.objects.filter(id=child.id).update(live_revision=None)

        call_command(
            "backfill_live_revisions", "--dry-run", stdout=StringIO(), stderr=StringIO()
        )

        child.refresh_from_db()
        assert child.live_revision is None

    def test_backfills_live_revision_for_page_missing_one(self, root_page):
        child = root_page.add_child(
            instance=Page(title="Needs Backfill", slug="needs-backfill-page", live=True)
        )
        Page.objects.filter(id=child.id).update(live_revision=None)
        child.refresh_from_db()
        assert child.live_revision is None

        out = StringIO()
        call_command("backfill_live_revisions", stdout=out, stderr=StringIO())

        child.refresh_from_db()
        assert child.live_revision is not None
        assert "Backfill complete" in out.getvalue()

    def test_limit_caps_pages_processed(self, root_page):
        for i in range(3):
            root_page.add_child(
                instance=Page(
                    title=f"Limit Test {i}", slug=f"limit-backfill-{i}", live=True
                )
            )
        # All pages (root + 3 children) start with live_revision=None
        Page.objects.all().update(live_revision=None)
        needs_backfill_before = Page.objects.filter(
            live_revision__isnull=True, live=True
        ).count()

        call_command(
            "backfill_live_revisions", "--limit=1", stdout=StringIO(), stderr=StringIO()
        )

        needs_backfill_after = Page.objects.filter(
            live_revision__isnull=True, live=True
        ).count()
        assert needs_backfill_after == needs_backfill_before - 1
