import os

from wagtail.models import Page
from wagtail.images.models import Image
from django.conf import settings
from django.core.files import File
from django.contrib.contenttypes.models import ContentType
from home.models import (
    DawsonPage,
    # SimpleCardGroup,
    # SimpleCards,
    # RelatedPage,
    PhotoDedication,
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

        content_type = ContentType.objects.get_for_model(DawsonPage)

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
            "content_type": content_type,
            "show_in_menus": True,
            "menu_item_name": "DAWSON (eFILING SYSTEM)",
            "navigation_category": NavigationCategories.eFILING_AND_CASE_MAINTENANCE,
            "photo_dedication": [photo_dedication],
        }

        # Check if a DawsonPage with the given slug already exists
        existing_page = DawsonPage.objects.filter(slug=slug).first()

        if existing_page:
            # Update scenario
            self.logger.write(f"- {title} page already exists. Updating content.")

            for field_name, field_value in page_fields.items():
                setattr(existing_page, field_name, field_value)

            existing_page.save()

            self.logger.write(f"Successfully updated the '{title}' page.")

        else:
            # Create scenario
            self.logger.write(f"Creating the '{title}' page.")
            new_page = DawsonPage(**page_fields)

            # Add the new page under home_page
            home_page.add_child(instance=new_page)

            self.logger.write(f"Successfully created the '{title}' page.")
