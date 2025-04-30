from wagtail.models import Page, Site
from home.models import HomePage, HomePageEntry, HomePageImage
from home.management.commands.pages.page_initializer import PageInitializer
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
            title="",
            body=(
                'Guidance on remote (virtual) proceedings and example videos of various procedures in a virtual courtroom can be found <a target="_blank" href="https://ustaxcourt.gov/zoomgov.html">here.</a>'
            ),
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="The Tax Court announced that Chief Special Trial Judge Lewis R. Carluzzo has decided to step down as Chief Special Trial Judge, effective May 2, 2025, and that Special Trial Judge Zachary S. Fried has been named Chief Special Trial Judge, effective May 3, 2025.",
            body=(
                "See the <a target='_blank' href='/press-release'>Press Release</a>."
            ),
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="Tax Court Judge Julian I. Jacobs passed away on April 5, 2025.",
            body=(
                "See the <a target='_blank' href='/press-release'>Press Release</a>."
            ),
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
                "<p>The IRS posts current <a href='https://www.irs.gov/newsroom/tax-scams-consumer-alerts' target='_blank'>warnings and alerts</a> about all types of tax scams on its website (including information about how to report tax scams). In addition, you may file a consumer complaint about a tax scam with the <a href='https://www.ftc.gov' target='_blank'>Federal Trade Commission</a> (FTC) or the <a href='https://www.fbi.gov' target='_blank'>Federal Bureau of Investigation</a> (FBI). These websites are maintained by the FTC and FBI — government agencies that are unrelated to the Tax Court.</p>"
                "<p>If you would like to verify that the communication you received is really from the Tax Court, please call the Court at (202) 521-0700.</p>"
            ),
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

        logger.info("Successfully updated the new Home page.")
