"""Tests for home/utils/custom_link_extractor.py"""

import pytest
from home.utils.custom_link_extractor import CustomLinkExtractor
from home.models.pages.enhanced_standard import EnhancedStandardPage
from wagtail.images.tests.utils import Image, get_test_image_file
from wagtail.models import Collection


class TestCustomExtractor:
    def test_extract_from_value_that_is_empty(self):
        value = ""
        extractor = CustomLinkExtractor()
        result = extractor.extract_from_value(value)

        assert result == []

    @pytest.mark.parametrize(
        "input, expected",
        [
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
                [{"text": "External Button", "url": "https://www.bing.com/"}],
            ),
            (
                {
                    "type": "quick_access_tiles",
                    "value": {
                        "tiles_hover_enabled": True,
                        "icon_position": "desktop_top_mobile_left",
                        "tiles": [
                            {
                                "type": "item",
                                "value": {
                                    "title": "External Link in Quick Access Tile",
                                    "description": '<p data-block-key="qd375">This leads to an external link</p>',
                                    "icon": {"svg_file": 714},
                                    "content_alignment": "center",
                                    "link": [
                                        {
                                            "type": "external_url",
                                            "value": "https://www.google.com",
                                            "id": "b3972343-dec1-4053-9de6-fcf4765ab9a6",
                                        }
                                    ],
                                },
                                "id": "d8c58746-ec7a-439f-a530-a9bc9d6db87d",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "title": "Internal Link in Quick Access Tile",
                                    "description": '<p data-block-key="qd375">This leads to an internal/related link</p>',
                                    "icon": {"svg_file": 714},
                                    "content_alignment": "center",
                                    "link": [
                                        {
                                            "type": "related_page",
                                            "value": 6,
                                            "id": "4b34b7d5-21c0-45d4-8026-dee0d82b974b",
                                        }
                                    ],
                                },
                                "id": "dccecb35-9c20-4d6d-9564-67846dce9906",
                            },
                        ],
                    },
                    "id": "5664774c-265d-4242-b49a-95d003f2f7ce",
                },
                [
                    {
                        "text": "External Link in Quick Access Tile",
                        "url": "https://www.google.com",
                    }
                ],
            ),
            (
                {
                    "type": "card_tiles",
                    "value": {
                        "tiles": [
                            {
                                "type": "item",
                                "value": {
                                    "icon": 718,
                                    "icon_direction": "top",
                                    "card_header": "Internal Link in Card Tile",
                                    "link": [
                                        {
                                            "type": "internal_page",
                                            "value": 3,
                                            "id": "4b30362d-0cf0-486a-ac36-f9bbe5475c81",
                                        }
                                    ],
                                    "card_hover": True,
                                },
                                "id": "7517df62-c468-4a07-b47c-85740af410ba",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "icon": 718,
                                    "icon_direction": "top",
                                    "card_header": "External Link in Card Tile",
                                    "link": [
                                        {
                                            "type": "external_url",
                                            "value": "https://www.firefox.com/en-US/?redirect_source=mozilla-org",
                                            "id": "a784cc9c-adc5-4eac-8f2d-d0350351d479",
                                        }
                                    ],
                                    "card_hover": True,
                                },
                                "id": "f19d1632-330e-4797-814d-43bbc5d35ddf",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "icon": 718,
                                    "icon_direction": "top",
                                    "card_header": "Anchor",
                                    "link": [
                                        {
                                            "type": "anchor_page",
                                            "value": {
                                                "breadcrumb_title": "Anchor Link in Card Tile",
                                                "body": [
                                                    {
                                                        "type": "paragraph",
                                                        "value": '<p data-block-key="bwn6r">hello there</p>',
                                                        "id": "58134c3f-b5f9-4bce-b16d-677d370db29a",
                                                    }
                                                ],
                                            },
                                            "id": "537ebd18-b7cf-4867-8559-234ab21fc22e",
                                        }
                                    ],
                                    "card_hover": True,
                                },
                                "id": "7937eef6-88be-4b99-b750-e57f66181a72",
                            },
                        ],
                        "default_content": [],
                    },
                    "id": "905b8804-60d7-49b4-93e5-79e77e82339d",
                },
                [
                    {
                        "text": "External Link in Card Tile",
                        "url": "https://www.firefox.com/en-US/?redirect_source=mozilla-org",
                    }
                ],
            ),
            # (
            #     {
            #         "type": "image",
            #         "value": {
            #             "image": {
            #                 "image": 30,
            #                 "alt_text": "External Link in Image",
            #                 "decorative": False,
            #             },
            #             "link": [
            #                 {
            #                     "type": "external_url",
            #                     "value": "https://www.google.com",
            #                     "id": "9e652d82-488d-4d6a-b25b-6e4edcec0f0c",
            #                 }
            #             ],
            #         },
            #         "id": "735b91e3-bca6-4559-969f-b494225b6f94",
            #     },
            #     ImageWithLinkBlock,
            #     [{"text": "External Link in Image", "url": "https://www.google.com"}]
            # ),
            (
                {
                    "type": "table",
                    "value": {
                        "columns": [{"type": "text", "heading": "Table Checking Link"}],
                        "rows": [
                            {
                                "values": [
                                    '<p data-block-key="xqdfh"><a href="https://www.msn.com">External Link in Table Cell</a><a class="phone" href="tel:+2025210700">202) 521-0700</a><a href="mailto:dawson.support@ustaxcourt.gov?subject=Assistance%20for%20Dawson"> dawson.support@ustaxcourt.gov</a><a href="#ROPP" title="Individual Rules by Title"><i class=""></i> Individual Rules by Title</a></p>'
                                ]
                            }
                        ],
                        "caption": "",
                    },
                    "id": "5b5d8ffe-0e8d-4a29-8c9b-6a81b9f00938",
                },
                [{"text": "External Link in Table Cell", "url": "https://www.msn.com"}],
            ),
            (
                {
                    "type": "links",
                    "value": {
                        "class": "indented",
                        "links": [
                            {
                                "type": "item",
                                "value": {
                                    "title": "External Link in List of Links",
                                    "icon": "",
                                    "document": None,
                                    "video": None,
                                    "url": "www.google.com",
                                    "text_only": False,
                                },
                                "id": "5c58620c-df4a-4334-8dc3-6ca8938d4603",
                            }
                        ],
                    },
                    "id": "c01d118a-60aa-475c-87b1-ee1cd05d3098",
                },
                [{"text": "External Link in List of Links", "url": "www.google.com"}],
            ),
        ],
    )
    @pytest.mark.django_db
    def test_extract_from_value_returns_expected_result(self, input, expected):
        result = None
        extractor = CustomLinkExtractor()

        page = EnhancedStandardPage(body=[input])
        result = extractor.extract_from_page(page)
        assert result == expected

    @pytest.mark.django_db
    def test_extract_from_imageWithLinkBlock_returns_expected_result(self):
        imageTitle = "External Link in Image"

        rootCollection = Collection.add_root(name="Root")

        testImage = Image.objects.create(
            title=imageTitle, file=get_test_image_file(), collection=rootCollection
        )

        input = {
            "type": "image",
            "value": {
                "image": {
                    "image": testImage.pk,
                    "alt_text": "Image Alt Text",
                    "decorative": False,
                },
                "link": [
                    {
                        "type": "external_url",
                        "value": "https://www.google.com",
                        "id": "9e652d82-488d-4d6a-b25b-6e4edcec0f0c",
                    }
                ],
            },
            "id": "735b91e3-bca6-4559-969f-b494225b6f94",
        }
        expected = [{"text": imageTitle, "url": "https://www.google.com"}]

        extractor = CustomLinkExtractor()

        page = EnhancedStandardPage(body=[input])
        result = extractor.extract_from_page(page)
        assert result == expected
