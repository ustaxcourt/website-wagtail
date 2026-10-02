from types import SimpleNamespace

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
    assert [button["text"] for button in buttons] == [form["button"] for form in forms]
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
