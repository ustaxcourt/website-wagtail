from home.models import NavigationRibbon, NavigationRibbonLink, IconCategories
import logging

logger = logging.getLogger(__name__)

ribbon_snippet_name = "Guidance for Petitioners Ribbon"


class NavigationRibbonInitializer:
    def __init__(self):
        self.logger = logger

    def create(self):
        if NavigationRibbon.objects.filter(name=ribbon_snippet_name).exists():
            logger.info("Guidance for Petitioners Ribbon already exists.")
            return

        logger.info("Creating the Guidance for Petitioners Ribbon.")

        navigation_ribbon = NavigationRibbon(
            name=ribbon_snippet_name,
        )
        navigation_ribbon.save()

        links = [
            {
                "title": "Introduction",
                "icon": IconCategories.INFO,
                "url": "/petitioners",
            },
            {
                "title": "About the Court",
                "icon": IconCategories.BUILDING_BANK,
                "url": "/petitioners-about",
            },
            {
                "title": "Starting A Case",
                "icon": IconCategories.FILE,
                "url": "/petitioners-start",
            },
            {
                "title": "Things That Occur Before Trial",
                "icon": IconCategories.CALENDAR_MONTH,
                "url": "/petitioners-before",
            },
            {
                "title": "Things That Occur During Trial",
                "icon": IconCategories.HAMMER,
                "url": "/petitioners-during",
            },
            {
                "title": "Things That Occur After Trial",
                "icon": IconCategories.SCALE,
                "url": "/petitioners-after",
            },
            {
                "title": "Glossary",
                "icon": IconCategories.BOOK,
                "url": "/petitioners-glossary",
            },
        ]

        for link in links:
            link = NavigationRibbonLink(
                navigation_ribbon=navigation_ribbon,
                title=link["title"],
                icon=link["icon"],
                url=link["url"],
            )
            link.save()

        self.model = navigation_ribbon
