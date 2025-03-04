from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage


class FillInFormsInstructionsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "forms_instructions"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            self.logger.write("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Fill-in Forms Instructions"

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
                        "value": """Tax Court forms can be filled-in and saved/printed directly from Adobe Reader 3.0 (or later). However, the information entered on a form cannot be saved to your device unless you are using the full Adobe Acrobat software suite.""",
                    },
                    {
                        "type": "paragraph",
                        "value": """Clicking on a form link will launch the Adobe Reader plug-in and display the form within your browser window. From the browser window, be sure to save the form to a location on your device.""",
                    },
                    {
                        "type": "h4",
                        "value": """Filling-in the Form:""",
                    },
                    {
                        "type": "paragraph",
                        "value": """
                        <ul>
                            <li>Launch Adobe Reader and open the form that you previously saved to your device.</li>
                            <li>Move the mouse pointer or click to select a blank field (e.g. Petitioner(s) name) on the form. The cursor will turn into a vertical beam, indicating that the field is editable.</li>
                            <li>Begin typing in the form field.</li>
                            <li>Repeat until all required form fields are completed.</li>
                            <li>When you have completed the form, click once on a blank area of the form to de-select the last active field. If a field is left active, the information it contains will not print.</li>
                            <li>Save the completed form to your device.</li>
                            <li>If you wish to print the form, click the print icon on the Acrobat toolbar.</li>
                        </ul>""",
                    },
                ],
            )
        )
        self.logger.write(f"Successfully created the '{title}' page.")
        new_page.save()
