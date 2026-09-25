from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.test import override_settings

from home.management.commands.snippets.call_to_action_box import (
    CallToActionBoxInitializer,
    snippet_name,
)
from home.models import CallToActionBox


def _button_payload(text, url, icon=None, icon_location="before", style="primary"):
    return [
        {
            "type": "button",
            "value": {
                "icon": icon,
                "icon_location": icon_location,
                "text": text,
                "url": [
                    {
                        "type": "external_url",
                        "value": url,
                        "id": "9c7f0c22-5f0f-4ac6-bd4e-0adbb0a7d2c1",
                    }
                ],
                "style": style,
                "button_hover": True,
            },
            "id": "f5dcb1fa-3c3a-4b6c-b8f0-0d2f0126d1d0",
        }
    ]


@pytest.mark.django_db
@override_settings(SITE_IS_LIVE=False)
def test_update_preserves_unrelated_cta_boxes():
    CallToActionBox.objects.create(
        header="Unrelated CTA",
        body="Keep me",
        buttons=_button_payload("Read more", "https://example.com/keep-me"),
    )
    CallToActionBox.objects.create(
        header=snippet_name,
        body="Old body",
        buttons=_button_payload("Old CTA", "https://example.com/old-cta"),
    )

    initializer = CallToActionBoxInitializer()
    with patch.object(
        CallToActionBoxInitializer,
        "_get_arrow_forward_document",
        return_value=(SimpleNamespace(pk=99), ""),
    ):
        initializer.update()

    assert CallToActionBox.objects.filter(header="Unrelated CTA").count() == 1
    updated_box = CallToActionBox.objects.get(header=snippet_name)
    assert updated_box.body == (
        "Once you have your documents ready, start your petition through DAWSON, "
        "the Court's electronic filing system."
    )


@pytest.mark.django_db
@override_settings(SITE_IS_LIVE=True)
def test_update_is_noop_on_live_site():
    CallToActionBox.objects.create(
        header="Unrelated CTA",
        body="Keep me",
        buttons=_button_payload("Read more", "https://example.com/keep-me"),
    )
    CallToActionBox.objects.create(
        header=snippet_name,
        body="Old body",
        buttons=_button_payload("Old CTA", "https://example.com/old-cta"),
    )

    initializer = CallToActionBoxInitializer()
    with patch.object(
        CallToActionBoxInitializer,
        "_get_arrow_forward_document",
        return_value=(SimpleNamespace(pk=99), ""),
    ):
        initializer.update()

    assert CallToActionBox.objects.filter(header="Unrelated CTA").count() == 1
    assert CallToActionBox.objects.get(header=snippet_name).body == "Old body"
