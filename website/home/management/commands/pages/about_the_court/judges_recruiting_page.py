from wagtail.models import Page
from home.models import JudgesRecruiting
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
                                "judge_name": "Judge John Doe",
                                "description": "Currently recruiting for the position of Judge.",
                                "apply_to_email": "(202) 555-0123",
                                "display_from": "2024-10-01",
                                "display_to": "2025-12-31",
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
