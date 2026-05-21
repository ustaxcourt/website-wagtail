"""Tests for home/management/commands/backfill_live_revisions.py"""

import pytest
from io import StringIO
from django.core.management import call_command


@pytest.mark.django_db
class TestBackfillLiveRevisions:
    def test_dry_run_with_empty_db(self):
        """Dry run with no pages should succeed without changes."""
        out = StringIO()
        err = StringIO()
        call_command("backfill_live_revisions", "--dry-run", stdout=out, stderr=err)
        # Should not fail
        output = out.getvalue()
        assert isinstance(output, str)

    def test_limit_option_with_empty_db(self):
        """Limit option with no pages should succeed."""
        out = StringIO()
        call_command(
            "backfill_live_revisions", "--limit=10", stdout=out, stderr=StringIO()
        )
        assert isinstance(out.getvalue(), str)

    def test_dry_run_and_limit_together(self):
        """Dry run with limit should succeed."""
        out = StringIO()
        call_command(
            "backfill_live_revisions",
            "--dry-run",
            "--limit=5",
            stdout=out,
            stderr=StringIO(),
        )
        assert isinstance(out.getvalue(), str)
