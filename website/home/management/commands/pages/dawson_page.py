from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.models import DawsonPage
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationCategories


class DawsonPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson"
        title = "DAWSON"

        body_content = (
            "DAWSON (Docket Access Within a Secure Online Network) is the U.S. Tax Court's electronic filing and "
            'case management system. See the <a href="https://ustaxcourt.gov/dawson_user_guides.html">user guides</a> '
            "for more information and instructions.<br/><br/> Technical questions about DAWSON? Please contact "
            '<a href="mailto:dawson.support@ustaxcourt.gov">dawson.support@ustaxcourt.gov</a>. No documents can be '
            "filed with the Court at this email address. Any documents received via email will NOT be filed in your case."
        )

        content_type = ContentType.objects.get_for_model(DawsonPage)

        page_fields = {
            "title": title,
            "body": body_content,
            "slug": slug,
            "seo_title": title,
            "search_description": "Dawson",
            "content_type": content_type,
            "show_in_menus": True,
            "menu_item_name": "DAWSON (eFILING SYSTEM)",
            "navigation_category": NavigationCategories.eFILING_AND_CASE_MAINTENANCE,
        }

        # Check if a DawsonPage with the given slug already exists
        existing_page = DawsonPage.objects.filter(slug=slug).first()

        if existing_page:
            # Update scenario
            self.logger.write(f"- {title} page already exists. Updating content.")

            for field_name, field_value in page_fields.items():
                setattr(existing_page, field_name, field_value)

            # If your site uses Wagtail’s draft/publish workflow, use:
            # existing_page.save_revision().publish()
            # Otherwise, plain save() might be enough:
            existing_page.save()

            self.logger.write(f"Successfully updated the '{title}' page.")

        else:
            # Create scenario
            self.logger.write(f"Creating the '{title}' page.")
            new_page = DawsonPage(**page_fields)

            # Add the new page under home_page
            home_page.add_child(instance=new_page)

            self.logger.write(f"Successfully created the '{title}' page.")
