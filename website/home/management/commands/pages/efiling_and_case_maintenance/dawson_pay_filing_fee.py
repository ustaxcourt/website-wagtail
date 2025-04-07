from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage

docs = {
    "dawson_pay_filing_fee.py": "",
    "Application_for_Waiver_of_Filing_Fee.pdf": "",
}


class DawsonPayFilingFeeInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "pay-filing-fee"
        title = "How to Pay the Filing Fee"

        page = Page.objects.filter(slug=slug).first()
        if page:
            self.logger.write(f"- {title} page already exists. Updating...")
            return

        self.logger.write(f"Creating the '{title}' page.")

        for doc_name in docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            docs[doc_name] = document

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=None,
                search_description=title,
                body=[
                    {
                        "type": "paragraph",
                        "value": f"""
                            Filing fees are required to submit a petition. The Court’s filing fee is $60 and may be paid online, by mail, or in person. The fee may be waived by filing an <a href="{docs['Application_for_Waiver_of_Filing_Fee.pdf'].file.url}">Application for Waiver of Filing Fee</a>. Your petition must be processed by the Court before the Application for Waiver of Filing fee can be filed electronically.
                        """,
                    },
                ],
            ),
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
