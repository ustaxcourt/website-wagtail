from wagtail.models import Page
from home.models import RedirectPage
from home.management.commands.pages.page_initializer import PageInitializer
from django.contrib.contenttypes.models import ContentType


class RedirectPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "redirect"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "redirect"
        title = "redirect"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        content_type = ContentType.objects.get_for_model(RedirectPage)

        new_page = home_page.add_child(
            instance=RedirectPage(
                title=title,
                body="You are now leaving the Official Web Site of the United States Tax Court. One moment please....",
                slug=slug,
                seo_title=title,
                search_description="redirect",
                content_type=content_type,
                show_in_menus=True,
            )
        )

        self.logger.write(f"Successfully created the '{new_page.title}' page.")
