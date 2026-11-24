import logging

from django.db import transaction
from wagtail.models import Page

from home.models import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)


class PetitionersDefinitionsButtonUpdater:
    """Enable and publish the floating Definitions button on Petitioners pages."""

    COMMAND_NAME = "Enable Definitions button on Petitioners guidance pages"
    PAGE_SLUGS = (
        "petitioners-guidance",
        "petitioners-help",
        "petitioners-forms",
        "petitioners-prepare-to-file",
        "petitioners-timeline",
    )

    def update(self):
        pages = {
            page.slug: page
            for page in Page.objects.filter(slug__in=self.PAGE_SLUGS).specific()
            if isinstance(page, PetitionerExperiencePage)
        }
        missing_slugs = set(self.PAGE_SLUGS) - pages.keys()
        if missing_slugs:
            logger.warning(
                "Petitioners guidance pages not found; skipping Definitions button "
                "update: %s",
                ", ".join(sorted(missing_slugs)),
            )
            return None

        updated_slugs = []
        for slug in self.PAGE_SLUGS:
            page = pages[slug]
            if page.show_floating_definitions_button:
                continue

            page.show_floating_definitions_button = True
            page.save_revision().publish()
            updated_slugs.append(slug)

        if updated_slugs:
            message = (
                "Enabled the Definitions button on: " + ", ".join(updated_slugs) + "."
            )
        else:
            message = "Definitions button is already enabled on all Petitioners guidance pages."
        logger.info(message)
        return message

    def run(self):
        if ExecuteScript.command_exists(self.COMMAND_NAME):
            logger.info("Script '%s' already exists. Skipping.", self.COMMAND_NAME)
            return 0

        try:
            with transaction.atomic():
                message = self.update()
                if message is None:
                    return 0
                ExecuteScript.create_script(
                    self.COMMAND_NAME,
                    execution_status="SUCCESS",
                    execution_log=message,
                )
        except Exception as error:
            logger.exception("Failed to enable the Definitions button.")
            ExecuteScript.create_script(
                self.COMMAND_NAME,
                execution_status="FAILURE",
                execution_log=f"<strong>Error:</strong> {error}",
            )
            raise

        return 0
