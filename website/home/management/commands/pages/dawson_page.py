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
from django.core.exceptions import ValidationError
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
        try:
            home_page.get_children().live().filter(slug=slug).first().delete()
            print(f"Deleted existing {title} page.")
        except ValidationError:
            pass
        home_page.add_child(instance=dawson_page)
        print(f"Created {title} page stub.")

        dawson_content_type = ContentType.objects.get_for_model(DawsonPage)

        dawson_card_group = SimpleCardGroup(
            group_label="Filing a Petition", parent_page=dawson_page
        )

        dawson_card_group.save()
        print("Created 'Filing a Petition' card group.")

        standard_pages = [
            {
                "title": "How to eFile a Petition",
                "body": "Before starting the e-filing process, please review the helpful tips provided below. They will instruct you in what is needed and how to go about filing your petition electronically in DAWSON (Docket Access Within and Secure Online Network), the Court’s electronic filing and case management system. For more detailed instructions, refer to the DAWSON user guides.",
                "slug": "petition",
                "show_in_menus": False,
                "path": "petition",
                "depth": 4,
                "search_description": "How to eFile a Petition",
            },
            {
                "title": "How to Pay the Filing Fee",
                "body": "Filing fees are required to submit a petition. The Court’s filing fee is $60 and may be paid online, by mail, or in person. The fee may be waived by filing an Application for Waiver of Filing Fee. Your petition must be processed by the Court before the Application for Waiver of Filing fee can be filed electronically.",
                "slug": "file-fee",
                "show_in_menus": False,
                "path": "file-fee",
                "depth": 4,
                "search_description": "How to Pay the Filing Fee",
            },
            {
                "title": "How to Merge PDFs",
                "body": "These instructions apply only to Adobe Acrobat Professional and Standard. A user utilizing other software to create PDFs must follow the software vendor's instructions for creating a single PDF from multiple PDFs.",
                "slug": "merge-pdfs",
                "show_in_menus": False,
                "path": "merge-pdfs",
                "depth": 4,
                "search_description": "How to Merge PDFs",
            },
        ]

        new_std_pages = []
        for page in standard_pages:
            std_page = home_page.get_children().live().filter(slug=page["slug"]).first()
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

            # related_page = RelatedPage(related_page=new_std_page)

            # dawson_card_group.cards.add(related_page)
            # related_pages.append(related_page)

        petition_simple_card = SimpleCards(
            card_title="Filing a Petition",
            card_icon="file-text",
            # related_pages=related_pages,
            parent_page=dawson_card_group,
        )

        petition_simple_card.save()
        print("Created 'Filing a Petition' card.")

        for std_page in new_std_pages:
            RelatedPage.objects.create(card=petition_simple_card, related_page=std_page)

        petition_simple_card.save()

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
            "card_groups": [dawson_card_group],
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
