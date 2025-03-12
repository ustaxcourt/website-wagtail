from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import (
    EnhancedStandardPage,
    IconCategories,
)


class CaseProcedurePageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "case_procedure"
        title = "Which Case Procedure Should I Choose?"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title="Case Procedure Information",
                navigation_ribbon=None,
                search_description="Case Procedure Information",
                body=[
                    {
                        "type": "paragraph",
                        "value": "For specific case types, the amount of the tax in dispute will affect whether or not you qualify for small tax case procedures.",
                    },
                    {"type": "hr", "value": True},
                    {"type": "h3", "value": "Eligible for small tax case procedure"},
                    {
                        "type": "table",
                        "value": {
                            "columns": [
                                {"type": "text", "heading": "Case Type"},
                                {"type": "text", "heading": "Type of Notice/Complaint"},
                                {"type": "text", "heading": "Amount"},
                            ],
                            "rows": [
                                {
                                    "values": [
                                        "CDP (Lien/Levy)",
                                        "Notice of Determination Concerning Collection Action/CDP (Lien/Levy)",
                                        "Total amount of unpaid tax is $50,000 or less for all years combined",
                                    ]
                                },
                                {
                                    "values": [
                                        "Deficiency",
                                        "Notice of Deficiency",
                                        "Deficiency in dispute (including any additions to tax and penalties) is $50,000 or less for any one year",
                                    ]
                                },
                                {
                                    "values": [
                                        "Innocent Spouse",
                                        "Notice of Determination Concerning Relief From Joint and Several Liability Under Section 6015/Innocent Spouse",
                                        "Amount of spousal relief sought is $50,000 or less for all years at issue",
                                    ]
                                },
                                {
                                    "values": [
                                        "Interest Abatement",
                                        "Notice of Final Determination for Full or Partial Disallowance of Interest Abatement Claim/Interest Abatement - Failure of IRS to Make Final Determination Within 180 Days After Claim for Abatement",
                                        "Amount of the abatement sought is $50,000 or less",
                                    ]
                                },
                                {"values": ["Other", "Other", ""]},
                                {
                                    "values": [
                                        "Worker Classification",
                                        "Notice of Determination of Worker Classification/Worker Classification",
                                        "Amount in dispute is $50,000 or less for any calendar quarter",
                                    ]
                                },
                            ],
                        },
                    },
                    {
                        "type": "h3",
                        "value": "Not eligible for small tax case procedure",
                    },
                    {
                        "type": "table",
                        "value": {
                            "columns": [
                                {"type": "text", "heading": "Case Type"},
                                {"type": "text", "heading": "Type of Notice/Complaint"},
                                {"type": "text", "heading": "Amount"},
                            ],
                            "rows": [
                                {
                                    "values": [
                                        "CDP (Lien/Levy)",
                                        "Notice of Determination Concerning Collection Action/CDP (Lien/Levy)",
                                        "Total amount of unpaid tax is greater than $50,000 for all years combined",
                                    ]
                                },
                                {
                                    "values": [
                                        "Deficiency",
                                        "Notice of Deficiency",
                                        "Deficiency in dispute (including any additions to tax and penalties) is greater than $50,000 for any one year",
                                    ]
                                },
                                {
                                    "values": [
                                        "Innocent Spouse",
                                        "Notice of Determination Concerning Relief From Joint and Several Liability Under Section 6015/Innocent Spouse",
                                        "Amount of spousal relief sought is greater than $50,000 for all years at issue",
                                    ]
                                },
                                {
                                    "values": [
                                        "Interest Abatement",
                                        "Notice of Final Determination for Full or Partial Disallowance of Interest Abatement Claim/Interest Abatement - Failure of IRS to Make Final Determination Within 180 Days After Claim for Abatement",
                                        "Amount of the abatement sought is greater than $50,000",
                                    ]
                                },
                                {
                                    "values": [
                                        "Worker Classification",
                                        "Notice of Determination of Worker Classification/Worker Classification",
                                        "Amount in dispute is greater than $50,000 for any calendar quarter",
                                    ]
                                },
                                {
                                    "values": [
                                        "Declaratory Judgment (Exempt Organization)",
                                        "Adverse Determination Concerning a Tax Exempt Status",
                                        "",
                                    ]
                                },
                                {
                                    "values": [
                                        "Declaratory Judgment (Retirement Plan)",
                                        "Revocation Letter Concerning a Retirement Plan",
                                        "",
                                    ]
                                },
                                {
                                    "values": [
                                        "Disclosure",
                                        "Notice - We Are Going To Make Your Determination Letter Available for Public Inspection",
                                        "",
                                    ]
                                },
                                {
                                    "values": [
                                        "Disclosure",
                                        "Notice of Intention to Disclose/Disclosure",
                                        "",
                                    ]
                                },
                                {
                                    "values": [
                                        "Partnership (BBA Section 1101)",
                                        "Partnership Action Under BBA Section 1101",
                                        "",
                                    ]
                                },
                                {
                                    "values": [
                                        "Partnership (Section 6226)",
                                        "Readjustment of Partnership Items Code Section 6226",
                                        "",
                                    ]
                                },
                                {
                                    "values": [
                                        "Partnership (Section 6228)",
                                        "Adjustment of Partnership Items Code Section 6228",
                                        "",
                                    ]
                                },
                                {
                                    "values": [
                                        "Passport",
                                        "Notice of Certification of Your Seriously Delinquent Federal Tax Debt to the Department of State/Passport",
                                        "",
                                    ]
                                },
                                {
                                    "values": [
                                        "Whistleblower",
                                        "Notice of Determination Under Section 7623 Concerning Whistleblower Action/Whistleblower",
                                        "",
                                    ]
                                },
                            ],
                        },
                    },
                    {
                        "type": "h2",
                        "value": "If you file as a small tax case procedure, you'll have:",
                    },
                    {
                        "type": "card",
                        "value": [
                            {
                                "icon": IconCategories.CHECK,
                                "title": "More trial location options",
                                "description": "Small tax case trials are held in 15 more locations than regular cases.",
                                "color": "green",
                            },
                            {
                                "icon": IconCategories.CHECK,
                                "title": "Less formal procedures",
                                "description": "Small case pre-trial and trial procedures are less formal than regular cases.",
                                "color": "green",
                            },
                            {
                                "icon": IconCategories.CHECK,
                                "title": "Relaxed evidence rules",
                                "description": "Judges can consider any evidence that's relevant.",
                                "color": "green",
                            },
                            {
                                "icon": IconCategories.EXCLAMATION_MARK,
                                "title": "No appeals process",
                                "description": "If you lose your case or lose some issues in your case, you can't appeal the decision.",
                                "color": "yellow",
                            },
                        ],
                    },
                    {
                        "type": "paragraph",
                        "value": "<b>Do I have to choose small tax case procedure if I qualify?</b>",
                    },
                    {
                        "type": "paragraph",
                        "value": "No. You may choose to have your case conducted under regular tax case procedures.",
                    },
                    {
                        "type": "paragraph",
                        "value": "<b>If I don't choose small tax case procedure now, may I choose it later?</b>",
                    },
                    {
                        "type": "paragraph",
                        "value": "Yes. If your case qualifies, you may request to change it to a small tax case procedure anytime before trial. After your trial begins, you may not be able to change the case procedure.",
                    },
                    {
                        "type": "paragraph",
                        "value": "<b>If I choose small tax case procedure now, may I change it to regular tax case procedure later?</b>",
                    },
                    {
                        "type": "paragraph",
                        "value": "Yes. You may request a case procedure change before the trial of your case begins. The Tax Court has 15 more trial locations for small cases than for regular cases so a new trial location may need to be selected if your case changes from small to regular.",
                    },
                ],
                show_in_menus=False,
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
