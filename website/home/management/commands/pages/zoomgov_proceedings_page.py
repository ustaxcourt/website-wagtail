from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.models import ZoomProceedingsDetailPage, RemoteProceedingsPage
from home.management.commands.pages.page_initializer import PageInitializer
# from wagtail.admin.panels import PageChooserPanel


class ZoomProceedingsDetailPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        """Creates the Zoom Proceedings Detail Page under Remote Proceedings Page."""
        try:
            parent_page = RemoteProceedingsPage.objects.get(slug="zoomgov")
        except RemoteProceedingsPage.DoesNotExist:
            self.logger.write(
                "Remote Proceedings Page does not exist. Create it first."
            )
            return

        self.create_page_info(parent_page)

    def create_page_info(self, parent_page):
        child_slug = "zoomgov_proceedings"
        child_title = "ZoomGov Proceedings"

        if Page.objects.filter(slug=child_slug).exists():
            self.logger.write(f"- {child_title} page already exists.")
            return

        self.logger.write(f"Creating the '{child_title}' page.")

        content_type = ContentType.objects.get_for_model(ZoomProceedingsDetailPage)

        new_page = parent_page.add_child(
            instance=ZoomProceedingsDetailPage(
                title=child_title,
                body="Detailed information about Zoom proceedings.",
                slug=child_slug,
                seo_title=child_title,
                search_description="Details on Zoom proceedings for remote court sessions.",
                content_type=content_type,
                show_in_menus=True,
                additional_info="Additional information regarding Zoom proceedings.",
            )
        )
        new_page.save_revision().publish()

        self.logger.write(f"Successfully created the '{child_title}' page.")
