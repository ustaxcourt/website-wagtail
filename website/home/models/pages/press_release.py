import re
import os
from collections import defaultdict
from operator import itemgetter

from wagtail import blocks
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.fields import StreamField
from wagtail.search import index
from wagtail.admin.panels import FieldPanel
from django.utils import timezone
from django.utils.html import strip_tags
from django.template.response import TemplateResponse

from home.models.custom_blocks.button import ButtonBlock
from home.models.pages.enhanced_standard import EnhancedStandardPage
from home.models.pages.home_page import HomePageEntry
from home.models.snippets.news_item import NewsItem


def extract_pdf_filename_from_body(html):
    """Extracts the .pdf filename from an anchor tag's href in the HTML string. Returns the filename (e.g., '04072025.pdf') or None."""
    match = re.search(r'href="([^"]+\.pdf)"', html or "", re.IGNORECASE)
    if match:
        pdf_url = match.group(1)
        return os.path.basename(pdf_url)  # Extract just the filename
    return None


class NewsItemListBlock(blocks.StructBlock):
    """Block that automatically displays all live NewsItem snippets."""

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        # Get all live NewsItem snippets ordered by publish_date descending
        context["news_items"] = NewsItem.objects.live().order_by("-publish_date")
        return context

    class Meta:
        icon = "list-ul"
        label = "All News Items"
        template = "blocks/news_items_list.html"


class PressReleasePage(RoutablePageMixin, EnhancedStandardPage):
    """
    A specialized page for managing press releases with grouping and archive routing.
    """

    press_release_body = StreamField(
        [
            ("button", ButtonBlock()),
            ("news_items", NewsItemListBlock()),
            (
                "press_releases",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            ("release_date", blocks.DateBlock(required=False)),
                            (
                                "details",
                                blocks.StructBlock(
                                    [
                                        (
                                            "description",
                                            blocks.TextBlock(required=False),
                                        ),
                                        ("file", DocumentChooserBlock(required=False)),
                                    ],
                                    required=False,
                                ),
                            ),
                        ]
                    )
                ),
            ),
        ],
        blank=True,
        use_json_field=True,
        null=True,
    )

    content_panels = EnhancedStandardPage.content_panels + [
        FieldPanel("press_release_body"),
    ]

    search_fields = EnhancedStandardPage.search_fields + [
        index.SearchField("press_release_body"),
    ]

    @route("archives/")
    def archive_view(self, request):
        grouped = self.group_press_releases_by_year
        all_years = list(grouped.keys())
        archived_years = all_years[5:]  # After first 5 years
        archived_releases = {year: grouped[year] for year in archived_years}

        context = self.get_context(request)
        context["press_releases_by_year"] = archived_releases
        context["is_archive"] = True
        self.title = "Press Release Archive"
        return TemplateResponse(request, self.template, context)

    @property
    def group_press_releases_by_year(self):
        grouped = defaultdict(list)
        seen_press_release_keys = set()  # (title, pdf), (description, file)

        for block in self.press_release_body:
            # Handle news_items block (NewsItem snippets)
            if block.block_type == "news_items":
                # Get all live NewsItem snippets with publish_date <= current datetime
                news_items = (
                    NewsItem.objects.live()
                    .filter(publish_date__lte=timezone.now())
                    .order_by("-publish_date")
                )
                for news_item in news_items:
                    release_date = (
                        news_item.publish_date.date()
                        if news_item.publish_date
                        else None
                    )
                    if release_date:
                        year = release_date.year

                        # Create release entry from NewsItem
                        release_entry = {
                            "is_news_item": True,
                            "release_date": release_date,
                            "details": {
                                "description": news_item.title,
                                "file": news_item.document,
                            },
                        }
                        grouped[year].append(release_entry)

                        # Track for duplication prevention
                        description = strip_tags(news_item.title.strip().lower())
                        file = news_item.document

                        if file and hasattr(file, "url"):
                            pdf_filename = os.path.basename(file.url).strip().lower()
                            seen_press_release_keys.add(("file", pdf_filename))

                            if description:
                                seen_press_release_keys.add(
                                    ("desc+file", description, pdf_filename)
                                )

        # Step 2: Add homepage entries, only if not duplicate
        persisted_entries = HomePageEntry.objects.filter(
            persist_to_press_releases=True, end_date__lt=timezone.now()
        ).order_by("-end_date")

        for entry in persisted_entries:
            pdf_url = extract_pdf_filename_from_body(entry.body)
            pdf_filename = os.path.basename(pdf_url).strip().lower() if pdf_url else ""
            title = entry.title.strip() if entry.title else ""
            is_duplicate = ("file", pdf_filename) in seen_press_release_keys or (
                "desc+file",
                title,
                pdf_filename,
            ) in seen_press_release_keys
            if is_duplicate:
                continue

            if not is_duplicate:
                release_date = entry.end_date.date() if entry.end_date else None
                year = release_date.year if release_date else "Unknown"
                grouped[year].append(
                    {
                        "is_homepage_entry": True,
                        "release_date": release_date,
                        "id": entry.id,
                        "title": entry.title,
                        "body": entry.body,
                        "file": pdf_filename,
                    }
                )
        # Sort releases in each year by descending date
        sorted_grouped = {
            year: sorted(releases, key=itemgetter("release_date"), reverse=True)
            for year, releases in grouped.items()
        }
        return dict(sorted(sorted_grouped.items(), reverse=True))

    def get_context(self, request):
        context = super().get_context(request)
        grouped = self.group_press_releases_by_year
        all_years = list(grouped.keys())
        first_five_years = all_years[:5]
        main_page_releases = {year: grouped[year] for year in first_five_years}
        context["press_releases_by_year"] = main_page_releases
        context["is_archive"] = False
        return context

    class Meta:
        verbose_name = "Press Release Page"
