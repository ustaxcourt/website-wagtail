"""
Test page initializer for Table with all block types.
This creates an EnhancedStandardPage with Table containing one of each
block type allowed in the page body. For local testing only.
"""

from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)


class TableTestPageInitializer(PageInitializer):
    """
    Creates a test page with Table containing examples of all block types
    allowed in EnhancedStandardPage body.
    """

    def __init__(self):
        super().__init__()
        self.slug = "table-test"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.info("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Table Test Page"

        if Page.objects.filter(slug=self.slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        # Content before Table
        intro_paragraph = {
            "type": "paragraph",
            "value": "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>",
        }

        # TableListBlock with sample data - showcasing all component types
        table_block = {
            "type": "enhanced_table",
            "value": {
                "table": {
                    "columns": [
                        {"type": "components", "heading": "Feature"},
                        {"type": "components", "heading": "Details"},
                        {"type": "components", "heading": "Notes"},
                        {"type": "components", "heading": "Actions"},
                    ],
                    "rows": [
                        {
                            "values": [
                                # Text block
                                [
                                    {
                                        "type": "text",
                                        "value": "<p><strong>User Authentication</strong></p>",
                                    }
                                ],
                                # Callout block
                                [
                                    {
                                        "type": "callout",
                                        "value": {
                                            "heading": "Security Notice",
                                            "text": "<p>Multi-factor authentication is <strong>required</strong> for all admin users.</p>",
                                            "callout_type": "warning",
                                        },
                                    }
                                ],
                                # Accordion block
                                [
                                    {
                                        "type": "accordion",
                                        "value": {
                                            "title": "Implementation Details",
                                            "description": [
                                                {
                                                    "type": "prose",
                                                    "value": "<p>Uses OAuth 2.0 with JWT tokens. Session timeout is 30 minutes.</p>",
                                                },
                                            ],
                                        },
                                    }
                                ],
                                # Button block
                                [
                                    {
                                        "type": "button",
                                        "value": {
                                            "text": "View Docs",
                                            "url": [
                                                {
                                                    "type": "external_url",
                                                    "value": "https://example.com/auth-docs",
                                                }
                                            ],
                                            "style": "primary",
                                            "button_hover": True,
                                        },
                                    }
                                ],
                            ]
                        },
                        {
                            "values": [
                                [
                                    {
                                        "type": "text",
                                        "value": "<p><strong>Dashboard Analytics</strong></p>",
                                    }
                                ],
                                [
                                    {
                                        "type": "callout",
                                        "value": {
                                            "heading": "New Feature",
                                            "text": "<p>Real-time metrics now available with <em>live updates</em>.</p>",
                                            "callout_type": "success",
                                        },
                                    }
                                ],
                                [
                                    {
                                        "type": "accordion",
                                        "value": {
                                            "title": "Metrics Included",
                                            "description": [
                                                {
                                                    "type": "prose",
                                                    "value": "<p>Page views, user sessions, conversion rates, and custom events.</p>",
                                                },
                                            ],
                                        },
                                    }
                                ],
                                [
                                    {
                                        "type": "button",
                                        "value": {
                                            "text": "Open Dashboard",
                                            "url": [
                                                {
                                                    "type": "external_url",
                                                    "value": "https://example.com/dashboard",
                                                }
                                            ],
                                            "style": "primary",
                                            "button_hover": True,
                                        },
                                    }
                                ],
                            ]
                        },
                        {
                            "values": [
                                [
                                    {
                                        "type": "text",
                                        "value": "<p><strong>API Integration</strong></p>",
                                    }
                                ],
                                [
                                    {
                                        "type": "callout",
                                        "value": {
                                            "heading": "API Status",
                                            "text": "<p>RESTful endpoints are available at <code>/api/v2/</code>.</p>",
                                            "callout_type": "info",
                                        },
                                    }
                                ],
                                [
                                    {
                                        "type": "accordion",
                                        "value": {
                                            "title": "Supported Methods",
                                            "description": [
                                                {
                                                    "type": "prose",
                                                    "value": "<p>GET, POST, PUT, PATCH, DELETE. Rate limit: 1000 requests/hour.</p>",
                                                },
                                            ],
                                        },
                                    }
                                ],
                                [
                                    {
                                        "type": "button",
                                        "value": {
                                            "text": "API Reference",
                                            "url": [
                                                {
                                                    "type": "external_url",
                                                    "value": "https://example.com/api-docs",
                                                }
                                            ],
                                            "style": "primary",
                                            "button_hover": True,
                                        },
                                    }
                                ],
                            ]
                        },
                        {
                            "values": [
                                [
                                    {
                                        "type": "text",
                                        "value": "<p><strong>System Maintenance</strong></p>",
                                    }
                                ],
                                [
                                    {
                                        "type": "callout",
                                        "value": {
                                            "heading": "Scheduled Downtime",
                                            "text": "<p>Maintenance window: <strong>Sunday 2-4 AM EST</strong>.</p>",
                                            "callout_type": "emergency",
                                        },
                                    }
                                ],
                                [
                                    {
                                        "type": "accordion",
                                        "value": {
                                            "title": "What to Expect",
                                            "description": [
                                                {
                                                    "type": "prose",
                                                    "value": "<p>Brief service interruption. All data will be preserved. Backup systems active.</p>",
                                                },
                                            ],
                                        },
                                    }
                                ],
                                [
                                    {
                                        "type": "button",
                                        "value": {
                                            "text": "Status Page",
                                            "url": [
                                                {
                                                    "type": "external_url",
                                                    "value": "https://example.com/status",
                                                }
                                            ],
                                            "style": "primary",
                                            "button_hover": True,
                                        },
                                    }
                                ],
                            ]
                        },
                        {
                            "values": [
                                [
                                    {
                                        "type": "text",
                                        "value": "<p><strong>Data Export</strong></p>",
                                    }
                                ],
                                [
                                    {
                                        "type": "callout",
                                        "value": {
                                            "heading": "Export Formats",
                                            "text": "<p>CSV, JSON, XML, and Excel formats supported.</p>",
                                            "callout_type": "info",
                                        },
                                    }
                                ],
                                [
                                    {
                                        "type": "accordion",
                                        "value": {
                                            "title": "Export Limits",
                                            "description": [
                                                {
                                                    "type": "prose",
                                                    "value": "<p>Max 100,000 rows per export. Large exports queued for background processing.</p>",
                                                },
                                            ],
                                        },
                                    }
                                ],
                                [
                                    {
                                        "type": "button",
                                        "value": {
                                            "text": "Export Data",
                                            "url": [
                                                {
                                                    "type": "external_url",
                                                    "value": "https://example.com/export",
                                                }
                                            ],
                                            "style": "primary",
                                            "button_hover": True,
                                        },
                                    }
                                ],
                            ]
                        },
                        {
                            "values": [
                                [
                                    {
                                        "type": "text",
                                        "value": "<p><strong>Error Handling</strong></p>",
                                    }
                                ],
                                [
                                    {
                                        "type": "callout",
                                        "value": {
                                            "heading": "Error Detected",
                                            "text": "<p>Some validation errors require immediate attention.</p>",
                                            "callout_type": "error",
                                        },
                                    }
                                ],
                                [
                                    {
                                        "type": "accordion",
                                        "value": {
                                            "title": "Common Errors",
                                            "description": [
                                                {
                                                    "type": "prose",
                                                    "value": "<p>400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Server Error.</p>",
                                                },
                                            ],
                                        },
                                    }
                                ],
                                [
                                    {
                                        "type": "button",
                                        "value": {
                                            "text": "Error Guide",
                                            "url": [
                                                {
                                                    "type": "external_url",
                                                    "value": "https://example.com/errors",
                                                }
                                            ],
                                            "style": "primary",
                                            "button_hover": True,
                                        },
                                    }
                                ],
                            ]
                        },
                    ],
                    "caption": "",
                },
                "header": "Feature Overview with All Component Types",
                "caption": "This table demonstrates all supported component types within table cells.",
                "caption_location": "top",
                "style": "styled",
            },
        }

        # Content after Table
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
                search_description="Test page for Table with all block types",
                body=[intro_paragraph, table_block, accordion_block],
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
