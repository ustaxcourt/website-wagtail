from django.core.management.base import BaseCommand
from home.management.commands.pages.case_related_forms_page import (
    CaseRelatedFormPageInitializer,
)
from home.management.commands.pages.dawson_page import DawsonPageInitializer
from home.management.commands.pages.dawson_search_page import (
    DawsonSearchPageInitializer,
)

pages_to_initialize = [
    DawsonSearchPageInitializer,
    DawsonPageInitializer,
    CaseRelatedFormPageInitializer,
]


class Command(BaseCommand):
    help = "Create initial pages and form records if they don't already exist."

    def handle(self, *args, **options):
        for page_class in pages_to_initialize:
            page_instance = page_class(self.stdout)
            page_instance.create()

        self.stdout.write(self.style.SUCCESS("All pages have been initialized."))
