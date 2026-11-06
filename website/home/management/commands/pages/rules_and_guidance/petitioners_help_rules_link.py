import logging

from django.db import transaction
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
        """Add the Rules link if it is missing.

        Returns a log message describing what happened, or None if the page,
        the rules page, or the card could not be found and nothing was done.
        """
        page = Page.objects.filter(slug=self.PAGE_SLUG).first()
        rules_page = Page.objects.filter(slug="rules").first()
        if page is None or rules_page is None:
            logger.warning(
                f"'{self.PAGE_SLUG}' or 'rules' page not found. Skipping Rules link."
            )
            return None

        card = SideCard.objects.filter(
            page_id=page.pk, header_title=self.CARD_TITLE
        ).first()
        if card is None:
            logger.warning(f"'{self.CARD_TITLE}' card not found. Skipping Rules link.")
            return None

        raw_links = list(card.links.raw_data)
        if any(link["value"].get("text") == self.LINK_TEXT for link in raw_links):
            message = "Rules link already on the Helpful Links card."
            logger.info(message)
            return message

        card.links = raw_links + [build_rules_link(rules_page)]
        card.save()

        # SideCards live in revision content, so republish to keep the editor
        # from loading a revision without the new link.
        page.specific.save_revision().publish()
        message = "Added the Rules link to the Helpful Links card."
        logger.info(message)
        return message

    def run(self):
        if ExecuteScript.command_exists(self.COMMAND_NAME):
            logger.info(f"Script '{self.COMMAND_NAME}' already exists. Skipping.")
            return 0

        try:
            # The card save, the republish and the SUCCESS record commit
            # together, so a failed publish can't leave the card and the
            # latest revision out of sync.
            with transaction.atomic():
                message = self.update()
                if message is None:
                    # Nothing to update yet. Don't record the script, so the
                    # next deploy tries again.
                    return 0
                ExecuteScript.create_script(
                    self.COMMAND_NAME,
                    execution_status="SUCCESS",
                    execution_log=message,
                )

        except Exception as e:
            logger.error(e)
            ExecuteScript.create_script(
                self.COMMAND_NAME,
                execution_status="FAILURE",
                execution_log=f"<strong>Error:</strong> {e}",
            )
            raise
