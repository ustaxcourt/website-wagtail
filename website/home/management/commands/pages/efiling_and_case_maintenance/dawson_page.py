from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.models import (
    DawsonPage,
    FancyCard,
    SimpleCardGroup,
    SimpleCard,
    RelatedPage,
    PhotoDedication,
    EnhancedStandardPage,
)
from home.management.commands.pages.page_initializer import PageInitializer


class DawsonPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_related_pages(self, card, related_std_pages, category, standard_pages):
        for a_page in related_std_pages:
            RelatedPage.objects.create(
                display_title=next(
                    (
                        p["title"]
                        for p in standard_pages[category]
                        if p["slug"] == a_page.slug
                    ),
                    a_page.title,
                ),
                card=card,
                related_page=a_page,
            )
        card.save()

    def create_page_info(self, home_page):
        slug = "dawson"
        title = "DAWSON"

        existing_dawson_page = home_page.get_children().live().filter(slug=slug).first()
        if existing_dawson_page:
            self.logger.write(f"- {title} page already exists.")
            return

        body_content = (
            "DAWSON (Docket Access Within a Secure Online Network) is the U.S. Tax Court's electronic filing and "
            'case management system. See the <a href="/dawson-user-guides">user guides</a> '
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

        home_page.add_child(instance=dawson_page)
        self.logger.write(f"Created {title} page stub.")

        dawson_content_type = ContentType.objects.get_for_model(DawsonPage)

        dawson_fancy_card = FancyCard(
            url="https://dawson.ustaxcourt.gov/",
            text="DAWSON has been designed to work with most modern browsers (Chrome, Firefox, Safari, Edge, etc.). Internet Explorer is not supported by this system.",
            parent_page=dawson_page,
        )
        login_image = self.load_image_from_images_dir(
            "dawson", "DAWSON-log-in.png", "DAWSON Log In"
        )
        dawson_fancy_card.photo = login_image

        dawson_petition_card_group = SimpleCardGroup(
            group_label="", parent_page=dawson_page
        )
        dawson_petition_card_group.save()

        dawson_card_group = SimpleCardGroup(
            group_label="Filing a Petition", parent_page=dawson_page
        )
        dawson_card_group.save()

        self.logger.write("Created card groups.")

        standard_pages = {
            "petition": [
                {
                    "title": "How to eFile a Petition",
                    "slug": "efile-a-petition",
                    "path": "efile-a-petition",
                    "depth": 4,
                    "search_description": "How to eFile a Petition",
                },
                {
                    "title": "How to Pay the Filing Fee",
                    "slug": "pay-filing-fee",
                    "path": "pay-filing-fee",
                    "depth": 4,
                    "search_description": "How to Pay the Filing Fee",
                },
                {
                    "title": "How to Merge PDFs",
                    "slug": "merging-files",
                    "path": "merging-files",
                    "depth": 4,
                    "search_description": "How to Merge PDFs",
                },
            ],
            "managing_case": [
                {
                    "title": "How to View Your Dashboard",
                    "slug": "dashboard",
                    "path": "dashboard",
                    "depth": 4,
                    "search_description": "How to View Your Dashboard",
                },
                {
                    "title": "How to Update Your Contact Information",
                    "slug": "update-contact-information",
                    "path": "update-contact-information",
                    "depth": 4,
                    "search_description": "How to Update Your Contact Information",
                },
            ],
            "searching_case": [
                {
                    "title": "How to Search for a Case",
                    "slug": "find-a-case",
                    "path": "find-a-case",
                    "depth": 4,
                    "search_description": "How to Search for a Case",
                },
                {
                    "title": "How to Search for an Order",
                    "slug": "find-an-order",
                    "path": "find-an-order",
                    "depth": 4,
                    "search_description": "How to Search for an Order",
                },
                {
                    "title": "How to Search for an Opinion",
                    "slug": "find-an-opinion",
                    "path": "find-an-opinion",
                    "depth": 4,
                    "search_description": "How to Search for an Opinion",
                },
            ],
            "reference_materials": [
                {
                    "title": "FAQs",
                    "slug": "dawson-faqs-basics",
                    "path": "dawson-faqs-basics",
                    "depth": 4,
                    "search_description": "FAQs",
                },
                {
                    "title": "Terms of Use",
                    "slug": "dawson-tou",
                    "path": "dawson-tou",
                    "depth": 4,
                    "search_description": "Terms of Use",
                },
                {
                    "title": "Definitions",
                    "slug": "definitions",
                    "path": "definitions",
                    "depth": 4,
                    "search_description": "Definitions",
                },
                {
                    "title": "What Documents Can Be eFiled",
                    "slug": "documents-eligible-for-efiling",
                    "path": "documents-eligible-for-efiling",
                    "depth": 4,
                    "search_description": "What Documents Can Be eFiled",
                },
                {
                    "title": "Privacy and Public Access to Case Files",
                    "slug": "notice-regarding-privacy",
                    "path": "notice-regarding-privacy",
                    "depth": 4,
                    "search_description": "Privacy and Public Access to Case Files",
                },
                {
                    "title": "Release Notes",
                    "slug": "release-notes",
                    "path": "release-notes",
                    "depth": 4,
                    "search_description": "Release Notes",
                },
                {
                    "title": "DAWSON User Guides",
                    "slug": "dawson-user-guides",
                    "path": "dawson-user-guides",
                    "depth": 4,
                    "search_description": "DAWSON User Guides",
                },
                {
                    "title": "DAWSON Status",
                    "slug": "dawson-status",
                    "path": "https://status.ustaxcourt.gov/",
                    "depth": 4,
                    "search_description": "DAWSON Status",
                },
            ],
            "registration": [
                {
                    "title": "Petitioner Registration",
                    "slug": "dawson-petitioner-registration",
                    "path": "https://app.dawson.ustaxcourt.gov/create-account/petitioner",
                    "depth": 4,
                    "search_description": "Petitioner Registration",
                },
                {
                    "title": "Practitioner Registration",
                    "slug": "dawson-account-practitioner",
                    "path": "dawson-account-practitioner",
                    "depth": 4,
                    "search_description": "Practitioner Registration",
                },
            ],
        }

        all_new_std_pages = {}
        for card_name, pages in standard_pages.items():
            new_std_pages = []
            for page in pages:
                std_page = (
                    home_page.get_children().live().filter(slug=page["slug"]).first()
                )
                if std_page:
                    new_std_pages.append(std_page.specific)
                else:
                    new_std_page = EnhancedStandardPage(**page)
                    home_page.add_child(instance=new_std_page)
                    self.logger.write(f"Created {new_std_page.title} page.")
                    new_std_pages.append(new_std_page)
            all_new_std_pages[card_name] = new_std_pages

        register_card = SimpleCard(
            card_title="",
            card_icon="",
            parent_page=dawson_petition_card_group,
        )
        register_card.save()

        petition_simple_card = SimpleCard(
            card_title="Filing a Petition",
            card_icon="file-lines",
            parent_page=dawson_card_group,
        )
        petition_simple_card.save()

        managing_case_card = SimpleCard(
            card_title="Managing Your Cases",
            card_icon="gears",
            parent_page=dawson_card_group,
        )
        managing_case_card.save()

        searching_case_card = SimpleCard(
            card_title="Searching for Cases and Documents",
            card_icon="search",
            parent_page=dawson_card_group,
        )
        searching_case_card.save()

        reference_materials_card = SimpleCard(
            card_title="Reference Materials",
            card_icon="book",
            parent_page=dawson_card_group,
        )
        reference_materials_card.save()

        self.logger.write("Created cards.")

        self.create_related_pages(
            register_card,
            all_new_std_pages["registration"],
            "registration",
            standard_pages,
        )
        self.create_related_pages(
            petition_simple_card,
            all_new_std_pages["petition"],
            "petition",
            standard_pages,
        )
        self.create_related_pages(
            managing_case_card,
            all_new_std_pages["managing_case"],
            "managing_case",
            standard_pages,
        )
        self.create_related_pages(
            searching_case_card,
            all_new_std_pages["searching_case"],
            "searching_case",
            standard_pages,
        )
        self.create_related_pages(
            reference_materials_card,
            all_new_std_pages["reference_materials"],
            "reference_materials",
            standard_pages,
        )

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

        dawson_image = self.load_image_from_images_dir(
            "dawson", "judge-howard-a-dawson-jr.png", "Judge Howard A. Dawson, Jr."
        )
        photo_dedication.photo = dawson_image

        page_fields = {
            "title": title,
            "body": body_content,
            "slug": slug,
            "seo_title": title,
            "search_description": "Dawson",
            "content_type": dawson_content_type,
            "fancy_card": [dawson_fancy_card],
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
