from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)

petitioners_docs = {
    "Dubroff_Hellwig.pdf": "",
    "Petition_Kit.pdf": "",
}


class PetitionersAboutInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners-about"
        title = "Guidance for Petitioners: About the Court"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        for document in petitioners_docs.keys():
            uploaded_document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=document,
                title=document,
            )
            petitioners_docs[document] = uploaded_document.file.url

        questions = [
            {
                "question": "What is the United States Tax Court?",
                "answer": "The United States Tax Court is a Federal trial court. Because it is a court of record, a record is made of all its proceedings. It is an independent judicial forum. It is not controlled by or connected with the Internal Revenue Service (IRS). Congress created the Tax Court as an independent judicial authority for taxpayers disputing certain IRS determinations. The Tax Court’s authority to resolve these disputes is called its jurisdiction. Generally, a taxpayer may file a petition in the Tax Court in response to certain IRS determinations. A taxpayer who begins such a proceeding is known as the “petitioner”, and the Commissioner of Internal Revenue is the “respondent”. <br><br>The Tax Court is based in Washington, D.C. Its <strong><a href='/judges' title='Judges'>Judges</a></strong> and <strong><a href='/judges' title='Judges'>Special Trial Judges</a></strong> preside at trials in 74 U.S. <strong><a href='/dpt-cities' title='Places of Trial'>cities</a></strong>.",
                "anchortag": "START1",
            },
            {
                "question": "What are the Tax Court's hours of operation?",
                "answer": 'The Tax Court is open from 8 a.m. to 4:30 p.m. (EST) on all days except Saturdays, Sundays, and <strong><a href="/holidays" title="Legal holidays">legal holidays</a></strong> in the District of Columbia.',
                "anchortag": "START2",
            },
            {
                "question": "What is the life cycle of a Tax Court case?",
                "answer": f'A case in the Tax Court is commenced by the filing of a petition. The petition must be timely filed within the allowable time. The Court cannot extend the time for filing which is set by statute.<br><br>A $60 filing fee must be paid when the petition is filed. Once the petition is filed, payment of the underlying tax ordinarily is postponed until the case has been decided.<br><br>In certain tax disputes involving $50,000 or less, taxpayers may elect to have their case conducted under the Court\'s simplified <strong><a href="{petitioners_docs["Petition_Kit.pdf"]}" target="_blank" title="Petition Kit">small tax case procedure</a></strong>. Trials in small tax cases generally are less formal and result in a speedier disposition. However, decisions entered pursuant to small tax case procedures are not appealable.<br><br>Cases are calendared for trial as soon as practicable (on a first in/ first out basis) after the case becomes at issue. When a case is calendared, the parties are notified by the Court of the date, time, and place of trial. Trials are conducted before one judge, without a jury, and taxpayers are permitted to represent themselves if they desire. Taxpayers may be represented by practitioners admitted to the bar of the Tax Court.<br><br>Most cases are settled by mutual agreement without trial. However, if a trial is conducted, in due course a report is ordinarily issued by the presiding judge setting forth findings of fact and an opinion. The case is then closed in accordance with the judge\'s opinion by entry of a decision.',
                "anchortag": "START3",
            },
            {
                "question": "How can I obtain information about the history of the Tax Court?",
                "answer": f'The revised and expanded <strong><em><a href="{petitioners_docs["Dubroff_Hellwig.pdf"]}" target="_blank" title="The United States Tax Court: An Historical Analysis (Second Edition)">The United States Tax Court: An Historical Analysis (Second Edition)</em></a></strong> by Professors Harold Dubroff and Brant J. Hellwig is available as a <strong><a href="{petitioners_docs["Dubroff_Hellwig.pdf"]}" target="_blank"> PDF download</a></strong> (6MB) or at the <strong><a href="https://bookstore.gpo.gov/user/login?destination=node/10107" target="_blank" title="Government Printing Office bookstore">Government Printing Office bookstore</a></strong> in print and other e-pub formats.',
                "anchortag": "START4",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Guidance for Petitioners - About the Court",
                body=[
                    {"type": "h2", "value": "About the Court"},
                    {"type": "questionanswers", "value": questions},
                ],
            )
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")
