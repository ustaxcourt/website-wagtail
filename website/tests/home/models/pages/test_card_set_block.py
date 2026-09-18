"""
Unit tests for the Card Set ("card") StreamField block schema on
EnhancedStandardPage, reshaped as part of WAG-1338 to support the
Petitioner Experience card designs: Card Color, Numbered Icon (+
alignment), Title Icon (+ alt text), Card Sub-title, Card Title, Body
Text, and an optional (0-1) Button.
"""

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from wagtail.blocks.list_block import ListBlockValidationError

from home.models.pages.enhanced_standard import EnhancedStandardPage


def get_card_set_block():
    body_field = EnhancedStandardPage._meta.get_field("body")
    return body_field.stream_block.child_blocks["card"]


def get_card_block():
    return get_card_set_block().child_block


class CardColorChoicesTest(SimpleTestCase):
    def test_card_color_has_all_five_expected_options(self):
        color_block = get_card_block().child_blocks["color"]
        choices = list(color_block.field.choices)
        self.assertEqual(
            choices,
            [
                ("white", "White"),
                ("gray", "Gray"),
                ("dark-primary", "Dark-Primary"),
                ("green", "Green"),
                ("yellow", "Yellow"),
            ],
        )


class NumberedIconChoicesTest(SimpleTestCase):
    def test_numbered_icon_has_expected_options_and_font_awesome_classes(self):
        numbered_icon_block = get_card_block().child_blocks["numbered_icon"]
        choices = dict(numbered_icon_block.field.choices)
        self.assertEqual(
            choices,
            {
                "": "None",
                "fa-solid fa-1": "One",
                "fa-solid fa-2": "Two",
                "fa-solid fa-3": "Three",
                "fa-solid fa-check": "Check",
                "fa-solid fa-exclamation": "Exclamation",
            },
        )

    def test_numbered_icon_is_optional(self):
        numbered_icon_block = get_card_block().child_blocks["numbered_icon"]
        self.assertFalse(numbered_icon_block.required)


class NumberedIconAlignmentChoicesTest(SimpleTestCase):
    def test_alignment_has_left_center_right_with_no_blank_option(self):
        alignment_block = get_card_block().child_blocks["numbered_icon_alignment"]
        choices = list(alignment_block.field.choices)
        self.assertEqual(
            choices, [("left", "Left"), ("center", "Center"), ("right", "Right")]
        )

    def test_alignment_is_required_with_a_sensible_default(self):
        alignment_block = get_card_block().child_blocks["numbered_icon_alignment"]
        self.assertTrue(alignment_block.required)
        self.assertEqual(alignment_block.get_default(), "left")


class CardFieldOptionalityTest(SimpleTestCase):
    def test_title_icon_subtitle_title_and_description_are_optional(self):
        card_block = get_card_block()
        for field_name in (
            "title_icon",
            "title_icon_alt_text",
            "subtitle",
            "title",
            "description",
        ):
            with self.subTest(field=field_name):
                self.assertFalse(card_block.child_blocks[field_name].required)

    def test_card_color_is_required(self):
        self.assertTrue(get_card_block().child_blocks["color"].required)


class CardSetMaxCardsTest(SimpleTestCase):
    def _minimal_card(self, title):
        return {
            "color": "white",
            "numbered_icon": "",
            "numbered_icon_alignment": "left",
            "title_icon": None,
            "title_icon_alt_text": "",
            "subtitle": "",
            "title": title,
            "description": "",
            "buttons": [],
        }

    def test_allows_up_to_three_cards(self):
        card_set_block = get_card_set_block()
        raw_data = [self._minimal_card(f"Card {i}") for i in range(3)]
        value = card_set_block.to_python(raw_data)
        # Should not raise.
        card_set_block.clean(value)

    def test_rejects_more_than_three_cards(self):
        card_set_block = get_card_set_block()
        raw_data = [self._minimal_card(f"Card {i}") for i in range(4)]
        value = card_set_block.to_python(raw_data)
        with self.assertRaises(ListBlockValidationError):
            card_set_block.clean(value)


class CardButtonsFieldTest(SimpleTestCase):
    def test_buttons_allows_zero_or_one(self):
        buttons_block = get_card_block().child_blocks["buttons"]
        self.assertEqual(buttons_block.meta.min_num, 0)
        self.assertEqual(buttons_block.meta.max_num, 1)

    def test_buttons_rejects_two(self):
        buttons_block = get_card_block().child_blocks["buttons"]
        button_value = {
            "icon": None,
            "text": "Download",
            "url": [{"type": "external_url", "value": "https://example.com"}],
            "style": "primary",
            "button_hover": True,
        }
        value = buttons_block.to_python([button_value, button_value])
        with self.assertRaises((ListBlockValidationError, ValidationError)):
            buttons_block.clean(value)
