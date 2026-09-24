from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import PetitionerExperiencePage
from home.models.snippets.call_to_action import CallToActionBox
import logging
from urllib.parse import urljoin
from home.models.utils.execute_script import ExecuteScript
from django.conf import settings
from wagtail.documents.models import Document

logger = logging.getLogger(__name__)


class PetitionersTimelinePageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners-timeline"
        title = "Process and Timeline"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        _snippet_name = "Ready to begin your petition?"
        _cta_box = CallToActionBox.objects.filter(header=_snippet_name).first()

        _base_url = getattr(settings, "BASE_URL", "")
        _petitioner_prepare_to_file_url = urljoin(
            _base_url, "/petitioners-prepare-to-file"
        )
        _petitioner_forms_url = urljoin(_base_url, "/petitioners-forms")
        _petitioner_help_url = urljoin(_base_url, "/petitioners-help")
        _rule37_doc = Document.objects.filter(title="rule-37.pdf").first()
        _rule37_doc_url = "" if _rule37_doc is None else _rule37_doc.url
        _rule143_doc = Document.objects.filter(title="rule-143.pdf").first()
        _rule143_doc_url = "" if _rule143_doc is None else _rule143_doc.url
        _rule162_doc = Document.objects.filter(title="rule-162.pdf").first()
        _rule162_doc_url = "" if _rule162_doc is None else _rule162_doc.url

        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=title,
                introductory_text="What to expect during the tax court process, what documents you will need, links to forms, and a checklist to use.",
                call_to_action=_cta_box,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
                body=[
                    {
                        "type": "summary_timeline",
                        "value": {
                            "title": "TYPICAL CASE TIMELINE",
                            "phases": [
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "File Petition",
                                        "date_range": "Day 0-Deadline",
                                    },
                                    "id": "0e88e4c5-a9c6-49a5-9181-d9103c991a0d",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "IRS Answer",
                                        "date_range": "~60 days",
                                    },
                                    "id": "035ef5a0-94a6-4022-98c1-aa65490c272a",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "Pre-Trial",
                                        "date_range": "2-12 months",
                                    },
                                    "id": "312473bc-6f85-41c7-a12c-c913d16029be",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "Trial",
                                        "date_range": "12-24+ months",
                                    },
                                    "id": "50c5f9c3-9f47-4776-b98a-e1de5b4b0b3e",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "Decision",
                                        "date_range": "6-12+ months",
                                    },
                                    "id": "81478e67-3c14-4339-a5a2-d1f12aa85f04",
                                },
                            ],
                        },
                        "id": "8c34cf67-1a49-4da5-a508-f35217759926",
                    },
                    {
                        "type": "detailed_timeline",
                        "value": {
                            "title": "United States Tax Court Case Timeline",
                            "introduction": '<p data-block-key="lamyb">Please note: The timeline of every court case is different. This is a general timeline to help you<br/>understand the lifecycle of a case and should not be used for planning purposes.</p>',
                            "phases": [
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Receive an IRS Notice",
                                        "date_range": "Day 0",
                                        "instructions": '<p data-block-key="7qeva">You receive an IRS Notice.</p><ul><li data-block-key="2f120">Note the deadline on the notice - this is your starting point.</li><li data-block-key="d1h80">Do not ignore this notice.</li></ul>',
                                        "your_tasks": [
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Review your Notice carefully.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Note the date and amounts listed on the notice.</p>',
                                                },
                                                "id": "ab246cb9-c514-4cb0-bedd-855f70644732",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Calculate your deadline (No later than 11:59 pm Eastern Time on the last date to file).</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Mark this date on your calendar - It generally cannot be extended.</p>',
                                                },
                                                "id": "49bb3d8b-910e-450c-8864-0d154cfb415a",
                                            },
                                        ],
                                        "helpful_information": [
                                            {
                                                "type": "item",
                                                "value": {
                                                    "icon": "outbound",
                                                    "information": f'<p data-block-key="8x988">Prepare documents using the <a href="{_petitioner_prepare_to_file_url}"><b>pre-filing checklist</b></a> before getting started in DAWSON.</p>',
                                                    "information_subtext": "",
                                                },
                                                "id": "7bca949f-9af8-4e6e-8f37-eb7cd9101dc1",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "icon": "help",
                                                    "information": '<p data-block-key="8x988">Can I represent myself?</p>',
                                                    "information_subtext": f'<p data-block-key="rrk5u">You can represent yourself or get help with your case. View <a href="{_petitioner_help_url}">full FAQ</a> for more details.</p>',
                                                },
                                                "id": "645cb15d-8ae1-4c31-b3da-c45eb02290c9",
                                            },
                                        ],
                                    },
                                    "id": "b4941d41-ab20-4e73-9ea6-66e6a22001fb",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "File Your Petition",
                                        "date_range": "Day 0-Deadline",
                                        "instructions": '<p data-block-key="y4e6l">Review the deadlines on any notices or other correspondence. You must file your petition with the United States Tax Court by the deadline.</p><ul><li data-block-key="6gu4c">File electronically via DAWSON or by mail to the United States Tax Court (United States Tax Court, 400 Second St. NW Washington, DC 20217).</li><li data-block-key="fcj3q">Pay the $60 filing fee (or request fee waiver if you qualify).</li><li data-block-key="5deul"> In most cases, the United States Tax Court must receive your petition no later than 11:59 pm Eastern Time on the last date to file.</li><li data-block-key="edgto">Need help? Low Income Taxpayer Clinics (LITCs) provide free or low-cost representation and tax advice. You may qualify based on income.</li></ul>',
                                        "your_tasks": [
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Determine if you would like to elect small tax case status.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Deficiency disputes $50,000 or less per year are eligible.</p>',
                                                },
                                                "id": "3e35c1a1-b320-4727-81be-1a7977eb5eac",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Complete the Petition form using <a href="https://dawson.ustaxcourt.gov/">dawson.ustaxcourt.gov</a> petition generator.</p>',
                                                    "subtext": f'<p data-block-key="7tw0u">Otherwise download a Petition form (form 2) from <a href="{_petitioner_forms_url}">our Forms page</a>.</p>',
                                                },
                                                "id": "55ed77fc-61be-49e0-bef4-ec1712dccbb7",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Download and complete the Taxpayer Identification Number (STIN) form.</p>',
                                                    "subtext": "",
                                                },
                                                "id": "52840bf2-46a4-45b0-b9da-6d1df571e0c0",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Complete the Corporate Disclosure Statement form ONLY if you are filing on behalf of a company.</p>',
                                                    "subtext": f'<p data-block-key="7tw0u">Download from <a href="{_petitioner_forms_url}">our Forms page</a>.</p>',
                                                },
                                                "id": "5e5f60d1-0222-4c55-8250-5151c2a1523d",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Save a copy of your IRS Notice.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">You will need to upload it to DAWSON and later on during the process.</p>',
                                                },
                                                "id": "8b9e11a9-2276-4f5f-b33c-36c6bf33a1ff",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">File petition via DAWSON or mail.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">In most cases, the United States Tax Court must receive your petition no later than 11:59 pm Eastern Time on the last date to file.</p>',
                                                },
                                                "id": "20d2273e-cf55-4c31-bb21-106c4276b07a",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Pay the $60 filing fee.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Fee waiver may be available for demonstrated financial hardship once a petition is filed. Payment is due once you receive your docket number. E-filers receive their docket number immediately, while people who file by mail will receive it by mail.</p>',
                                                },
                                                "id": "d5ca7ea0-5258-486e-8088-3b18826ce1de",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Keep proof of filing/mailing.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Receipt or certified mail tracking.</p>',
                                                },
                                                "id": "58b175ec-cc9f-4cf8-bf54-f185e6a67a90",
                                            },
                                        ],
                                        "helpful_information": [],
                                    },
                                    "id": "36557146-a5db-462b-9955-a436cd87d486",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "IRS Files Answer",
                                        "date_range": "Up To 60 Days After the Petition is Filed",
                                        "instructions": f'<p data-block-key="k0m49">The IRS responds to your “Petition” with an “Answer.”</p><ul><li data-block-key="en9kt">IRS has 60 days to respond. You may need to fie a reply if there are affirmative allegations made in the Answer (<a href="{_rule37_doc_url}">Rule 37</a>).</li><li data-block-key="29g5r">Review the IRS answer carefully. The answer will tell you the name and phone number of the IRS lawyer assigned to your case.</li></ul>',
                                        "your_tasks": [],
                                        "helpful_information": [
                                            {
                                                "type": "item",
                                                "value": {
                                                    "icon": "outbound",
                                                    "information": '<p data-block-key="8x988">What is an Answer?</p>',
                                                    "information_subtext": "",
                                                },
                                                "id": "c580b26a-44e8-4267-986b-13db49a5dad0",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "icon": "outbound",
                                                    "information": '<p data-block-key="8x988">How can I check on the status of my case? </p>',
                                                    "information_subtext": "",
                                                },
                                                "id": "f20f7982-acca-4077-8047-1ed42634c55a",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "icon": "help",
                                                    "information": '<p data-block-key="8x988">Who can I contact if I have questions? </p>',
                                                    "information_subtext": "",
                                                },
                                                "id": "e4b8e5eb-2200-40e9-ba93-849d624b4919",
                                            },
                                        ],
                                    },
                                    "id": "96ce579b-89c6-4b01-9013-e33a079314dc",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Trial Date is Scheduled",
                                        "date_range": "6-13 Months",
                                        "instructions": '<ul><li data-block-key="whj1m">It could be several months before your trial is scheduled.</li><li data-block-key="9gv8b">You will be notified approximately 5 months before trial date.</li></ul>',
                                        "your_tasks": [],
                                        "helpful_information": [],
                                    },
                                    "id": "c711466a-53f8-4deb-aa63-a0edb2b05cb2",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Discovery & Discussion",
                                        "date_range": "4-12 Months",
                                        "instructions": '<p data-block-key="5t5z1">Exchange information and documents with the IRS.</p><ul><li data-block-key="aekn5">Exchange documents and supporting materials.</li><li data-block-key="38ts4">Participate in discussions about your case with the IRS.</li><li data-block-key="4e0df">Cases may be set for trial or motion during this time.</li></ul>',
                                        "your_tasks": [
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Respond to all court deadlines.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Including orders for status reports and to participate in conference calls. </p>',
                                                },
                                                "id": "37ddca32-14b5-48cd-863d-43f51be394ad",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Participate in discussions with the IRS.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Many cases settle before trial.</p>',
                                                },
                                                "id": "39c020dd-f507-4c1a-ba6f-3a96a0d88589",
                                            },
                                        ],
                                        "helpful_information": [],
                                    },
                                    "id": "90c53c79-43a6-45d7-b384-a067bc4355e3",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Trial Preparation",
                                        "date_range": "2-4 Months Before Trial",
                                        "instructions": '<p data-block-key="zq81q">Prepare for trial if your case doesn\'t settle.</p><ul><li data-block-key="8eh1q">Finalize witness list.</li><li data-block-key="bu5u0">Prepare exhibits and stipulations.</li><li data-block-key="50qsa">Review trial procedures.</li><li data-block-key="cludo">Submit Pre-Trial Memorandum.</li></ul>',
                                        "your_tasks": [
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Gather all relevant documents.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Tax returns, receipts, prior correspondence with IRS.</p>',
                                                },
                                                "id": "aafffc52-4101-484e-9037-ffd886977834",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Organize evidence to support your position.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Documents, receipts, bank statements, etc. Make sure you have copies for yourself, the IRS, and the Judge.</p>',
                                                },
                                                "id": "3213a259-bd28-4ae2-87a7-5198104d0f5e",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Prepare witness list if applicable.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Consider identifying potential witnesses (including yourself) who could provide testimony in support of your case.</p>',
                                                },
                                                "id": "8e4cd5b1-f39d-4e5e-9224-387d03627f08",
                                            },
                                            {
                                                "type": "item",
                                                "value": {
                                                    "text": '<p data-block-key="l4ngx">Prepare for trial if case has not settled.</p>',
                                                    "subtext": '<p data-block-key="7tw0u">Pre-trial memorandum, exhibits, etc.</p>',
                                                },
                                                "id": "d3e16464-1209-4a07-af02-31d10c489a7a",
                                            },
                                        ],
                                        "helpful_information": [],
                                    },
                                    "id": "92fbd6bf-b338-4993-a5e7-ddffe874c42b",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Trial",
                                        "date_range": "12-24+ Months After Filing",
                                        "instructions": f'<p data-block-key="x2hae">Present your case before a United States Tax Court Judge.</p><ul><li data-block-key="933h0">Trial held in person or remotely. The United States Tax Court Rules and the <a href="{_rule143_doc_url}">rules of evidence</a> apply either way.</li><li data-block-key="dhe25">Present evidence and witnesses.</li><li data-block-key="ddceg">The Judge may not issue a decision right away. You will receive a copy when the Judge issues in your case.</li></ul>',
                                        "your_tasks": [],
                                        "helpful_information": [],
                                    },
                                    "id": "49330a63-e33a-4028-9104-32063c7541c0",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Decision",
                                        "date_range": "6-12+ Months After Trial",
                                        "instructions": f'<p data-block-key="49sn9">US Tax Court decision.</p><ul><li data-block-key="d03o0">Any motion to vacate or revise a decision should be filed within 30 days (See <a href="{_rule162_doc_url}">Rule 162</a>). The United States Tax Court may allow more time.</li></ul>',
                                        "your_tasks": [],
                                        "helpful_information": [],
                                    },
                                    "id": "6c4a7579-026c-444a-ae78-41d71ce33e7a",
                                },
                            ],
                        },
                        "id": "b050e963-8231-4c33-817c-101d50838d56",
                    },
                ],
            )
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")

    def run(self):
        """Update the Petitioners Timeline page."""
        command_name = "Initialize Petitioners Timeline page"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.create()
            execution_log_text = "Petitioners Timeline page updated successfully."
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = execution_log_text
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
