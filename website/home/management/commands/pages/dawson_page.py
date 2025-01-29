import os

from wagtail.models import Page
from wagtail.images.models import Image
from django.conf import settings
from django.core.files import File
from django.contrib.contenttypes.models import ContentType
from home.models import (
    DawsonPage,
    SimpleCardGroup,
    SimpleCards,
    RelatedPage,
    PhotoDedication,
    StandardPage,
)
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationCategories


class DawsonPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson"
        title = "DAWSON"

        body_content = (
            "DAWSON (Docket Access Within a Secure Online Network) is the U.S. Tax Court's electronic filing and "
            'case management system. See the <a href="https://ustaxcourt.gov/dawson_user_guides.html">user guides</a> '
            "for more information and instructions.<br/><br/> Technical questions about DAWSON? Please contact "
            '<a href="mailto:dawson.support@ustaxcourt.gov">dawson.support@ustaxcourt.gov</a>. No documents can be '
            "filed with the Court at this email address. Any documents received via email will NOT be filed in your case."
        )

        dawson_page = DawsonPage(
            title=title,
            slug=slug,
            search_description="Dawson eFiling main page",
            body="Placeholder body text.",
        )

        existing_dawson_page = home_page.get_children().live().filter(slug=slug).first()
        if existing_dawson_page:
            existing_dawson_page.delete()
            print(f"Deleted existing {title} page.")

        home_page.add_child(instance=dawson_page)
        print(f"Created {title} page stub.")

        dawson_content_type = ContentType.objects.get_for_model(DawsonPage)

        dawson_petition_card_group = SimpleCardGroup(
            group_label="", parent_page=dawson_page
        )
        dawson_petition_card_group.save()

        dawson_card_group = SimpleCardGroup(
            group_label="Filing a Petition", parent_page=dawson_page
        )
        dawson_card_group.save()

        print("Created card groups.")

        standard_pages = {
            "petition": [
                {
                    "title": "How to eFile a Petition",
                    "body": "Before starting the e-filing process, please review the helpful tips provided below. They will instruct you in what is needed and how to go about filing your petition electronically in DAWSON (Docket Access Within and Secure Online Network), the Court’s electronic filing and case management system. For more detailed instructions, refer to the DAWSON user guides.",
                    "slug": "efile_a_petition",
                    "show_in_menus": False,
                    "path": "efile_a_petition",
                    "depth": 4,
                    "search_description": "How to eFile a Petition",
                },
                {
                    "title": "How to Pay the Filing Fee",
                    "body": "Filing fees are required to submit a petition. The Court’s filing fee is $60 and may be paid online, by mail, or in person. The fee may be waived by filing an Application for Waiver of Filing Fee. Your petition must be processed by the Court before the Application for Waiver of Filing fee can be filed electronically.",
                    "slug": "pay_filing_fee",
                    "show_in_menus": False,
                    "path": "pay_filing_fee",
                    "depth": 4,
                    "search_description": "How to Pay the Filing Fee",
                },
                {
                    "title": "How to Merge PDFs",
                    "body": "These instructions apply only to Adobe Acrobat Professional and Standard. A user utilizing other software to create PDFs must follow the software vendor's instructions for creating a single PDF from multiple PDFs.",
                    "slug": "merging_files",
                    "show_in_menus": False,
                    "path": "merge-pdfs",
                    "depth": 4,
                    "search_description": "How to Merge PDFs",
                },
            ],
            "managing_case": [
                {
                    "title": "How to View Your Dashboard",
                    "body": "Dashboard Your dashboard is your main landing page once you are signed in to DAWSON.",
                    "slug": "dashboard",
                    "show_in_menus": False,
                    "path": "dashboard",
                    "depth": 4,
                    "search_description": "How to View Your Dashboard",
                },
                {
                    "title": "How to Update Your Contact Information",
                    "body": "Update Contact Information",
                    "slug": "update_contact_information",
                    "show_in_menus": False,
                    "path": "update_contact_information",
                    "depth": 4,
                    "search_description": "How to Update Your Contact Information",
                },
            ],
            "searching_case": [
                {
                    "title": "How to Search for a Case",
                    "body": "Find a Case: To search for a case in DAWSON, go to the DAWSON homepage. You can search for a case by Petitioner Name or Docket Number on the Case tab.",
                    "slug": "find_a_case",
                    "show_in_menus": False,
                    "path": "find_a_case",
                    "depth": 4,
                    "search_description": "How to Search for a Case",
                },
                {
                    "title": "How to Search for an Order",
                    "body": "Find an Order: An Order is a written direction or command issued by a Judge. Each day’s Orders are posted on the Court’s website, www.ustaxcourt.gov, under “Today’s Orders” in “Orders & Opinions”. To search for an order, you can search by a keyword or phrase. In addition, you may also narrow your search results by adding in a specific Docket number, Case Title/Petitioner’s name, the Judge who issued the order, or by including a specific date or date range.",
                    "slug": "find_an_order",
                    "show_in_menus": False,
                    "path": "find_an_order",
                    "depth": 4,
                    "search_description": "How to Search for an Order",
                },
                {
                    "title": "How to Search for an Opinion",
                    "body": "Find an Opinion: An opinion is the written determination of a Judge on the issues tried and submitted to the Court for decision. Each dayʼs opinions are posted on the Courtʼs website, www.ustaxcourt.gov, in “Todayʼs Opinions” under “Orders & Opinions”. If you need to search for an opinion, you can search by a keyword or phrase. In addition, you may narrow your search results by adding in a specific Docket Number, Case Title/Petitionerʼs name, the Judge who issued the Opinion, or by including a specific date or date range. You may also filter by opinion type.",
                    "slug": "find_an_opinion",
                    "show_in_menus": False,
                    "path": "find_an_opinion",
                    "depth": 4,
                    "search_description": "How to Search for an Opinion",
                },
            ],
            "reference_materials": [
                {
                    "title": "FAQs",
                    "body": "Frequently Asked Questions About DAWSON",
                    "slug": "dawson_faqs",
                    "show_in_menus": False,
                    "path": "dawson_faqs",
                    "depth": 4,
                    "search_description": "FAQs",
                },
                {
                    "title": "Terms of Use",
                    "body": """Terms of Use
Acceptance of the Terms of Use constitutes an agreement to abide by all Court Rules, policies, and procedures governing the use of the Court’s electronic access and filing system (DAWSON). By registering for DAWSON, practitioners and petitioners consent to receive electronic service (eService) of documents pursuant to Rule 21(b)(1)(D). The notification of service to all parties and persons in the case who have consented to electronic service in conjunction with the entry on the Court's docket record constitutes service on all parties who have consented to electronic service. Practitioners and petitioners who consent to receive eService agree to regularly log on to DAWSON to view served documents. The combination of user name and password serves as the signature of the individual filing the documents. Individuals must protect the security of their login credentials and immediately notify the Court by emailing dawson.support@ustaxcourt.gov if they learn that their account has been compromised. The Terms of Use can be changed at any time without notice.

Acknowledgment of Policies and Procedures

I understand that:

I must provide accurate and complete information when I register for electronic access to DAWSON. I must promptly notify the Court of any changes to that information. See also Rule 21(b)(4).

Registration is for my and my authorized agent’s use only, and I am responsible for preventing unauthorized use of my user name and password. If I believe there has been unauthorized use, I must notify the Court by emailing dawson.support@ustaxcourt.gov.

The United States Tax Court reserves the right to deny, limit, or suspend access to DAWSON to anyone: (1) Who provides information that is fraudulent, (2) whose usage has the potential to cause disruption to the system; or (3) who in the judgment of the Court is misusing the system.""",
                    "slug": "dawson_tou",
                    "show_in_menus": False,
                    "path": "dawson_tou",
                    "depth": 4,
                    "search_description": "Terms of Use",
                },
                {
                    "title": "Definitions",
                    "body": "“Designated Service Person” means the practitioner designated to receive service of documents in a case. The first counsel of record is generally the Designated Service Person, see Rule 21(b)(2). The ability to designate an additional service person in DAWSON is coming soon. “Document” means any written matter filed by or with the Court including, but not limited to motions, pleadings, applications, petitions, notices, declarations, affidavits, exhibits, briefs, memoranda of law, orders, and deposition transcripts.",
                    "slug": "definitions",
                    "show_in_menus": False,
                    "path": "definitions",
                    "depth": 4,
                    "search_description": "Definitions",
                },
                {
                    "title": "What Documents Can Be eFiled",
                    "body": "What Documents May be eFiled?",
                    "slug": "documents_eligible_for_efiling",
                    "show_in_menus": False,
                    "path": "documents_eligible_for_efiling",
                    "depth": 4,
                    "search_description": "What Documents Can Be eFiled",
                },
                {
                    "title": "Privacy and Public Access to Case Files",
                    "body": "Notice Regarding Privacy and Public Access to Case Files: Pursuant to 26 USC Section 7461(a), all reports of the Tax Court and all evidence received by the Tax Court, including a transcript of the record of the hearings, generally are public records open to inspection by the public. In order to provide access to case files while also protecting personal privacy and other legitimate interests, parties are encouraged to refrain from including or to take appropriate steps to redact the following information from all pleadings and papers filed with the Court, in electronic or paper form, including exhibits thereto, except as otherwise required by the Court’s Rules or as directed by the Court:",
                    "slug": "notice_regarding_privacy",
                    "show_in_menus": False,
                    "path": "notice_regarding_privacy",
                    "depth": 4,
                    "search_description": "Privacy and Public Access to Case Files",
                },
                {
                    "title": "Release Notes",
                    "body": "DAWSON Release Notes: See below for more information about additional code deployed to DAWSON since its launch on December 28, 2020. For questions or comments email ​dawson.support@ustaxcourt.gov​.",
                    "slug": "release_notes",
                    "show_in_menus": False,
                    "path": "release_notes",
                    "depth": 4,
                    "search_description": "Release Notes",
                },
                {
                    "title": "User Guides",
                    "body": "DAWSON User Guides",
                    "slug": "dawson_user_guides",
                    "show_in_menus": False,
                    "path": "dawson_user_guides",
                    "depth": 4,
                    "search_description": "User Guides",
                },
                {
                    "title": "DAWSON Status",
                    "body": "",
                    "slug": "dawson_status",
                    "show_in_menus": False,
                    "path": "https://status.ustaxcourt.gov/",
                    "depth": 4,
                    "search_description": "DAWSON Status",
                },
            ],
            "registration": [
                {
                    "title": "Petitioner Registration",
                    "body": "",
                    "slug": "dawson_petitioner_registration",
                    "show_in_menus": False,
                    "path": "https://app.dawson.ustaxcourt.gov/create-account/petitioner",
                    "depth": 4,
                    "search_description": "Petitioner Registration",
                },
                {
                    "title": "Practitioner Registration",
                    "body": "How to Get a DAWSON Account: Practitioners: The Court will create DAWSON accounts for practitioners.",
                    "slug": "dawson_account_practitioner",
                    "show_in_menus": False,
                    "path": "dawson_account_practitioner",
                    "depth": 4,
                    "search_description": "Practitioner Registration",
                },
            ],
        }

        all_new_std_pages = {}
        for card_name in standard_pages.keys():
            new_std_pages = []
            for page in standard_pages[card_name]:
                std_page = (
                    home_page.get_children().live().filter(slug=page["slug"]).first()
                )
                if std_page:
                    std_page.title = page["title"]
                    std_page.body = page["body"]
                    std_page.search_description = page["search_description"]
                    dawson_page.add_child(instance=std_page)
                    dawson_page.save()
                    print(f"Updated {std_page.title} page.")
                    new_std_pages.append(std_page)
                else:
                    new_std_page = StandardPage(**page)
                    dawson_page.add_child(instance=new_std_page)
                    print(f"Created {new_std_page.title} page.")
                    new_std_pages.append(new_std_page)
            all_new_std_pages[card_name] = new_std_pages

        petition_simple_card = SimpleCards(
            card_title="Filing a Petition",
            card_icon="file-text",
            parent_page=dawson_card_group,
        )
        petition_simple_card.save()

        managing_case_card = SimpleCards(
            card_title="Managing Your Cases",
            card_icon="file-text",
            parent_page=dawson_card_group,
        )
        managing_case_card.save()

        searching_case_card = SimpleCards(
            card_title="Searching for Cases and Documents",
            card_icon="file-text",
            parent_page=dawson_card_group,
        )
        searching_case_card.save()

        reference_materials_card = SimpleCards(
            card_title="Reference Materials",
            card_icon="file-text",
            parent_page=dawson_card_group,
        )
        reference_materials_card.save()

        register_card = SimpleCards(
            card_title="",
            card_icon="",
            parent_page=dawson_petition_card_group,
        )
        register_card.save()

        print("Created cards.")

        for registration_std_page in all_new_std_pages["registration"]:
            RelatedPage.objects.create(
                card=register_card, related_page=registration_std_page
            )
        register_card.save()

        for petition_std_page in all_new_std_pages["petition"]:
            RelatedPage.objects.create(
                card=petition_simple_card, related_page=petition_std_page
            )
        petition_simple_card.save()

        for managing_case_std_page in all_new_std_pages["managing_case"]:
            RelatedPage.objects.create(
                card=managing_case_card, related_page=managing_case_std_page
            )
        managing_case_card.save()

        for searching_case_std_page in all_new_std_pages["searching_case"]:
            RelatedPage.objects.create(
                card=searching_case_card, related_page=searching_case_std_page
            )
        searching_case_card.save()

        for reference_materials_std_page in all_new_std_pages["reference_materials"]:
            RelatedPage.objects.create(
                card=reference_materials_card, related_page=reference_materials_std_page
            )
        reference_materials_card.save()

        photo_dedication = PhotoDedication(
            title="Judge Howard A. Dawson, Jr.",
            paragraph_text="""The Tax Court’s electronic filing and case management system, launched in 2020, is named for the Court’s longest-serving judge, Howard A. Dawson, Jr.
<br/><br/>
Judge Dawson was born in Arkansas in 1922. A graduate of Woodrow Wilson High School in Washington, D.C., Judge Dawson received a B.S. from the University of North Carolina and earned his J.D. with honors from the George Washington University School of Law.
<br/><br/>
He had a long career in public service, spending two years in the European Theater with the U.S. Army, and many more as a member of the U.S. Army Reserve. He held several positions at the Internal Revenue Service, including Assistant Chief Counsel (Administration), before being appointed to the Tax Court by President Kennedy in 1962. He was reappointed by President Nixon for a second term. Judge Dawson served as a Senior Judge on recall from 1985 until his death in 2016.
<br/><br/>
Judge Dawson was Chief Judge of the Tax Court for three terms. Known as a meticulous record keeper and for his wealth of information on virtually every aspect of Tax Court history and lore, he was always happy to share his knowledge with everyone. It is only fitting that the case management system, the records base for the Tax Court itself, should be named in his memory.""",
        )

        image_path = os.path.join(
            settings.BASE_DIR,  # points to your project base directory
            "app",
            "static",
            "images",
            "page",
            "judge-howard-a-dawson-jr.png",
        )

        with open(image_path, "rb") as f:
            dj_file = File(f, name="judge-howard-a-dawson-jr.png")

            new_image = Image(title="Judge Howard A. Dawson, Jr.")
            new_image.file.save("judge-howard-a-dawson-jr.png", dj_file, save=True)

            photo_dedication.photo = new_image

        page_fields = {
            "title": title,
            "body": body_content,
            "slug": slug,
            "seo_title": title,
            "search_description": "Dawson",
            "content_type": dawson_content_type,
            "show_in_menus": True,
            "menu_item_name": "DAWSON (eFILING SYSTEM)",
            "navigation_category": NavigationCategories.eFILING_AND_CASE_MAINTENANCE,
            "card_groups": [dawson_petition_card_group, dawson_card_group],
            "photo_dedication": [photo_dedication],
        }

        # Check if a DawsonPage with the given slug already exists
        existing_page = DawsonPage.objects.filter(slug=slug).first()

        if existing_page:
            # Update
            self.logger.write(f"- {title} page already exists. Updating content.")

            for field_name, field_value in page_fields.items():
                setattr(existing_page, field_name, field_value)

            existing_page.save()

            self.logger.write(f"Successfully updated the '{title}' page.")

        else:
            # Create
            self.logger.write(f"Creating the '{title}' page.")
            new_page = DawsonPage(**page_fields)

            # Add the new page under home_page
            home_page.add_child(instance=new_page)

            self.logger.write(f"Successfully created the '{title}' page.")
