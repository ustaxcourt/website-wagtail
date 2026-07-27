"""
Test page initializer for CardTiles with all block types.

This creates an EnhancedStandardPage with CardTiles containing one of each
block type allowed in the page body. For local testing only.
"""

from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage, IconCategories
import logging

logger = logging.getLogger(__name__)


class CardTilesTestPageInitializer(PageInitializer):
    """
    Creates a test page with CardTiles containing examples of all block types
    allowed in EnhancedStandardPage body.
    """

    def __init__(self):
        super().__init__()
        self.slug = "card-tiles-test"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.info("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def get_svg_icons(self):
        """Load or get SVG icons for card tiles."""
        icons = {
            "start": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="start_icon.svg",
                title="Start Icon (Test)",
            ),
            "calendar": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="calendar_icon.svg",
                title="Calendar Icon (Test)",
            ),
            "search": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="search_icon.svg",
                title="Search Icon (Test)",
            ),
            "orders": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="orders_icon.svg",
                title="Orders Icon (Test)",
            ),
        }
        return icons

    def get_all_block_types_content(self):
        """
        Returns a list of all block types allowed in EnhancedStandardPage body.
        Each block type is represented with sample content.
        """
        return [
            # heading - StructBlock with text, level, and optional id
            {
                "type": "heading",
                "value": {
                    "text": "Sample Heading Block",
                    "level": "h2",
                    "id": "sample-heading",
                },
            },
            # h2 - Simple CharBlock
            {"type": "h2", "value": "Sample H2 Heading"},
            # h3 - Simple CharBlock
            {"type": "h3", "value": "Sample H3 Heading"},
            # h4 - Simple CharBlock
            {"type": "h4", "value": "Sample H4 Heading"},
            # paragraph - RichTextBlock
            {
                "type": "paragraph",
                "value": "<p>This is a <strong>sample paragraph</strong> with some <em>rich text</em> formatting. It demonstrates the paragraph block type.</p>",
            },
            # hr - BooleanBlock (horizontal rule)
            {"type": "hr", "value": True},
            # iframe - StructBlock
            {
                "type": "iframe",
                "value": {
                    "src": "https://www.example.com",
                    "width": "100%",
                    "height": "300",
                    "title": "Sample Iframe",
                },
            },
            # alert - StructBlock with alert_type and content
            {
                "type": "alert",
                "value": {
                    "alert_type": "info",
                    "content": "<p>This is an <strong>info alert</strong> message.</p>",
                },
            },
            # embedded_video - StructBlock
            {
                "type": "embedded_video",
                "value": {
                    "title": "Sample Video",
                    "description": "<p>This is a sample embedded video description.</p>",
                    "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                },
            },
            # questionanswers - ListBlock of StructBlocks
            {
                "type": "questionanswers",
                "value": [
                    {
                        "question": "What is this block?",
                        "answer": "<p>This is a <strong>Question and Answer</strong> block.</p>",
                        "anchortag": "qa-sample",
                    },
                ],
            },
            # list - Nested list block
            {
                "type": "list",
                "value": {
                    "list_type": "unordered",
                    "items": [
                        {"text": "<p>First list item</p>", "nested_list": []},
                        {"text": "<p>Second list item</p>", "nested_list": []},
                    ],
                },
            },
            # card - ListBlock of card StructBlocks
            {
                "type": "card",
                "value": [
                    {
                        "icon": IconCategories.INFO.value,
                        "title": "Sample Card",
                        "description": "<p>This is a sample card description.</p>",
                        "color": "green",
                    },
                ],
            },
            # accordion - AccordionBlock
            {
                "type": "accordion",
                "value": {
                    "title": "Sample Accordion",
                    "description": [
                        {"type": "prose", "value": "<p>This is accordion content.</p>"},
                    ],
                },
            },
            # callout - StyledCalloutBlock
            {
                "type": "callout",
                "value": {
                    "heading": "Sample Callout",
                    "text": "<p>This is a callout block with important information.</p>",
                    "callout_type": "info",
                },
            },
            # button - ButtonBlock (requires external URL since we can't reference pages)
            {
                "type": "button",
                "value": {
                    "text": "Sample Button",
                    "url": [
                        {"type": "external_url", "value": "https://www.example.com"}
                    ],
                    "style": "primary",
                    "button_hover": True,
                },
            },
            # links - StructBlock with list of links
            {
                "type": "links",
                "value": {
                    "class": "indented",
                    "links": [
                        {
                            "title": "Sample Link 1",
                            "icon": IconCategories.LINK.value,
                            "url": "https://www.example.com",
                        },
                        {
                            "title": "Sample Link 2",
                            "icon": IconCategories.PDF.value,
                            "url": "https://www.example.com/sample.pdf",
                        },
                    ],
                },
            },
            # columns - ColumnBlock (with nested CommonBlock content)
            {
                "type": "columns",
                "value": {
                    "column": [
                        [
                            {"type": "h2", "value": "Column 1 Header"},
                            {"type": "hr", "value": True},
                        ],
                        [
                            {"type": "h2", "value": "Column 2 Header"},
                            {"type": "hr", "value": True},
                        ],
                    ],
                },
            },
            # Note: The following block types require external resources or complex formats:
            # - snippet: Requires a CommonText snippet to exist
            # - image: Requires an uploaded image
            # - photo_dedication: Requires an uploaded image
            # - table/unstyled_table: TypedTableBlock has complex internal format
        ]

    def create_page_info(self, home_page):
        title = "Card Tiles Test Page"

        if Page.objects.filter(slug=self.slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        # Load SVG icons for card tiles
        icons = self.get_svg_icons()
        if not all(icons.values()):
            logger.error(
                "Failed to load one or more SVG icons. Aborting page creation."
            )
            return

        # Get all block types content for the first card's anchor page body
        all_blocks_content = self.get_all_block_types_content()

        # Create the card_tiles block with 4 CardTiles:
        # 1. Anchor page with body content (icon: top)
        # 2. External URL (icon: left)
        # 3. Internal page link (icon: right)
        # 4. Anchor page with no content (icon: bottom)
        card_tiles_block = {
            "type": "card_tiles",
            "value": {
                "tiles": [
                    # Card 1: Anchor page with all block types (icon: top)
                    {
                        "icon": icons["start"].id,
                        "icon_direction": "top",
                        "card_header": "All Block Types Demo",
                        "link": [
                            {
                                "type": "anchor_page",
                                "value": {
                                    "breadcrumb_title": "All Blocks",
                                    "body": all_blocks_content,
                                },
                            }
                        ],
                        "card_hover": True,
                    },
                    # Card 2: External URL (icon: left)
                    {
                        "icon": icons["calendar"].id,
                        "icon_direction": "left",
                        "card_header": "External Link Example",
                        "link": [
                            {
                                "type": "external_url",
                                "value": "https://www.example.com",
                            }
                        ],
                        "card_hover": True,
                    },
                    # Card 3: Internal page link (icon: right)
                    {
                        "icon": icons["search"].id,
                        "icon_direction": "right",
                        "card_header": "Internal Page Link",
                        "link": [
                            {
                                "type": "internal_page",
                                "value": home_page.id,
                            }
                        ],
                        "card_hover": True,
                    },
                    # Card 4: Anchor page with no content (icon: bottom)
                    {
                        "icon": icons["orders"].id,
                        "icon_direction": "bottom",
                        "card_header": "Empty Anchor Page",
                        "link": [
                            {
                                "type": "anchor_page",
                                "value": {
                                    "breadcrumb_title": "Empty Page",
                                    "body": [],
                                },
                            }
                        ],
                        "card_hover": True,
                    },
                ],
                "default_content": [
                    {
                        "type": "paragraph",
                        "value": "<p>Click on the cards above to test different link types and icon directions.</p>",
                    },
                ],
            },
        }

        # Content before CardTiles
        intro_paragraph = {
            "type": "paragraph",
            "value": "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>",
        }

        # Content after CardTiles
        accordion_block = {
            "type": "accordion",
            "value": {
                "title": "Additional Information (Accordion)",
                "description": [
                    {
                        "type": "prose",
                        "value": "<p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>",
                    },
                ],
            },
        }

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description="Test page for CardTiles with all block types",
                body=[intro_paragraph, card_tiles_block, accordion_block],
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
