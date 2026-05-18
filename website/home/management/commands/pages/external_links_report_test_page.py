"""
Test page initializer for validating that external links in different components
appear in the External Links Report.
This creates an EnhancedStandardPage with components that can hold an external link.
For local testing only.
"""

from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)


class ExternalLinksReportTestPageInitializer(PageInitializer):
    """
    Creates a test page with components containing an external link.
    """

    def __init__(self):
        super().__init__()
        self.slug = "external-links-report-test"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.info("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "External Links Report Test Page"

        if Page.objects.filter(slug=self.slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        body = [
            {
                "type": "button",
                "value": {
                    "icon": None,
                    "text": "PDF Button",
                    "url": [
                        {
                            "type": "internal_pdf",
                            "value": 708,
                            "id": "8aa40708-d47d-41e6-a68c-33c190c7ddea",
                        }
                    ],
                    "style": "primary",
                    "button_hover": True,
                },
                "id": "156a2bcd-5183-4557-bb6f-ac82514ad7fa",
            },
            {
                "type": "button",
                "value": {
                    "icon": None,
                    "text": "Internal Button",
                    "url": [
                        {
                            "type": "internal_page",
                            "value": 6,
                            "id": "3b8629dd-804c-4368-a58d-86ba94041410",
                        }
                    ],
                    "style": "primary",
                    "button_hover": True,
                },
                "id": "0a70f3ff-b8ac-499c-a07e-73c9fea7f801",
            },
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
            {
                "type": "paragraph",
                "value": '<p data-block-key="1wv5f">This is to test the <a href="#btn-6-accordian">Anchor Link in Paragraph</a> on page</p><p data-block-key="d4osk">This is to test the <a href="https://ustaxcourt.gov/court-fees/#btn-4-accordian">Anchor Link in Paragraph on different page</a></p><p data-block-key="2i48b">Checking <a linktype="page" id="6">Internal Link</a></p><p data-block-key="cljnb">Checking <a href="https://www.youtube.com/?themeRefresh=1">External Link in Paragraph</a></p>',
                "id": "9112521b-26b2-4177-b95f-cf49cb4dffe7",
            },
            {
                "type": "photo_dedication",
                "value": {
                    "image_position": "left",
                    "title": "This is a photo + text to see if anchor works",
                    "photo": 31,
                    "alt_text": "This is an image",
                    "paragraph_text": '<p data-block-key="1h5e8">Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.</p><p data-block-key="8coe5">Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.</p><p data-block-key="2qon5">Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.</p><p data-block-key="fcof1"><a href="https://guides.18f.org/">External Link in Paragraph of Photo + Text</a></p>',
                    "link": [],
                },
                "id": "eb7ef844-0e52-45a2-923f-430a4e87dffe",
            },
            {
                "type": "accordian",
                "value": {
                    "title": "This is an accordion",
                    "description": [
                        {
                            "type": "prose",
                            "value": '<p data-block-key="byr0k">Text that goes into accordian <a href="https://webaim.org/resources/contrastchecker/">External Link in Prose of Accordian Block</a></p>',
                            "id": "aab4950a-e9f0-45d4-9890-fe1a78e9df77",
                        }
                    ],
                    "default_to_open": False,
                },
                "id": "d97b487d-3c30-423f-9f42-a0b0ccf869bb",
            },
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
            {
                "type": "grid",
                "value": {
                    "columns": "1",
                    "width": "full",
                    "gridStyle": "styled",
                    "cells": [
                        {
                            "type": "item",
                            "value": {
                                "header": "This is a grid",
                                "header_color": "#f1f9fc",
                                "caption": '<p data-block-key="7lenn">this is a caption for grid. <a href="https://ustc-isd.monday.com/auth/login_monday/email_password">External Link in Grid Cell Caption</a></p>',
                                "italic_caption": False,
                                "body": [
                                    {
                                        "type": "prose",
                                        "value": '<p data-block-key="ipqmw"><a href="https://www.section508.gov/training/web-software/andi-training-videos/">External Link in Grid Cell Body</a></p>',
                                        "id": "3a05d75c-7194-4f44-801b-ed9e3ae53966",
                                    }
                                ],
                            },
                            "id": "92da3bc3-7cbb-4c5e-b7fc-ab453128e94d",
                        }
                    ],
                },
                "id": "d409a5b7-d189-4aef-ab4f-5d24145f96cb",
            },
            {
                "type": "enhanced_table",
                "value": {
                    "header": "This is a table",
                    "caption": '<p data-block-key="l43en">A space for the caption</p>',
                    "caption_location": "top",
                    "style": "styled",
                    "fixed": False,
                    "table": {
                        "columns": [{"type": "components", "heading": "Checking Link"}],
                        "rows": [
                            {
                                "values": [
                                    [
                                        {
                                            "type": "text",
                                            "value": '<p data-block-key="805i1"><a href="https://www.ssa.gov/accessibility/andi/help/install.html">External Link in Enhanced Table Cell</a></p>',
                                            "id": "c884132b-c514-46e6-abdb-9f97df3ffdf1",
                                        }
                                    ]
                                ]
                            }
                        ],
                        "caption": "",
                    },
                },
                "id": "5eeeda81-a38b-42d5-a85a-bfc00b61af42",
            },
            {
                "type": "alert",
                "value": {
                    "alert_type": "info",
                    "content": '<p data-block-key="iyt9o"><a href="https://www.google.com">External Link in Alert</a></p>',
                },
                "id": "5f48de91-1cbe-4149-9020-3cc546798032",
            },
            {
                "type": "callout",
                "value": {
                    "heading": "callout test",
                    "text": '<p data-block-key="xa6hs"><a href="https://www.google.com">External Link in Callout Block</a></p>',
                    "callout_type": "info",
                },
                "id": "e00f047d-eeb8-4875-9ac9-8d43efba1462",
            },
            {
                "type": "embedded_video",
                "value": {
                    "title": "",
                    "description": '<p data-block-key="y04su"><a href="https://www.youtube.com">External Link in Video Embed</a></p>',
                    "video_url": "https://www.youtube.com/embed/sF80I-TQiW0",
                    "text_location": "below",
                },
                "id": "578d1ed5-aebe-4c99-a51d-2a61aff6f047",
            },
            {
                "type": "list",
                "value": {
                    "list_type": "ordered",
                    "items": [
                        {
                            "type": "item",
                            "value": {
                                "text": '<p data-block-key="nvpop"><a href="https://www.google.com">External Link in List Item</a></p>',
                                "image": {
                                    "image": None,
                                    "alt_text": None,
                                    "decorative": None,
                                },
                                "nested_list": [],
                            },
                            "id": "2c0c914f-0c47-406f-ba1c-48d106989e10",
                        }
                    ],
                },
                "id": "264b3299-abad-4994-b5b6-8847068ca064",
            },
            {
                "type": "questionanswers",
                "value": [
                    {
                        "type": "item",
                        "value": {
                            "question": "Q1",
                            "answer": '<p data-block-key="jsnxn"><a href="https://www.google.com">External Link in Q&amp;A</a></p>',
                            "anchortag": "QA1",
                        },
                        "id": "06f8c64e-7985-4141-be19-0d141db5bdc4",
                    },
                    {
                        "type": "item",
                        "value": {
                            "question": "Q2",
                            "answer": '<p data-block-key="i1xjt"><a href="https://www.google.com">https://www.google.com</a></p>',
                            "anchortag": "QA2",
                        },
                        "id": "3a0a087c-cbc4-40d4-b9dd-19a34820681b",
                    },
                    {
                        "type": "item",
                        "value": {
                            "question": "Q3",
                            "answer": '<p data-block-key="i1xjt"><a href="http://www.yahoo.com">http://www.yahoo.com External Link in Q&amp;A with URL in text</a></p>',
                            "anchortag": "QA3",
                        },
                        "id": "4390fba0-5624-461e-a3ac-bf005dd1c001",
                    },
                ],
                "id": "df2f2ede-33b9-402d-8cb0-6d76f62b4a94",
            },
            {
                "type": "table",
                "value": {
                    "columns": [{"type": "text", "heading": "Table Checking Link"}],
                    "rows": [
                        {
                            "values": [
                                '<p data-block-key="xqdfh"><a href="https://www.msn.com">External Link in Table Cell</a></p>'
                            ]
                        }
                    ],
                    "caption": "",
                },
                "id": "5b5d8ffe-0e8d-4a29-8c9b-6a81b9f00938",
            },
            {
                "type": "unstyled_table",
                "value": {
                    "columns": [
                        {"type": "text", "heading": "Unstyled table checking link"}
                    ],
                    "rows": [
                        {
                            "values": [
                                '<p data-block-key="et0ky"><a href="https://www.google.com">External Link in Unstyled Table Cell</a></p>'
                            ]
                        }
                    ],
                    "caption": "",
                },
                "id": "07fc1d94-ef58-4c72-93ef-dff89a8d187e",
            },
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
            {
                "type": "image",
                "value": {
                    "image": {
                        "image": 30,
                        "alt_text": "External Link in Image",
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
            },
        ]

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description="Test page for External Links Report",
                body=body,
            )
        )

        logger.info(f"Created the '{title}' page.")

    def delete(self):
        """Delete the test page if it exists."""
        try:
            page = Page.objects.get(slug=self.slug)
            page.delete()
            logger.info(f"Deleted test page with slug '{self.slug}'.")
        except Page.DoesNotExist:
            logger.info(f"Test page with slug '{self.slug}' does not exist.")
