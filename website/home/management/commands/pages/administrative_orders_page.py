from wagtail.admin.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import models
from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import StandardPage


class AdministrativeOrdersPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "administrative_orders"
        title = "Administrative Orders"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        _ = models.ForeignKey(
            "PDFListComponent", null=True, blank=True, on_delete=models.SET_NULL
        )

        content_panels = Page.content_panels + [
            SnippetChooserPanel("pdf_list"),
        ]

        _ = StandardPage(
            title=title,
            draft_title=title,
            slug=slug,
            search_description="Administrative Orders",
            seo_title=title,
            content_panels=content_panels,
        )
