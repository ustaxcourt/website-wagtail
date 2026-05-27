from wagtail_external_links_report.utils import LinkExtractor
from bs4 import BeautifulSoup
from wagtail.rich_text import RichText
from wagtail.contrib.typed_table_block.blocks import TypedTable
from home.models.custom_blocks.button import ButtonBlock
from home.blocks import QuickAccessTileBlock
from home.models.pages.enhanced_standard import CardTileBlock
from home.models.custom_blocks.image_with_link import ImageWithLinkBlock
from wagtail.blocks import StructValue


class CustomLinkExtractor(LinkExtractor):
    def _get_external_link_with_text_from_attribute(value, text_attribute):
        links = []
        if value["url"]:
            for child in value["url"]:
                if hasattr(child, "block_type") and child.block_type == "external_url":
                    links.extend({"text": value[text_attribute], "url": child.value})

        return links

    def extract_from_value(self, value):
        """Recursively extract links depending on value type."""
        links = []

        if isinstance(value, StructValue) and isinstance(value, ButtonBlock):
            links.extend(self._get_external_link_with_text_from_attribute("text"))
            return links

        if isinstance(value, StructValue) and isinstance(value, QuickAccessTileBlock):
            links.extend(self._get_external_link_with_text_from_attribute("title"))
            return links

        if isinstance(value, StructValue) and isinstance(value, CardTileBlock):
            links.extend(
                self._get_external_link_with_text_from_attribute("card_header")
            )
            return links

        if isinstance(value, StructValue) and isinstance(value, ImageWithLinkBlock):
            links.extend(self._get_external_link_with_text_from_attribute("image"))
            return links

        # Handles external links in Enhanced Tables, Styled Tables, and Unstyled Tables
        if isinstance(value, TypedTable):
            for row in value.rows:
                for cell in row:
                    links.extend(self.extract_from_value(cell.value))

            return links

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
