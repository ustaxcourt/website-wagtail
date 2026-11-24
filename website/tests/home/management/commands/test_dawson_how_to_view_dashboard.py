import pytest
from taggit.models import Tag
from wagtail.models import Collection, Locale, Page, Site

from home.management.commands.pages.rules_and_guidance.dawson_how_to_view_dashboard import (
    DawsonHowToViewDashboard,
)
from home.management.commands.pages.rules_and_guidance.side_card_seed_data import (
    add_need_legal_help_side_card,
)
from home.management.commands.update_pages import pages_to_update
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript
from home.utils.document_collection_and_tag_assignment import get_tags_for_document

SLUG = "dawson-how-to-view-dashboard"
SCRIPT_NAME = DawsonHowToViewDashboard.SCRIPT_NAME


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
    for filename in DawsonHowToViewDashboard.DOCUMENT_FILENAMES.values():
        for tag_name in get_tags_for_document(filename):
            Tag.objects.get_or_create(name=tag_name)
    return home_page


@pytest.fixture
def user_guides_page(home_page):
    return home_page.add_child(
        instance=Page(title="DAWSON User Guides", slug="dawson-user-guides")
    )


def _add_placeholder(home_page, **kwargs):
    placeholder = home_page.add_child(
        instance=PetitionerExperiencePage(
            title="How to view the DAWSON dashboard", slug=SLUG, **kwargs
        )
    )
    placeholder.save_revision().publish()
    return placeholder


def _page(slug=SLUG):
    return PetitionerExperiencePage.objects.get(slug=slug)


def _tiles(page):
    return page.resource_cards[0].value["tiles"]


def test_initializer_is_registered_in_update_pages():
    assert DawsonHowToViewDashboard in pages_to_update


def test_run_creates_the_guide(user_guides_page):
    DawsonHowToViewDashboard().run()

    page = _page()
    timeline = page.body[0].value
    phases = timeline["phases"]

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
    assert timeline["introduction"].source.count("<p>") == 2
    assert [phase.value["title"] for phase in phases] == [
        "Access Your Dashboard",
        "Tips and Tricks",
    ]
    assert [phase.value["bubble_content"] for phase in phases] == ["number", "info"]
    assert all(phase.value["default_to_open"] for phase in phases)
    assert all(not phase.value["your_tasks"] for phase in phases)
    assert (
        ExecuteScript.objects.get(command_name=SCRIPT_NAME).execution_status
        == "SUCCESS"
    )


def test_phase_content_matches_the_mockup(user_guides_page):
    DawsonHowToViewDashboard().run()

    access, tips = [
        phase.value["instructions"].source for phase in _page().body[0].value["phases"]
    ]

    assert "<b>My Cases</b>" in access
    assert "(open and closed)" in access
    assert "It is typical for a self-represented (pro se) petitioner" in access
    assert access.count('embedtype="image"') == 2
    assert tips.count("<li>") == 4
    assert "The number of cases for each is displayed in parentheses." in tips
    assert "embedtype" not in tips


def test_run_adds_the_four_resource_cards(user_guides_page):
    DawsonHowToViewDashboard().run()

    tiles = _tiles(_page())

    assert [tile["title"] for tile in tiles] == [
        "DAWSON Self-Represented (Pro se) Electronic Filing Instructions",
        "DAWSON Practitioner Electronic Filing Instructions",
        "Case Related Forms",
        "Places of Trial",
    ]
    assert [tile["icon"]["svg_file"].title for tile in tiles] == [
        "PDF_icon.svg",
        "PDF_icon.svg",
        "PDF_icon.svg",
        "icon-account-balance.svg",
    ]
    assert all(len(tile["link"]) == 1 for tile in tiles)
    # The two guides link to the uploaded documents, so they stay in this environment.
    assert all(tiles[index]["link"][0].block_type == "external_url" for index in (0, 1))
    assert "DAWSON_Petitioner_Training_Guide" in tiles[0]["link"][0].value
    assert "DAWSON_Practitioner_Training_Guide" in tiles[1]["link"][0].value


def test_resource_cards_fall_back_to_public_urls_when_pages_are_missing(
    user_guides_page,
):
    DawsonHowToViewDashboard().run()

    tiles = _tiles(_page())

    assert tiles[2]["link"][0].block_type == "external_url"
    assert tiles[2]["link"][0].value == "https://ustaxcourt.gov/case-related-forms/"
    assert tiles[3]["link"][0].block_type == "external_url"
    assert tiles[3]["link"][0].value == "https://ustaxcourt.gov/dpt-cities"


def test_resource_cards_link_to_the_site_pages_when_they_exist(
    home_page, user_guides_page
):
    forms = home_page.add_child(
        instance=Page(title="Case Related Forms", slug="case-related-forms")
    )
    places = home_page.add_child(instance=Page(title="Places", slug="dpt-cities"))

    DawsonHowToViewDashboard().run()

    tiles = _tiles(_page())
    assert tiles[2]["link"][0].block_type == "related_page"
    assert tiles[2]["link"][0].value.pk == forms.pk
    assert tiles[3]["link"][0].block_type == "related_page"
    assert tiles[3]["link"][0].value.pk == places.pk


def test_run_adds_the_need_legal_help_side_card(user_guides_page):
    DawsonHowToViewDashboard().run()

    card = _page().side_cards.get()

    assert card.header_title == "Need Legal Help?"
    assert card.color == "navy"
    assert card.link_display_style == "button"
    assert "free or low-cost representation" in card.introductory_text
    link = card.links[0].value
    assert link["text"] == "Find an LITC Near You"
    assert link["style"] == "inverted-primary"
    assert link["icon"] == "open_in_new"


def test_run_populates_the_empty_placeholder_page(home_page, user_guides_page):
    ribbon = NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")
    placeholder = _add_placeholder(home_page, body=[], navigation_ribbon=ribbon)

    DawsonHowToViewDashboard().run()

    page = _page()
    assert page.pk == placeholder.pk
    assert page.navigation_ribbon is None
    assert len(page.body[0].value["phases"]) == 2
    assert page.breadcrumb_page_url == user_guides_page.url
    assert len(_tiles(page)) == 4
    assert page.side_cards.count() == 1
    assert ExecuteScript.objects.filter(command_name=SCRIPT_NAME).count() == 1


def test_run_does_not_duplicate_an_existing_side_card(home_page, user_guides_page):
    placeholder = _add_placeholder(home_page, body=[])
    add_need_legal_help_side_card(DawsonHowToViewDashboard(), placeholder)

    DawsonHowToViewDashboard().run()

    assert _page().side_cards.count() == 1


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

    DawsonHowToViewDashboard().run()

    page = PetitionerExperiencePage.objects.get(pk=placeholder.pk)
    assert page.body[0].value["title"] == "Edited by an editor"
    assert not page.resource_cards
    assert page.side_cards.count() == 0


def test_run_rejects_a_page_that_is_not_a_petitioner_experience_page(
    home_page, user_guides_page
):
    home_page.add_child(instance=Page(title="Wrong type", slug=SLUG))

    with pytest.raises(TypeError):
        DawsonHowToViewDashboard().run()

    script = ExecuteScript.objects.get(command_name=SCRIPT_NAME)
    assert script.execution_status == "FAILURE"


def test_run_is_skipped_when_it_has_already_run(user_guides_page):
    DawsonHowToViewDashboard().run()

    assert DawsonHowToViewDashboard().run() == 0
    assert ExecuteScript.objects.filter(command_name=SCRIPT_NAME).count() == 1


def test_run_raises_without_recording_when_user_guides_page_missing(home_page):
    with pytest.raises(Exception, match="dawson-user-guides"):
        DawsonHowToViewDashboard().run()

    assert not Page.objects.filter(slug=SLUG).exists()
    assert not ExecuteScript.objects.filter(command_name=SCRIPT_NAME).exists()
