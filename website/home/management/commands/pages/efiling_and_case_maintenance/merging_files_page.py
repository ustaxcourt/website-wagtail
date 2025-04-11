from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer


merging_files_images = [
    {
        "title": "Combine Files Dropdown",
        "filename": "combine-files.jpg",
    },
    {
        "title": "Add Files",
        "filename": "add-files.jpg",
    },
    {
        "title": "Select Files",
        "filename": "select-files.jpg",
    },
    {
        "title": "Order Files",
        "filename": "order-files.jpg",
    },
    {
        "title": "Combine All Files",
        "filename": "combine-all-files.jpg",
    },
    {
        "title": "Final Files",
        "filename": "final-files.jpg",
    },
]


class MergingFilesPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "merging-files"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "How to Merge Files into One PDF"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        uploaded_images = {}

        for image in merging_files_images:
            image_uploaded = self.load_image_from_images_dir(
                "dawson", image["filename"], image["title"]
            )

            if image_uploaded:
                uploaded_images[image["filename"]] = {
                    "id": image_uploaded.id,
                    "url": image_uploaded.file.url,
                }

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                body=[
                    {
                        "type": "paragraph",
                        "value": "These instructions apply only to Adobe Acrobat Professional and Standard. A user utilizing other software to create PDFs must follow the software vendor's instructions for creating a single PDF from multiple PDFs.",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h2",
                        "value": "Merging Two or More PDF Documents",
                    },
                    {
                        "type": "paragraph",
                        "value": "To merge two or more PDF documents:",
                    },
                    {
                        "type": "list",
                        "value": {
                            "list_type": "ordered",
                            "items": [
                                {
                                    "text": "With Adobe Acrobat open, click on the Create menu.",
                                },
                                {
                                    "text": 'Select the menu item "Combine Files into a Single PDF ... "',
                                    "image": uploaded_images["combine-files.jpg"]["id"],
                                },
                                {
                                    "text": 'A new window will open. Click on the "Add Files ... " menu.',
                                },
                                {
                                    "text": 'Select the "Add Files ... " option from the drop-down menu.',
                                    "image": uploaded_images["add-files.jpg"]["id"],
                                },
                                {
                                    "text": "Select each file to be combined by clicking on the file name in the Add Files dialog box. Holding down the Shift or Ctrl key when clicking on a file name permits a user to add more than one file at a time.",
                                },
                                {
                                    "text": "When finished selecting file names, click Open at the bottom of the dialog box.",
                                    "image": uploaded_images["select-files.jpg"]["id"],
                                },
                                {
                                    "text": "The selected files now appear in the Combine Files window in Adobe Acrobat. The files may be viewed as thumbnails or in a list (as shown below) by selecting the view type at the top right of the window.",
                                },
                                {
                                    "text": "To change the order in which the files appear in the merged combined document, highlight the name of the file to appear first, then click the up arrow at the bottom left of the window to move that file to the top of the list.",
                                    "image": uploaded_images["order-files.jpg"]["id"],
                                },
                                {
                                    "text": "Once you are satisfied with the order of your documents, click on Combine Files button.",
                                    "image": uploaded_images["combine-all-files.jpg"][
                                        "id"
                                    ],
                                },
                                {
                                    "text": "The files you selected in the previous step will be combined into one document.",
                                    "image": uploaded_images["final-files.jpg"]["id"],
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h2",
                        "value": "Merging Two or More Documents in Multiple Formats",
                    },
                    {
                        "type": "paragraph",
                        "value": "If a user wishes to combine documents that currently exist in various formats into a single PDF, the easiest process is to print out all the documents and scan them into a single document from a scanner that creates PDFs.",
                    },
                    {"type": "hr", "value": True},
                ],
                search_description="Learn how to merge multiple PDF files into a single PDF document using Adobe Acrobat",
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Successfully created the '{title}' page.")
