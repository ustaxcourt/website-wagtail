from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import IconCategories
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)

practitioners_docs = {
    "04292025.pdf": "",
    "01282025.pdf": "",
    "02202024.pdf": "",
    "05082023.pdf": "",
    "05302024.pdf": "",
    "09232024.pdf": "",
    "10222024.pdf": "",
    "11282023.pdf": "",
    "2018_Nonattorney_Exam.pdf": "",
    "2021_Nonattorney_Exam.pdf": "",
    "2023_Nonattorney_Exam.pdf": "",
    "Administrative_Order_2020-03.pdf": "",
    "Admissions_Information_Attorney_12212021.pdf": "",
    "Application_for_Admission_to_Practice_Attorney_Form_30.pdf": "",
    "DAWSON_Practitioner_Training_Guide.pdf": "",
    "DAWSON_Reminders_for_Practitioners.pdf": "",
    "NonAttorney_Exam_Statistics.pdf": "",
    "Nonattorney_Examination_Procedures_050322.pdf": "",
    "Rule-200(2nd-amended).pdf": "",
    "Rule-201.pdf": "",
    "Rule-202.pdf": "",
    "lea_faq.pdf": "",
}


class GuidenceForPractitionersPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "practitioners"
        title = "Guidance for Practitioners"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        for doc_name in practitioners_docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            practitioners_docs[doc_name] = document

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=None,
                search_description="Guidance for Practitioners",
                body=[
                    {"type": "h2", "value": "Electronic Case Access and Filing"},
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "DAWSON Practitioner Training Guide",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs[
                                        "DAWSON_Practitioner_Training_Guide.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "DAWSON Tips and Reminders for Practitioners",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs[
                                        "DAWSON_Reminders_for_Practitioners.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Case Procedure Information",
                                    "icon": IconCategories.LINK,
                                    "document": None,
                                    "url": "/case-procedure",
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {"type": "h2", "value": "Tax Court Bar"},
                    {"type": "h3", "value": "Rules of Practice and Procedure"},
                    {
                        "type": "paragraph",
                        "value": """The Court's Rules of Practice and Procedure governing admission and discipline can be found in Title XX, Practice Before the Court:""",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Rule 200. Admission to Practice and Periodic Registration Fee",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs[
                                        "Rule-200(2nd-amended).pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Rule 201. Conduct of Practice Before the Court",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs["Rule-201.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Rule 202. Disciplinary Matters",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs["Rule-202.pdf"].id,
                                    "url": None,
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {"type": "h3", "value": "Admission of Attorneys"},
                    {
                        "type": "paragraph",
                        "value": f"""On May 2, 2020, the Court announced that attorney applications for admission to practice before the Court may be emailed to the <a href="mailto:Admissions@ustaxcourt.gov" title="Email Admissions@ustaxcourt.gov">Admissions Office</a> and must include:
                        <ul>
                            <li><a href="{practitioners_docs["Application_for_Admission_to_Practice_Attorney_Form_30.pdf"].file.url}" title="Application for Admission to Practice, Form 30" target="_blank">Application for Admission to Practice, Form 30</a>. For instructions on completing the form, please see <a href="{practitioners_docs["Admissions_Information_Attorney_12212021.pdf"].file.url}" title="Admissions Information for Attorneys" target="_blank">Admissions Information for Attorneys</a>.</li>
                            <li>Proof of payment of the $50 Application Fee (pay via <a href="https://www.pay.gov/public/form/start/16762207" title="Pay.gov">Pay.gov</a>).</li>
                            <li>A certificate of good standing from the Clerk of the appropriate court issued within 90 calendar days of the application filing date.</li>
                        </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {"type": "h3", "value": "Admission of Nonattorneys"},
                    {
                        "type": "paragraph",
                        "value": f"""A nonattorney may be admitted to practice before the Court provided the requirements outlined in the Tax Court Rules of Practice and Procedure are satisfied. See <a href="{practitioners_docs["Rule-200(2nd-amended).pdf"].file.url}" title="Rule 200" target="_blank">Rule 200</a>, Tax Court Rules of Practice and Procedure.
                        <br/><br/><strong>Resources</strong>""",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Press Release announcing the 2023 Nonattorney Examination",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs["05082023.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Statistical Information Regarding the Nonattorney Examination",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs[
                                        "NonAttorney_Exam_Statistics.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Procedures for the Preparation and Grading of the Nonattorney Examination",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs[
                                        "Nonattorney_Examination_Procedures_050322.pdf"
                                    ].id,
                                    "url": None,
                                },
                            ],
                        },
                    },
                    {
                        "type": "paragraph",
                        "value": """Downloadable copies of the last three examinations can be found below. To order paper copies, please submit a request via <a href="https://www.pay.gov/public/form/start/16749996" title="Pay.gov">Pay.gov</a>.""",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Prior Year Exam 2018",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs[
                                        "2018_Nonattorney_Exam.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Prior Year Exam 2021",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs[
                                        "2021_Nonattorney_Exam.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Prior Year Exam 2023",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs[
                                        "2023_Nonattorney_Exam.pdf"
                                    ].id,
                                    "url": None,
                                },
                            ],
                        },
                    },
                    {
                        "type": "paragraph",
                        "value": f"""
                        <strong>Character and Fitness</strong><br/><br/>
                        An applicant must establish to the satisfaction of the Court that he or she is of good moral and professional character, including by providing sponsorship letters. See <a href="{practitioners_docs["Rule-200(2nd-amended).pdf"].file.url}" title="Rule 200" target="_blank">Rule 200</a>, Tax Court <a href="/rules" title="Rules of Practice and Procedure">Rules of Practice and Procedure</a>. Accordingly, after administration of the Nonattorney Exam, those who pass will be required to undergo a character and fitness review. The review will include requests for additional background information, sponsorship letters, and a remote interview. Any necessary documentation will be requested at that time.""",
                    },
                    {"type": "hr", "value": True},
                    {"type": "h3", "value": "Certificates of Good Standing"},
                    {
                        "type": "paragraph",
                        "value": """
                        <ul>
                            <li>To request an electronic certificate of good standing free of charge, email your request to the <a href="mailto:Admissions@ustaxcourt.gov" title="Email Admissions@ustaxcourt.gov">Admissions Office</a> with your name and US Tax Court bar number.</li>
                            <li>To request a paper certificate of good standing with the Court's raised seal, submit $15 payment via <a href="https://www.pay.gov/public/form/start/802285219" title="Pay.gov">Pay.gov</a> and it will be mailed directly to you.</li>
                        </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {"type": "h3", "value": "Disciplinary Matters"},
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Disciplinary Matters Press Release - April 29, 2025",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs["04292025.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Disciplinary Matters Press Release - January 28, 2025",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs["01282025.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Disciplinary Matters Press Release - October 22, 2024",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs["10222024.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Disciplinary Matters Press Release - September 23, 2024",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs["09232024.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Disciplinary Matters Press Release - May 30, 2024",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs["05302024.pdf"].id,
                                    "url": None,
                                },
                            ],
                        },
                    },
                    {
                        "type": "paragraph",
                        "value": """For additional disciplinary action, refer to previous <a href="/press-releases" title="Press Releases">Press Releases</a>.""",
                    },
                    {"type": "hr", "value": True},
                    {"type": "h2", "value": "Limited Entries of Appearance"},
                    {
                        "type": "paragraph",
                        "value": f"""On May 29, 2020, the Court issued <a href="{practitioners_docs["Administrative_Order_2020-03.pdf"].file.url}" title="Administrative Order 2020-03" target="_blank">Administrative Order 2020-03</a> which outlines the procedures for entering a limited entry of appearance. These procedures are effective June 1, 2020.""",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Administrative Order 2020-03 - Limited Entry of Appearance Procedures",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs[
                                        "Administrative_Order_2020-03.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Frequently Asked Questions Regarding Limited Entries of Appearance",
                                    "icon": IconCategories.PDF,
                                    "document": practitioners_docs["lea_faq.pdf"].id,
                                    "url": None,
                                },
                            ]
                        },
                    },
                ],
            )
        )
