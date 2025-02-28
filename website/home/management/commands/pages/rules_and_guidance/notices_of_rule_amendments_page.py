from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import IconCategories
from home.models import EnhancedStandardPage

notice_docs = {
    "08082024v3.pdf": "",
    "03202023.pdf": "",
    "10062020.pdf": "",
    "01152020.pdf": "",
    "071519.pdf": "",
    "113018.pdf": "",
    "070612.pdf": "",
    "050511.pdf": "",
    "112009.pdf": "",
    "091809.pdf": "",
    "100308.pdf": "",
    "011508.pdf": "",
    "040307.pdf": "",
    "011207.pdf": "",
    "092105.pdf": "",
    "063003.pdf": "",
}


class NoticesOfRuleAmendmentsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "notices_of_rule_amendments"
        title = "Notices of Rule Amendments"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        for doc_name in notice_docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            notice_docs[doc_name] = document

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=None,
                search_description="Notices of Rule Amendments",
                body=[
                    {
                        "type": "paragraph",
                        "value": "Below are the press releases announcing previously enacted amendments to the Tax Court Rules of Practice and Procedure.",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on August 8, 2024",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["08082024v3.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on March 20, 2023",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["03202023.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on October 6, 2020",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["10062020.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on January 15, 2020",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["01152020.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on July 15, 2019",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["071519.pdf"].id,
                                    "url": None,
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {"type": "h2", "value": "Archived Press Releases"},
                    {"type": "hr", "value": True},
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on November 30, 2018",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["113018.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on July 6, 2012",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["070612.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on May 5, 2011",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["050511.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on November 20, 2009",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["112009.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on September 18, 2009",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["091809.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on October 3, 2008",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["100308.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on January 15, 2008",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["011508.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on April 3, 2007",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["040307.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on January 12, 2007",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["011207.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on September 21, 2005",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["092105.pdf"].id,
                                    "url": None,
                                },
                                {
                                    "title": "Final Amendments adopted to the Rules of Practice and Procedure on June 30, 2003",
                                    "icon": IconCategories.PDF,
                                    "document": notice_docs["063003.pdf"].id,
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
