"""Tests for home/utils/custom_link_extractor.py"""

import pytest
from home.utils.custom_link_extractor import CustomLinkExtractor

# from wagtail.rich_text import RichText
# from wagtail.contrib.typed_table_block.blocks import TypedTable
from home.models.custom_blocks.button import ButtonBlock
# from home.blocks import QuickAccessTileBlock
# from home.models.pages.enhanced_standard import CardTileBlock
# from home.models.custom_blocks.image_with_link import ImageWithLinkBlock


class TestCustomExtractor:
    def test_extract_from_value_that_is_empty(self):
        value = ""
        extractor = CustomLinkExtractor()
        result = extractor.extract_from_value(value)

        assert not any(result)

    @pytest.mark.parametrize(
        "input, type, expected",
        [
            (
                {"title": "test title", "url": "test url"},
                dict,
                [{"text": "test title", "url": "test url"}],
            ),
            (
                {
                    "type": "button",
                    "value": {
                        "icon": None,
                        "text": "External Button",
                        "url": [
                            {
                                "type": "external_url",
                                "value": "https://www.bing.com/",
                                "id": "a8f047ac-8af3-431c-a295-23ee03f88cd7",
                            }
                        ],
                        "style": "primary",
                        "button_hover": True,
                    },
                    "id": "50c4d553-7c32-453e-a705-c244874ddf63",
                },
                ButtonBlock,
                [{"text": "External Button", "url": "https://www.bing.com/"}],
            ),
        ],
    )
    def test_extract_from_value_returns_expected_result(self, input, type, expected):
        obj = None
        result = None
        extractor = CustomLinkExtractor()

        if type is dict:
            obj_value = input
        else:
            obj = type()
            # for key, value in input['value'].items():
            #     setattr(obj, key, value)
            obj_value = obj.to_python(input["value"])

        result = extractor.extract_from_value(obj_value)
        assert result == expected
