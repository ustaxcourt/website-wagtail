from home.models import NavigationRibbon, NavigationRibbonLink, IconCategories


ribbon_snippet_name = "Guidance for Petitioners Ribbon"
remote_proceedings_ribbon_name = "Remote Proceedings Ribbon"


class NavigationRibbonInitializer:
    def __init__(self, logger):
        self.logger = logger

    def create(self):
        if NavigationRibbon.objects.filter(name=ribbon_snippet_name).exists():
            self.logger.write("Guidance for Petitioners Ribbon already exists.")
            return

        self.logger.write("Creating the Guidance for Petitioners Ribbon.")

        navigation_ribbon = NavigationRibbon(
            name=ribbon_snippet_name,
        )
        navigation_ribbon.save()

        links = [
            {
                "title": "Introduction",
                "icon": IconCategories.INFO_CIRCLE_FILLED,
                "url": "/petitioners",
            },
            {
                "title": "About the Court",
                "icon": IconCategories.BUILDING_BANK,
                "url": "/petitioners_about",
            },
            {
                "title": "Starting A Case",
                "icon": IconCategories.FILE,
                "url": "/petitioners_start",
            },
            {
                "title": "Things That Occur Before Trial",
                "icon": IconCategories.CALENDAR_MONTH,
                "url": "/petitioners_before",
            },
            {
                "title": "Things That Occur During Trial",
                "icon": IconCategories.HAMMER,
                "url": "/petitioners_during",
            },
            {
                "title": "Things That Occur After Trial",
                "icon": IconCategories.SCALE,
                "url": "/petitioners_after",
            },
            {
                "title": "Glossary",
                "icon": IconCategories.BOOK_2,
                "url": "/petitioners_glossary",
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


class RemoteProceedingsRibbonInitializer:
    def __init__(self, logger):
        self.logger = logger

    def create(self):
        if NavigationRibbon.objects.filter(
            name=remote_proceedings_ribbon_name
        ).exists():
            self.logger.write("Remote Proceedings Ribbon already exists.")
            return

        self.logger.write("Creating the Remote Proceedings Ribbon.")

        navigation_ribbon = NavigationRibbon(
            name=remote_proceedings_ribbon_name,
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
