from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage


class CommentsAndSuggestionsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "rules_comments"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            self.logger.write("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Comments and Suggestions"

        if Page.objects.filter(slug=self.slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description=title,
                show_in_menus=False,
                body=[
                    {
                        "type": "columns",
                        "value": {
                            "column": [
                                [  # First column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Regarding Amendments Proposed to the Rules of Practice and Procedure on January 22, 2024</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Press Release Announcing Amendments Adopted to the Rules of Practice and Procedure</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Discussion of Comments Received</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Mario Trujillo and Bertha Rico</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Sean O’Connell and Audrey Patten, Tax Clinic at the Legal Services Center of Harvard Law School</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Marjorie A. Rollinson, Chief Counsel, Internal Revenue Service</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Lewis C. Taishoff, Esq.</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Press Release Announcing Proposed Amendments</p></a></strong>""",
                                        },
                                    },
                                ],
                                [  # Second column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Date</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>08/08/2024</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>08/08/2024</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>03/22/2024</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>03/22/2024</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>03/21/2024</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>01/23/2024</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>01/22/2024</p>""",
                                        },
                                    },
                                ],
                            ]
                        },
                    },
                    {
                        "type": "columns",
                        "value": {
                            "column": [
                                [  # First column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Regarding Amendments Proposed to the Rules of Practice and Procedure on March 23, 2022</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Press Release Announcing Amendments Adopted to the Rules of Practice and Procedure</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Discussion of Comments Received</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>ABA Section of Taxation</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Suzanne McCrory</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Nina E. Olson, Executive Director, Center for Taxpayer Rights</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Wm. Mark Scott, PLLC</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Drita Tonuzi, Deputy Chief Counsel (Operations), Internal Revenue Service</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>T. Keith Fogg, Director, Tax Clinic at the Legal Services Center of Harvard Law School</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Cheryl Siler, Director, CompuLaw Operations, Aderant</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Dan Wise, CPA, CohnReznick</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Press Release Announcing Proposed Amendments</p></a></strong>""",
                                        },
                                    },
                                ],
                                [  # Second column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Date</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>03/20/2023</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>03/20/2023</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/25/2022</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/25/2022</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/25/2022</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/25/2022</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/24/2022</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/20/2022</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/16/2022</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>03/24/2022</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>03/23/2022</p>""",
                                        },
                                    },
                                ],
                            ]
                        },
                    },
                    {
                        "type": "columns",
                        "value": {
                            "column": [
                                [  # First column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Regarding Amendments Proposed to the Rules of Practice and Procedure on May 18, 2020</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Press Release Announcing Amendments Adopted to the Rules of Practice and Procedure</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>ABA Section of Taxation</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Kathryn A. Zuba, Associate Chief Counsel (Procedure & Administration), Internal Revenue Service</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>T. Keith Fogg, Clinical Professor of Law and Director, Tax Clinic Legal Services Center of Harvard Law School</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Press Release Announcing Proposed Amendments</p></a></strong>""",
                                        },
                                    },
                                ],
                                [  # Second column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Date</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>10/06/2020</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>06/01/2020</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/29/2020</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/27/2020</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/18/2020</p>""",
                                        },
                                    },
                                ],
                            ]
                        },
                    },
                    {
                        "type": "columns",
                        "value": {
                            "column": [
                                [  # First column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Regarding Amendments Proposed to the Rules of Practice and Procedure on December 19, 2018</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Press Release Announcing Amendments Adopted to the Rules of Practice and Procedure</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Drita Tonuzi, Deputy Chief Counsel (Operations), Internal Revenue Service</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Press Release Announcing Proposed Amendments</p></a></strong>""",
                                        },
                                    },
                                ],
                                [  # Second column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Date</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>07/15/2019</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>03/01/2019</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>12/19/2018</p>""",
                                        },
                                    },
                                ],
                            ]
                        },
                    },
                    {
                        "type": "columns",
                        "value": {
                            "column": [
                                [  # First column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Regarding Amendments Proposed to the Rules of Practice and Procedure on January 11, 2016</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Press Release Announcing Amendments Adopted to the Rules of Practice and Procedure</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Catherine C. Scheid on behalf of the Tax Section of the State Bar of Texas</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>ABA Section of Taxation</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>ABA Section of Taxation</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Alyson Outenreath on behalf of the Tax Section of the State Bar of Texas</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Drita Tonuzi, Associate Chief Counsel (Procedure and Administration), Internal Revenue Service</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Carlton M. Smith, Esq.</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Drita Tonuzi, Associate Chief Counsel (Procedure and Administration), Internal Revenue Service</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>ABA Section of Taxation</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Alyson Outenreath on behalf of the Tax Section of the State Bar of Texas</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>United States Tax Court, Press Release Announcing Proposed Amendments</p></a></strong>""",
                                        },
                                    },
                                ],
                                [  # Second column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Date</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>11/30/2018</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>11/06/2018</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>10/03/2018</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>05/04/2016</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>04/27/2016</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>04/26/2016</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>02/22/2016</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>02/12/2016</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>02/10/2016</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>02/08/2016</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>01/11/2016</p>""",
                                        },
                                    },
                                ],
                            ]
                        },
                    },
                    {
                        "type": "columns",
                        "value": {
                            "column": [
                                [  # First column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Other Comments Received in Response to the Court's Ongoing Efforts to Improve Its Rules</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Jenny Austin and Daniel Rosen, Partners, Baker & McKenzie</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>ABA Section of Taxation</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>John H. Dies</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Professor Keith Fogg, Director, Federal Tax Clinic, Legal Services Center of Harvard Law School</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Alyson Outenreath on behalf of the Tax Section of the State Bar of Texas</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Thomas N. Thompson, Attorney at Law</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Lewis C. Taishoff, Attorney-at-Law</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>Carlton M. Smith, Esq.</p></a></strong>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<strong><a href=""><p>William J. Wilkins, Chief Counsel, Internal Revenue Service</p></a></strong>""",
                                        },
                                    },
                                ],
                                [  # Second column
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<h3>Date</h3>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>11/23/2015</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>11/10/2015</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>10/30/2015</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>10/30/2015</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>10/30/2015</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>10/05/2015</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>09/28/2015</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>09/25/2015</p>""",
                                        },
                                    },
                                    {
                                        "type": "paragraph",
                                        "value": {
                                            "text": """<p>09/11/2015</p>""",
                                        },
                                    },
                                ],
                            ]
                        },
                    },
                ],
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
