from django.db import transaction
from wagtail.models import GroupPagePermission, Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.management.commands.snippets.dawson_faqs_ribbon import (
    dawson_faqs_ribbon_name,
)
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript
from home.utils.page_references import repoint_page_references
import logging

logger = logging.getLogger(__name__)


class DawsonUserGuidesPEPageInitializer(PageInitializer):
    """
    Replace the EnhancedStandardPage at /dawson-user-guides with a
    PetitionerExperiencePage, without breaking internal links to it.

    Internal links point at the page ID, so: build the new page under a
    temporary slug, repoint every reference to the old page at the new one,
    delete the old page, then take over its slug.
    """

    COMMAND_NAME = "Replace DAWSON User Guides page with a Petitioner Experience page"

    def __init__(self):
        super().__init__()
        self.slug = "dawson-user-guides"
        self.temp_slug = "dawson-user-guides-pe"
        self.title = "DAWSON User Guides"

    def create(self):
        old_page = Page.objects.filter(slug=self.slug).first()
        if old_page is None:
            logger.info(f"- No '{self.slug}' page to replace.")
            return
        if isinstance(old_page.specific, PetitionerExperiencePage):
            logger.info(f"- {self.title} is already a Petitioner Experience page.")
            return

        with transaction.atomic():
            new_page = self.create_draft_page(old_page.get_parent())

            for line in repoint_page_references(old_page, new_page):
                logger.info(f"  repointed: {line}")

            # Not in the ReferenceIndex, but would cascade-delete with the old page.
            GroupPagePermission.objects.filter(page=old_page).update(page=new_page)
            for child in old_page.get_children():
                child.move(new_page, pos="last-child")

            old_page.delete()

            # Publish only after taking the slug, so the temp slug is never live
            # and no auto-redirect gets created from it.
            new_page.refresh_from_db()
            new_page.slug = self.slug
            new_page.save_revision().publish()

        logger.info(f"Replaced the '{self.title}' page (now page {new_page.pk}).")

    def create_draft_page(self, parent):
        # TODO: placeholder content - swap in the real page design.
        navigation_ribbon = NavigationRibbon.objects.filter(
            name=dawson_faqs_ribbon_name
        ).first()

        new_page = parent.add_child(
            instance=PetitionerExperiencePage(
                title=self.title,
                slug=self.temp_slug,
                seo_title=self.title,
                search_description=self.title,
                navigation_ribbon=navigation_ribbon,
                introductory_text="<p>Placeholder Petitioner Experience version of the DAWSON User Guides page.</p>",
                live=False,
            )
        )
        new_page.save_revision()
        return new_page

    def run(self):
        if ExecuteScript.command_exists(self.COMMAND_NAME):
            logger.info(f"Script '{self.COMMAND_NAME}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(self.COMMAND_NAME)

        try:
            self.create()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = f"{self.title} page replaced successfully."
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
