from collections import defaultdict
from operator import itemgetter

from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.utils import timezone
from django.template.response import TemplateResponse

from home.models.pages.enhanced_standard import EnhancedStandardPage
from home.models.snippets.news_item import NewsItem
from home.models.snippets.banners import Banner


class PressReleasePage(RoutablePageMixin, EnhancedStandardPage):
    """
    A specialized page for managing press releases with grouping and archive routing.
    """

    @route("archives/")
    def archive_view(self, request):
        grouped = self.group_press_releases_by_year
        all_years = list(grouped.keys())
        archived_years = all_years[4:]  # After first 4 years
        archived_releases = {year: grouped[year] for year in archived_years}

        context = self.get_context(request)
        context["press_releases_by_year"] = archived_releases
        context["is_archive"] = True
        self.title = self.title + " Archive"
        return TemplateResponse(request, self.template, context)

    @property
    def group_press_releases_by_year(self):
        grouped = defaultdict(list)

        # Process NewsItems
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
                        "category": None,
                    }
                    grouped[year].append(release_entry)
                else:
                    release_entry = {
                        "id": news_item.id,
                        "is_homepage_entry": True,
                        "release_date": release_date,
                        "details": {
                            "description": news_item.title,
                        },
                        "title": news_item.title,
                        "body": news_item.description,
                        "file": None,
                        "category": None,
                    }
                    grouped[year].append(release_entry)

        # Process standalone Banners
        banners = (
            Banner.objects.live()
            .filter(banner_start_date__lte=timezone.now())
            .order_by("-banner_start_date")
        )
        for banner in banners:
            release_date = (
                banner.banner_start_date.date() if banner.banner_start_date else None
            )
            if release_date:
                year = release_date.year

                # Determine banner type label
                banner_label = (
                    "High Priority" if banner.priority_level == "high" else "Critical"
                )

                # Create release entry from Banner
                release_entry = {
                    "is_news_item": True,
                    "is_banner": True,
                    "release_date": release_date,
                    "banner_label": banner_label,  # "High Priority" or "Critical"
                    "banner_title": banner.banner_title,  # The title to be bolded
                    "banner_body": banner.description,  # The body text
                    "banner_type": banner.priority_level,  # "high" or "critical" for styling
                    "details": {
                        "description": "",  # Not used for banners
                        "file": banner.document,
                    },
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
        first_four_years = all_years[:4]
        main_page_releases = {year: grouped[year] for year in first_four_years}
        context["press_releases_by_year"] = main_page_releases
        context["is_archive"] = False
        return context

    class Meta:
        verbose_name = "News and Announcements Page"
