import logging

from wagtail.models import Page

from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon, PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)

PETITIONER_RIBBON_NAME = "Guidance for Petitioners Ribbon"


class PetitionerExperiencePageInitializer(PageInitializer):
    slug = ""
    title = ""
    introductory_text = ""
    command_name = ""

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        if ExecuteScript.command_exists(self.command_name):
            logger.info("Script '%s' already exists. Skipping.", self.command_name)
            return

        script_entry = ExecuteScript.create_script(self.command_name)
        try:
            if Page.objects.filter(slug=self.slug).exists():
                logger.info("- %s page already exists.", self.title)
                script_entry.execution_status = "SUCCESS"
                script_entry.execution_log = (
                    f"Skipped creation because the '{self.slug}' page already exists."
                )
            else:
                navigation_ribbon = NavigationRibbon.objects.filter(
                    name=PETITIONER_RIBBON_NAME
                ).first()
                page = home_page.add_child(
                    instance=PetitionerExperiencePage(
                        title=self.title,
                        slug=self.slug,
                        seo_title=self.title,
                        search_description=self.title,
                        navigation_ribbon=navigation_ribbon,
                        show_floating_definitions_button=True,
                        introductory_text=self.introductory_text,
                    )
                )
                page.save_revision().publish()
                logger.info("Created the '%s' page.", self.title)
                script_entry.execution_log = f"Created the '{self.slug}' page."
                script_entry.execution_status = "SUCCESS"
            script_entry.save()
        except Exception as error:
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {error}"
            script_entry.save()
            raise


class GuidanceForSelfRepresentedPetitionersPageInitializer(
    PetitionerExperiencePageInitializer
):
    slug = "petitioners"
    title = "Guidance for Self-Represented Petitioners"
    introductory_text = (
        "“Pro Se” (pronounced pro say) means representing yourself without an attorney "
        "or other authorized practitioner."
    )
    command_name = "Create Petitioner Experience Guidance page"


class ProcessAndTimelinePageInitializer(PetitionerExperiencePageInitializer):
    slug = "petitioners-timeline"
    title = "Process and Timeline"
    introductory_text = (
        "What to expect during the tax court process, what documents you will need, "
        "links to forms, and a checklist to use."
    )
    command_name = "Create Petitioner Experience Process and Timeline page"


class PrepareToFilePageInitializer(PetitionerExperiencePageInitializer):
    slug = "petitioners-prepare-to-file"
    title = "Prepare to File"
    introductory_text = (
        "The United States Tax Court encourages electronic filing through DAWSON, the "
        "court’s electronic filing and case management system."
        "<p><strong>Note:</strong> If filing using DAWSON, once you start this process "
        "you won’t be able to save your work and come back to it. Petitioners who file "
        "by paper cannot immediately switch to electronic access. To protect your "
        "information, the Court will mail identity verification instructions to your "
        "address of record. Switching to electronic access will be available only after "
        "the verification process is complete. Consider filing electronically from the "
        "start to get electronic access to your case immediately.</p>"
    )
    command_name = "Create Petitioner Experience Prepare to File page"


class FormsToFilePetitionPageInitializer(PetitionerExperiencePageInitializer):
    slug = "petitioners-forms"
    title = "Forms to File a Petition"
    introductory_text = "Download forms you may need."
    command_name = "Create Petitioner Experience Forms page"


class FrequentlyAskedQuestionsPageInitializer(PetitionerExperiencePageInitializer):
    slug = "petitioners-help"
    title = "Frequenetly Asked Questions"
    introductory_text = ""
    command_name = "Create Petitioner Experience Help page"
