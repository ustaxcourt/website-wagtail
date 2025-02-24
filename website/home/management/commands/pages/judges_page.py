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
                        "type": "paragraph",
                        "value": "<p>Learn more about the judges of the United States Tax Court.</p>",
                    },
                    {
                        "type": "column",
                        "value": [
                            {
                                "type": "paragraph",
                                "value": "<p>Click on a judge's name to learn more about them.</p>",
                            },
                            {
                                "type": "judges",
                                "value": "Text to be replaced by the judges list.",
                            },
                        ],
                    },
                ],
            )
        )

        EnhancedStandardPage.objects.filter(id=new_page.id).update(
            menu_item_name=title.upper(),
            navigation_category=NavigationCategories.ABOUT_THE_COURT,
        )

        self.logger.write(f"Created the '{title}' page.")
