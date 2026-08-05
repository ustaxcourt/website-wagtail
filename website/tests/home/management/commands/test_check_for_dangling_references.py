"""Tests for home/management/commands/backfill_live_revisions.py"""

import pytest
from io import StringIO
from django.core.management import call_command
from wagtail.models import Locale, Page
from home.models.pages.enhanced_standard import EnhancedStandardPage


@pytest.fixture
def root_page(db):
    Locale.objects.get_or_create(language_code="en")
    return Page.add_root(title="Root", slug="root")


@pytest.mark.django_db
class TestCheckForDanglingReferences:
    def test_no_dangling_references_when_chosen_page_has_no_content(self, root_page):
        child = root_page.add_child(
            instance=Page(
                title="Home Page Substitute", slug="home-page-substitute", live=True
            )
        )

        out = StringIO()
        call_command("check_for_dangling_references", stdout=out)

        assert f"Starting Page ID: {child.id}" in out.getvalue()
        assert "Broken references: 0" in out.getvalue()

    def test_dangling_reference_found_when_chosen_page_has_content_with_dangling_reference(
        self, root_page
    ):
        child = root_page.add_child(
            instance=Page(
                title="Home Page Substitute", slug="home-page-substitute", live=True
            )
        )

        child.add_child(
            instance=EnhancedStandardPage(
                title="Bad Page",
                slug="bad-page",
                live=True,
                body=[
                    {
                        "type": "paragraph",
                        "value": '<p data-block-key="9cba2"><a linktype="document" id="2">appellate_report_april_2025.pdf</a></p>',
                        "id": "6588f81b-a575-4806-a951-dd616217b56f",
                    }
                ],
            )
        )

        out = StringIO()
        call_command("check_for_dangling_references", stdout=out)

        assert f"Starting Page ID: {child.id}" in out.getvalue()
        assert "Broken references: 1" in out.getvalue()
