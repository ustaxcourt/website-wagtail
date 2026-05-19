from wagtail_external_links_report.utils import LinkExtractor
from bs4 import BeautifulSoup
from wagtail.rich_text import RichText
from wagtail.contrib.typed_table_block.blocks import TypedTable


class CustomLinkExtractor(LinkExtractor):
    def extract_from_value(self, value):
        """Recursively extract links depending on value type."""
        links = []

        # Handles external links in Enhanced Tables, Styled Tables, and Unstyled Tables
        # Other custom handlers are called by similar logic in the base LinkExtractor's
        # extract_from_value() method.
        for block_cls, handler in self.custom_handlers.items():
            if isinstance(value, TypedTable) and isinstance(value, block_cls):
                return handler(value)

        if isinstance(value, RichText):
            html = value.source
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if (
                    not href.startswith("mailto:")
                    and not href.startswith("tel:")
                    and not href.startswith("#")
                ):
                    links.append(
                        {
                            "text": a.get_text(strip=True),
                            "url": href,
                        }
                    )
            return links
        elif (
            isinstance(value, dict)
            and "title" in value
            and "url" in value
            and value["title"] is not None
            and value["url"] is not None
            and isinstance(value["url"], str)
        ):
            # Handles external links in a List of Links component
            links.append({"text": value["title"], "url": value["url"]})
            return links
        else:
            return super().extract_from_value(value)
