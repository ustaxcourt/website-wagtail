from django.core.management.base import BaseCommand
from wagtail.contrib.search_promotions.models import SearchPromotion, Query
from wagtail.models import Page


class Command(BaseCommand):
    help = "Update promoted search settings"

    def handle(self, *args, **kwargs):
        self.stdout.write("Updating promoted search settings...")
        query_string = "Taxpayer".lower()
        try:
            query = Query.objects.get(query_string=query_string)
        except Query.DoesNotExist:
            query = Query.objects.create(query_string=query_string)

        if query:
            page = Page.objects.get(slug="petitioners")
            SearchPromotion.objects.update_or_create(
                query=query,
                page=page,
                defaults={
                    "sort_order": 0,  # Lower numbers appear higher
                    "description": page.search_description,
                },
            )
            self.stdout.write(
                f"Created and configured new query: {query_string} with page: {page.title}"
            )
        else:
            self.stdout.write(f"Using existing query: {query_string}")
