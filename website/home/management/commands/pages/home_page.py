from wagtail.models import Page, Site
from home.models import HomePage
from home.management.commands.pages.page_initializer import PageInitializer
import logging


logger = logging.getLogger(__name__)

home_page_documents = {
    "calendar_icon.svg": "",
    "DAWSON_icon.svg": "",
    "learn_icon.svg": "",
    "opinions_icon.svg": "",
    "orders_icon.svg": "",
    "PDF_icon.svg": "",
    "practitioners_icon.svg": "",
    "rules_icon.svg": "",
    "search_icon.svg": "",
    "start_icon.svg": "",
}


class HomePageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        root = Page.objects.filter(depth=1).first()
        title = "Home"

        if not root:
            logger.info("Error: No root page found. Cannot create Home page.")
            return

        if HomePage.objects.filter(title=title).exists():
            logger.info(f"- {title} page already exists.")
            return

        static_cards = [
            {
                "type": "card",
                "value": {
                    "title": "U.S. Tax Court Warning about Tax Scams",
                    "body": '<p data-block-key="apxhb">Some people may receive unsolicited phone calls, emails, or other communications from individuals fraudulently claiming to be from the Tax Court, the Internal Revenue Service (IRS), or Federal government agencies and demanding immediate payment by money order, gift card, debit card, or other means to settle a tax debt.\u2028\u2028</p><p data-block-key="1ecb5">The Tax Court does not want anyone to be victimized by a tax scam. It is important that you know that the Tax Court will never do any of the following:\u2028</p><ul><li data-block-key="btkfc">call or email demanding payment of immigration visa application fees or taxes;</li><li data-block-key="8hah0">call or email threatening arrest;</li><li data-block-key="c9b1h">call or email insisting that a specific payment method be used to pay Court fees, a tax debt, or requesting credit or debit card numbers over the phone.</li></ul><p data-block-key="15feq">The IRS posts current <a href="https://ustaxcourt.gov/redirect_irs_tax_scams.html">warnings and alerts</a> about all types of tax scams on its website (including information about how to report tax scams). In addition, you may file a consumer complaint about a tax scam with the <a href="https://reportfraud.ftc.gov/">Federal Trade Commission </a>(FTC) or the <a href="https://www.ic3.gov/">Federal Bureau of Investigation</a> (FBI). These websites are maintained by the FTC and FBI \u2014 government agencies that are unrelated to the Tax Court.\u2028\u2028If you would like to verify that the communication you received is really from the Tax Court please call the Court at (202) 521-0700.</p>',
                    "start_date": "2025-10-01T11:54:00-04:00",
                    "end_date": None,
                },
            }
        ]

        hero_background = {
            "title": "image of the united states tax court building far away",
            "filename": "home-hero-bg.jpg",
        }

        image_uploaded = self.load_image_from_images_dir(
            "home", hero_background["filename"], hero_background["title"]
        )

        homepage = HomePage(
            title=title,
            intro="U.S. Tax Court website homepage",
            draft_title="Home",
            slug=None,
            search_description="Official Site of the United States Tax Court",
            seo_title="United States Tax Court",
            static_text_cards=static_cards,
            hero_background_image=image_uploaded,
        )

        root.add_child(instance=homepage)
        homepage.save_revision().publish()

        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.root_page = homepage
            site.save()
            logger.info("Updated default site root to the new Home page.")

        # delete the wagtail generated page (it doesn't have the mixin)
        wagtailHome = Page.objects.filter(
            title="Welcome to your new Wagtail site!"
        ).first()
        if wagtailHome:
            logger.info("Deleting the default wagtail home")
            wagtailHome.delete()

        # set the new home page slug as home now that the wagtail default page is deleted
        homepage.slug = "home"
        homepage.save_revision().publish()

        logger.info("Successfully created the new Home page.")

    def update(self):
        title = "Home"

        if HomePage.objects.filter(title=title).exists():
            logger.info(f"- {title} page already exists. Updating the existing page.")
        else:
            logger.info("Page does not exist. Nothing to update. STOPPING.")
            return

    def get_page(self, slug):
        try:
            page = Page.objects.live().filter(slug=slug).first()
            if page:
                return page.specific
            logger.info(f"WARNING: Page with slug '{slug}' not found")
            return None
        except Page.DoesNotExist:
            logger.info(f"WARNING: Page with slug '{slug}' not found")
            return None

    def update_home_page(self):
        logger.info("Updating Home page quick access tiles...")

        # Load icon documents and store the actual Document objects
        for doc_name in home_page_documents:
            doc_object = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            home_page_documents[doc_name] = doc_object

        # Build the StreamField data with the correct structure
        quick_access_tiles = [
            {
                "type": "tile",
                "value": {
                    "title": "Begin the Petition Filing Process",
                    "description": "Start your case on DAWSON to file and track your petition.",
                    "icon": {"svg_file": home_page_documents["start_icon.svg"].pk},
                    "related_page": self.get_page("efile-a-petition").pk,
                },
            }
            # Add other tiles as needed...
        ]

        # Get the homepage
        homepage = self.get_page("home")

        if homepage:
            # Assign the list of data to the StreamField
            homepage.quick_access_tiles = quick_access_tiles

            # Save a new revision and publish the changes to make them live
            homepage.save_revision().publish()

            logger.info("Successfully updated Home page with quick access tiles.")
        else:
            logger.warning("Could not find Home page to update.")
