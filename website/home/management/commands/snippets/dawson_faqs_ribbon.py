from home.models import NavigationRibbon, NavigationRibbonLink, IconCategories
import logging

logger = logging.getLogger(__name__)

dawson_faqs_ribbon_name = "Dawson FAQs Ribbon"


class DawsonFAQsRibbonInitializer:
    def __init__(self):
        self.logger = logger

    def create(self):
        if NavigationRibbon.objects.filter(name=dawson_faqs_ribbon_name).exists():
            logger.info(f"{dawson_faqs_ribbon_name} already exists.")
            return

        logger.info(f"Creating the {dawson_faqs_ribbon_name}.")

        navigation_ribbon = NavigationRibbon(
            name=dawson_faqs_ribbon_name,
        )
        navigation_ribbon.save()

        links = [
            {
                "title": "The Basics",
                "icon": IconCategories.INFO,
                "url": "/dawson-faqs-basics",
                "sort_order": 0,
            },
            {
                "title": "Account Management",
                "icon": IconCategories.SETTINGS,
                "url": "/dawson-faqs-account-management",
                "sort_order": 1,
            },
            {
                "title": "Case Management",
                "icon": IconCategories.BRIEFCASE,
                "url": "/dawson-faqs-case-management",
                "sort_order": 2,
            },
            {
                "title": "Training and Support",
                "icon": IconCategories.USER,
                "url": "/dawson-faqs-training-and-support",
                "sort_order": 3,
            },
            {
                "title": "Searches and Public Access",
                "icon": IconCategories.SEARCH,
                "url": "/dawson-faqs-searches-public-access",
                "sort_order": 4,
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
