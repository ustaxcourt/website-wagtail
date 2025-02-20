from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import IconCategories, NavigationCategories
from home.models import EnhancedStandardPage

practitioners_docs = {
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
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "practitioners"
        title = "Guidance for Practitioners"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        for doc_name in practitioners_docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory="guidence_for_practitioners",
                filename=doc_name,
                title=doc_name,
            )
            practitioners_docs[doc_name] = document

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=None,
                search_description="Guidance for Practitioners",
                body=[
                    {"type": "heading", "value": "Electronic Case Access and Filing"},
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
                                    "url": "/case_procedure",
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {"type": "heading", "value": "Tax Court Bar"},
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "DAWSON Self-Represented (Pro Se) Training Guide",
                                    "icon": IconCategories.PDF,
                                    "document": document.id,
                                    "url": None,
                                },
                                {
                                    "title": " Clinic Program Information",
                                    "icon": IconCategories.INFO_CIRCLE_FILLED,
                                    "document": None,
                                    "url": "/clinics",
                                },
                                {
                                    "title": "Case Procedure Information",
                                    "icon": IconCategories.INFO_CIRCLE_FILLED,
                                    "document": None,
                                    "url": "/case_procedure",
                                },
                            ]
                        },
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": "For more detailed information, consult the Tax Court <a href='/rules'>Rules of Practice and Procedure</a>.",
                    },
                ],
                show_in_menus=True,
            )
        )

        EnhancedStandardPage.objects.filter(id=new_page.id).update(
            menu_item_name="GUIDANCE FOR PETITIONERS",
            navigation_category=NavigationCategories.RULES_AND_GUIDANCE,
        )
