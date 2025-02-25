from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationCategories, EnhancedStandardPage


class JudgesPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "judges"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            self.logger.write("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Judges"

        if Page.objects.filter(slug=self.slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description=title,
                show_in_menus=True,
                body=[
                    {
                        "type": "columns",
                        "value": {
                            "column": [
                                [  # First column
                                    {
                                        "type": "h3WithAnchorTag",
                                        "value": {
                                            "text": "Judges",
                                            "anchortag": "JUDGES",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Kathleen Kerrigan, Chief Judge",
                                            "url": "/judges/kerrigan",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Jeffrey S. Arbeit",
                                            "url": "/judges/arbeit",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Tamara W. Ashford",
                                            "url": "/judges/ashford",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Ronald L. Buch",
                                            "url": "/judges/buch",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Elizabeth A. Copeland",
                                            "url": "/judges/copeland",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Maurice B. Foley",
                                            "url": "/judges/foley",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Cathy Fung",
                                            "url": "/judges/fung",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Travis A. Greaves",
                                            "url": "/judges/greaves",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Benjamin A. Guider III",
                                            "url": "/judges/guider",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Rose E. Jenkins",
                                            "url": "/judges/jenkins",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Courtney D. Jones",
                                            "url": "/judges/jones",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Adam B. Landy",
                                            "url": "/judges/landy",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Alina I. Marshall",
                                            "url": "/judges/marshall",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Joseph W. Nega",
                                            "url": "/judges/nega",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Cary Douglas Pugh",
                                            "url": "/judges/pugh",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Emin Toro",
                                            "url": "/judges/toro",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Patrick J. Urda",
                                            "url": "/judges/urda",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Kashi Way",
                                            "url": "/judges/way",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Christian N. Weiler",
                                            "url": "/judges/weiler",
                                        },
                                    },
                                ],
                                [  # Second column
                                    {
                                        "type": "h3WithAnchorTag",
                                        "value": {
                                            "text": "Senior Judges",
                                            "anchortag": "SENIOR",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Mary Ann Cohen",
                                            "url": "/judges/cohen",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Joseph Robert Goeke",
                                            "url": "/judges/goeke",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "David Gustafson",
                                            "url": "/judges/gustafson",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "James S. Halpern",
                                            "url": "/judges/halpern",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Mark V. Holmes",
                                            "url": "/judges/holmes",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Albert G. Lauber",
                                            "url": "/judges/lauber",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "L. Paige Marvel",
                                            "url": "/judges/marvel",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Richard T. Morrison",
                                            "url": "/judges/morrison",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Elizabeth Crewson Paris",
                                            "url": "/judges/paris",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Michael B. Thornton",
                                            "url": "/judges/thornton",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Juan F. Vasquez",
                                            "url": "/judges/vasquez",
                                        },
                                    },
                                ],
                                [  # Third column
                                    {
                                        "type": "h3WithAnchorTag",
                                        "value": {
                                            "text": "Special Trial Judges",
                                            "anchortag": "SPECIAL",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Lewis R. Carluzzo, Chief ST Judge",
                                            "url": "/judges/carluzzo",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Zachary S. Fried",
                                            "url": "/judges/fried",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Diana L. Leyden",
                                            "url": "/judges/leyden",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Peter J. Panuthos",
                                            "url": "/judges/panuthos",
                                        },
                                    },
                                    {
                                        "type": "clickableButton",
                                        "value": {
                                            "text": "Jennifer E. Siegel",
                                            "url": "/judges/siegel",
                                        },
                                    },
                                ],
                            ]
                        },
                    },
                ],
            )
        )

        EnhancedStandardPage.objects.filter(id=new_page.id).update(
            menu_item_name=title.upper(),
            navigation_category=NavigationCategories.ABOUT_THE_COURT,
        )

        self.logger.write(f"Created the '{title}' page.")
