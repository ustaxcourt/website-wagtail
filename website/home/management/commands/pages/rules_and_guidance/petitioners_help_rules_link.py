import logging

from wagtail.models import Page

from home.management.commands.pages.rules_and_guidance.side_card_seed_data import (
    build_rules_link,
)
from home.models import SideCard
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)


class PetitionersHelpRulesLinkUpdater:
    """Append the "Tax Court Rules" link to the existing Helpful Links card.

    Edits the card in place rather than recreating the page, so editor
    changes on the Petitioners Help page survive.
    """

    COMMAND_NAME = "WAG-1465: Add Rules link to Petitioners Help Helpful Links card"
    PAGE_SLUG = "petitioners-help"
    CARD_TITLE = "Helpful Links"
    LINK_TEXT = "Tax Court Rules"

    def update(self):
        page = Page.objects.filter(slug=self.PAGE_SLUG).first()
        rules_page = Page.objects.filter(slug="rules").first()
        if page is None or rules_page is None:
            logger.warning(
                f"'{self.PAGE_SLUG}' or 'rules' page not found. Skipping Rules link."
            )
            return

        card = SideCard.objects.filter(
            page_id=page.pk, header_title=self.CARD_TITLE
        ).first()
        if card is None:
            logger.warning(f"'{self.CARD_TITLE}' card not found. Skipping Rules link.")
            return

        raw_links = list(card.links.raw_data)
        if any(link["value"].get("text") == self.LINK_TEXT for link in raw_links):
            logger.info("Rules link already on the Helpful Links card.")
            return

        card.links = raw_links + [build_rules_link(rules_page)]
        card.save()

        # SideCards live in revision content, so republish to keep the editor
        # from loading a revision without the new link.
        page.specific.save_revision().publish()
        logger.info("Added the Rules link to the Helpful Links card.")

    def run(self):
        if ExecuteScript.command_exists(self.COMMAND_NAME):
            logger.info(f"Script '{self.COMMAND_NAME}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(self.COMMAND_NAME)

        try:
            self.update()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = "Rules link added to Helpful Links card."
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
