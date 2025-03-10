from wagtail.models import Page
from home.models import VacancyAnnouncementsPage
from home.management.commands.pages.page_initializer import PageInitializer


class VacancyAnnouncementsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")

        slug = "vacancy_announcements"
        title = "Vacancy Announcements"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        home_page.add_child(
            instance=VacancyAnnouncementsPage(
                title=title,
                body="Current vacancy announcements for the United States Tax Court are listed below.",
                slug=slug,
                seo_title=title,
                search_description="Vacancy Announcements for the United States Tax Court",
                show_in_menus=True,
            )
        )

        self.logger.write(f"Successfully created the '{title}' page.")
