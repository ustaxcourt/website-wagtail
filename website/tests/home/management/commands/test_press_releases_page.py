# Most code coverage for the /news-and-announcements page is handled in test_about_the_court_pages.py.
# This handles code coverage of cases specific to that page.

from django.test import TestCase
from tests.home.management.commands.base_page_initializer_test import (
    BasePageInitializerTestCase,
)
from wagtail.models import Page
from home.models.utils.execute_script import ExecuteScript
from unittest.mock import patch

from home.management.commands.pages.about_the_court.press_releases_page import (
    PressReleasesPageInitializer,
)
import pytest


class TestPressReleasesPage(TestCase):
    def setUp(self):
        BasePageInitializerTestCase().setUp()

    def test_create_fails_to_create_page_when_executescript_exists(self):
        initializer = PressReleasesPageInitializer
        slug = "/news-and-announcements"
        with (
            patch(
                "home.models.utils.execute_script.ExecuteScript.command_exists",
                return_value=True,
            ),
        ):
            self.assertFalse(Page.objects.filter(slug=slug).exists())
            initializer().create()
            self.assertFalse(Page.objects.filter(slug=slug).exists())

    def test_create_fails_to_seed_news_items_when_load_image_throws_exception(self):
        initializer = PressReleasesPageInitializer
        slug = "/news-and-announcements"
        with (
            patch(
                "home.management.commands.pages.page_initializer.PageInitializer.load_document_from_documents_dir",
                side_effect=Exception,
            ),
        ):
            self.assertFalse(Page.objects.filter(slug=slug).exists())
            with pytest.raises(Exception):
                initializer().create()
                self.assertTrue(
                    ExecuteScript.objects.filter(
                        command_name="Press release data migration to snippets - Press releases"
                    ).exists()
                )

                es = ExecuteScript.objects.get(
                    command_name="Press release data migration to snippets - Press releases"
                )
                self.assertEqual(es.execution_status, "FAILURE")
                self.assertContains(
                    es.execution_log, "Failed to seed press release NewsItems:"
                )
