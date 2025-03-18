from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationCategories, EnhancedStandardPage, IconCategories


class EmploymentPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "employment"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            self.logger.write("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Employment"

        if Page.objects.filter(slug=self.slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description="Employment",
                show_in_menus=True,
                body=[
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Vacancy Announcements",
                                    "icon": IconCategories.CHEVRON_RIGHT,
                                    "document": None,
                                    "url": "/employment/vacancy-announcements",
                                },
                                {
                                    "title": "Internship Programs",
                                    "icon": IconCategories.CHEVRON_RIGHT,
                                    "document": None,
                                    "url": "/internship-programs",
                                },
                                {
                                    "title": "Law Clerk Program",
                                    "icon": IconCategories.CHEVRON_RIGHT,
                                    "document": None,
                                    "url": "/law-clerk-program",
                                },
                            ],
                        },
                    },
                ],
            )
        )

        EnhancedStandardPage.objects.filter(id=new_page.id).update(
            menu_item_name="EMPLOYMENT",
            navigation_category=NavigationCategories.ABOUT_THE_COURT,
        )

        self.logger.write(f"Created the '{title}' page.")
