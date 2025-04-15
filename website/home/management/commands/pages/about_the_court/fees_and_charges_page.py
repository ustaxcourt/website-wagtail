from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import IconCategories

documents = {
    "Rule-190.pdf": "",
    "Rule-200(2nd-amended).pdf": "",
    "Rule-148.pdf": "",
    "Rule-11(superseded).pdf": "",
    "fee_schedule.pdf": "",
}

documents_ids = {}


class FeesAndChargesPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "fees-and-charges"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Fees & Charges"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        for document in documents.keys():
            uploaded_document = self.load_document_from_documents_dir(None, document)
            documents[document] = uploaded_document.file.url
            documents_ids[document] = uploaded_document.id

        body_content = [
            {"type": "h1", "value": "Fees & Charges"},
            {
                "type": "alert",
                "value": {
                    "alert_type": "success",
                    "content": "<strong>PAYMENT BY CREDIT CARD</strong><br/><br/>The Tax Court offers the option of paying for certain court fees by credit or debit card through <strong><a href='https://www.pay.gov/public/search/agencyforms?agencyFilters=United+States+Tax+Court&searchCategory=PAYMENT&searchType=AGENCYPAYMENT&agencyId=1392'>Pay.gov</a></strong>. Information on paying by check is below.",
                },
            },
            {
                "type": "alert",
                "value": {
                    "alert_type": "info",
                    "content": "<strong>NOTICE TO CUSTOMERS MAKING PAYMENT BY CHECK</strong><br/><br/>Any check sent to the U.S. Tax Court will be converted into an electronic funds transfer (EFT). We will scan your check and use the account information on it to electronically debit your account for the amount of the check. The debit from your account will usually occur within 24 hours and will be shown on your regular account statement.<br/><br/>We will not return your original check. It will be destroyed, but we will keep an electronic copy. If the EFT cannot be processed for technical reasons, your submission of the check for payment authorizes us to process the electronic copy in place of the original check. If the EFT cannot be completed because of insufficient funds, we may try to make the transfer up to two times.<br/><br/><strong>Privacy Information</strong> - The United States Tax Court's authority to collect fees associated with case processing is documented under Title 26 United States Code Sections 7451 & 7471 through 7475. Information captured from checks received will be strictly used in accordance with the petitioner's request to process their respective cases. Furnishing the check information is voluntary, but a decision not to do so may require you to make payment by some other method.<br/><br/><strong>Checks and money orders should be made payable to \"Clerk, United States Tax Court\".</strong>",
                },
            },
            {
                "type": "links",
                "value": {
                    "links": [
                        {
                            "title": "Fee Schedule",
                            "icon": IconCategories.PDF,
                            "document": documents_ids["fee_schedule.pdf"],
                            "url": None,
                        },
                    ]
                },
            },
            {"type": "hr", "value": True},
            {"type": "h2", "value": "Filing Fees"},
            {
                "type": "paragraph",
                "value": '<em>(Issued in accordance with 26 U.S.C. sections 7451 and 7470 and </em><strong><em><a href="'
                + documents["Rule-190.pdf"]
                + '" target="_blank" title="Rule 190">Rule 190</a></em></strong><em>)</em>',
            },
            {"type": "hr", "value": True},
            {
                "type": "unstyled_table",
                "value": {
                    "columns": [
                        {"type": "text", "heading": "Fee Type"},
                        {"type": "text", "heading": "Amount"},
                    ],
                    "rows": [
                        {"values": ["<strong>Petition Filing Fee</strong>", "$60.00"]},
                        {
                            "values": [
                                "<strong>Notice of Appeal Filing Fee</strong>",
                                'Amount of filing fee determined under the Court of Appeals <a href="https://www.uscourts.gov/services-forms/fees/court-appeals-miscellaneous-fee-schedule" target="_blank">Miscellaneous Fee Schedule</a> issued pursuant to 28 U.S.C. sec. 1913.',
                            ]
                        },
                    ],
                },
            },
            {"type": "hr", "value": True},
            {"type": "h2", "value": "Admission and Membership Fees"},
            {
                "type": "paragraph",
                "value": '<em>(Issued in accordance with 26 U.S.C. sections 7451, 7452 and 7470 and </em><strong><em><a href="'
                + documents["Rule-200(2nd-amended).pdf"]
                + '" target="_blank" title="Rule 200(a) and (g)">Rule 200(a) and (g)</a></em></strong><em>)</em>',
            },
            {"type": "hr", "value": True},
            {
                "type": "unstyled_table",
                "value": {
                    "columns": [
                        {"type": "text", "heading": "Fee Type"},
                        {"type": "text", "heading": "Amount"},
                    ],
                    "rows": [
                        {
                            "values": [
                                "<strong>Original admission to practice before the Court</strong>",
                                "$50.00",
                            ]
                        },
                        {
                            "values": [
                                "<strong>Application for nonattorney examination</strong>",
                                "$150.00",
                            ]
                        },
                        {
                            "values": [
                                "<strong>Certificate of admission suitable for framing</strong>",
                                "$15.00",
                            ]
                        },
                        {
                            "values": [
                                "<strong>Certificate of good standing</strong>",
                                "$15.00",
                            ]
                        },
                    ],
                },
            },
            {"type": "hr", "value": True},
            {"type": "h2", "value": "Copy Fees"},
            {
                "type": "paragraph",
                "value": "<em>(Issued in accordance with 26 U.S.C. sections 7451 and 7474)</em>",
            },
            {"type": "hr", "value": True},
            {
                "type": "unstyled_table",
                "value": {
                    "columns": [
                        {"type": "text", "heading": "Fee Type"},
                        {"type": "text", "heading": "Amount"},
                    ],
                    "rows": [
                        {
                            "values": [
                                "<strong>Reproducing a paper copy from original documents</strong>",
                                "$0.50 per page; per-document cap of $3.00",
                            ]
                        },
                        {
                            "values": [
                                "<strong>Certification of document or paper</strong>",
                                "$10.00",
                            ]
                        },
                        {
                            "values": [
                                "<strong>Copy of transcripts of proceedings</strong>",
                                "Available from the Court reporter for the first 90 days at such rates as fixed by contract between the Court and the reporter. Available as a copy request after 90 days.",
                            ]
                        },
                        {
                            "values": [
                                "<strong>Copy of Tax Court Rules of Practice and Procedure</strong>",
                                "$20.00",
                            ]
                        },
                    ],
                },
            },
            {"type": "hr", "value": True},
            {"type": "h2", "value": "Witness Fees"},
            {
                "type": "paragraph",
                "value": '<em>(Issued in accordance with 26 U.S.C. section 7457, 28 U.S.C. section 1821, and </em><strong><em><a href="'
                + documents["Rule-148.pdf"]
                + '" target="_blank" title="Rule 148">Rule 148</a></em></strong><em>)</em>',
            },
            {"type": "hr", "value": True},
            {
                "type": "unstyled_table",
                "value": {
                    "columns": [
                        {"type": "text", "heading": "Fee Type"},
                        {"type": "text", "heading": "Amount"},
                    ],
                    "rows": [
                        {
                            "values": [
                                "<strong>Attendance</strong>",
                                "$40.00/day",
                            ]
                        },
                        {
                            "values": [
                                "<strong>Automobile mileage</strong>",
                                'As prescribed by the Administrator of General Services pursuant to 5 U.S.C. section 5704. Paid by petitioner or respondent to the witness. Current mileage rates can be obtained from the United States General Services Administration website at <a href="https://www.gsa.gov/mileage" target="_blank">https://www.gsa.gov/mileage</a>. In addition to mileage, a witness is also entitled to reimbursement of any parking fees incurred.',
                            ]
                        },
                    ],
                },
            },
            {"type": "hr", "value": True},
            {
                "type": "paragraph",
                "value": 'In accordance with procedures that the Court establishes, payments to the Court for fees or charges may be made electronically through <strong><a href="https://www.pay.gov/public/search/agencyforms?agencyFilters=United+States+Tax+Court&searchCategory=PAYMENT&searchType=AGENCYPAYMENT&agencyId=1392">www.Pay.gov</a></strong>. If a fee is paid by check, money order, or other draft, it should be payable to "Clerk, United States Tax Court". (<strong><em><a href="'
                + documents["Rule-11(superseded).pdf"]
                + '" target="_blank" title="Rule 11">Rule 11</a></em></strong>, Tax Court Rules of Practice and Procedure). Cash, checks or money orders may be mailed to: United States Tax Court, 400 Second Street, N.W., Washington, D.C. 20217.<br><br>',
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Fees and charges for the U.S. Tax Court",
                body=body_content,
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
