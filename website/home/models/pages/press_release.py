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
        grouped = self.group_press_releases_by_year()
        all_years = list(grouped.keys())
        archived_years = all_years[4:]  # After first 4 years
        archived_releases = {year: grouped[year] for year in archived_years}

        context = self.get_context(request)
        context["press_releases_by_year"] = archived_releases
        context["is_archive"] = True
        self.title = self.title + " Archive"
        return TemplateResponse(request, self.template, context)

    def group_press_releases_by_year(self, preview_banner=None):
        """
        Build the year -> [release entries] mapping shown on this page.

        `preview_banner` is only used when this page is being rendered as a
        stand-in for the Banner "announcements page" preview (see
        Banner.get_preview_context). When provided:
          - that banner's normal live/date-based queryset entry (if any) is
            excluded, to avoid showing it twice.
          - a forced entry for that banner is always included, regardless of
            its live status or scheduled start/end dates, so editors can see
            how an unpublished or future-scheduled banner will look.
        Normal page rendering never passes this argument, so production
        behavior is unchanged.
        """
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
        if preview_banner is not None and preview_banner.pk:
            # Avoid a duplicate entry if the banner being previewed also
            # happens to genuinely be live right now.
            banners = banners.exclude(pk=preview_banner.pk)

        for banner in banners:
            release_entry = banner.as_press_release_entry()
            release_date = release_entry["release_date"]
            if release_date:
                year = release_date.year
                grouped[year].append(release_entry)

        if preview_banner is not None:
            # Ignore live status and scheduled dates entirely for the banner
            # under preview - fall back to "today" if it has no start date
            # yet, so it always appears somewhere in the preview.
            forced_date = (
                preview_banner.banner_start_date.date()
                if preview_banner.banner_start_date
                else timezone.now().date()
            )
            preview_entry = preview_banner.as_press_release_entry(
                force_release_date=forced_date
            )
            preview_entry["is_preview_entry"] = True
            grouped[forced_date.year].append(preview_entry)

        sorted_grouped = {
            year: sorted(releases, key=itemgetter("release_date"), reverse=True)
            for year, releases in grouped.items()
        }
        return dict(sorted(sorted_grouped.items(), reverse=True))

    def get_context(self, request, preview_banner=None):
        context = super().get_context(request)
        grouped = self.group_press_releases_by_year(preview_banner=preview_banner)
        all_years = list(grouped.keys())
        first_four_years = all_years[:4]

        if preview_banner is not None:
            # The previewed banner's year may fall outside the years normally
            # shown on the main (non-archive) page. Force it into view so the
            # preview always reflects the banner, rather than silently
            # routing it to the archive view.
            preview_year = (
                preview_banner.banner_start_date.date().year
                if preview_banner.banner_start_date
                else timezone.now().date().year
            )
            if preview_year in grouped and preview_year not in first_four_years:
                first_four_years = [preview_year] + first_four_years

        main_page_releases = {year: grouped[year] for year in first_four_years}
        context["press_releases_by_year"] = main_page_releases
        context["is_archive"] = False
        return context

    class Meta:
        verbose_name = "News and Announcements Page"
