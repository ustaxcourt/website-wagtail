from collections import defaultdict
from operator import itemgetter

from wagtail import blocks
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.fields import StreamField
from wagtail.search import index
from wagtail.admin.panels import FieldPanel
from django.utils import timezone
from django.template.response import TemplateResponse

from home.models.custom_blocks.button import ButtonBlock
from home.models.pages.enhanced_standard import EnhancedStandardPage
from home.models.snippets.news_item import NewsItem


class PressReleasePage(RoutablePageMixin, EnhancedStandardPage):
    """
    A specialized page for managing press releases with grouping and archive routing.
    """

    press_release_body = StreamField(
        [
            ("button", ButtonBlock()),
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
        # seen_press_release_keys = set()  # (title, pdf), (description, file)

        news_items = (
            NewsItem.objects.live()
            .filter(publish_date__lte=timezone.now())
            .order_by("-publish_date")
        )
        for news_item in news_items:
            release_date = (
                news_item.publish_date.date() if news_item.publish_date else None
            )
            if release_date:
                year = release_date.year

                # Create release entry from NewsItem
                if news_item.document:
                    release_entry = {
                        "is_news_item": True,
                        "release_date": release_date,
                        "details": {
                            "description": news_item.title,
                            "file": news_item.document,
                        },
                    }
                    grouped[year].append(release_entry)
                else:
                    release_entry = {
                        "id": news_item.id,
                        "is_homepage_entry": True,
                        "release_date": release_date,
                        "title": news_item.title,
                        "body": news_item.description,
                        "file": None,
                    }
                    grouped[year].append(release_entry)

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
