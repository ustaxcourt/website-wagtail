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
                "icon": IconCategories.INFO_CIRCLE_FILLED,
                "url": "/dawson_faqs_basics",
            },
            {
                "title": "Account Management",
                "icon": IconCategories.SETTINGS,
                "url": "/dawson_faqs_account_management",
            },
            {
                "title": "Case Management",
                "icon": IconCategories.BRIEFCASE,
                "url": "/dawson_faqs_case_management",
            },
            {
                "title": "Training and Support",
                "icon": IconCategories.USER,
                "url": "/dawson_faqs_training_and_support",
            },
            {
                "title": "Search and Public Access",
                "icon": IconCategories.SEARCH,
                "url": "/dawson_faqs_searches_public_access",
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
