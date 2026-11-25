# Most code coverage for the /history page is handled in test_about_the_court_pages.py.
# This handles code coverage of cases specific to that page.

from django.test import TestCase
from tests.home.management.commands.base_page_initializer_test import (
    BasePageInitializerTestCase,
)
from wagtail.models import Page
from unittest.mock import patch

from home.management.commands.pages.about_the_court.history_page import (
    HistoryPageInitializer,
)


class TestHistoryPage(TestCase):
    def setUp(self):
        BasePageInitializerTestCase().setUp()

    def test_create_fails_to_create_page_when_history_image_does_not_exist(self):
        initializer = HistoryPageInitializer
        slug = "history"
        with (
            patch(
                "home.management.commands.pages.page_initializer.PageInitializer.load_image_from_images_dir",
                return_value=None,
            ),
        ):
            self.assertFalse(Page.objects.filter(slug=slug).exists())
            initializer().create()
            self.assertFalse(Page.objects.filter(slug=slug).exists())
