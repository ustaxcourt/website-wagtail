from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.snippets.call_to_action import CallToActionBox
import logging

logger = logging.getLogger(__name__)


class PetitionersHelpPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners-help"
        title = "Frequently Asked Questions"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        _snippet_name = "Ready to begin your petition?"
        _cta_box = CallToActionBox.objects.filter(header=_snippet_name).first()
        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=title,
                call_to_action=_cta_box,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
            )
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")
