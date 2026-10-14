from types import SimpleNamespace

import pytest
from django.template.loader import render_to_string
from django.test import SimpleTestCase
from wagtail.admin.rich_text import get_rich_text_editor_widget
from wagtail.rich_text import RichText

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

    special_description = body[4]["value"]
    assert 'href="/files/documents/rule-50.pdf"' in special_description
    assert body[-1]["type"] == "callout"
    assert body[-1]["value"]["callout_type"] == "info"


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
