from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import IconCategories
from home.models import EnhancedStandardPage

docs = {
    "DAWSON_Public_Training_Guide.pdf": "",
    "DAWSON_Petitioner_Training_Guide.pdf": "",
    "DAWSON_Practitioner_Training_Guide.pdf": "",
    "GMT20201013-122947_Jessica-Ma_1600x900.mp4": "",
    "efiling_in_consolidated_cases.mp4": "",
}


class DawsonUserGuidesPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson-user-guides"
        title = "DAWSON User Guides"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            Page.objects.filter(slug=slug).delete()

        self.logger.write(f"Creating the '{title}' page.")

        for doc_name in docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            docs[doc_name] = document

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=None,
                search_description=title,
                body=[
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "DAWSON Public Training Guide",
                                    "icon": IconCategories.PDF,
                                    "document": docs[
                                        "DAWSON_Public_Training_Guide.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "DAWSON Self-Represented (Pro Se) Training Guide",
                                    "icon": IconCategories.PDF,
                                    "document": docs[
                                        "DAWSON_Petitioner_Training_Guide.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "DAWSON Practitioner Training Guide",
                                    "icon": IconCategories.PDF,
                                    "document": docs[
                                        "DAWSON_Practitioner_Training_Guide.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "DAWSON Training Video",
                                    "icon": IconCategories.VIDEO,
                                    "video": docs[
                                        "GMT20201013-122947_Jessica-Ma_1600x900.mp4"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "DAWSON Training: Simultaneously eFile Documents in Consolidated Cases",
                                    "icon": IconCategories.VIDEO,
                                    "video": docs[
                                        "efiling_in_consolidated_cases.mp4"
                                    ].id,
                                    "url": None,
                                },
                            ],
                        },
                    },
                ],
            ),
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
