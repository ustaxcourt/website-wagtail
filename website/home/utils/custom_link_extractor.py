from wagtail_external_links_report.utils import LinkExtractor
from bs4 import BeautifulSoup
from wagtail.rich_text import RichText


class CustomLinkExtractor(LinkExtractor):
    def extract_from_value(self, value):
        """Recursively extract links depending on value type."""
        links = []

        if isinstance(value, RichText):
            html = value.source
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if not href.startswith("mailto:") and not href.startswith("tel:"):
                    links.append(
                        {
                            "text": a.get_text(strip=True),
                            "url": href,
                        }
                    )
            return links
        else:
            return super().extract_from_value(value)
