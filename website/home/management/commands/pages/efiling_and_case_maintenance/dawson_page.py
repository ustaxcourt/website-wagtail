from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.models import (
    DawsonPage,
    DawsonFancyCard,
    SimpleCardGroup,
    SimpleCardGroupItem,
    DawsonSimpleCard,
    PhotoDedication,
    EnhancedStandardPage,
    SimpleCard,
    FancyCard,
    RelatedPage,
)
from home.management.commands.pages.page_initializer import PageInitializer
import logging

logger = logging.getLogger(__name__)


class DawsonPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_related_pages(
        self, card_snippet, related_std_pages, category, standard_pages
    ):
        """Create RelatedPage instances for a SimpleCard snippet."""
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
                card=card_snippet,
                related_page=a_page,
            )
        card_snippet.save()

    def create_page_info(self, home_page):
        slug = "dawson"
        title = "DAWSON"

        existing_dawson_page = home_page.get_children().live().filter(slug=slug).first()
        if existing_dawson_page:
            logger.info(f"- {title} page already exists.")
            return
        else:
            dawson_page = DawsonPage(
                title=title,
                slug=slug,
                search_description="Dawson eFiling main page",
                body="Placeholder body text.",
            )
            home_page.add_child(instance=dawson_page)
            logger.info(f"Created {title} page stub.")

        body_content = (
            "DAWSON (Docket Access Within a Secure Online Network) is the U.S. Tax Court's electronic filing and "
            'case management system. See the <a href="/dawson-user-guides">user guides</a> '
            "for more information and instructions.<br/><br/> Technical questions about DAWSON? Please contact "
            '<a href="mailto:dawson.support@ustaxcourt.gov">dawson.support@ustaxcourt.gov</a>. No documents can be '
            "filed with the Court at this email address. Any documents received via email will NOT be filed in your case."
        )

        dawson_content_type = ContentType.objects.get_for_model(DawsonPage)

        # Clear existing relationships
        DawsonFancyCard.objects.filter(parent_page=dawson_page).delete()
        DawsonSimpleCard.objects.filter(parent_page=dawson_page).delete()
        SimpleCardGroup.objects.filter(parent_page=dawson_page).delete()

        # Create FancyCard snippet
        fancy_card_snippet = FancyCard(
            url="https://dawson.ustaxcourt.gov/",
            text="DAWSON has been designed to work with most modern browsers (Chrome, Firefox, Safari, Edge, etc.). Internet Explorer is not supported by this system.",
            live=True,
        )
        login_image = self.load_image_from_images_dir(
            "dawson", "DAWSON-log-in.png", "DAWSON Log In"
        )
        fancy_card_snippet.photo = login_image
        fancy_card_snippet.save()

        # Link FancyCard snippet to DawsonPage
        dawson_fancy_card_link = DawsonFancyCard(
            parent_page=dawson_page, fancy_card=fancy_card_snippet
        )
        dawson_fancy_card_link.save()

        dawson_petition_card_group = SimpleCardGroup(
            group_label="", parent_page=dawson_page
        )
        dawson_petition_card_group.save()

        dawson_card_group = SimpleCardGroup(
            group_label="Filing a Petition", parent_page=dawson_page
        )
        dawson_card_group.save()

        logger.info("Created card groups.")

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
                    "title": "User Guides",
                    "slug": "dawson-user-guides",
                    "path": "dawson-user-guides",
                    "depth": 4,
                    "search_description": "DAWSON User Guides",
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

        # Create SimpleCard snippets
        register_card_snippet = SimpleCard(
            card_title="Registration", card_icon="user-plus", live=True
        )
        register_card_snippet.save()

        petition_card_snippet = SimpleCard(
            card_title="Filing a Petition", card_icon="file-lines", live=True
        )
        petition_card_snippet.save()

        managing_case_card_snippet = SimpleCard(
            card_title="Managing Your Cases", card_icon="gears", live=True
        )
        managing_case_card_snippet.save()

        searching_case_card_snippet = SimpleCard(
            card_title="Searching for Cases and Documents",
            card_icon="search",
            live=True,
        )
        searching_case_card_snippet.save()

        reference_materials_card_snippet = SimpleCard(
            card_title="Reference Materials", card_icon="book", live=True
        )
        reference_materials_card_snippet.save()

        # Link SimpleCard snippets to groups via SimpleCardGroupItem
        SimpleCardGroupItem.objects.create(
            group=dawson_petition_card_group, simple_card=register_card_snippet
        )

        SimpleCardGroupItem.objects.create(
            group=dawson_card_group, simple_card=petition_card_snippet
        )

        SimpleCardGroupItem.objects.create(
            group=dawson_card_group, simple_card=managing_case_card_snippet
        )

        SimpleCardGroupItem.objects.create(
            group=dawson_card_group, simple_card=searching_case_card_snippet
        )

        SimpleCardGroupItem.objects.create(
            group=dawson_card_group, simple_card=reference_materials_card_snippet
        )

        logger.info("Created cards.")

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
                    logger.info(f"Created {new_std_page.title} page.")
                    new_std_pages.append(new_std_page)
            all_new_std_pages[card_name] = new_std_pages

        self.create_related_pages(
            register_card_snippet,
            all_new_std_pages["registration"],
            "registration",
            standard_pages,
        )
        self.create_related_pages(
            petition_card_snippet,
            all_new_std_pages["petition"],
            "petition",
            standard_pages,
        )
        self.create_related_pages(
            managing_case_card_snippet,
            all_new_std_pages["managing_case"],
            "managing_case",
            standard_pages,
        )
        self.create_related_pages(
            searching_case_card_snippet,
            all_new_std_pages["searching_case"],
            "searching_case",
            standard_pages,
        )
        self.create_related_pages(
            reference_materials_card_snippet,
            all_new_std_pages["reference_materials"],
            "reference_materials",
            standard_pages,
        )

        dawson_petitioner_registration_page = RelatedPage.objects.get(
            related_page__slug="dawson-petitioner-registration"
        )
        dawson_petitioner_registration_page.related_page = None
        dawson_petitioner_registration_page.url = (
            "https://app.dawson.ustaxcourt.gov/create-account/petitioner"
        )
        dawson_petitioner_registration_page.save()

        RelatedPage.objects.create(
            display_title="DAWSON Status",
            card=reference_materials_card_snippet,
            related_page=None,
            url="https://status.ustaxcourt.gov/",
        )

        reference_materials_card_snippet.save()

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
        }

        logger.info(f"- {title} page already exists. Updating content.")

        for field_name, field_value in page_fields.items():
            setattr(dawson_page, field_name, field_value)

        dawson_page.save()

        # Save the photo dedication instance
        photo_dedication.dawson_page = dawson_page
        photo_dedication.save()

        logger.info(f"Successfully updated the '{title}' page.")
