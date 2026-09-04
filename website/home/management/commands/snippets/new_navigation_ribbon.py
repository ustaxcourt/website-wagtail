from home.models import NavigationRibbon, NavigationRibbonLink, IconCategories
import logging

logger = logging.getLogger(__name__)

ribbon_snippet_name = "Guidance for Self-Represented Petitioners Ribbon"


class NewNavigationRibbonInitializer:
    def __init__(self):
        self.logger = logger

    def create(self):
        if NavigationRibbon.objects.filter(name=ribbon_snippet_name).exists():
            logger.info(
                "Guidance for Self-Represented Petitioners Ribbon already exists."
            )
            return

        logger.info("Creating the Guidance for Self-Represented Petitioners Ribbon.")

        navigation_ribbon = NavigationRibbon(
            name=ribbon_snippet_name,
        )
        navigation_ribbon.save()

        links = [
            {
                "title": "Guidance for Self-Represented Petitioners",
                "icon": IconCategories.SIGNPOST,
                "url": "/petitioners-guidance",
                "sort_order": 0,
            },
            {
                "title": "Process and Timeline",
                "icon": IconCategories.TIMELINE,
                "url": "/petitioners-timeline",
                "sort_order": 1,
            },
            {
                "title": "Prepare to File",
                "icon": IconCategories.NOTES,
                "url": "/petitioners-prepare-to-file",
                "sort_order": 2,
            },
            {
                "title": "Forms",
                "icon": IconCategories.FORMS,
                "url": "/petitioners-forms",
                "sort_order": 3,
            },
            {
                "title": "Help",
                "icon": IconCategories.HELP,
                "url": "/petitioners-help",
                "sort_order": 4,
            },
            {
                "title": "DAWSON LOG-IN",
                "icon": IconCategories.DAWSON,
                "url": "https://app.dawson.ustaxcourt.gov/login",
                "sort_order": 5,
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
