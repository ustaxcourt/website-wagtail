from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.models import StandardPage
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationCategories


class TodaysOpinionsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "todays_opinions"
        title = "Todays Opinions"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        content_type = ContentType.objects.get_for_model(StandardPage)

        new_page = home_page.add_child(
            instance=StandardPage(
                title=title,
                body="Todays Opinions Page - Redirect",
                slug=slug,
                seo_title=title,
                search_description="Todays Opinions",
                content_type=content_type,
                show_in_menus=True,
            )
        )

        StandardPage.objects.filter(id=new_page.id).update(
            menu_item_name="TODAY'S OPINIONS",
            navigation_category=NavigationCategories.ORDERS_AND_OPINIONS,
            redirectLink="https://dawson.ustaxcourt.gov/todays-opinions",
        )

        self.logger.write(f"Successfully created the '{title}' page.")
