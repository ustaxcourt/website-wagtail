from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.models import DawsonPage
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationCategories


class DawsonEFilingPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson-efile"
        title = "Dawson"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        content_type = ContentType.objects.get_for_model(DawsonPage)

        new_page = home_page.add_child(
            instance=DawsonPage(
                title=title,
                body='DAWSON (Docket Access Within a Secure Online Network) is the U.S. Tax Court\'s electronic filing and case management system. See the <a href="https://ustaxcourt.gov/dawson_user_guides.html">user guides</a> for more information and instructions.<br/><br/> Technical questions about DAWSON? Please contact <a href="mailto:dawson.support@ustaxcourt.gov">dawson.support@ustaxcourt.gov</a>. No documents can be filed with the Court at this email address. Any documents received via email will NOT be filed in your case.',
                slug=slug,
                seo_title=title,
                search_description="Dawson",
                content_type=content_type,
                show_in_menus=True,
            )
        )

        DawsonPage.objects.filter(id=new_page.id).update(
            menu_item_name="DAWSON (eFILING SYSTEM)",
            navigation_category=NavigationCategories.eFILING_AND_CASE_MAINTENANCE,
        )

        self.logger.write(f"Successfully created the '{title}' page.")
