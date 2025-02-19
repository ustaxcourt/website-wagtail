from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import (
    NavigationRibbon,
    NavigationCategories,
    EnhancedStandardPage,
)
from home.management.commands.snippets.navigation_ribbon import ribbon_snippet_name


class GettingReadyPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "zoomgov_getting_ready"
        title = "Zoomgov Proceedings"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name=ribbon_snippet_name
        ).first()

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Getting Ready",
                body=[{}],
                show_in_menus=True,
            )
        )

        EnhancedStandardPage.objects.filter(id=new_page.id).update(
            menu_item_name="GUIDANCE FOR PETITIONERS",
            navigation_category=NavigationCategories.RULES_AND_GUIDANCE,
        )
