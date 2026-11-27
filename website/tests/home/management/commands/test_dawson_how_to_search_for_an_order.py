import pytest
from wagtail.models import Collection, Locale, Page, Site

from home.management.commands.pages.rules_and_guidance.dawson_how_to_search_for_an_order import (
    DawsonHowToSearchForAnOrder,
)
from home.management.commands.update_pages import pages_to_update
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript

SLUG = "dawson-how-to-search-for-an-order"
SCRIPT_NAME = DawsonHowToSearchForAnOrder.SCRIPT_NAME
PHASE_TITLES = [
    "Access Order Search",
    "Search by Keyword, Phrase, Judge, or Date",
    "Search by Docket Number or Case Title/Petitioner Name",
    "Review Search Results",
    "Tips and Tricks",
]


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
            title="How to search for an order", slug=SLUG, **kwargs
        )
    )
    placeholder.save_revision().publish()
    return placeholder


def _phases(page):
    return page.body[0].value["phases"]


def _instructions(page):
    return [phase.value["instructions"].source for phase in _phases(page)]


def test_initializer_is_registered_in_update_pages():
    assert DawsonHowToSearchForAnOrder in pages_to_update


def test_run_creates_the_guide(user_guides_page):
    DawsonHowToSearchForAnOrder().run()

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
    assert [phase.value["title"] for phase in phases] == PHASE_TITLES
    assert [phase.value["bubble_content"] for phase in phases] == [
        "number",
        "number",
        "number",
        "number",
        "info",
    ]
    assert not any(phase.value["default_to_open"] for phase in phases)
    assert all(not phase.value["your_tasks"] for phase in phases)
    assert (
        ExecuteScript.objects.get(command_name=SCRIPT_NAME).execution_status
        == "SUCCESS"
    )


def test_introduction_links_todays_orders_in_this_environment(user_guides_page):
    DawsonHowToSearchForAnOrder().run()

    introduction = (
        PetitionerExperiencePage.objects.get(slug=SLUG)
        .body[0]
        .value["introduction"]
        .source
    )

    assert "An order is a written direction or command issued by a Judge." in (
        introduction
    )
    assert introduction.count("<p>") == 3
    # Non-production environments link to the dev DAWSON, never to production.
    assert 'href="https://dev.ef-cms.ustaxcourt.gov/todays-orders"' in introduction


def test_phase_content_matches_the_mockup(user_guides_page):
    DawsonHowToSearchForAnOrder().run()

    access, keyword, docket, results, tips = _instructions(
        PetitionerExperiencePage.objects.get(slug=SLUG)
    )

    assert "<b>Petitioner/Public</b>" in access
    assert "<b>Practitioner</b>" in access
    assert access.count('embedtype="image"') == 3

    assert "<b>Search by Keyword or Phrase</b>" in keyword
    assert "Pharase" not in keyword
    assert "<b>OR ( | )</b>" in keyword
    assert "<b>AND ( + )</b>" in keyword
    assert "<b>Example</b>: Lien | Levy" in keyword
    assert "Note: the default is “All judges”." in keyword
    assert keyword.count("<li>") == 7

    assert "To search orders by docket number:" in docket
    assert "To search orders by case title or petitioner name:" in docket
    assert docket.count("<li>") == 2

    assert "returned the first 5,000 matches" in results
    assert results.count('embedtype="image"') == 1

    assert "Searches are not case sensitive." in tips
    assert "No Matches Found. Check your search terms and try again." in tips
    assert "embedtype" not in tips


def test_run_adds_the_resource_cards(user_guides_page):
    DawsonHowToSearchForAnOrder().run()

    tiles = (
        PetitionerExperiencePage.objects.get(slug=SLUG).resource_cards[0].value["tiles"]
    )

    assert [tile["title"] for tile in tiles] == ["DAWSON", "Today’s Orders"]
    assert [tile["icon"]["svg_file"].title for tile in tiles] == [
        "DAWSON_logo.svg",
        "scales_icon.svg",
    ]
    assert all(len(tile["link"]) == 1 for tile in tiles)
    assert all(tile["link"][0].block_type == "external_url" for tile in tiles)
    assert [tile["link"][0].value for tile in tiles] == [
        "https://dev.ef-cms.ustaxcourt.gov/",
        "https://dev.ef-cms.ustaxcourt.gov/todays-orders",
    ]


def test_run_uses_production_dawson_urls_in_production(user_guides_page, settings):
    settings.ENVIRONMENT = "production"

    DawsonHowToSearchForAnOrder().run()

    page = PetitionerExperiencePage.objects.get(slug=SLUG)
    tiles = page.resource_cards[0].value["tiles"]
    assert [tile["link"][0].value for tile in tiles] == [
        "https://dawson.ustaxcourt.gov/",
        "https://dawson.ustaxcourt.gov/todays-orders",
    ]
    assert 'href="https://dawson.ustaxcourt.gov/todays-orders"' in (
        page.body[0].value["introduction"].source
    )


def test_run_populates_the_empty_placeholder_page(home_page, user_guides_page):
    ribbon = NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")
    placeholder = _add_placeholder(home_page, body=[], navigation_ribbon=ribbon)

    DawsonHowToSearchForAnOrder().run()

    page = PetitionerExperiencePage.objects.get(slug=SLUG)
    assert page.pk == placeholder.pk
    assert page.navigation_ribbon is None
    assert [phase.value["title"] for phase in _phases(page)] == PHASE_TITLES
    assert page.breadcrumb_page_url == user_guides_page.url
    assert len(page.resource_cards[0].value["tiles"]) == 2
    assert ExecuteScript.objects.filter(command_name=SCRIPT_NAME).count() == 1


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

    DawsonHowToSearchForAnOrder().run()

    page = PetitionerExperiencePage.objects.get(pk=placeholder.pk)
    assert page.body[0].value["title"] == "Edited by an editor"
    assert not page.resource_cards


def test_run_rejects_a_page_that_is_not_a_petitioner_experience_page(
    home_page, user_guides_page
):
    home_page.add_child(instance=Page(title="Wrong type", slug=SLUG))

    with pytest.raises(TypeError):
        DawsonHowToSearchForAnOrder().run()

    script = ExecuteScript.objects.get(command_name=SCRIPT_NAME)
    assert script.execution_status == "FAILURE"


def test_run_is_skipped_when_it_has_already_run(user_guides_page):
    DawsonHowToSearchForAnOrder().run()

    assert DawsonHowToSearchForAnOrder().run() == 0
    assert ExecuteScript.objects.filter(command_name=SCRIPT_NAME).count() == 1


def test_run_raises_without_recording_when_user_guides_page_missing(home_page):
    with pytest.raises(Exception, match="dawson-user-guides"):
        DawsonHowToSearchForAnOrder().run()

    assert not Page.objects.filter(slug=SLUG).exists()
    assert not ExecuteScript.objects.filter(command_name=SCRIPT_NAME).exists()
