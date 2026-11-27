import pytest
from wagtail.models import Collection, Locale, Page, Site

from home.management.commands.pages.rules_and_guidance.dawson_how_to_search_for_a_case import (
    DawsonHowToSearchForACase,
)
from home.management.commands.update_pages import pages_to_update
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript

SLUG = "dawson-how-to-search-for-a-case"


@pytest.fixture
def home_page(db):
    Locale.objects.get_or_create(language_code="en")
    if not Collection.objects.exists():
        Collection.add_root(name="Root")
    home_page = Page.objects.filter(slug="home").first()
    if home_page is None:
        home_page = Page.add_root(title="Home", slug="home")
    Site.objects.get_or_create(
        hostname="localhost",
        defaults={"root_page": home_page, "is_default_site": True},
    )
    return home_page


@pytest.fixture
def user_guides_page(home_page):
    return home_page.add_child(
        instance=Page(title="DAWSON User Guides", slug="dawson-user-guides")
    )


def _add_placeholder(home_page, **kwargs):
    placeholder = home_page.add_child(
        instance=PetitionerExperiencePage(
            title="How to search for a case", slug=SLUG, **kwargs
        )
    )
    placeholder.save_revision().publish()
    return placeholder


def _phases(page):
    return page.body[0].value["phases"]


def test_initializer_is_registered_in_update_pages():
    assert DawsonHowToSearchForACase in pages_to_update


def test_run_creates_the_guide(user_guides_page):
    DawsonHowToSearchForACase().run()

    page = PetitionerExperiencePage.objects.get(slug=SLUG)
    timeline = page.body[0].value
    phases = _phases(page)

    assert page.live
    assert page.show_floating_definitions_button is True
    assert page.navigation_ribbon is None
    assert page.breadcrumb_page_url == user_guides_page.url
    assert (
        page.breadcrumb_title == "DAWSON User Guides & Electronic Filing Instructions"
    )
    assert timeline["show_title"] is False
    assert timeline["print_button_text"] == "Print"
    assert timeline["show_numbers_in_bubbles"] is True
    assert "Docket Access Within and Secure Online Network" in (
        timeline["introduction"].source
    )
    assert [phase.value["title"] for phase in phases] == [
        "Search by Docket Number",
        "Search by Petitioner Name",
        "Tips and Tricks",
    ]
    assert [phase.value["bubble_content"] for phase in phases] == [
        "number",
        "number",
        "info",
    ]
    assert not any(phase.value["default_to_open"] for phase in phases)
    assert all(not phase.value["your_tasks"] for phase in phases)
    assert all(not phase.value["helpful_information"] for phase in phases)
    assert ExecuteScript.objects.get(
        command_name=DawsonHowToSearchForACase.SCRIPT_NAME
    ).execution_status == ("SUCCESS")


def test_phase_content_matches_the_mockup(user_guides_page):
    DawsonHowToSearchForACase().run()

    docket, name, tips = [
        phase.value["instructions"].source
        for phase in _phases(PetitionerExperiencePage.objects.get(slug=SLUG))
    ]

    assert "The docket number must include the dash (for example, 123-18)." in docket
    assert "(S, L, SL, R, X, D, or P)" in docket
    assert '"No Matches Found"' in docket
    assert "<b>Case</b> tab" in docket
    assert docket.count('embedtype="image"') == 1

    assert "Partial name searches are not currently supported." in name
    assert name.count("<li>") == 6
    assert "<li>Case Type (Docket Suffix)</li>" in name
    assert "U.S. Territories and military bases are included." in name
    assert name.count('embedtype="image"') == 1

    assert tips.count("<li>") == 4
    assert "Apply filters to refine your search results." in tips
    assert "embedtype" not in tips


def test_run_adds_a_single_dawson_resource_card(user_guides_page):
    DawsonHowToSearchForACase().run()

    page = PetitionerExperiencePage.objects.get(slug=SLUG)
    tiles = page.resource_cards[0].value["tiles"]

    assert len(tiles) == 1
    assert tiles[0]["title"] == "DAWSON"
    assert tiles[0]["icon"]["svg_file"].title == "DAWSON_logo.svg"
    assert len(tiles[0]["link"]) == 1
    assert tiles[0]["link"][0].block_type == "external_url"
    # Local/dev/sandbox are all non-production, so they use the dev DAWSON.
    assert tiles[0]["link"][0].value == "https://dev.ef-cms.ustaxcourt.gov/"


def test_run_uses_production_dawson_url_in_production(user_guides_page, settings):
    settings.ENVIRONMENT = "production"

    DawsonHowToSearchForACase().run()

    tiles = (
        PetitionerExperiencePage.objects.get(slug=SLUG).resource_cards[0].value["tiles"]
    )
    assert tiles[0]["link"][0].value == "https://dawson.ustaxcourt.gov/"


def test_run_populates_the_empty_placeholder_page(home_page, user_guides_page):
    ribbon = NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")
    placeholder = _add_placeholder(home_page, body=[], navigation_ribbon=ribbon)

    DawsonHowToSearchForACase().run()

    page = PetitionerExperiencePage.objects.get(slug=SLUG)
    assert page.pk == placeholder.pk
    assert page.navigation_ribbon is None
    assert [phase.value["title"] for phase in _phases(page)] == [
        "Search by Docket Number",
        "Search by Petitioner Name",
        "Tips and Tricks",
    ]
    assert page.breadcrumb_page_url == user_guides_page.url
    assert len(page.resource_cards[0].value["tiles"]) == 1
    assert (
        ExecuteScript.objects.filter(
            command_name=DawsonHowToSearchForACase.SCRIPT_NAME
        ).count()
        == 1
    )


def test_run_does_not_overwrite_a_page_that_already_has_content(
    home_page, user_guides_page
):
    placeholder = _add_placeholder(
        home_page,
        body=[
            {
                "type": "detailed_timeline",
                "value": {
                    "title": "Edited by an editor",
                    "introduction": "<p>Edited</p>",
                    "print_button_text": "Print",
                    "phases": [],
                },
            }
        ],
    )

    DawsonHowToSearchForACase().run()

    page = PetitionerExperiencePage.objects.get(pk=placeholder.pk)
    assert page.body[0].value["title"] == "Edited by an editor"
    assert not page.resource_cards


def test_run_rejects_a_page_that_is_not_a_petitioner_experience_page(
    home_page, user_guides_page
):
    home_page.add_child(instance=Page(title="Wrong type", slug=SLUG))

    with pytest.raises(TypeError):
        DawsonHowToSearchForACase().run()

    script = ExecuteScript.objects.get(
        command_name=DawsonHowToSearchForACase.SCRIPT_NAME
    )
    assert script.execution_status == "FAILURE"


def test_run_is_skipped_when_it_has_already_run(user_guides_page):
    DawsonHowToSearchForACase().run()

    assert DawsonHowToSearchForACase().run() == 0
    assert (
        ExecuteScript.objects.filter(
            command_name=DawsonHowToSearchForACase.SCRIPT_NAME
        ).count()
        == 1
    )


def test_run_raises_without_recording_when_user_guides_page_missing(home_page):
    with pytest.raises(Exception, match="dawson-user-guides"):
        DawsonHowToSearchForACase().run()

    assert not Page.objects.filter(slug=SLUG).exists()
    assert not ExecuteScript.objects.filter(
        command_name=DawsonHowToSearchForACase.SCRIPT_NAME
    ).exists()
