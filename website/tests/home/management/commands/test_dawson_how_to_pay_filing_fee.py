import pytest
from taggit.models import Tag
from wagtail.models import Collection, Locale, Page, Site

from home.management.commands.pages.rules_and_guidance.dawson_how_to_pay_filing_fee import (
    DawsonHowToPayFilingFee,
)
from home.management.commands.update_pages import pages_to_update
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript
from home.utils.document_collection_and_tag_assignment import get_tags_for_document

SLUG = "dawson-how-to-pay-filing-fee"
SCRIPT_NAME = DawsonHowToPayFilingFee.SCRIPT_NAME
PHASE_TITLES = [
    "How to Pay the Filing Fee Online",
    "How to Pay the Filing Fee by Mail, or in Person",
    "Other Filing Fee Options",
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
    for filename in DawsonHowToPayFilingFee.DOCUMENT_FILENAMES.values():
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
            title="How to Pay Filing Fee", slug=SLUG, **kwargs
        )
    )
    placeholder.save_revision().publish()
    return placeholder


def _page():
    return PetitionerExperiencePage.objects.get(slug=SLUG)


def _phases(page):
    return page.body[0].value["phases"]


def _instructions(page):
    return [phase.value["instructions"].source for phase in _phases(page)]


def test_initializer_is_registered_in_update_pages():
    assert DawsonHowToPayFilingFee in pages_to_update


def test_run_creates_the_guide(user_guides_page):
    DawsonHowToPayFilingFee().run()

    page = _page()
    timeline = page.body[0].value
    phases = _phases(page)

    assert page.live
    assert page.title == "How to pay the filing fee"
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
        "info",
        "number",
    ]
    assert all(phase.value["default_to_open"] for phase in phases)
    assert all(not phase.value["your_tasks"] for phase in phases)
    assert (
        ExecuteScript.objects.get(command_name=SCRIPT_NAME).execution_status
        == "SUCCESS"
    )


def test_introduction_links_pay_gov_and_the_uploaded_waiver_form(user_guides_page):
    DawsonHowToPayFilingFee().run()

    introduction = _page().body[0].value["introduction"].source

    assert introduction.count("<p>") == 1
    assert "filing fee is $60" in introduction
    assert '<a href="https://www.pay.gov/public/home">pay.gov</a>' in introduction
    # The waiver form is the uploaded document, so the link stays in this environment.
    assert 'href="/documents/' in introduction
    assert "Application_for_Waiver_of_Filing_Fee" in introduction


def test_online_phase_matches_the_mockup(user_guides_page):
    DawsonHowToPayFilingFee().run()

    online = _instructions(_page())[0]

    assert 'href="https://www.pay.gov/public/form/start/60485840"' in online
    assert "<b>Continue to the Form</b>" in online
    assert "xxxxx-xx format (e.g., 12345-20)" in online
    assert '12345-20L, enter 12345-20 and omit the "L".' in online
    assert "<b>For example</b>" in online
    assert "<b>Submit Payment</b>" in online
    assert "Print Confirmation Page" in online
    assert "<p><b>Tips and Tricks</b></p>" in online
    assert online.count('embedtype="image"') == 3
    # No stray zero-width characters from the mockup text.
    assert "​" not in online
    # Five bullet lists (split up by the screenshots) plus the docket number
    # details nested under the "Fill out personal details" step.
    assert online.count("<ul>") == 6
    assert online.count("</li><ul>") == 0
    assert "(e.g., 12345-20).<ul><li>If your docket number" in online


def test_by_mail_phase_includes_the_check_notice(user_guides_page):
    DawsonHowToPayFilingFee().run()

    by_mail = _instructions(_page())[1]

    assert "<b>Clerk of the Court<br/>United States Tax Court<br/>" in by_mail
    assert "NOTICE TO CUSTOMERS MAKING PAYMENT BY CHECK" in by_mail
    assert "Rule 11</a>" in by_mail
    assert "Sections 7451 &amp; 7471 through 7475" in by_mail
    assert "embedtype" not in by_mail


def test_other_options_phase_lists_the_waiver_steps(user_guides_page):
    DawsonHowToPayFilingFee().run()

    other = _instructions(_page())[2]

    assert "Can't afford to pay the filing fee?" in other
    assert "<ol><li>Fill in the form.</li>" in other
    assert "File the form to your case:<ul>" in other
    assert other.count("<li>") == 5
    assert "400 Second Street, NW" in other


def test_run_adds_the_two_resource_cards(user_guides_page):
    DawsonHowToPayFilingFee().run()

    tiles = _page().resource_cards[0].value["tiles"]

    assert [tile["title"] for tile in tiles] == [
        "United States Tax Court Fees - Petitions",
        "Application for Waiver of Filing Fee",
    ]
    assert all(tile["icon"]["svg_file"].title == "open_in_new.svg" for tile in tiles)
    assert all(len(tile["link"]) == 1 for tile in tiles)
    assert all(tile["link"][0].block_type == "external_url" for tile in tiles)
    assert tiles[0]["link"][0].value == "https://www.pay.gov/public/form/start/60485840"
    assert "Application_for_Waiver_of_Filing_Fee" in tiles[1]["link"][0].value
    assert tiles[1]["link"][0].value.startswith("/documents/")


def test_run_populates_the_empty_placeholder_page(home_page, user_guides_page):
    ribbon = NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")
    placeholder = _add_placeholder(home_page, body=[], navigation_ribbon=ribbon)

    DawsonHowToPayFilingFee().run()

    page = _page()
    assert page.pk == placeholder.pk
    # The placeholder's title is corrected to match the mockup.
    assert page.title == "How to pay the filing fee"
    assert page.seo_title == "How to pay the filing fee"
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

    DawsonHowToPayFilingFee().run()

    page = PetitionerExperiencePage.objects.get(pk=placeholder.pk)
    assert page.title == "How to Pay Filing Fee"
    assert page.body[0].value["title"] == "Edited by an editor"
    assert not page.resource_cards


def test_run_rejects_a_page_that_is_not_a_petitioner_experience_page(
    home_page, user_guides_page
):
    home_page.add_child(instance=Page(title="Wrong type", slug=SLUG))

    with pytest.raises(TypeError):
        DawsonHowToPayFilingFee().run()

    script = ExecuteScript.objects.get(command_name=SCRIPT_NAME)
    assert script.execution_status == "FAILURE"


def test_run_is_skipped_when_it_has_already_run(user_guides_page):
    DawsonHowToPayFilingFee().run()

    assert DawsonHowToPayFilingFee().run() == 0
    assert ExecuteScript.objects.filter(command_name=SCRIPT_NAME).count() == 1


def test_run_raises_without_recording_when_user_guides_page_missing(home_page):
    with pytest.raises(Exception, match="dawson-user-guides"):
        DawsonHowToPayFilingFee().run()

    assert not Page.objects.filter(slug=SLUG).exists()
    assert not ExecuteScript.objects.filter(command_name=SCRIPT_NAME).exists()
