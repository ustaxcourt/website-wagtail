from wagtail.models import Page, Site
from home.models import HomePage, HomePageEntry, HomePageImage
from home.management.commands.pages.page_initializer import PageInitializer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

carousel_images = [
    {
        "title": "image of the united states tax court building far away",
        "filename": "building_far.jpg",
    },
    {
        "title": "image of the united states tax court building from the front",
        "filename": "building_front.jpg",
    },
    {
        "title": "image of the united states tax court building with trees",
        "filename": "building_tree.jpg",
    },
]

home_docs = {
    "05052025.pdf": "",
    "04292025.pdf": "",
    "04162025.pdf": "",
    "04072025.pdf": "",
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

        homepage = HomePage(
            title=title,
            draft_title="Home",
            slug=None,
            search_description="Official Site of the United States Tax Court",
            seo_title="United States Tax Court",
        )

        loaded_images = []
        for image in carousel_images:
            image_uploaded = self.load_image_from_images_dir(
                "home", image["filename"], image["title"]
            )
            loaded_images.append(HomePageImage(image=image_uploaded))

        if loaded_images:
            homepage.images = loaded_images

        root.add_child(instance=homepage)
        homepage.save_revision().publish()

        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.root_page = homepage
            site.save()
            logger.info("Updated default site root to the new Home page.")

        for document in home_docs.keys():
            uploaded_document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=document,
                title=document,
            )
            home_docs[document] = uploaded_document.file.url

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

        HomePageEntry.objects.create(
            homepage=homepage,
            title="Remote Proceedings Info",
            body=(
                'Guidance on remote (virtual) proceedings and example videos of various procedures in a virtual courtroom can be found <a target="_blank" href="/zoomgov">here.</a>'
            ),
            start_date=datetime(2024, 12, 31, 6, 0),  # Example: 6 AM EST
            end_date=datetime(2025, 1, 1, 23, 59),  # Example: 11.59 PM EST
            persist_to_press_releases=True,
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="Closed for Holidays",
            body=(
                "In addition to observing the Christmas Day holiday on Wednesday, December 25, 2024, the Court will be closed on Tuesday, December 24, 2024. DAWSON will remain available for electronic access and electronic filing."
            ),
            start_date=datetime(2024, 12, 1, 6, 0),
            end_date=datetime(2024, 12, 25, 23, 59),
            persist_to_press_releases=True,
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="",
            body=(
                'Guidance on remote (virtual) proceedings and example videos of various procedures in a virtual courtroom can be found <a target="_blank" href="/zoomgov">here.</a>'
            ),
            start_date=datetime(2025, 4, 14, 6, 0),
            end_date=None,
            persist_to_press_releases=True,
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="Tax Court disciplinary matters.",
            body=(
                f"""See the <a href="{home_docs["04292025.pdf"]}" target="_blank" title="Press Release">Press Release</a>."""
            ),
            start_date=datetime(2025, 4, 29, 6, 0),
            end_date=None,
            persist_to_press_releases=True,
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="The Tax Court announced that Chief Special Trial Judge Lewis R. Carluzzo has decided to step down as Chief Special Trial Judge, effective May 2, 2025, and that Special Trial Judge Zachary S. Fried has been named Chief Special Trial Judge, effective May 3, 2025.",
            body=(
                f"""See the <a href="{home_docs["04162025.pdf"]}" target="_blank" title="Press Release">Press Release</a>."""
            ),
            start_date=datetime(2025, 4, 14, 6, 0),
            end_date=None,
            persist_to_press_releases=True,
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="Tax Court Judge Julian I. Jacobs passed away on April 5, 2025",
            body=(
                f"""See the <a href="{home_docs["04072025.pdf"]}" target="_blank" title="Press Release">Press Release</a>."""
            ),
            start_date=datetime(2025, 4, 7, 6, 0),
            end_date=datetime(2025, 5, 5, 23, 59),
            persist_to_press_releases=True,
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="U.S. Tax Court Warning about Tax Scams",
            body=(
                "<p>Some people may receive unsolicited phone calls, emails, or other communications from individuals fraudulently claiming to be from the Tax Court, the Internal Revenue Service (IRS), or Federal government agencies and demanding immediate payment by money order, gift card, debit card, or other means to settle a tax debt.</p>"
                "<p>The Tax Court does not want anyone to be victimized by a tax scam. It is important that you know that the Tax Court will never do any of the following:</p>"
                "<ul>"
                "<li>call or email demanding payment of immigration visa application fees or taxes;</li>"
                "<li>call or email threatening arrest;</li>"
                "<li>call or email insisting that a specific payment method be used to pay Court fees, a tax debt, or requesting credit or debit card numbers over the phone.</li>"
                "</ul>"
                "<p>The IRS posts current <a href='https://www.irs.gov/newsroom/tax-scams-consumer-alerts' target='_blank'>warnings and alerts</a> about all types of tax scams on its website (including information about how to report tax scams). In addition, you may file a consumer complaint about a tax scam with the <a href='https://www.ftc.gov' target='_blank'>Federal Trade Commission</a> (FTC) or the <a href='https://www.ic3.gov' target='_blank' title='Report Fraud'>Federal Bureau of Investigation</a> (FBI). These websites are maintained by the FTC and FBI — government agencies that are unrelated to the Tax Court.</p>"
                "<p>If you would like to verify that the communication you received is really from the Tax Court, please call the Court at (202) 521-0700.</p>"
            ),
            start_date=None,
            end_date=None,
            persist_to_press_releases=True,
        )

        logger.info("Successfully created the new Home page.")

    def update(self):
        title = "Home"

        if HomePage.objects.filter(title=title).exists():
            logger.info(f"- {title} page already exists. Updating the existing page.")
            homepage = HomePage.objects.get(title=title)
        else:
            logger.info("Page does not exist. Nothing to update. STOPPING.")
            return

        remote_proceeding_entry = HomePageEntry.objects.filter(
            homepage=homepage, title="Remote Proceedings Info"
        )

        if remote_proceeding_entry.exists():
            remote_proceeding_entry.update(
                body=(
                    'Guidance on remote (virtual) proceedings and example videos of various procedures in a virtual courtroom can be found <a href="/zoomgov">here.</a>'
                )
            )
        else:
            logger.info(
                "Remote Proceedings Info entry does not exist. Nothing to update."
            )

        entries_to_add = [
            {
                "title": "2025 Nonattorney Examination",
                "body": f"""The United States Tax Court hereby announces that the examination for nonattorney applicants for admission to practice before the Court will be held remotely using the ExamSoft platform on Wednesday, November 5, 2025, 12:30pm Eastern Time.
                </br>
                </br>
                See the <a href="{home_docs["05052025.pdf"]}" target="_blank">Press Release</a>.""",
                "start_date": datetime(2025, 5, 5, 6, 0),
                "end_date": None,
                "persist_to_press_releases": True,
            },
            # Add more entries as needed
        ]

        # 🔁 Loop through entries and create them if they don't exist
        for entry_data in entries_to_add:
            if not HomePageEntry.objects.filter(
                homepage=homepage, title=entry_data["title"]
            ).exists():
                HomePageEntry.objects.create(
                    homepage=homepage,
                    title=entry_data["title"],
                    body=entry_data["body"],
                    start_date=entry_data["start_date"],
                    end_date=entry_data["end_date"],
                    persist_to_press_releases=entry_data["persist_to_press_releases"],
                )
                logger.info(f"{entry_data['title']} entry created successfully.")
            else:
                logger.info(
                    f"{entry_data['title']} entry already exists. No action taken."
                )

        logger.info("Finished updating Home page entries.")
