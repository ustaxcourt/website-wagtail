from wagtail.models import Page, Site
from home.models import HomePage
from home.management.commands.pages.page_initializer import PageInitializer
import logging
from django.conf import settings

from home.models.utils.execute_script import ExecuteScript
from django.db import DatabaseError
from django.core.exceptions import ValidationError

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
                    "body": '<p data-block-key="apxhb">Some people may receive unsolicited phone calls, emails, or other communications from individuals fraudulently claiming to be from the Tax Court, the Internal Revenue Service (IRS), or Federal government agencies and demanding immediate payment by money order, gift card, debit card, or other means to settle a tax debt.\u2028\u2028</p><p data-block-key="1ecb5">The Tax Court does not want anyone to be victimized by a tax scam. It is important that you know that the Tax Court will never do any of the following:\u2028</p><ul><li data-block-key="btkfc">call or email demanding payment of immigration visa application fees or taxes;</li><li data-block-key="8hah0">call or email threatening arrest;</li><li data-block-key="c9b1h">call or email insisting that a specific payment method be used to pay Court fees, a tax debt, or requesting credit or debit card numbers over the phone.</li></ul><p data-block-key="15feq">The IRS posts current <a href="https://www.irs.gov/help/tax-scams/recognize-tax-scams-and-fraud">warnings and alerts</a> about all types of tax scams on its website (including information about how to report tax scams). In addition, you may file a consumer complaint about a tax scam with the <a href="https://reportfraud.ftc.gov/">Federal Trade Commission </a>(FTC) or the <a href="https://www.ic3.gov/">Federal Bureau of Investigation</a> (FBI). These websites are maintained by the FTC and FBI \u2014 government agencies that are unrelated to the Tax Court.\u2028\u2028If you would like to verify that the communication you received is really from the Tax Court please call the Court at (202) 521-0700.</p>',
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
            # intro="U.S. Tax Court website homepage",
            intro_text="Welcome to the United States Tax Court.",
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
            base_url = getattr(settings, "BASE_URL", "")
            if "127.0.0.1:8000" in base_url or "localhost:8000" in base_url:
                site.hostname = "localhost"
                site.port = 8000
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

    @staticmethod
    def get_environment_specific_dawson_url(prefix=None):
        if settings.ENVIRONMENT == "production":
            url = "dawson.ustaxcourt.gov"
        elif settings.ENVIRONMENT == "train":
            url = "test.ef-cms.ustaxcourt.gov"
        else:  # Default to development [local, dev, sandbox, all others]
            url = "dev.ef-cms.ustaxcourt.gov"
        if prefix:
            return f"https://{prefix}.{url}"
        return f"https://{url}"

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
                    "link": [
                        {"type": "related_page", "value": self.get_page("dawson").pk}
                    ],
                },
            },
            {
                "type": "tile",
                "value": {
                    "title": "Learn How to Start a Case",
                    "description": "Read these FAQ’s before filing to prepare for starting your case.",
                    "icon": {"svg_file": home_page_documents["learn_icon.svg"].pk},
                    "link": [
                        {
                            "type": "related_page",
                            "value": self.get_page("petitioners-start").pk,
                        }
                    ],
                },
            },
            {
                "type": "tile",
                "value": {
                    "title": "DAWSON Case Management",
                    "description": "Our online system, DAWSON, allows users to file documents and track their case status.",
                    "icon": {"svg_file": home_page_documents["DAWSON_icon.svg"].pk},
                    "link": [
                        {
                            "type": "external_url",
                            "value": self.get_environment_specific_dawson_url(),
                        }
                    ],
                },
            },
            {
                "type": "tile",
                "value": {
                    "title": "Tax Court Rules",
                    "description": "The Court's current Rules of Practice & Procedure, forms, and fee schedule.",
                    "icon": {"svg_file": home_page_documents["rules_icon.svg"].pk},
                    "link": [
                        {"type": "related_page", "value": self.get_page("rules").pk}
                    ],
                },
            },
            {
                "type": "tile",
                "value": {
                    "title": "Today's Opinions",
                    "description": "Access the most recent court opinions issued by Tax Court judges.",
                    "icon": {"svg_file": home_page_documents["opinions_icon.svg"].pk},
                    "link": [
                        {
                            "type": "external_url",
                            "value": f"{self.get_environment_specific_dawson_url()}/todays-opinions",
                        }
                    ],
                },
            },
            {
                "type": "tile",
                "value": {
                    "title": "Today’s Orders",
                    "description": "Access the most recent court orders issued by Tax Court judges.",
                    "icon": {"svg_file": home_page_documents["orders_icon.svg"].pk},
                    "link": [
                        {
                            "type": "external_url",
                            "value": f"{self.get_environment_specific_dawson_url()}/todays-orders",
                        }
                    ],
                },
            },
            {
                "type": "tile",
                "value": {
                    "title": "Guidance for Practitioners",
                    "description": "Resources for attorneys and practitioners, including DAWSON access, and practice rules.",
                    "icon": {
                        "svg_file": home_page_documents["practitioners_icon.svg"].pk
                    },
                    "link": [
                        {
                            "type": "related_page",
                            "value": self.get_page("practitioners").pk,
                        }
                    ],
                },
            },
            {
                "type": "tile",
                "value": {
                    "title": "Case Related Forms",
                    "description": "Forms for filing petitions, motions, and other court documents.",
                    "icon": {"svg_file": home_page_documents["PDF_icon.svg"].pk},
                    "link": [
                        {
                            "type": "related_page",
                            "value": self.get_page("case-related-forms").pk,
                        }
                    ],
                },
            },
            {
                "type": "tile",
                "value": {
                    "title": "Find a Trial Session",
                    "description": "Search for scheduled trial sessions by location, type, or judge.",
                    "icon": {"svg_file": home_page_documents["calendar_icon.svg"].pk},
                    "link": [
                        {
                            "type": "external_url",
                            "value": f"{self.get_environment_specific_dawson_url()}/trial-sessions",
                        }
                    ],
                },
            },
        ]
        full_width_quick_access_tile = [
            {
                "type": "tile",
                "value": {
                    "title": "Find a Case, Order, Opinion or Practitioner",
                    "icon": {"svg_file": home_page_documents["search_icon.svg"].pk},
                    "link": [
                        {
                            "type": "external_url",
                            "value": self.get_environment_specific_dawson_url(),
                        }
                    ],
                },
            },
        ]

        # Get the homepage
        homepage = self.get_page("home")

        if homepage:
            # Assign the list of data to the StreamField
            homepage.quick_access_tiles = quick_access_tiles
            homepage.full_width_quick_access_tile = full_width_quick_access_tile

            # Save a new revision and publish the changes to make them live
            homepage.save_revision().publish()

            logger.info("Successfully updated Home page with quick access tiles.")
        else:
            logger.warning("Could not find Home page to update.")

    def run(self):
        """Update the homepage quick access tiles as an execution script"""
        command_name = "HomePage update for homepage redesign"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.update_home_page()
            execution_log_text = "HomePage updated for homepage redesign"
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = execution_log_text
            script_entry.save()

        except HomePage.DoesNotExist:
            error_msg = "HomePage settings not found in database. Cannot update non-existent homepage."
            logger.error(error_msg)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {error_msg}"
            script_entry.save()
            raise

        except DatabaseError as e:
            error_msg = f"Database error occurred while updating homepage: {str(e)}"
            logger.error(error_msg)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Database Error:</strong> {error_msg}"
            script_entry.save()
            raise

        except ValidationError as e:
            error_msg = f"Validation error occurred while saving homepage: {str(e)}"
            logger.error(error_msg)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = (
                f"<strong>Validation Error:</strong> {error_msg}"
            )
            script_entry.save()
            raise

        except Exception as e:
            error_msg = f"Unexpected error during homepage update: {type(e).__name__} - {str(e)}"
            logger.error(error_msg)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = (
                f"<strong>Unexpected Error:</strong> {error_msg}"
            )
            script_entry.save()
            raise
