# """Tests for home/management/commands/create_litc_cities_page.py"""

# import pytest
# from io import StringIO
# from unittest.mock import MagicMock, patch, call
# from home.management.commands.create_litc_cities_page import Command
# from home.management.commands.pages.efiling_and_case_maintenance import (
#     LITCPageInitializer,
# )
# from wagtail.models import Locale, Page, Collection
# from home.models.utils.execute_script import ExecuteScript


# @pytest.fixture
# def root_page(db):
#     Locale.objects.get_or_create(language_code="en")
#     Collection.add_root(name="Root")
#     return Page.add_root(title="Home", slug="home")


# @pytest.mark.django_db
# class TestCreatePage:
#     def _make_cmd(self):
#         cmd = Command.__new__(Command)
#         cmd.stdout = StringIO()
#         cmd.style = MagicMock()
#         cmd.style.SUCCESS = lambda s: s
#         cmd.style.WARNING = lambda s: s
#         return cmd

#     def _was_page_created(self):
#         page = None
#         try:
#             page = Page.objects.get(slug="clinics-and-pro-bono-programs")
#         except Page.DoesNotExist:
#             page = None

#         return page is not None

#     def test_page_creation_with_root_page_existing_creates_page(self, root_page):
#         with patch(
#             "home.management.commands.pages.efiling_and_case_maintenance.LITC_page.logger"
#         ) as mock_logger:
#             cmd = self._make_cmd()
#             cmd.handle()

#         assert self._was_page_created()
#         assert mock_logger.info.call_count == 2
#         assert mock_logger.info.call_args_list == [
#             call("Creating the 'Clinics and Pro Bono Programs' page."),
#             call("'Clinics and Pro Bono Programs' page created and published."),
#         ]

#     def test_page_creation_without_root_page_existing_raises_exception(self):
#         cmd = self._make_cmd()
#         with pytest.raises(Page.DoesNotExist) as excinfo:
#             cmd.handle()

#         assert str(excinfo.value) == "Page matching query does not exist."
#         assert not self._was_page_created()

#     def test_page_creation_twice_with_root_page_existing_creates_page(self, root_page):
#         with patch(
#             "home.management.commands.pages.efiling_and_case_maintenance.LITC_page.logger"
#         ) as mock_logger:
#             cmd = self._make_cmd()
#             cmd.handle()
#             cmd.handle()

#         assert self._was_page_created()
#         assert mock_logger.info.call_count == 3
#         assert mock_logger.info.call_args_list == [
#             call("Creating the 'Clinics and Pro Bono Programs' page."),
#             call("'Clinics and Pro Bono Programs' page created and published."),
#             call("- Clinics and Pro Bono Programs page already exists."),
#         ]

#     def test_initializer_run_once_creates_page(self, root_page):
#         with patch(
#             "home.management.commands.pages.efiling_and_case_maintenance.LITC_page.logger"
#         ) as mock_logger:
#             initializer = LITCPageInitializer()
#             initializer.run()

#         assert self._was_page_created()
#         assert mock_logger.info.call_count == 2
#         assert mock_logger.info.call_args_list == [
#             call("Creating the 'Clinics and Pro Bono Programs' page."),
#             call("'Clinics and Pro Bono Programs' page created and published."),
#         ]

#     def test_initializer_run_twice_creates_page_does_not_update_page(self, root_page):
#         with patch(
#             "home.management.commands.pages.efiling_and_case_maintenance.LITC_page.logger"
#         ) as mock_logger:
#             initializer = LITCPageInitializer()
#             initializer.run()
#             initializer.run()

#         assert self._was_page_created()
#         assert mock_logger.info.call_count == 3
#         assert mock_logger.info.call_args_list == [
#             call("Creating the 'Clinics and Pro Bono Programs' page."),
#             call("'Clinics and Pro Bono Programs' page created and published."),
#             call(
#                 "Script 'Create Clinics and Pro Bono Programs page' already ran. Update not necessary."
#             ),
#         ]

#     def test_initializer_run_then_update_creates_page_does_not_update_page(
#         self, root_page
#     ):
#         with patch(
#             "home.management.commands.pages.efiling_and_case_maintenance.LITC_page.logger"
#         ) as mock_logger:
#             initializer = LITCPageInitializer()
#             initializer.run()
#             initializer.update()

#         script = None
#         try:
#             script = ExecuteScript.objects.first()
#         except ExecuteScript.DoesNotExist:
#             script = None

#         assert script is not None
#         assert script.execution_status == "SUCCESS"
#         assert script.execution_log == "LITC Cities page created successfully."

#         assert self._was_page_created()
#         assert mock_logger.info.call_count == 3
#         assert mock_logger.info.call_args_list == [
#             call("Creating the 'Clinics and Pro Bono Programs' page."),
#             call("'Clinics and Pro Bono Programs' page created and published."),
#             call("- Clinics and Pro Bono Programs page already exists, skipping."),
#         ]

#     def test_initializer_run_once_error_during_executions_raises_exception(
#         self, root_page
#     ):
#         with (
#             patch(
#                 "home.management.commands.pages.efiling_and_case_maintenance.LITC_page.logger"
#             ) as mock_logger,
#             patch(
#                 "home.management.commands.pages.efiling_and_case_maintenance.LITCPageInitializer.update",
#                 side_effect=RuntimeError("Test Error"),
#             ),
#         ):
#             initializer = LITCPageInitializer()
#             with pytest.raises(RuntimeError) as excinfo:
#                 initializer.run()

#                 assert str(excinfo.value) == "RuntimeError: Test Error"

#         script = None
#         try:
#             script = ExecuteScript.objects.first()
#         except ExecuteScript.DoesNotExist:
#             script = None

#         assert script is not None
#         assert script.execution_status == "FAILURE"
#         assert (
#             script.execution_log
#             == "<strong>Error:</strong> Unexpected error during LITC Cities page creation: RuntimeError - Test Error"
#         )

#         assert not self._was_page_created()
#         assert mock_logger.error.call_count == 1
#         assert mock_logger.error.call_args_list == [
#             call(
#                 "Unexpected error during LITC Cities page creation: RuntimeError - Test Error"
#             )
#         ]
