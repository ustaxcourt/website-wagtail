from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)

docs = {
    "08082024v3.pdf": "",
    "Rule_13_Package-Discussion_of_Comments_Received_8-08-2024.pdf": "",
    "Trujillo_and_Rico_Public_Comment.pdf": "",
    "Harvard-Clinic_Comment_re_Proposed-Amendment.pdf": "",
    "Tax_Court_Rules_Amendments_1-22-24_-Chief_Counsel_Comments_Paul_Butler_3-21-24.pdf": "",
    "Lewis_C_Taishoff.pdf": "",
    "01222024.pdf": "",
    "03202023.pdf": "",
    "Discussion_of_Comments_March_2023.pdf": "",
    "ABA_Section_of_Taxation_05252022.pdf": "",
    "Suzanne_McCrory.pdf": "",
    "Center_for-Taxpayer_Rights_Nina_E_Olson_05252022.pdf": "",
    "Law_Office_of_Wm_Mark_Scott_PLLC_05252022.pdf": "",
    "IRS_Chief_Counsel_Drita_Tonuzi.pdf": "",
    "Legal_Services_Center_of_Harvard-Law_School_Keith_Fogg_05202022.pdf": "",
    "Aderant_Cheryl-Siler_05162022.pdf": "",
    "CohnReznick_Dan_Wise_CPA_03242022.pdf": "",
    "03232022.pdf": "",
    "10062020.pdf": "",
    "ABA_Tax_Section_Comments_on_Amendments_to_Rule_24_06012020.pdf": "",
    "TC_RULE_24_Chief_Counsel_IRS_05292020.pdf": "",
    "Tax_Court_Rule_24_Comments_05272020.pdf": "",
    "05182020.pdf": "",
    "071519.pdf": "",
    "IRS_3-1-19.pdf": "",
    "121918.pdf": "",
    "113018.pdf": "",
    "Tax_Section_State_Bar_of_Texas_11-6-18.pdf": "",
    "ABA_Tax_Section_10-3-18.pdf": "",
    "ABA_Tax_Section_5-4-16.pdf": "",
    "Tax_Section_State_Bar_of_Texas_4-27-16.pdf": "",
    "IRS_-4-26-16.pdf": "",
    "Carlton_M-_Smith_2-22-16.pdf": "",
    "IRS_-2-12-16.pdf": "",
    "ABA_Tax_Section_2-10-16.pdf": "",
    "Tax_Section_State_Bar_of_Texas_2-8-16.pdf": "",
    "011116.pdf": "",
    "Baker_and_McKenzie_11-23-15.pdf": "",
    "ABA_Tax_Section_11-10-15.pdf": "",
    "John_H_Dies_10-30-15.pdf": "",
    "Harvard_10-30-15.pdf": "",
    "Tax_Section_State_Bar_of_Texas_10-30-15.pdf": "",
    "Thomas_N_Thompson_10-5-15.pdf": "",
    "Lewis_C_Taishoff_9-28-15.pdf": "",
    "Carlton_M-_Smith_9-25-15.pdf": "",
    "IRS_-9-11-15.pdf": "",
}


class CommentsAndSuggestionsPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()
        self.slug = "rules-comments"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.info("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Comments and Suggestions"

        if Page.objects.filter(slug=self.slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        for document in docs.keys():
            uploaded_document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=document,
                title=document,
            )
            docs[document] = uploaded_document.file.url

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description=title,
                body=[
                    {
                        "type": "table",
                        "value": {
                            "columns": [
                                {
                                    "type": "text",
                                    "heading": "Regarding Amendments Proposed to the Rules of Practice and Procedure on January 22, 2024",
                                },
                                {"type": "text", "heading": "Date"},
                            ],
                            "rows": [
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["08082024v3.pdf"]}">United States Tax Court, Press Release Announcing Amendments Adopted to the Rules of Practice and Procedure</a>""",
                                        "08/08/2024",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Rule_13_Package-Discussion_of_Comments_Received_8-08-2024.pdf"]}">United States Tax Court, Discussion of Comments Received</a>""",
                                        "08/08/2024",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Trujillo_and_Rico_Public_Comment.pdf"]}">Mario Trujillo and Bertha Rico</a>""",
                                        "03/22/2024",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Harvard-Clinic_Comment_re_Proposed-Amendment.pdf"]}">Sean O’Connell and Audrey Patten, Tax Clinic at the Legal Services Center of Harvard Law School</a>""",
                                        "03/22/2024",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Tax_Court_Rules_Amendments_1-22-24_-Chief_Counsel_Comments_Paul_Butler_3-21-24.pdf"]}">Marjorie A. Rollinson, Chief Counsel, Internal Revenue Service</a>""",
                                        "03/21/2024",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Lewis_C_Taishoff.pdf"]}">Lewis C. Taishoff, Esq.</a>""",
                                        "01/23/2024",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["01222024.pdf"]}">United States Tax Court, Press Release Announcing Proposed Amendments</a>""",
                                        "01/22/2024",
                                    ]
                                },
                            ],
                        },
                    },
                    {
                        "type": "table",
                        "value": {
                            "columns": [
                                {
                                    "type": "text",
                                    "heading": "Regarding Amendments Proposed to the Rules of Practice and Procedure on March 23, 2022",
                                },
                                {"type": "text", "heading": "Date"},
                            ],
                            "rows": [
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["03202023.pdf"]}">United States Tax Court, Press Release Announcing Amendments Adopted to the Rules of Practice and Procedure</a>""",
                                        "03/20/2023",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Discussion_of_Comments_March_2023.pdf"]}">United States Tax Court, Discussion of Comments Received</a>""",
                                        "03/20/2023",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["ABA_Section_of_Taxation_05252022.pdf"]}">ABA Section of Taxation</a>""",
                                        "05/25/2022",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Suzanne_McCrory.pdf"]}">Suzanne McCrory</a>""",
                                        "05/25/2022",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Center_for-Taxpayer_Rights_Nina_E_Olson_05252022.pdf"]}">Nina E. Olson, Executive Director, Center for Taxpayer Rights</a>""",
                                        "05/25/2022",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Law_Office_of_Wm_Mark_Scott_PLLC_05252022.pdf"]}">Wm. Mark Scott, PLLC</a>""",
                                        "05/25/2022",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["IRS_Chief_Counsel_Drita_Tonuzi.pdf"]}">Drita Tonuzi, Deputy Chief Counsel (Operations), Internal Revenue Service</a>""",
                                        "05/24/2022",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Legal_Services_Center_of_Harvard-Law_School_Keith_Fogg_05202022.pdf"]}">T. Keith Fogg, Director, Tax Clinic at the Legal Services Center of Harvard Law School</a>""",
                                        "05/20/2022",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Aderant_Cheryl-Siler_05162022.pdf"]}">Cheryl Siler, Director, CompuLaw Operations, Aderant</a>""",
                                        "05/16/2022",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["CohnReznick_Dan_Wise_CPA_03242022.pdf"]}">Dan Wise, CPA, CohnReznick</a>""",
                                        "03/24/2022",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["03232022.pdf"]}">United States Tax Court, Press Release Announcing Proposed Amendments</a>""",
                                        "03/23/2022",
                                    ]
                                },
                            ],
                        },
                    },
                    {
                        "type": "table",
                        "value": {
                            "columns": [
                                {
                                    "type": "text",
                                    "heading": "Regarding Amendments Proposed to the Rules of Practice and Procedure on May 18, 2020",
                                },
                                {"type": "text", "heading": "Date"},
                            ],
                            "rows": [
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["10062020.pdf"]}">United States Tax Court, Press Release Announcing Amendments Adopted to the Rules of Practice and Procedure</a>""",
                                        "10/06/2020",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["ABA_Tax_Section_Comments_on_Amendments_to_Rule_24_06012020.pdf"]}">ABA Section of Taxation</a>""",
                                        "06/01/2020",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["TC_RULE_24_Chief_Counsel_IRS_05292020.pdf"]}">Kathryn A. Zuba, Associate Chief Counsel (Procedure & Administration), Internal Revenue Service</a>""",
                                        "05/29/2020",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Tax_Court_Rule_24_Comments_05272020.pdf"]}">T. Keith Fogg, Clinical Professor of Law and Director, Tax Clinic Legal Services Center of Harvard Law School</a>""",
                                        "05/27/2020",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["05182020.pdf"]}">United States Tax Court, Press Release Announcing Proposed Amendments</a>""",
                                        "05/18/2020",
                                    ]
                                },
                            ],
                        },
                    },
                    {
                        "type": "table",
                        "value": {
                            "columns": [
                                {
                                    "type": "text",
                                    "heading": "Regarding Amendments Proposed to the Rules of Practice and Procedure on December 19, 2018",
                                },
                                {"type": "text", "heading": "Date"},
                            ],
                            "rows": [
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["071519.pdf"]}">United States Tax Court, Press Release Announcing Amendments Adopted to the Rules of Practice and Procedure</a>""",
                                        "07/15/2019",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["IRS_3-1-19.pdf"]}">Drita Tonuzi, Deputy Chief Counsel (Operations), Internal Revenue Service</a>""",
                                        "03/01/2019",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["121918.pdf"]}">United States Tax Court, Press Release Announcing Proposed Amendments</a>""",
                                        "12/19/2018",
                                    ]
                                },
                            ],
                        },
                    },
                    {
                        "type": "table",
                        "value": {
                            "columns": [
                                {
                                    "type": "text",
                                    "heading": "Regarding Amendments Proposed to the Rules of Practice and Procedure on January 11, 2016",
                                },
                                {"type": "text", "heading": "Date"},
                            ],
                            "rows": [
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["113018.pdf"]}">United States Tax Court, Press Release Announcing Amendments Adopted to the Rules of Practice and Procedure</a>""",
                                        "11/30/2018",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Tax_Section_State_Bar_of_Texas_11-6-18.pdf"]}">Catherine C. Scheid on behalf of the Tax Section of the State Bar of Texas</a>""",
                                        "11/06/2018",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["ABA_Tax_Section_10-3-18.pdf"]}">ABA Section of Taxation</a>""",
                                        "10/03/2018",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["ABA_Tax_Section_5-4-16.pdf"]}">ABA Section of Taxation</a>""",
                                        "05/04/2016",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Tax_Section_State_Bar_of_Texas_4-27-16.pdf"]}">Alyson Outenreath on behalf of the Tax Section of the State Bar of Texas</a>""",
                                        "04/27/2016",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["IRS_-4-26-16.pdf"]}">Drita Tonuzi, Associate Chief Counsel (Procedure and Administration), Internal Revenue Service</a>""",
                                        "04/26/2016",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Carlton_M-_Smith_2-22-16.pdf"]}">Carlton M. Smith, Esq.</a>""",
                                        "02/22/2016",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["IRS_-2-12-16.pdf"]}">Drita Tonuzi, Associate Chief Counsel (Procedure and Administration), Internal Revenue Service</a>""",
                                        "02/12/2016",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["ABA_Tax_Section_2-10-16.pdf"]}">ABA Section of Taxation</a>""",
                                        "02/10/2016",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Tax_Section_State_Bar_of_Texas_2-8-16.pdf"]}">Alyson Outenreath on behalf of the Tax Section of the State Bar of Texas</a>""",
                                        "02/08/2016",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["011116.pdf"]}">United States Tax Court, Press Release Announcing Proposed Amendments</a>""",
                                        "01/11/2016",
                                    ]
                                },
                            ],
                        },
                    },
                    {
                        "type": "table",
                        "value": {
                            "columns": [
                                {
                                    "type": "text",
                                    "heading": "Other Comments Received in Response to the Court's Ongoing Efforts to Improve Its Rules",
                                },
                                {"type": "text", "heading": "Date"},
                            ],
                            "rows": [
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Baker_and_McKenzie_11-23-15.pdf"]}">Jenny Austin and Daniel Rosen, Partners, Baker & McKenzie</a>""",
                                        "11/23/2015",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["ABA_Tax_Section_11-10-15.pdf"]}">ABA Section of Taxation</a>""",
                                        "11/10/2015",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["John_H_Dies_10-30-15.pdf"]}">John H. Dies</a>""",
                                        "10/30/2015",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Harvard_10-30-15.pdf"]}">Professor Keith Fogg, Director, Federal Tax Clinic, Legal Services Center of Harvard Law School</a>""",
                                        "10/30/2015",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Tax_Section_State_Bar_of_Texas_10-30-15.pdf"]}">Alyson Outenreath on behalf of the Tax Section of the State Bar of Texas</a>""",
                                        "10/30/2015",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Thomas_N_Thompson_10-5-15.pdf"]}">Thomas N. Thompson, Attorney at Law</a>""",
                                        "10/05/2015",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Lewis_C_Taishoff_9-28-15.pdf"]}">Lewis C. Taishoff, Attorney-at-Law</a>""",
                                        "09/28/2015",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["Carlton_M-_Smith_9-25-15.pdf"]}">Carlton M. Smith, Esq.</a>""",
                                        "09/25/2015",
                                    ]
                                },
                                {
                                    "values": [
                                        f"""<a class="font-normal" href="{docs["IRS_-9-11-15.pdf"]}">William J. Wilkins, Chief Counsel, Internal Revenue Service</a>""",
                                        "09/11/2015",
                                    ]
                                },
                            ],
                        },
                    },
                ],
            )
        )

        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")
