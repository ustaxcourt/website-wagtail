from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage

docs = {
    "dawson_pay_filing_fee.py": "",
    "Application_for_Waiver_of_Filing_Fee.pdf": "",
}

images = {
    "dawson_filing_fee_option_pay_by_debit_credit_pay_now.png": "",
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

        for image_name in images.keys():
            image_uploaded = self.load_image_from_images_dir(
                "dawson", image_name, images[image_name]
            )
            images[image_name] = image_uploaded

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
                    {
                        "type": "hr",
                        "value": True,
                    },
                    {
                        "type": "h2",
                        "value": "Tips & Tricks",
                    },
                    {
                        "type": "paragraph",
                        "value": """
<ul>
<li>Accepted payment methods include bank account/electronic check, Amazon or PayPal account, debit card, or credit card.</li>
<li>Be sure to have the Docket Number(s) handy for reference during the payment process.</li>
<li>You can also access the <a href="https://www.pay.gov/" title="pay.gov">pay.gov</a> site directly from DAWSON, if you have a DAWSON account.</li>
</ul>
""",
                    },
                    {
                        "type": "image",
                        "value": images[
                            "dawson_filing_fee_option_pay_by_debit_credit_pay_now.png"
                        ].id,
                    },
                    {
                        "type": "hr",
                        "value": True,
                    },
                    {
                        "type": "h2",
                        "value": "How to Pay the Filing Fee by Mail",
                    },
                    {
                        "type": "paragraph",
                        "value": """
To pay the filing fee by mail, make checks/money orders payable to:
<p>
Clerk, United States Tax Court<br/>
400 Second Street, NW<br/>
Washington, DC 20217
</p>
Include petitioner(s)' name(s) and Docket Number(s) on the check.
""",
                    },
                    {
                        "type": "hr",
                        "value": True,
                    },
                    {
                        "type": "h2",
                        "value": "How to Pay the Filing Fee in Person",
                    },
                    {
                        "type": "paragraph",
                        "value": """
Hand deliver the filing fee to the address below, making checks/money orders payable to:
<p>
Clerk, United States Tax Court<br/>
400 Second Street, NW<br/>
Washington, DC 20217
</p>
Include petitioner(s)' name(s) and Docket Number(s) on the check.
""",
                    },
                    {
                        "type": "hr",
                        "value": True,
                    },
                    {
                        "type": "h2",
                        "value": "Other Filing Fee Options",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""
Can't afford to pay the filing fee? Submit an <a href="{docs['Application_for_Waiver_of_Filing_Fee.pdf'].file.url}", title='Application for Waiver of Filing Fee'>Application for Waiver of Filing Fee</a>. This form is a fillable PDF.

<ol>
<li>Fill in the form.</li>
<li>Print the form, or save the file to your computer.</li>
<li>File the form to your case:
<ul>
<li>If you filed your petition electronically in DAWSON, you may upload the application to your case.</li>
<li>If you filed your petition by paper, <strong>hand deliver</strong> or <strong>mail the application</strong> to the address below:
<p>Clerk, United States Tax Court <br/>
400 Second Street, NW<br/>
Washington, DC 20217</p>
</li> </ul>
</ol>
                        """,
                    },
                    {
                        "type": "hr",
                        "value": True,
                    },
                    {
                        "type": "h2",
                        "value": "Need Help?",
                    },
                    {
                        "type": "paragraph",
                        "value": """Contact DAWSON Support at <a href="mailto:dawson.support@ustaxcourt.gov" title="Email dawson.support@ustaxcourt.gov">dawson.support@ustaxcourt.gov</a>.""",
                    },
                ],
            ),
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
