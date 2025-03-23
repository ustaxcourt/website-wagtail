from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import (
    IconCategories,
    EnhancedStandardPage,
    PhotoDedication,
)

HISTORY_DATA = [
    {
        "title": "The United States Tax Court: An Historical Analysis (Second Edition) by Professors Harold Dubroff and Brant J. Hellwig",
        "name": "Dubroff_Hellwig.pdf",
    },
]


class HistoryPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "history"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            self.logger.write("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "History"

        if Page.objects.filter(slug=self.slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        history_image = self.load_image_from_images_dir(
            "history", "us_tax_court_building.jpg", "US Tax Court Building"
        )

        if not history_image:
            self.logger.write("Failed to load history image. Aborting page creation.")
            return

        info = [
            {
                "title": "The United States Tax Court: An Historical Analysis (Second Edition) by Professors Harold Dubroff and Brant J. Hellwig",
                "document": "Dubroff_Hellwig.pdf",
            }
        ]

        info_links = []

        for item in info:
            document = self.load_document_from_documents_dir(
                None,
                item["document"],
                item["title"],
            )

            info_links.append(
                {
                    "title": item["title"],
                    "icon": IconCategories.PDF,
                    "document": document.id,
                    "url": None,
                }
            )

        photo_dedication = PhotoDedication.objects.create(
            paragraph_text="""<p>In the Revenue Act of 1924, Congress established the Board of Tax Appeals (Board) as an independent agency in the Executive Branch to permit taxpayers to challenge determinations made by the Internal Revenue Service (IRS) of their tax liabilities before payment. In 1942, Congress changed the name of the Board to the "Tax Court of the United States," but the Tax Court of the United States remained an independent agency in the Executive Branch.
                                                 In the Tax Reform Act of 1969, Congress reconstituted the Tax Court of the United States as the United States Tax Court (Tax Court or Court); repealed the statutory designation of the Tax Court as an Executive Branch agency; and included in the legislative history that the Court, unlike its quasi-judicial predecessors, would not be within the Executive Branch. Section 7441 of Title 26 of the United States Code provides that:
                                             </p>
                                             <blockquote>
                                                 There is hereby established, under article I of the <a href="https://www.archives.gov/founding-docs/constitution" title="U.S.Constitution">Constitution of the United States</a>, a court of record to be known as the United States Tax Court. The members of the Tax Court shall be the chief judge and the judges of the Tax Court. The Tax Court is not an agency of, and shall be independent of, the executive branch of the Government.
                                             </blockquote>
                                             <p>
                                                 The Tax Court is a court of law with nationwide jurisdiction exercising judicial power independent of the Executive and Legislative Branches. The Tax Court is one of the courts in which taxpayers can bring suit to contest IRS determinations, and it is the primary court in which taxpayers can do so without prepaying any portion of the disputed taxes.
                                             </p>""",
            alt_text="US Tax Court Building",
        )

        photo_dedication.photo = history_image
        photo_dedication.save()

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description="History",
                body=[
                    {
                        "type": "links",
                        "value": {
                            "links": info_links,
                        },
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "photo_dedication",
                        "value": {
                            "title": "Historical Overview",
                            "paragraph_text": photo_dedication.paragraph_text,
                            "photo": photo_dedication.photo.id,
                            "alt_text": photo_dedication.alt_text,
                        },
                    },
                    {
                        "type": "paragraph",
                        "value": """<h2>Judges</h2>
                                <br>
                                The Tax Court is composed of 19 presidentially appointed members. Trial sessions are conducted and other work of the Court is performed by those
                                <a href='/judges' title='Judges'>judges</a>, by <a href='/judges/#SENIOR' title='Senior Judges'>senior judges</a> serving on recall, and by <a href='/judges/#SPECIAL' title='Special Trial Judges'>special trial judges</a>. Although the Court is physically located in Washington, D.C., <a href='/judges' title='Judges'>the judges</a> travel nationwide to conduct trials in various <a href='/dpt-cities' title='Places of Trial'>designated places of trial</a>.""",
                    },
                    {
                        "type": "paragraph",
                        "value": """<h2>Washington, D.C. Courthouse</h2>
                                <br>
                                Designed for the Tax Court and dedicated on November 22, 1974, the courthouse is a landmark work by architect Victor Lundy. It is held out as a prominent example of the "formalist modern" style of architecture in Washington, D.C. The U. S. Tax Court Courthouse was added to the National Register of Historic Places in August 2008.
                                <br>
                                <br>
                                Learn more about the courthouse by visiting <a href='https://www.gsa.gov/real-estate/gsa-properties/visiting-public-buildings/united-states-tax-court' title='gsa.gov'>GSA’s website</a>, or more about <strong><em>Victor Lundy by watching Victor Lundy: Sculptor of Space</em></strong>.""",
                    },
                    {
                        "type": "embedded_video",
                        "value": {
                            "title": "Victor Lundy: Sculptor of Space",
                            "description": """<p>We are excited to include here <strong><em>Victor Lundy: Sculptor of Space.</em></strong> This informative and entertaining documentary was produced by the GSA (General Services Administration) as part of <em><a href="https://www.youtube.com/playlist?list=PLvdwyPgXnxxU_f2Ee8FnuBdflb6pEtF_Z"  target="_blank" title="The Historic Building Film Series">The Historic Building Film Series</a></em>.</p>
                                            <blockquote><i>Victor Lundy: Sculptor of Space captures the recollections of the modern American master architect and artist who designed GSA's historic U.S. Tax Court Building in Washington, DC.</i>
                                            <cite title="Source Title">- GSA YouTube Channel</cite>
                                            </blockquote>""",
                            "video_url": "https://www.youtube.com/embed/s6umLipF7-E",
                        },
                    },
                ],
            )
        )

        self.logger.write(f"Created the '{title}' page.")
