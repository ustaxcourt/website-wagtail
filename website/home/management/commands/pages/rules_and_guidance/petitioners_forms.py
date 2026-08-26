from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import PetitionerExperiencePage
import logging

logger = logging.getLogger(__name__)


class PetitionersFormsPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners-forms"
        title = "Forms to File a Petition"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        # questions = [
        #     {
        #         "question": "What happens at the beginning of the trial session?",
        #         "answer": "On the first morning of the trial session, a Tax Court employee, the trial clerk, will announce the name of (call) each case that has not been settled. This process is known as a calendar call. Be sure to arrive in court in time to attend the calendar call. When your name is called by the trial clerk, come forward and identify yourself to the Judge by stating your name. The attorney representing the IRS will also state his/her name. The Judge may ask a few questions to determine the status of your case.<br/><br/>In many cities, there are tax clinics and organizations of tax practitioners that we refer to as calendar call programs; these practitioners may provide assistance to unrepresented taxpayers. If there is such a clinic or calendar call program in the city where you have requested trial, the Judge may identify the volunteer practitioners at the beginning of the trial session. If you want to speak with one of the clinic or calendar call lawyers, you should ask the Judge for an opportunity to do so.<br/><br/>After the calendar call, the Judge will schedule cases for trial at specific times and days during the trial session. The time and date for your trial will be announced by the Judge or the trial clerk.<br/><br/>Beginning two weeks before the start of a trial session, the parties may also jointly contact a Judge's chambers to request a time and date certain for trial. The Judge will attempt to accommodate the request, if practicable. You may not need to appear at the calendar call if your case has been set for a time and date certain.",
        #         "anchortag": "DURING1",
        #     },
        # ]
        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=title,
                introductory_text="Download forms you may need.",
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
                body=[],
            )
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")
