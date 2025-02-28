from wagtail.models import Page
from home.models import PamphletsPage, PamphletEntry, NavigationCategories
from home.management.commands.pages.page_initializer import PageInitializer
from django.contrib.contenttypes.models import ContentType

# Example pamphlet data
pamphlets_data = [
    {
        "title": "Volume 161, Numbers 5 and 6",
        "pdf": "161_TC_112-328.pdf",
        "code": "161 T.C. 112-328",
        "date_range": "November 1, 2023 to December 31, 2023",
        "citation": "<p>Liberty Global, Inc.<br/>McKelvey, Andrew J., Estate<br/>Peters, Bradford G., Executor<br/>Sall, Madiodio<br/>Sanders, Tiffany Lashun<br/>Soroban Capital Partners GP LLC, Tax Matters Partner<br/>Soroban Capital Partners LP<br/>YA Global Investments, LP<br/>Yorkville Advisors, GP LLC, Tax Matters Partner<br/>Yorkville Advisors, LLC, Tax Matters Partner</p>",
        "volume_number": 161.5,
    },
    {
        "title": "Volume 161, Number 4",
        "pdf": "161_TC_58-112.pdf",
        "code": "161 T.C. 58-112",
        "date_range": "October 1, 2023 to October 31, 2023",
        "citation": "<p>Caan, James E., Estate<br/>Caan, Scott, Trustee, Special Administrator<br/>Jacaan Administrative Trust<br/>Kraske, Wolfgang, Frederick<br/>Whistleblower 8391-18W</p>",
        "volume_number": 161.4,
    },
    {
        "title": "Volume 161, Number 3",
        "pdf": "161_TC_9-58.pdf",
        "code": "161 T.C. 9-58",
        "date_range": "September 1, 2023 to September 30, 2023",
        "citation": "<p>Organic Cannabis Foundation, LLC<br/>Piper Trucking & Leasing, LLC</p>",
        "volume_number": 161.3,
    },
    {
        "title": "Volume 161, Numbers 1 and 2",
        "pdf": "161_TC_1-9.pdf",
        "code": "161 T.C. 1-9",
        "date_range": "July 1, 2023 to August 31, 2023",
        "citation": "<p>Joseph E. Abe, DDS, Inc.<br/>Pugh, Zola Jane</p>",
        "volume_number": 161.1,
    },
    {
        "title": "Volume 160, Number 6",
        "pdf": "160_TC_557-690.pdf",
        "code": "160 T.C. 557-690",
        "date_range": "June 1, 2023 to June 30, 2023",
        "citation": "<p>Castillo, Josefa<br/>Sanders, Antawn Jamal<br/>Amendments to Rules of Practice and Procedure</p>",
        "volume_number": 160.6,
    },
    {
        "title": "Volume 160, Number 5",
        "pdf": "160_TC_470-557.pdf",
        "code": "160 T.C. 470-557",
        "date_range": "May 1, 2023 to May 31, 2023",
        "citation": "<p>Berenblatt, Jeremy<br/>Growmark Inc. and Subsidiaries<br/>Meduty, Prince Amun-Ra Hotep Ankh<br/>Nutt, Roy A. and Bonnie W.<br/>United Therapeutics Corporation</p>",
        "volume_number": 160.5,
    },
    {
        "title": "Volume 160, Number 4",
        "pdf": "160_TC_399-470.pdf",
        "code": "160 T.C. 399-470",
        "date_range": "April 1, 2023 to April 30, 2023",
        "citation": "<p>Farhy, Alon<br/>Gerhardt, Alan A. and Audrey M.<br/>Gerhardt, Gladys L., et al.<br/>Gerhardt, Jack R. and Shelley R.<br/>Gerhardt, Pamela J. Holck<br/>Gerhardt, Tim L.<br/>Stanojevich, Srbislav B.<br/>Tice, David W.</p>",
        "volume_number": 160.4,
    },
    {
        "title": "Volume 160, Number 3",
        "pdf": "160_TC_389-399.pdf",
        "code": "160 T.C. 389-399",
        "date_range": "March 1, 2023 to March 31, 2023",
        "citation": "<p>Shands, Thomas</p>",
        "volume_number": 160.3,
    },
    {
        "title": "Volume 160, Number 2",
        "pdf": "160_TC_50-388.pdf",
        "code": "160 T.C. 50-388",
        "date_range": "February 1, 2023 to February 28, 2023",
        "citation": "<p>3M Company and Subsidiaries<br/>Thomas, Sydney Ann Chaney</p>",
        "volume_number": 160.2,
    },
    {
        "title": "Volume 160, Number 1",
        "pdf": "160_TC_1-49.pdf",
        "code": "160 T.C. 1-49",
        "date_range": "January 1, 2023 to January 31, 2023",
        "citation": "<p>Adams, Blake M.<br/>Johnson, Michael and Cynthia, et al.</p>",
        "volume_number": 160.1,
    },
    {
        "title": "Volume 159, Numbers 5 and 6",
        "pdf": "159_TC_80-183.pdf",
        "code": "159 T.C. 80-183",
        "date_range": "November 1, 2022 to December 31, 2022",
        "citation": "<p>Green Valley Investors, LLC, et al.<br/>Hallmark Research Collective</p>",
        "volume_number": 159.5,
    },
    {
        "title": "Volume 159, Numbers 3 and 4",
        "pdf": "159_TC_75-80.pdf",
        "code": "159 T.C. 75–80",
        "date_range": "September 1, 2022 to October 31, 2022",
        "citation": "<p>Cochran, Daniel and Kelley</p>",
        "volume_number": 159.3,
    },
    {
        "title": "Volume 159, Number 2",
        "pdf": "159_TC_28-75.pdf",
        "code": "159 T.C. 28-75",
        "date_range": "August 1, 2022 to August 31, 2022",
        "citation": "<p>Smith, Cory H.<br/>Whistleblower 769-16W</p>",
        "volume_number": 159.2,
    },
    {
        "title": "Volume 159, Number 1",
        "pdf": "159_TC_1-27.pdf",
        "code": "159 T.C. 1-27",
        "date_range": "July 1, 2022 to July 31, 2022",
        "citation": "<p>Whistleblower 972-17W</p>",
        "volume_number": 159.1,
    },
    {
        "title": "Volume 158, Numbers 3, 4, 5, and 6",
        "pdf": "158_TC_99-199.pdf",
        "code": "158 T.C. 99-199",
        "date_range": "March 1, 2022 to June 30, 2022",
        "citation": "<p>AptarGroup Inc.<br/>BATS Global Markets Holdings, Inc. and Subsidiaries<br/>Brown, Michael D.<br/>Chavis, Angela M.<br/>DelPonte, Michelle<br/>Lewis, Gina C.<br/>Treece Financial Services Group</p>",
        "volume_number": 158.3,
    },
    {
        "title": "Volume 158, Numbers 1 and 2",
        "pdf": "158_TC_1-98.pdf",
        "code": "158 T.C. 1-98",
        "date_range": "January 1, 2022 to February 28, 2022",
        "citation": "<p>Levine, Marion, Estate, Robert L. Larson, Personal Representative<br/>TBL Licensing LLC f.k.a. The Timberland Company, and Subsidiaries (A Consolidated Group)</p>",
        "volume_number": 158.1,
    },
]


class PamphletsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "pamphlets"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
            pamphlet_page = self.create_page_info(home_page)

            for pamphlet_data in pamphlets_data:
                self.create_pamphlet_entry(pamphlet_page, pamphlet_data)
        except Page.DoesNotExist:
            self.logger.write("Root page does not exist.")
            return

    def create_page_info(self, parent_page):
        title = "United States Tax Court Reports: Pamphlets"

        if Page.objects.filter(slug=self.slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return Page.objects.get(slug=self.slug)

        self.logger.write(f"Creating the '{title}' page.")

        content_type = ContentType.objects.get_for_model(PamphletsPage)

        new_page = parent_page.add_child(
            instance=PamphletsPage(
                title=title,
                body="The Tax Court's published Reports are available as monthly or bimonthly pamphlets that provide the correct citation pages before the semiannual bound volumes are printed. Pamphlets are now available electronically below. When the pamphlet opens, click a link in the Table of Cases to open an opinion.<br/><br/>Sample citation:<blockquote><i>Smith v. Commissioner, 159 T.C. 33 (2022)</i></blockquote>",
                slug=self.slug,
                seo_title="Tax Court Reports Pamphlets",
                show_in_menus=True,
                content_type=content_type,
                search_description="Tax Court Reports Pamphlets",
            )
        )

        PamphletsPage.objects.filter(id=new_page.id).update(
            menu_item_name="TAX COURT REPORTS: PAMPHLETS",
            navigation_category=NavigationCategories.ORDERS_AND_OPINIONS,
        )

        self.logger.write(f"Successfully created the '{title}' page.")
        return new_page

    def create_pamphlet_entry(self, parent_page, pamphlet_data):
        try:
            # Check if the pamphlet already exists
            if PamphletEntry.objects.filter(title=pamphlet_data["title"]).exists():
                self.logger.write(
                    f"  - Pamphlet entry for {pamphlet_data['title']} already exists."
                )
                return

            document = self.load_document_from_documents_dir(
                subdirectory="pamphlets",
                filename=pamphlet_data["pdf"],
                title=pamphlet_data["title"],
            )

            if not document:
                self.logger.write(
                    f"Failed to load document for pamphlet: {pamphlet_data['title']}"
                )
                return

            entry = PamphletEntry(
                title=pamphlet_data["title"],
                pdf=document,
                code=pamphlet_data["code"],
                date_range=pamphlet_data["date_range"],
                citation=pamphlet_data["citation"],
                volume_number=pamphlet_data["volume_number"],
                parentpage=parent_page,
            )
            entry.save()

            self.logger.write(
                f"Successfully created pamphlet entry: {pamphlet_data['title']}"
            )

        except Page.DoesNotExist:
            self.logger.write("Parent page 'Pamphlets' does not exist.")
            return
