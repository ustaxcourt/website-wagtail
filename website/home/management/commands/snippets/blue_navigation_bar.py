from home.models import BlueNavigationBar, BlueNavigationBarLink, IconCategories


class BlueNavigationBarInitializer:
    def __init__(self, logger):
        self.logger = logger

    def create(self):
        if BlueNavigationBar.objects.filter(name="Blue Navigation Bar").exists():
            self.logger.write("Blue navigation bar already exists.")
            return

        self.logger.write("Creating the blue navigation bar.")

        blue_navigation_bar = BlueNavigationBar(
            name="Blue Navigation Bar",
        )
        blue_navigation_bar.save()

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
            link = BlueNavigationBarLink(
                blue_navigation_bar=blue_navigation_bar,
                title=link["title"],
                icon=link["icon"],
                url=link["url"],
            )
            link.save()

        self.model = blue_navigation_bar
