from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer


class LawClerkProgramPageInitializer(PageInitializer):
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

        slug = "law-clerk-program"
        title = "Law Clerk Program"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        # Add as child of employment_page instead of home_page
        employment_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Vacancy Announcements for the United States Tax Court",
                body=[
                    {
                        "type": "paragraph",
                        "value": """It is the policy of U.S. Tax Court, as an equal opportunity employer, to attract and retain the best-qualified people available, without regard to race, gender, religion, national origin, age, or disability.
                                        <br/><br/>
                                        Law clerk positions are filled as vacancies occur, and many are filled by applicants who participate in the Court’s annual “Law Clerk Interview Day”, which occurs each Fall. A few weeks prior to Law Clerk Interview Day,
                                        the Court posts on its website the instructions for submitting applications to the Judges participating in this event. The Court also will notify law school career services offices about Law Clerk Interview Day. Candidates may submit application packets to one or more participating Judge.
                                        <br/><br/>
                                        <strong>Law Clerk Interview Days will be updated in April 2025.</strong><br/>
                                        Last held August-September 2024.
                                        <br/><br/>
                                        Law clerk vacancies also may occur throughout the year. Below is a list of Judges and Special Trial Judges currently recruiting for law clerks. Click each Judge's name to view their biography which may contain Additional Information or Requirements for Law Clerk Applicants. More information and specific application requirements are provided in the Application Procedure section below.""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": """<h2>Qualifications and Compensation</h2>
                                        Law clerks must be a law school graduate. While bar admission is not required at the time of appointment, law clerks must have passed the bar within 14 months of their appointment. In addition, not later than 24 months after their initial appointment, and thereafter during their service at the Tax Court, law clerks must be admitted to practice before the highest court of a state or the District of Columbia and in good standing.
                                        <br/><br/>
                                        The Judges of the United States Tax Court are primarily interested in the superior law school graduate who has completed Federal tax law courses and plans to practice in this specialized field. There is particular interest in a graduate who has worked on a law review and graduated in the upper one-third of his/her law school class. Some Judges, but not all, prefer candidates with an LL.M. degree in taxation or who have completed one year of professional experience in the Federal tax field.
                                        <br/><br/>
                                        Appointments typically begin at the Grade GS-11 level on the <strong><a href="https://www.opm.gov/policy-data-oversight/pay-leave/salaries-wages" title="Government Pay Scale">Government pay scale</a></strong>, but may be higher depending on the education level and professional experience of a candidate. Utilize the "General Schedule Salary Calculator" to determine the compensation for GS-11 in your locality.
                                        <br/><br/>
                                        The decision to make an offer, and the terms of the offer, are left to the discretion of each Judge.""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": """<h2>Security and Character Investigations</h2>
                                        All appointments are contingent upon satisfactory completion of a background, credit, and tax check.
                                       """,
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": """<h2>Insurance and Retirement Plans</h2>
                                        Benefits available to employees include health insurance and life insurance. Employees also participate in the benefits of the Government's Federal Employee's Retirement System, which includes the Thrift Savings Plan (TSP).
                                       """,
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": """<h2>Leave</h2>
                                        Law clerks without prior Government service are entitled to 13 days of annual leave and 13 days of sick leave for each year. Any leave balances remaining at the conclusion of the law clerk appointment are forfeited.                                       """,
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "heading",
                        "value": {
                            "text": "Application Procedure",
                            "id": "AP",
                            "level": "h2",
                        },
                    },
                    {
                        "type": "paragraph",
                        "value": """
                                        Please review the list of <strong><a href="/employment/judges-recruiting" title="Judges Currently Recruiting">Judges and Special Trial Judges currently recruiting</a></strong> for Law Clerks prior to submitting your application. Click each Judge's name to view Additional Information or Requirements for Law Clerk Applicants.
                                        <br/><br/>
                                        To apply, send a cover letter, a complete resume, and a copy of your law school transcript. A legal writing sample, preferably in the tax field, should also accompany the application materials. All documents should be submitted in PDF format.
                                        <br/><br/>
                                        Questions concerning the application process may be directed to the Court's Office of Human Resources at <a href="tel:+12025214700">(202) 521-4700</a>.""",
                    },
                ],
            )
        )

        self.logger.write(f"Successfully created the '{title}' page.")
