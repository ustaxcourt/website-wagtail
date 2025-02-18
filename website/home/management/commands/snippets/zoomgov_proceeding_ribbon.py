from home.models import NavigationRibbon, NavigationRibbonLink, IconCategories

ribbon_snippet_name = "Zoomgov Proceedings Ribbon"


class ZoomgovProceedingRibbonInitializer:
    def __init__(self, logger):
        self.logger = logger

    def create(self):
        if NavigationRibbon.objects.filter(name=ribbon_snippet_name).exists():
            self.logger.write(f"{ribbon_snippet_name} already exists.")
            return

        self.logger.write(f"Creating the {ribbon_snippet_name}.")

        navigation_ribbon = NavigationRibbon(
            name=ribbon_snippet_name,
        )
        navigation_ribbon.save()

        links = [
            {
                "title": "The Basics FAQs",
                "icon": IconCategories.INFO_CIRCLE_FILLED,
                "url": "/zoomgov_the_basics",
            },
            {
                "title": "Getting Ready FAQs",
                "icon": IconCategories.USER,
                "url": "/zoomgov_getting_ready",
            },
            {
                "title": "Zoomgov Proceedings FAQs",
                "icon": IconCategories.VIDEO,
                "url": "/zoomgov_zoomgov_proceedings",
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
