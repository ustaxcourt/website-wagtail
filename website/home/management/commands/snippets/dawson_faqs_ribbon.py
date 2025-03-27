from home.models import NavigationRibbon, NavigationRibbonLink, IconCategories

dawson_faqs_ribbon_name = "Dawson FAQs Ribbon"


class DawsonFAQsRibbonInitializer:
    def __init__(self, logger):
        self.logger = logger

    def create(self):
        if NavigationRibbon.objects.filter(name=dawson_faqs_ribbon_name).exists():
            self.logger.write(f"{dawson_faqs_ribbon_name} already exists.")
            return

        self.logger.write(f"Creating the {dawson_faqs_ribbon_name}.")

        navigation_ribbon = NavigationRibbon(
            name=dawson_faqs_ribbon_name,
        )
        navigation_ribbon.save()

        links = [
            {
                "title": "The Basics",
                "icon": IconCategories.INFO,
                "url": "/dawson-faqs-basics",
            },
            {
                "title": "Account Management",
                "icon": IconCategories.SETTINGS,
                "url": "/dawson-faqs-account-management",
            },
            {
                "title": "Case Management",
                "icon": IconCategories.BRIEFCASE,
                "url": "/dawson-faqs-case-management",
            },
            {
                "title": "Training and Support",
                "icon": IconCategories.USER,
                "url": "/dawson-faqs-training-and-support",
            },
            {
                "title": "Search and Public Access",
                "icon": IconCategories.SEARCH,
                "url": "/dawson-faqs-searches-public-access",
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
