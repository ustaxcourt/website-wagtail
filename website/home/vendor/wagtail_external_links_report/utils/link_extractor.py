# Vendored from wagtail-external-links-report 0.1.1
# (https://github.com/PBahner/wagtail-external-links-report). See
# home/vendor/wagtail_external_links_report/views.py for why this is vendored.
from bs4 import BeautifulSoup
from wagtail.rich_text import RichText
from wagtail.blocks import StructValue


class LinkExtractor:
    """
    Recursively walks over Wagtail field values (StreamField, StructBlock, RichText, etc.)
    and extracts external links.
    Custom extractors can be added for specific block types or fields.
    """

    def __init__(self, allowed_fields=None, custom_handlers=None):
        # list of fields to extract from (e.g. ["body", "sidebar"])
        self.allowed_fields = allowed_fields or ["body"]

        # optional dict: {block_class: handler_func}
        # handler_func(value) -> list of {text, url}
        self.custom_handlers = custom_handlers or {}

    def extract_from_page(self, page):
        """Extract links from all configured fields of a page."""
        links = []
        for field_name in self.allowed_fields:
            value = getattr(page, field_name, None)
            if value:
                links.extend(self.extract_from_value(value))
        return links

    def extract_from_value(self, value):
        """Recursively extract links depending on value type."""
        links = []

        if value is None:
            return links

        # --- custom handler for specific block types ---
        for block_cls, handler in self.custom_handlers.items():
            if isinstance(value, StructValue) and isinstance(value.block, block_cls):
                return handler(value)

        # --- RichText ---
        if isinstance(value, RichText):
            html = value.source
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http"):
                    links.append(
                        {
                            "text": a.get_text(strip=True),
                            "url": href,
                        }
                    )
            return links

        # --- plain text (no links) ---
        if isinstance(value, str):
            return links

        # --- StreamBlock / ListBlock (iterable) ---
        if hasattr(value, "__iter__") and not isinstance(value, dict):
            for child in value:
                if hasattr(child, "block_type") and hasattr(child, "value"):
                    links.extend(self.extract_from_value(child.value))
                else:
                    links.extend(self.extract_from_value(child))
            return links

        # --- StructBlock (dict-like) ---
        if isinstance(value, dict) or hasattr(value, "items"):
            for subval in value.values():
                links.extend(self.extract_from_value(subval))
            return links

        return links
