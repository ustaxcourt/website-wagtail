from wagtail.models import Page
from home.models import JudgesRecruiting, JudgeProfile
from home.management.commands.pages.page_initializer import PageInitializer


class JudgesRecruitingPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        # Find the Employment page instead of home page
        try:
            employment_page = Page.objects.get(slug="employment")
        except Page.DoesNotExist:
            self.logger.write(
                "Error: Employment page does not exist. Please create it first."
            )
            return

        slug = "judges-recruiting"
        title = "Judges Currently Recruiting"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        # Add as child of employment_page instead of home_page
        employment_page.add_child(
            instance=JudgesRecruiting(
                title=title,
                judges_recruiting=[
                    {
                        "type": "message",
                        "value": "No judges are currently recruiting. <p>Questions concerning the application process may be directed to the Court's Office of Human Resources at <a href='tel:2025214700' title='Call (202) 521-4700'>(202) 521-4700</a>.</p>",
                    },
                    {
                        "type": "judge",
                        "value": [
                            {
                                "judge_name": JudgeProfile.objects.get(
                                    first_name="Richard", last_name="Morrison"
                                ).id,
                                "description": """<p>
          Applicants should have an interest in taxation and possess strong academic credentials,
          superior research and writing skills, and excellent communication skills. Applications
          should include a cover letter, resume, unofficial undergraduate and law school transcripts,
          at least one writing sample (10-15 pages), and a list of references or letters of recommendation.
          Please submit your application materials to <a href="mailto:Morrison-LCApps@ustaxcourt.gov" title="Email: Morrison-LCApps@ustaxcourt.gov">Morrison-LCApps@ustaxcourt.gov</a>.
        </p>
        <p>
          In lieu of applicants uploading letters of recommendation, recommenders may e-mail their
          letter of recommendation to <a href="mailto:Morrison-LCApps@ustaxcourt.gov" title="Email: Morrison-LCApps@ustaxcourt.gov">Morrison-LCApps@ustaxcourt.gov</a>.
        </p>
        <p>
        <strong>Employment to begin:</strong> Fall 2025<br/>
        <strong>Commitment:</strong> Two Years
        </p>""",
                                "apply_to_email": "Morrison-LCApps@ustaxcourt.gov",
                                "display_from": "2024-10-01",
                                "display_to": "2024-12-31",
                            },
                        ],
                    },
                    {
                        "type": "judge",
                        "value": [
                            {
                                "judge_name": JudgeProfile.objects.get(
                                    first_name="Kashi", last_name="Way"
                                ).id,
                                "description": """<p>
          Judge Way intends to select one Fall 2024 Law Clerk for a one-year term and one Fall 2024 Law
          Clerk for a two-year term. Candidates must indicate in their emails whether they are interested
          in a one- or two-year term. Candidates may indicate interest in both term lengths. Judge Way
          reserves the right to limit any candidate to a renewable one-year term.
        </p>
        <p>
          Applicants should have an interest in taxation and possess strong academic credentials,
          superior research and writing skills, and excellent communication skills. Applications
          should include a cover letter, resume, unofficial law school transcript, at least one
          writing sample (5-10 pages), and a list of references or letters of recommendation.
        </p>
        <p>
        <strong>Employment to begin:</strong> Fall 2024<br/>
        <strong>Commitment:</strong> One or Two Years
        </p>""",
                                "apply_to_email": "Way-LCApps@ustaxcourt.gov",
                                "display_from": "2024-10-01",
                                "display_to": "2024-12-31",
                            },
                        ],
                    },
                ],
                slug=slug,
                seo_title=title,
                search_description=f"{title} Announcements for the United States Tax Court",
            )
        )

        self.logger.write(f"Successfully created the '{title}' page.")
