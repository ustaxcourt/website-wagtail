from django.test import TestCase
from taggit.models import Tag
from wagtail.models import Collection, Locale, Page, Site
from home.data.tag_and_collection_names import TAGS_AND_COLLECTION_NAMES
from home.data.role_tag_names import ROLE_TAGS_NAMES
import re


def create_slug(name):
    name = name.lower()
    name = re.sub(r"\s+", "-", name)
    return name


ADDITIONAL_TAGS = ["News and Announcements"]


class BasePageInitializerTestCase(TestCase):
    def setUp(self):
        Locale.objects.get_or_create(language_code="en")
        if not Collection.objects.exists():
            Collection.add_root(name="Root")

        if Collection.get_first_root_node() is None:
            Collection.add_root(name="Root")
        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        for tag_name in TAGS_AND_COLLECTION_NAMES + ROLE_TAGS_NAMES + ADDITIONAL_TAGS:
            slug = create_slug(tag_name)
            # Use the slug to check for existence, and provide the name as a default
            # for creation. This avoids the unique constraint error.
            Tag.objects.get_or_create(slug=slug, defaults={"name": tag_name})
