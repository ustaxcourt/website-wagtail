"""
Management command to test functions called by Wagtail Transfer when an image has a Tag.
This is for local testing only. Run with:
    python manage.py validate_tag_retrieval_wagtail_transfer
"""

from django.core.management.base import BaseCommand
from taggit.models import Tag


class Command(BaseCommand):
    help = "Test functions called by Wagtail Transfer when an image has a Tag."

    def add_arguments(self, parser):
        parser.add_argument(
            "--id",
            help="Id of tag to find",
        )

    def handle(self, *args, **options):
        if options["id"]:
            id = options["id"]
            fields = {
                "taggit.tag": [
                    "slug"
                ],  # sensible default for taggit; can still be overridden
                "wagtailcore.locale": ["language_code"],
                "contenttypes.contenttype": ["app_label", "model"],
            }
            print(
                f"Command return value: {Tag.objects.values_list(*fields['taggit.tag']).get(pk=id)}"
            )
        else:
            print("--id argument must be provided.")
