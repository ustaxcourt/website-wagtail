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
            home_docs[document] = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=document,
                title=document,
            )

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
            homepage = HomePage.objects.get(title=title)
        else:
            logger.info("Page does not exist. Nothing to update. STOPPING.")
            return

        for document in home_docs.keys():
            home_docs[document] = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=document,
                title=document,
            )

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

        logger.info("Finished updating Home page entries.")
