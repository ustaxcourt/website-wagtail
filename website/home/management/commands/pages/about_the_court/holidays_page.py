from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage


class HolidaysPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "holidays"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            self.logger.write("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Legal Holidays"

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
                        "type": "paragraph",
                        "value": """
                        <ul>
                            <li>New Year's Day--January 1</li>
                            <li>Birthday of Martin Luther King, Jr.--Third Monday in January</li>
                            <li>Inauguration Day--Every fourth year</li>
                            <li>President's Day--Third Monday in February</li>
                            <li>Emancipation Day in Washington D.C.--April 16*</li>
                            <li>Memorial Day--Last Monday in May</li>
                            <li>Juneteenth National Independence Day--June 19</li>
                            <li>Independence Day--July 4</li>
                            <li>Labor Day--First Monday in September</li>
                            <li>Columbus Day--Second Monday in October</li>
                            <li>Veterans Day--November 11</li>
                            <li>Thanksgiving Day--Fourth Thursday in November</li>
                            <li>Christmas Day--December 25</li>
                        </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": '*Although the Tax Court is open on this day, it is a legal holiday for the purpose of computing time. <strong><a href="/media/documents/Rule-25.pdf" target="_blank" title="Rule 25" >See Rule 25</a></strong>.',
                    },
                ],
            )
        )
        self.logger.write(f"Successfully created the '{title}' page.")
        new_page.save()
