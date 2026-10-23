from unittest.mock import patch

import pytest
from wagtail.models import Locale, Page, Site

from home.management.commands.pages.rules_and_guidance.dawson_how_to_efile_petition import (
    DawsonHowToEfilePetitionPageInitializer,
)
from home.management.commands.update_pages import pages_to_update
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript


@pytest.mark.django_db
def test_initializer_creates_the_dawson_efile_guide():
    assert DawsonHowToEfilePetitionPageInitializer in pages_to_update

    Locale.objects.get_or_create(language_code="en")
    home_page = Page.add_root(title="Home", slug="home")
    Site.objects.create(hostname="localhost", root_page=home_page, is_default_site=True)
    user_guides_page = home_page.add_child(
        instance=Page(title="DAWSON User Guides", slug="dawson-user-guides")
    )

    with patch.object(
        DawsonHowToEfilePetitionPageInitializer,
        "get_document_url",
        side_effect=lambda filename: f"/documents/{filename}",
    ):
        DawsonHowToEfilePetitionPageInitializer().run()

    page = PetitionerExperiencePage.objects.get(slug="dawson-how-to-e-file-a-petition")
    script = ExecuteScript.objects.get(
        command_name="WAG-1451: Populate How to e-file a Petition User Guide"
    )
    timeline = page.body[0].value

    assert page.title == "How to e-file a Petition"
    assert page.show_floating_definitions_button is True
    assert (
        page.breadcrumb_title == "DAWSON User Guides & Electronic Filing Instructions"
    )
    assert page.breadcrumb_page_url == user_guides_page.url
    assert timeline["show_title"] is False
    assert timeline["show_numbers_in_bubbles"] is True
    assert timeline["warning_callout"]["heading"] == "Important Reminder"
    assert len(timeline["phases"]) == 5
    assert script.execution_status == "SUCCESS"

    with patch.object(
        DawsonHowToEfilePetitionPageInitializer,
        "get_document_url",
        side_effect=lambda filename: f"/documents/{filename}",
    ):
        DawsonHowToEfilePetitionPageInitializer().run()

    assert (
        PetitionerExperiencePage.objects.filter(
            slug="dawson-how-to-e-file-a-petition"
        ).count()
        == 1
    )
    assert ExecuteScript.objects.filter(command_name=script.command_name).count() == 1
