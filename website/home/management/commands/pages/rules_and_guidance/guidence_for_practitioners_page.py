from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import IconCategories
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)

practitioners_docs = {
    "Application_for_Admission_to_Practice_Attorney_Form_30.pdf": "",
    "Admissions_Information_Attorney_12212021.pdf": "",
    "rule-200.pdf": "",
    "rule-201.pdf": "",
    "rule-202.pdf": "",
    "Nonattorney_Examination_Procedures_050322.pdf": "",
    "NonAttorney_Exam_Statistics.pdf": "",
    "2023_Nonattorney_Exam.pdf": "",
    "2021_Nonattorney_Exam.pdf": "",
    "2018_Nonattorney_Exam.pdf": "",
    "DAWSON_Practitioner_Training_Guide.pdf": "",
}

practitioners_icons = {
    "scales_icon.svg": "",
    "graduation_cap_icon.svg": "",
    "computer_icon.svg": "",
    "star_icon.svg": "",
    "life_ring_icon.svg": "",
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

        for icon_name in practitioners_icons.keys():
            icon = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=icon_name,
                title=icon_name,
            )
            practitioners_icons[icon_name] = icon

        docs = practitioners_docs
        icons = practitioners_icons

        admission_of_attorneys_card = {
            "icon": icons["scales_icon.svg"].id,
            "icon_direction": "top",
            "card_header": "Admission of Attorneys",
            "card_hover": True,
            "link": [
                {
                    "type": "anchor_page",
                    "value": {
                        "breadcrumb_title": "Admission Requirements for Attorneys",
                        "body": [
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "Admission Requirements for Attorneys",
                                    "default_to_open": True,
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": f"""<p>Attorney admission applications may be emailed to the <a href="mailto:Admissions@ustaxcourt.gov" title="Email Admissions@ustaxcourt.gov">Admissions Office</a>. Your email must include:</p>
                                            <ul>
                                                <li><a linktype="document" id="{docs["Application_for_Admission_to_Practice_Attorney_Form_30.pdf"].id}" title="Application for Admission to Practice, Form 30" target="_blank">Application for Admission to Practice, Form 30</a>.</li>
                                                <li>Proof of payment of the $50 Application Fee (pay via <a href="https://www.pay.gov/public/form/start/16762207" title="Pay.gov">Pay.gov</a>).</li>
                                                <li>A certificate of good standing from the Clerk of the appropriate court issued within 90 calendar days of the application filing date.</li>
                                            </ul>
                                            <p>For further instructions, please see <a linktype="document" id="{docs["Admissions_Information_Attorney_12212021.pdf"].id}" title="Admissions Information for Attorneys" target="_blank">Admissions Information for Attorneys.</a></p>""",
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                }
            ],
        }

        admission_of_nonattorneys_card = {
            "icon": icons["graduation_cap_icon.svg"].id,
            "icon_direction": "top",
            "card_header": "Admission of NonAttorneys",
            "card_hover": True,
            "link": [
                {
                    "type": "anchor_page",
                    "value": {
                        "breadcrumb_title": "Admission of NonAttorneys",
                        "body": [
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "Nonattorney Examination Resources",
                                    "default_to_open": True,
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": f"""<p>A nonattorney may be admitted to practice before the Court provided the requirements outlined in the Tax Court Rules of Practice and Procedure are satisfied.<br/>See <a linktype="document" id="{docs["rule-200.pdf"].id}" title="Rule 200" target="_blank">Rule 200</a>, Tax Court Rules of Practice and Procedure.</p>
                                            <ul>
                                                <li><a linktype="document" id="{docs["Nonattorney_Examination_Procedures_050322.pdf"].id}" title="Procedures for the Preparation and Grading of the Nonattorney Examination" target="_blank">Procedures for the Preparation and Grading of the Nonattorney Examination</a></li>
                                                <li><a linktype="document" id="{docs["NonAttorney_Exam_Statistics.pdf"].id}" title="Statistical Information Regarding the Nonattorney Examination" target="_blank">Statistical Information Regarding the Nonattorney Examination</a></li>
                                            </ul>""",
                                        },
                                    ],
                                },
                            },
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "Prior Year Nonattorney Examinations",
                                    "default_to_open": False,
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": f"""<p>Downloadable copies of the last three examinations can be found below. To order paper copies, please submit a request via <a href="https://www.pay.gov/public/form/start/16749996" title="Pay.gov">Pay.gov</a>.</p>
                                            <ul>
                                                <li><a linktype="document" id="{docs["2023_Nonattorney_Exam.pdf"].id}" title="Prior Year Exam 2023" target="_blank">Prior Year Exam 2023</a></li>
                                                <li><a linktype="document" id="{docs["2021_Nonattorney_Exam.pdf"].id}" title="Prior Year Exam 2021" target="_blank">Prior Year Exam 2021</a></li>
                                                <li><a linktype="document" id="{docs["2018_Nonattorney_Exam.pdf"].id}" title="Prior Year Exam 2018" target="_blank">Prior Year Exam 2018</a></li>
                                            </ul>""",
                                        },
                                    ],
                                },
                            },
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "Character and Fitness",
                                    "default_to_open": False,
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": f"""<p>An applicant must establish to the satisfaction of the Court that he or she is of good moral and professional character, including by providing sponsorship letters. See <a linktype="document" id="{docs["rule-200.pdf"].id}" title="Rule 200" target="_blank">Rule 200</a>, Tax Court Rules of Practice and Procedure. Accordingly, after administration of the Nonattorney Exam, those who pass will be required to undergo a character and fitness review. The review will include requests for additional background information, sponsorship letters, and a remote interview. Any necessary documentation will be requested at that time.</p>""",
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                }
            ],
        }

        dawson_registration_card = {
            "icon": icons["computer_icon.svg"].id,
            "icon_direction": "top",
            "card_header": "DAWSON Practitioner Registration & eFiling",
            "card_hover": True,
            "link": [
                {
                    "type": "anchor_page",
                    "value": {
                        "breadcrumb_title": "DAWSON Registration & Case eFiling",
                        "body": [
                            {
                                "type": "quick_access_tiles",
                                "value": {
                                    "tiles_hover_enabled": True,
                                    "icon_position": "desktop_top_mobile_left",
                                    "tiles": [
                                        {
                                            "title": "Limited Entry of Appearance",
                                            "description": "",
                                            "icon": {
                                                "svg_file": icons[
                                                    "life_ring_icon.svg"
                                                ].id
                                            },
                                            "content_alignment": "center",
                                            "link": [
                                                {
                                                    "type": "external_url",
                                                    "value": "/limited-entries-of-appearance/",
                                                }
                                            ],
                                        },
                                    ],
                                },
                            },
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "How to Register as a Practitioner",
                                    "default_to_open": False,
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": """<p>To register as a practitioner, the Court must first create your DAWSON account. You will receive access with your admissions materials once approved. Only those admitted to practice before the Court may obtain eAccess:</p>
                                            <ul>
                                                <li>If you never had eAccess and need to register for DAWSON, email <a href="mailto:dawson.support@ustaxcourt.gov" title="Email dawson.support@ustaxcourt.gov">dawson.support@ustaxcourt.gov</a> for help.</li>
                                            </ul>""",
                                        },
                                    ],
                                },
                            },
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "DAWSON Resources",
                                    "default_to_open": False,
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": f"""<p>For additional resources regarding DAWSON, please review:</p>
                                            <ul>
                                                <li><a linktype="document" id="{docs["DAWSON_Practitioner_Training_Guide.pdf"].id}" title="DAWSON Practitioner Filing Instructions" target="_blank">DAWSON Practitioner Filing Instructions</a></li>
                                            </ul>
                                            <p><strong>DAWSON Tips and Reminders for Practitioners</strong></p>
                                            <ul>
                                                <li>Apply for admission to practice before the US Tax Court only once.
                                                    <ul>
                                                        <li>Your US Tax Court Bar number is associated with your DAWSON email address/login.</li>
                                                        <li>You do not need to pay the admission fee or submit your application a second time, even if you change from the IRS to private practice (or vice versa).</li>
                                                    </ul>
                                                </li>
                                                <li>If you change from the IRS to private practice (or vice versa), contact the US Tax Court Admissions office.
                                                    <ul>
                                                        <li>Be sure that you have:
                                                            <ul>
                                                                <li>Withdrawn from all of your previous cases.</li>
                                                                <li>Update your contact information in DAWSON.</li>
                                                                <li>Contact Admissions (<a href="mailto:admissions@ustaxcourt.gov" title="Email admissions@ustaxcourt.gov">admissions@ustaxcourt.gov</a>) to request an update to your practice type associated with your account (IRS, DOJ, Private), so that you have the appropriate role in DAWSON.</li>
                                                            </ul>
                                                        </li>
                                                    </ul>
                                                </li>
                                                <li>Use caution when including your contact information on the US Tax Court Application for Admission to Practice form.
                                                    <ul>
                                                        <li>Contact information that is provided in your application for admission to practice before the US Tax Court is added to your profile in DAWSON.</li>
                                                        <li>Be sure that you only input your phone, email, and address information that is associated with your professional employment.</li>
                                                    </ul>
                                                </li>
                                            </ul>""",
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                }
            ],
        }

        disciplinary_matters_card = {
            "icon": icons["star_icon.svg"].id,
            "icon_direction": "top",
            "card_header": "Disciplinary Matters & Certificates",
            "card_hover": True,
            "link": [
                {
                    "type": "anchor_page",
                    "value": {
                        "breadcrumb_title": "Disciplinary Matters & Certificates",
                        "body": [
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "Certificates of Good Standing",
                                    "default_to_open": False,
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": """<ul>
                                                <li>To request an electronic certificate of good standing free of charge, email your request to the <a href="mailto:Admissions@ustaxcourt.gov" title="Email Admissions@ustaxcourt.gov">Admissions Office</a> with your name and US Tax Court bar number.</li>
                                                <li>To request a paper certificate of good standing with the Court's raised seal, submit $15 payment via <a href="https://www.pay.gov/public/form/start/802285219" title="Pay.gov">Pay.gov</a> and it will be mailed directly to you.</li>
                                            </ul>""",
                                        },
                                    ],
                                },
                            },
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "Wall Certificates",
                                    "default_to_open": False,
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": """<p>How to order your wall certificate:</p>
                                            <ol>
                                                <li>Go to <a href="https://www.pay.gov/public/form/start/802285219" title="Pay.gov">Pay.gov</a> to complete the form and submit a $15 payment.</li>
                                                <li>Enter your Tax Court Bar number when prompted.</li>
                                            </ol>
                                            <p>Bar numbers admitted after 2020:</p>
                                            <ul>
                                                <li>The Pay.gov form has a character limit that won't fit your full DAWSON bar number</li>
                                                <li>Enter the first six characters of your bar number. We can still process your order with a partial number.</li>
                                            </ul>
                                            <p>Bar numbers admitted before 2021:</p>
                                            <ul>
                                                <li>Enter your complete bar number</li>
                                            </ul>
                                            <p>Once your order is paid, we will mail your certificate to you.</p>""",
                                        },
                                    ],
                                },
                            },
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "Disciplinary Matters Notices",
                                    "default_to_open": False,
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": """<p>Historical disciplinary action information can be found on our <a href="/news-and-announcements" title="News and Announcements">News & Announcements</a> page.</p>""",
                                        },
                                    ],
                                },
                            },
                            {
                                "type": "accordion",
                                "value": {
                                    "title": "Reporting Discipline",
                                    "default_to_open": False,
                                    "description": [
                                        {
                                            "type": "prose",
                                            "value": """<p>A member of the Bar of this Court must <a href="mailto:admissions@ustaxcourt.gov?subject=Attention%20to%20the%20Chair%20of%20the%20Court%E2%80%99s%20Committee%20on%20Admissions%2C%20Ethics%2C%20and%20Discipline" title="Email admissions@ustaxcourt.gov">email admissions</a> with attention to the Chair of the Court's Committee on Admissions, Ethics, and Discipline, within 30 days of any of the following:</p>
                                            <ul>
                                                <li>An entry of judgment of conviction of any felony or of any lesser crime described in Rule 202(a)(1),</li>
                                                <li>An entry of order of discipline as described Rule 202(a)(2), or</li>
                                                <li>Disbarment or suspension from practice before an agency of the United States Government exercising professional disciplinary jurisdiction</li>
                                            </ul>""",
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                }
            ],
        }

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=None,
                search_description="Guidance for Practitioners",
                body=[
                    {
                        "type": "paragraph",
                        "value": "<p>This page provides essential resources for legal professionals, including information on electronic filing, admission requirements, procedural rules, and practitioner responsibilities.</p>",
                    },
                    {
                        "type": "card_tiles",
                        "value": {
                            "tiles": [
                                admission_of_attorneys_card,
                                admission_of_nonattorneys_card,
                                dawson_registration_card,
                                disciplinary_matters_card,
                            ],
                            "show_back_button": True,
                            "back_button_text": "Back to Guidance",
                            "default_content": [
                                {"type": "h2", "value": "Tax Court Bar"},
                                {
                                    "type": "paragraph",
                                    "value": "<p>The Court's Rules of Practice and Procedure governing admission and discipline can be found in Title XX, Practice Before the Court:</p>",
                                },
                                {
                                    "type": "links",
                                    "value": {
                                        "class": "indented",
                                        "links": [
                                            {
                                                "title": "Rule 200. Admission to Practice and Periodic Registration Fee",
                                                "icon": IconCategories.PDF,
                                                "document": docs["rule-200.pdf"].id,
                                                "url": None,
                                            },
                                            {
                                                "title": "Rule 201. Conduct of Practice Before the Court",
                                                "icon": IconCategories.PDF,
                                                "document": docs["rule-201.pdf"].id,
                                                "url": None,
                                            },
                                            {
                                                "title": "Rule 202. Disciplinary Matters",
                                                "icon": IconCategories.PDF,
                                                "document": docs["rule-202.pdf"].id,
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
                            ],
                        },
                    },
                ],
            )
        )
