from wagtail.models import Page
from home.models import InternshipPrograms  # Ensure this is correctly imported
from home.management.commands.pages.page_initializer import PageInitializer
from datetime import datetime


class InternshipProgramsPageInitializer(PageInitializer):
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

        slug = "internship-programs"
        title = "Internship Programs"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        # Add as child of employment_page instead of home_page
        employment_page.add_child(
            instance=InternshipPrograms(
                title=title,
                internship_programs=[
                    {
                        "type": "internship",
                        "value": {
                            "section": [
                                {
                                    "type": "h2",
                                    "value": "Summer Internship Program",
                                },
                                {
                                    "type": "paragraph",
                                    "value": "The Summer Internship Program provides significant exposure to the inner workings of the U.S. Tax Court. Information Technology interns will provide one-on-one customer service to Judges and Court staff in a professional setting within the Court’s headquarters in Washington, D.C.",
                                },
                            ],
                            "paragraph": """Starting salary is dependent upon education and availability of funds. Paid interns do not receive paid leave or other employee benefits.
                                  <br>
                                  <br>
                                  More than one position may be filled from this announcement.""",
                            "description": """2023 Information Technology Internship Program – Student Intern (Summer)
                                                <br> GS-01/08 to GS-02/10""",
                            "display_from": datetime(2023, 1, 1).date(),
                            "closing_date": datetime(2024, 12, 31).date(),
                            "external_link": None,
                        },
                    },
                    {
                        "type": "internship",
                        "value": {
                            "section": [
                                {
                                    "type": "h2",
                                    "value": "Diversity in Government Internship Program",
                                },
                                {
                                    "type": "paragraph",
                                    "value": """The United States Tax Court Diversity in Government Internship Program (DiG Tax) will be virtual this summer and provide significant exposure to the inner workings of the U.S. Tax Court, a federal court located in Washington, D.C. DiG Tax interns will observe judges and lawyers; attend virtual trials, meetings, and presentations; and assist on projects with departments throughout the Court, including Case Services, Facilities, Finance, Human Resources, Library, Information Technology, and Public Affairs.
                                            <br>
                                            Prospective DiG Tax interns should demonstrate academic achievement; exhibit qualities such as strong character and self-sufficiency under challenging circumstances; and be self-directed and able to work with limited supervision.
                                            <br>
                                            <br>
                                            Additionally, applicants must:
                                            <ol>
                                            <li>Be a U.S. citizen or national;</li>
                                            <li>Be currently enrolled in an undergraduate or graduate program at an accredited U.S. institution of higher education recognized by the U.S. Department of Education (visit <a href="https://www.ed.gov/accreditation" title="https://www.ed.gov/accreditation">https://www.ed.gov/accreditation</a> to verify your school and/or program of study);</li>
                                            <li>Have and maintain a 3.0 GPA or better;</li>
                                            <li>Have an interest in working with the federal government; and</li>
                                            <li>Be able to work 40 hours per week during the summer internship.</li>
                                            </ol>
                                            To apply, send a cover letter and a resume along with a copy of your most recent undergraduate or graduate transcript to <a href="mailto:DiGTax@ustaxcourt.gov">DiGTax@ustaxcourt.gov</a> with “DiG Tax” in the subject line.
                                            <br>
                                            <br>
                                            The DiG Tax program provides significant exposure to the inner workings of the U.S. Tax Court. DiG Tax interns may assist on projects with departments throughout the Court, including Case Services, Facilities, Finance, Human Resources, Library, Information Technology, and Public Affairs.
                                            """,
                                },
                            ],
                            "paragraph": """Starting salary is dependent upon education and availability of funds. Paid interns do not receive paid leave or other employee benefits.
                                                                             <br>
                                                                             <br>
                                                                             More than one position may be filled from this announcement.""",
                            "description": """2022 Diversity in Government Internship Program – Student Intern (Summer)
                                                <br> GS-01/08 to GS-02/10""",
                            "display_from": datetime(2022, 5, 26).date(),
                            "closing_date": datetime(2024, 5, 26).date(),
                            "external_link": None,
                        },
                    },
                ],
                slug=slug,
                seo_title=title,
                search_description=f"{title} Announcements for the United States Tax Court",
            )
        )

        self.logger.write(f"Successfully created the '{title}' page.")
