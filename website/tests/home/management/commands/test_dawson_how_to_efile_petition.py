from unittest.mock import patch

from django.core.exceptions import ValidationError
import pytest
from wagtail.models import Collection, Locale, Page, Site

from home.blocks import QuickAccessTileBlock
from home.management.commands.pages.rules_and_guidance.dawson_how_to_efile_petition import (
    DawsonHowToEfilePetitionPageInitializer,
)
from home.management.commands.update_pages import pages_to_update
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript


def create_page_dependencies():
    Locale.objects.get_or_create(language_code="en")
    if Collection.get_first_root_node() is None:
        Collection.add_root(name="Root")

    home_page = Page.objects.filter(slug="home").first()
    if home_page is None:
        home_page = Page.add_root(title="Home", slug="home")
    Site.objects.get_or_create(
        hostname="localhost",
        defaults={"root_page": home_page, "is_default_site": True},
    )
    user_guides_page = home_page.add_child(
        instance=Page(title="DAWSON User Guides", slug="dawson-user-guides")
    )
    filing_checklist_page = home_page.add_child(
        instance=Page(title="Prepare to File", slug="petitioners-prepare-to-file")
    )
    return home_page, user_guides_page, filing_checklist_page


@pytest.mark.django_db
@pytest.mark.parametrize("existing_placeholder", [False, True])
def test_initializer_creates_or_updates_the_dawson_efile_guide(existing_placeholder):
    assert DawsonHowToEfilePetitionPageInitializer in pages_to_update

    home_page, user_guides_page, filing_checklist_page = create_page_dependencies()

    if existing_placeholder:
        placeholder = home_page.add_child(
            instance=PetitionerExperiencePage(
                title="How to e-file a Petition",
                slug="dawson-how-to-e-file-a-petition",
                body=[],
            )
        )
        placeholder.save_revision().publish()
        legacy_script = ExecuteScript.create_script(
            "WAG-1450: How to e-file a Petition", execution_status="SUCCESS"
        )

    with patch.object(
        DawsonHowToEfilePetitionPageInitializer,
        "get_document_url",
        side_effect=lambda filename: f"/documents/{filename}",
    ):
        DawsonHowToEfilePetitionPageInitializer().run()

    page = PetitionerExperiencePage.objects.get(slug="dawson-how-to-e-file-a-petition")
    script = ExecuteScript.objects.get(
        command_name=DawsonHowToEfilePetitionPageInitializer.SCRIPT_NAME
    )
    timeline = page.body[0].value

    assert page.title == "How to e-file a Petition"
    assert page.show_floating_definitions_button is True
    assert (
        page.breadcrumb_title == "DAWSON User Guides & Electronic Filing Instructions"
    )
    assert page.breadcrumb_page_url == user_guides_page.url
    assert timeline["show_title"] is False
    introduction = timeline["introduction"].source
    assert introduction.count("<p>") == 2
    assert (
        "management system.</p><p>In most cases, the Court must receive" in introduction
    )
    assert timeline["show_numbers_in_bubbles"] is True
    assert timeline["warning_callout"]["heading"] == "Important Reminder"
    assert len(timeline["phases"]) == 5
    assert all(not phase.value["your_tasks"] for phase in timeline["phases"])
    assert all(phase.value["default_to_open"] for phase in timeline["phases"])
    assert script.execution_status == "SUCCESS"
    assert page.live

    resource_script = ExecuteScript.objects.get(
        command_name=DawsonHowToEfilePetitionPageInitializer.RESOURCE_SCRIPT_NAME
    )
    resource_tiles = page.resource_cards[0].value["tiles"]
    assert [tile["title"] for tile in resource_tiles] == [
        "DAWSON Self-Represented (Pro se) Electronic Filing Instructions",
        "DAWSON Public Training Guide",
        "DAWSON Training Video: Petitioners",
        "DAWSON User Guides",
        "Filing Checklist - Pro se",
    ]
    assert [tile["icon"]["svg_file"].title for tile in resource_tiles] == [
        "PDF_icon.svg",
        "PDF_icon.svg",
        "videocam-icon.svg",
        "material_info_symbol.svg",
        "material_info_symbol.svg",
    ]
    assert [
        tile["link"][0].block_type == "external_url" for tile in resource_tiles
    ] == [True, True, True, False, False]
    assert resource_tiles[0]["link"][0].value.endswith(
        "DAWSON_Petitioner_Training_Guide.pdf"
    )
    assert resource_tiles[1]["link"][0].value.endswith(
        "DAWSON_Public_Training_Guide.pdf"
    )
    assert resource_tiles[2]["link"][0].value.endswith(
        "petitioners-how-to-efile-a-petition-in-dawson.mp4"
    )
    assert resource_tiles[3]["link"][0].value.pk == user_guides_page.pk
    assert resource_tiles[4]["link"][0].value.pk == filing_checklist_page.pk
    assert resource_script.execution_status == "SUCCESS"
    assert (
        ExecuteScript.objects.get(
            command_name=DawsonHowToEfilePetitionPageInitializer.INFO_ICON_SCRIPT_NAME
        ).execution_status
        == "SUCCESS"
    )

    if existing_placeholder:
        assert page.pk == placeholder.pk
        legacy_script.refresh_from_db()
        assert legacy_script.execution_status == "SUCCESS"
        assert script.pk != legacy_script.pk

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


@pytest.mark.django_db
def test_resource_script_updates_an_existing_page_without_replacing_its_body():
    home_page, _, _ = create_page_dependencies()
    page = home_page.add_child(
        instance=PetitionerExperiencePage(
            title="How to e-file a Petition",
            slug=DawsonHowToEfilePetitionPageInitializer.SLUG,
            body=[],
        )
    )
    page.save_revision().publish()
    ExecuteScript.create_script(
        DawsonHowToEfilePetitionPageInitializer.SCRIPT_NAME,
        execution_status="SUCCESS",
    )

    with patch.object(
        DawsonHowToEfilePetitionPageInitializer,
        "get_document_url",
        side_effect=lambda filename: f"/documents/{filename}",
    ):
        DawsonHowToEfilePetitionPageInitializer().run()

    page.refresh_from_db()
    assert not page.body
    assert len(page.resource_cards[0].value["tiles"]) == 5
    assert (
        ExecuteScript.objects.get(
            command_name=DawsonHowToEfilePetitionPageInitializer.RESOURCE_SCRIPT_NAME
        ).execution_status
        == "SUCCESS"
    )


@pytest.mark.django_db
def test_failed_resource_script_is_retried_on_the_next_run():
    home_page, _, _ = create_page_dependencies()
    page = home_page.add_child(
        instance=PetitionerExperiencePage(
            title="How to e-file a Petition",
            slug=DawsonHowToEfilePetitionPageInitializer.SLUG,
            body=[],
        )
    )
    page.save_revision().publish()
    ExecuteScript.create_script(
        DawsonHowToEfilePetitionPageInitializer.SCRIPT_NAME,
        execution_status="SUCCESS",
    )
    resource_script = DawsonHowToEfilePetitionPageInitializer.RESOURCE_SCRIPT_NAME

    with patch.object(
        DawsonHowToEfilePetitionPageInitializer,
        "get_document_url",
        side_effect=RuntimeError("document missing"),
    ):
        with pytest.raises(RuntimeError):
            DawsonHowToEfilePetitionPageInitializer().run()
    assert ExecuteScript.objects.get(command_name=resource_script).execution_status == (
        "FAILURE"
    )

    with patch.object(
        DawsonHowToEfilePetitionPageInitializer,
        "get_document_url",
        side_effect=lambda filename: f"/documents/{filename}",
    ):
        DawsonHowToEfilePetitionPageInitializer().run()

    page.refresh_from_db()
    assert len(page.resource_cards[0].value["tiles"]) == 5
    assert sorted(
        ExecuteScript.objects.filter(command_name=resource_script).values_list(
            "execution_status", flat=True
        )
    ) == ["FAILURE", "SUCCESS"]


@pytest.mark.django_db
def test_resource_script_populates_an_empty_resource_cards_block():
    home_page, _, _ = create_page_dependencies()
    page = home_page.add_child(
        instance=PetitionerExperiencePage(
            title="How to e-file a Petition",
            slug=DawsonHowToEfilePetitionPageInitializer.SLUG,
            body=[],
            resource_cards=[
                {
                    "type": "quick_access_tiles",
                    "value": {
                        "tiles_hover_enabled": True,
                        "icon_position": "desktop_top_mobile_left",
                        "tiles": [],
                    },
                }
            ],
        )
    )
    page.save_revision().publish()
    assert page.resource_cards
    assert not page.has_resource_tiles

    with patch.object(
        DawsonHowToEfilePetitionPageInitializer,
        "get_document_url",
        side_effect=lambda filename: f"/documents/{filename}",
    ):
        DawsonHowToEfilePetitionPageInitializer().add_resource_cards()

    page.refresh_from_db()
    assert len(page.resource_cards[0].value["tiles"]) == 5


@pytest.mark.django_db
def test_info_icon_update_replaces_existing_resource_card_icons():
    home_page, _, _ = create_page_dependencies()
    initializer = DawsonHowToEfilePetitionPageInitializer()
    old_icon = initializer.load_document_from_documents_dir(
        subdirectory=None,
        filename="PDF_icon.svg",
        title="PDF_icon.svg",
    )
    with patch.object(
        initializer,
        "get_document_url",
        side_effect=lambda filename: f"/documents/{filename}",
    ):
        resource_cards = initializer.build_resource_cards()
    for tile in resource_cards[0]["value"]["tiles"][3:]:
        tile["value"]["icon"]["svg_file"] = old_icon.pk

    page = home_page.add_child(
        instance=PetitionerExperiencePage(
            title=initializer.TITLE,
            slug=initializer.SLUG,
            resource_cards=resource_cards,
        )
    )
    page.save_revision().publish()

    initializer.update_resource_card_info_icons()

    page.refresh_from_db()
    assert [
        tile["icon"]["svg_file"].title
        for tile in page.resource_cards[0].value["tiles"]
        if tile["title"] in {"DAWSON User Guides", "Filing Checklist - Pro se"}
    ] == ["material_info_symbol.svg", "material_info_symbol.svg"]


@pytest.mark.django_db
def test_initializer_defers_when_the_page_has_unpublished_changes():
    home_page, _, _ = create_page_dependencies()
    page = home_page.add_child(
        instance=PetitionerExperiencePage(
            title="How to e-file a Petition",
            slug=DawsonHowToEfilePetitionPageInitializer.SLUG,
            body=[],
        )
    )
    page.save_revision().publish()
    page.introductory_text = "Editor draft"
    page.save_revision()

    assert page.has_unpublished_changes
    assert DawsonHowToEfilePetitionPageInitializer().run() == 0
    assert not page.resource_cards
    assert not ExecuteScript.objects.filter(
        command_name=DawsonHowToEfilePetitionPageInitializer.RESOURCE_SCRIPT_NAME
    ).exists()
    assert not ExecuteScript.objects.filter(
        command_name=DawsonHowToEfilePetitionPageInitializer.INFO_ICON_SCRIPT_NAME
    ).exists()


@pytest.mark.parametrize(
    "links",
    [
        [],
        [{"type": "related_page", "value": None}],
        [{"type": "external_url", "value": ""}],
        [
            {"type": "external_url", "value": "https://example.com/"},
            {"type": "external_url", "value": "https://example.org/"},
        ],
    ],
)
def test_quick_access_tile_link_requires_one_valid_destination(links):
    link_block = QuickAccessTileBlock().child_blocks["link"]
    value = link_block.to_python(links)

    with pytest.raises(ValidationError):
        link_block.clean(value)
