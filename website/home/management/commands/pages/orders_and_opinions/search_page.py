from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.models import StandardPage
from home.management.commands.pages.page_initializer import PageInitializer


class SearchPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "order-opinion-search"
        title = "Order Opinions Search"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        content_type = ContentType.objects.get_for_model(StandardPage)

        home_page.add_child(
            instance=StandardPage(
                title=title,
                body="Search Page - Redirect",
                slug=slug,
                seo_title=title,
                search_description="Dawson Search",
                content_type=content_type,
            )
        )

        self.logger.write(f"Successfully created the '{title}' page.")
