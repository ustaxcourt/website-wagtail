from home.models import NavigationRibbon, NavigationRibbonLink, IconCategories
import logging

logger = logging.getLogger(__name__)

remote_proceedings_ribbon_name = "Zoomgov Proceedings Ribbon"


class ZoomgovProceedingRibbonInitializer:
    def __init__(self):
        self.logger = logger

    def create(self):
        if NavigationRibbon.objects.filter(
            name=remote_proceedings_ribbon_name
        ).exists():
            logger.info(f"{remote_proceedings_ribbon_name} already exists.")
            return

        logger.info(f"Creating the {remote_proceedings_ribbon_name}.")

        navigation_ribbon = NavigationRibbon(
            name=remote_proceedings_ribbon_name,
        )
        navigation_ribbon.save()

        links = [
            {
                "title": "The Basics FAQs",
                "icon": IconCategories.INFO,
                "url": "/zoomgov-the-basics",
                "sort_order": 0,
            },
            {
                "title": "Getting Ready FAQs",
                "icon": IconCategories.USER,
                "url": "/zoomgov-getting-ready",
                "sort_order": 1,
            },
            {
                "title": "Zoomgov Proceedings FAQs",
                "icon": IconCategories.VIDEO,
                "url": "/zoomgov-zoomgov-proceedings",
                "sort_order": 2,
            },
        ]

        for link in links:
            link = NavigationRibbonLink(
                navigation_ribbon=navigation_ribbon,
                title=link["title"],
                icon=link["icon"],
                url=link["url"],
                sort_order=link["sort_order"],
            )
            link.save()

        self.model = navigation_ribbon
