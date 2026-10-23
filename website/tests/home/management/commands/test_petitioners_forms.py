from types import SimpleNamespace

import pytest
import re
from django.template.loader import render_to_string
from django.test import SimpleTestCase
from wagtail.admin.rich_text import get_rich_text_editor_widget
from wagtail.rich_text import RichText
from wagtail.models import Collection, Page, Locale, Site
from taggit.models import Tag
from home.models import NavigationRibbon
from home.models.utils.execute_script import ExecuteScript
from home.management.commands.pages.rules_and_guidance.petitioners_forms import (
    GETTING_STARTED_FORMS,
    SPECIAL_CIRCUMSTANCES_FORMS,
    PetitionersFormsPageInitializer,
)


def test_petitioners_forms_body_contains_editable_download_cards():
    forms = GETTING_STARTED_FORMS + SPECIAL_CIRCUMSTANCES_FORMS
    documents = {
        form["key"]: SimpleNamespace(pk=index)
        for index, form in enumerate(forms, start=1)
    }
    article_icon = SimpleNamespace(pk=20)
    download_icon = SimpleNamespace(pk=21)

    body = PetitionersFormsPageInitializer().build_page_body(
        documents, article_icon, download_icon
    )

    cards = [
        card for block in body if block["type"] == "card" for card in block["value"]
    ]
    assert len(cards) == 6
    assert [card["value"]["title"] for card in cards] == [
        form["title"] for form in forms
    ]
    assert [card["value"]["subtitle"] for card in cards] == [
        form["number"] for form in forms
    ]

    buttons = [card["value"]["buttons"][0]["value"] for card in cards]
    assert [button["text"] for button in buttons] == [
        "Download Form 4",
        "Download Petition Kit",
        "Download Form 2",
        "Download Waiver Application",
        "Download Form 6",
        "Download Motion Template",
    ]
    assert all(card["value"]["color"] == "gray" for card in cards)
    assert all(button["download"] is True for button in buttons)
    assert 'href="/dpt-cities"' in cards[5]["value"]["description"]
    assert all(button["icon"] == download_icon.pk for button in buttons)
    assert all(button["icon_location"] == "before" for button in buttons)
    assert all(card["value"]["title_icon"] == article_icon.pk for card in cards)
    assert all(
        button["url"][0]["value"] == documents[form["key"]].pk
        for button, form in zip(buttons, forms, strict=True)
    )

    paragraphs = [block["value"] for block in body if block["type"] == "paragraph"]
    assert len(paragraphs) == 1
    assert 'href="/files/documents/rule-50.pdf"' in paragraphs[0]

    callouts = [block["value"] for block in body if block["type"] == "callout"]
    assert [callout["heading"] for callout in callouts] == [
        "Note:",
        "Note for Petitioners who file by mail:",
    ]
    assert [callout["callout_type"] for callout in callouts] == ["info", "warning"]
    assert "identity verification instructions" in callouts[1]["text"]
    assert body[-1]["type"] == "callout"


@pytest.mark.parametrize(
    "source",
    [
        "Download forms you may need.",
        '<p>Download <a href="/petitioners-start/">forms</a> you may need.</p>',
        "<p>First paragraph.</p><p>Second paragraph.</p>",
    ],
)
def test_petitioners_forms_paragraphs_do_not_nest_after_editor_save(source):
    converter = get_rich_text_editor_widget("default").converter
    saved_source = converter.to_database_format(converter.from_database_format(source))

    for value in (source, saved_source):
        html = render_to_string(
            "includes/enhanced_body.html",
            {
                "page": SimpleNamespace(slug="petitioners-forms"),
                "blocks": [
                    SimpleNamespace(block_type="paragraph", value=RichText(value))
                ],
            },
        )

        SimpleTestCase().assertHTMLEqual(
            html,
            '<div class="forms-paragraph" data-testid="page-body-paragraph">'
            f"{RichText(value)}</div>",
        )
        assert html.count("<p") == str(RichText(value)).count("<p")


def test_other_pages_keep_existing_paragraph_markup():
    html = render_to_string(
        "includes/enhanced_body.html",
        {
            "page": SimpleNamespace(slug="petitioners-start"),
            "blocks": [
                SimpleNamespace(
                    block_type="paragraph", value=RichText("Existing content.")
                )
            ],
        },
    )

    SimpleTestCase().assertHTMLEqual(
        html, '<p data-testid="page-body-paragraph">Existing content.</p>'
    )


@pytest.mark.django_db
def test_run_without_page_existing_creates_page():
    command_name = "Update Forms to File a Petition content with new intro and callout"

    TAGS_AND_COLLECTION_NAMES = [
        "Administrative Orders",
        "Cases Commenced in the Court of Appeals",
        "Citation and Style Manual",
        "Clinics",
        "DAWSON Training Guides",
        "Directory",
        "Discipline",
        "Engagement & Outreach",
        "Events and Webinars",
        "Fees & Charges",
        "Forms",
        "Guidance for Petitioners",
        "Guidance for Practitioners",
        "History",
        "Internship Programs",
        "Judges & Bios",
        "Judicial Conduct and Disability Procedures",
        "Law Clerk Programs",
        "LITC",
        "Mission Statement",
        "Pamphlets",
        "Press Releases",
        "Pro Bono Programs",
        "Records (Transcripts & Copies)",
        "DAWSON Release Notes",
        "Remote Proceedings",
        "Reports & Statistics",
        "Rules Comments and Suggestions",
        "Tax Court Reports",
        "Tax Court Rules",
        "Trial Sessions",
        "Vacancy Announcements",
    ]

    ROLE_TAGS_NAMES = [
        "Role Content Manager",
        "Role Website Manager",
        "Role Chief Judge",
        "Role Dawson Contributor",
        "Role Public Affairs",
        "Role Clerk Office",
        "Role Hr Committee",
        "Role Pro Se Committee",
        "Role Rules Committee",
        "Role Admissions Committee",
        "Role Ethics Committee",
        "Role Disciplinary Committee",
        "Role Reporters Office",
        "Role Appellate Reports",
        "Role Case Services",
    ]

    Locale.objects.get_or_create(language_code="en")

    Collection.add_root(name="Root")

    root_page = Page.objects.filter(depth=1).first()
    if root_page is None:
        root_page = Page.add_root(title="Root", slug="root")

    home_page = Page(title="Home", slug="home")
    root_page.add_child(instance=home_page)

    Site.objects.get_or_create(
        hostname="localhost",
        defaults={"root_page": home_page, "is_default_site": True},
    )

    NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")

    for tag_name in TAGS_AND_COLLECTION_NAMES:
        slug = re.sub(r"\s+", "-", tag_name.lower())
        # Use the slug to check for existence, and provide the name as a default
        # for creation. This avoids the unique constraint error.
        Tag.objects.get_or_create(slug=slug, defaults={"name": tag_name})

    for tag_name in ROLE_TAGS_NAMES:
        slug = re.sub(r"\s+", "-", tag_name.lower())
        # Use the slug to check for existence, and provide the name as a default
        # for creation. This avoids the unique constraint error.
        Tag.objects.get_or_create(slug=slug, defaults={"name": tag_name})

    assert not ExecuteScript.command_exists(command_name)
    PetitionersFormsPageInitializer().run()
    assert ExecuteScript.command_exists(command_name)
