"""Tests for home/models/snippets/banners.py"""

import pytest

from home.models.snippets.navigation import (
    NavigationRibbon,
    NavigationRibbonLink,
    IconCategories,
)


class TestNavigationRibbon:
    def _make_navigation_ribbon(self):
        obj = NavigationRibbon(name="test_navigation_ribbon")
        obj.save()
        return obj

    @pytest.mark.django_db
    def test_links_sort_according_to_sort_order(self):
        ribbon = self._make_navigation_ribbon()

        links = [
            {
                "title": "Introduction",
                "icon": IconCategories.INFO,
                "url": "/petitioners",
                "sort_order": 5,
            },
            {
                "title": "About the Court",
                "icon": IconCategories.BUILDING_BANK,
                "url": "/petitioners-about",
                "sort_order": 3,
            },
            {
                "title": "Starting A Case",
                "icon": IconCategories.FILE,
                "url": "/petitioners-start",
                "sort_order": 4,
            },
            {
                "title": "Things That Occur Before Trial",
                "icon": IconCategories.CALENDAR_MONTH,
                "url": "/petitioners-before",
                "sort_order": 1,
            },
            {
                "title": "Things That Occur During Trial",
                "icon": IconCategories.HAMMER,
                "url": "/petitioners-during",
                "sort_order": 0,
            },
            {
                "title": "Things That Occur After Trial",
                "icon": IconCategories.SCALE,
                "url": "/petitioners-after",
                "sort_order": 2,
            },
        ]

        for link in links:
            link = NavigationRibbonLink(
                navigation_ribbon=ribbon,
                title=link["title"],
                icon=link["icon"],
                url=link["url"],
                sort_order=link["sort_order"],
            )
            link.save()

        updatedRibbon = NavigationRibbon.objects.get(pk=ribbon.pk)
        linksFromUpdatedRibbon = updatedRibbon.links.values()
        sorted_links = sorted(links, key=lambda x: x["sort_order"])
        i = 0
        for iteratedLink in linksFromUpdatedRibbon:
            assert iteratedLink["sort_order"] == i
            assert iteratedLink["title"] == sorted_links[i]["title"]
            assert iteratedLink["icon"] == sorted_links[i]["icon"]
            assert iteratedLink["url"] == sorted_links[i]["url"]
            assert iteratedLink["sort_order"] == sorted_links[i]["sort_order"]
            i = i + 1
