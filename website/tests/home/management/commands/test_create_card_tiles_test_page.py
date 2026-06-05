"""Tests for home/management/commands/create_card_tiles_test_page.py"""

import pytest
from io import StringIO
from unittest.mock import MagicMock, patch, call
from home.management.commands.create_card_tiles_test_page import Command
from wagtail.models import Locale, Page, Collection


@pytest.fixture
def root_page(db):
    Locale.objects.get_or_create(language_code="en")
    Collection.add_root(name="Root")
    return Page.add_root(title="Home", slug="home")


@pytest.mark.django_db
class TestCreatePage:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda s: s
        cmd.style.WARNING = lambda s: s
        return cmd

    def _was_page_created(self):
        page = None
        try:
            page = Page.objects.get(slug="card-tiles-test")
        except Page.DoesNotExist:
            page = None

        return page is not None

    def test_page_deletion_when_not_exists_logs_message(self, root_page):
        with patch(
            "home.management.commands.pages.card_tiles_test_page.logger"
        ) as mock_logger:
            cmd = self._make_cmd()
            cmd.handle(delete=True)

        assert cmd.stdout.getvalue() == "Card Tiles test page deleted (if it existed)."
        mock_logger.info.assert_called_once()
        assert (
            "Test page with slug 'card-tiles-test' does not exist."
            in mock_logger.info.call_args[0][0]
        )

    def test_page_creation_with_root_page_existing_creates_page(self, root_page):
        with patch(
            "home.management.commands.pages.card_tiles_test_page.logger"
        ) as mock_logger:
            cmd = self._make_cmd()
            cmd.handle(delete=False)

        assert self._was_page_created()
        assert mock_logger.info.call_count == 2
        assert mock_logger.info.call_args_list == [
            call("Creating the 'Card Tiles Test Page' page."),
            call("Created the 'Card Tiles Test Page' page."),
        ]

    def test_page_creation_without_root_page_existing_logs_message(self):
        with patch(
            "home.management.commands.pages.card_tiles_test_page.logger"
        ) as mock_logger:
            cmd = self._make_cmd()
            cmd.handle(delete=False)

        assert not self._was_page_created()
        assert mock_logger.info.call_count == 1
        assert mock_logger.info.call_args_list == [
            call("Root page (home) does not exist.")
        ]

    def test_page_creation_twice_with_root_page_existing_creates_page(self, root_page):
        with patch(
            "home.management.commands.pages.card_tiles_test_page.logger"
        ) as mock_logger:
            cmd = self._make_cmd()
            cmd.handle(delete=False)
            cmd.handle(delete=False)

        assert self._was_page_created()
        assert mock_logger.info.call_count == 3
        assert mock_logger.info.call_args_list == [
            call("Creating the 'Card Tiles Test Page' page."),
            call("Created the 'Card Tiles Test Page' page."),
            call("- Card Tiles Test Page page already exists."),
        ]

    def test_page_creation_with_root_page_existing_then_deleting(self, root_page):
        with patch(
            "home.management.commands.pages.card_tiles_test_page.logger"
        ) as mock_logger:
            cmd = self._make_cmd()
            cmd.handle(delete=False)
            cmd.handle(delete=True)

        assert not self._was_page_created()
        assert mock_logger.info.call_count == 3
        assert mock_logger.info.call_args_list == [
            call("Creating the 'Card Tiles Test Page' page."),
            call("Created the 'Card Tiles Test Page' page."),
            call("Deleted test page with slug 'card-tiles-test'."),
        ]

    # def test_page_creation_with_root_page_existing_but_icon_missing_logs_error(
    #     self, root_page
    # ):
    #     with (
    #         patch(
    #             "home.management.commands.pages.card_tiles_test_page.logger"
    #         ) as mock_logger,
    #         patch(
    #             "home.management.commands.pages.card_tiles_test_page.CardTilesTestPageInitializer.get_svg_icons",
    #             return_value={"start": False},
    #         ),
    #     ):
    #         cmd = self._make_cmd()
    #         cmd.handle(delete=False)

    #     assert not self._was_page_created()
    #     assert mock_logger.info.call_count == 1
    #     assert mock_logger.info.call_args_list == [
    #         call("Creating the 'Card Tiles Test Page' page.")
    #     ]
    #     assert mock_logger.error.call_count == 1
    #     assert mock_logger.error.call_args_list == [
    #         call("Failed to load one or more SVG icons. Aborting page creation.")
    #     ]

    def test_add_argument_adds_delete_argument_to_parser(self):
        cmd = self._make_cmd()
        parser = cmd.create_parser("test", None)
        assert any(
            item.option_strings == ["--delete"]
            for item in parser._get_optional_actions()
        )
