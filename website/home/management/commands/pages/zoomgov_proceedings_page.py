from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import (
    ZoomProceedingsDetailPage,
    NavigationRibbon,
    IconCategories,
    NavigationCategories,
)
from home.management.commands.snippets.navigation_ribbon import ribbon_snippet_name


class ZoomGovProceedingPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "zoomgov_proceedings"
        title = "ZoomGov Proceedings"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        content_type = ContentType.objects.get_for_model(ZoomProceedingsDetailPage)

        navigation_ribbon = NavigationRibbon.objects.filter(
            name=ribbon_snippet_name
        ).first()

        new_page = home_page.add_child(
            instance=ZoomProceedingsDetailPage(
                title=title,
                body="Detailed information about Zoom proceedings.",
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Details on Zoom proceedings for remote court sessions.",
                content_type=content_type,
                show_in_menus=True,
                additional_info="Additional information regarding Zoom proceedings.",
            )
        )

        new_page.body = [
            {"type": "heading", "value": "Introduction"},
            {"type": "hr", "value": True},
            {
                "type": "links",
                "value": {
                    "links": [
                        {
                            "title": "What should I do the day of my Zoomgov proceeding?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "Who can be in the Zoomgov courtroom during a proceeding?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "What happens when I join the proceeding?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "Do I have to be on video?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "Will my telephone number be visible if I call in?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "Does the Court have any tips for participating in a Zoomgov proceeding?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "What if I get disconnected?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "Can I record the Zoomgov proceeding?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "What if I want to speak with my representative (or client) privately?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "What is a breakout room?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "Will the Court allow low-income taxpayer clinics and calendar call programs to participate in Zoomgov proceedings?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                        {
                            "title": "How do I connect to a Zoomgov proceeding if I am a member of the general public or the press?",
                            "icon": IconCategories.INFO_CIRCLE_FILLED,
                            "document": None,
                            "url": "",
                        },
                    ],
                },
            },
        ]

        ZoomProceedingsDetailPage.objects.filter(id=new_page.id).update(
            menu_item_name="ZoomGov PROCEEDINGS",
            navigation_category=NavigationCategories.RULES_AND_GUIDANCE,
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
