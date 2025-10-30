from home.management.commands.pages.page_initializer import PageInitializer
from home.models import Footer
import logging

from home.models.utils.execute_script import ExecuteScript
from django.db import DatabaseError
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class FooterInitializer(PageInitializer):
    def create(self):
        settings = Footer.objects.all().first()

        if settings:
            logger.info("- Footer settings already exists.")
            return

        if not settings:
            Footer.objects.create(
                technicalQuestions=(
                    "For assistance with DAWSON, the Court's Electronic Filing and Case Management System, "
                    "refer to the "
                    '<a href="/dawson">DAWSON</a> page or email '
                    '<a href="mailto:dawson.support@ustaxcourt.gov?subject=Assistance%20for%20Dawson"> dawson.support@ustaxcourt.gov</a>.<br>'
                    '<span class="spacing-fix"></span>'
                    "Be sure to include your case docket number in your email. For all other questions contact the Office of the Clerk of Court at "
                    '(<a style="text-decoration: underline;" href="tel:+2025210700">202) 521-0700</a>.'
                ),
            )
            logger.info("Successfully created Footer settings.")

    def update(self):
        logger.info("Footer update called.")
        settings = Footer.objects.all().first()

        if settings:
            logger.info("- Footer settings already exists. Updating.")
        else:
            logger.warning("- Can't find Footer settings. STOPPING.")
            return

        footer = Footer.objects.first()
        footer.technicalQuestions = (
            "For assistance with DAWSON, the Court's Electronic Filing and Case Management System, "
            "refer to the "
            '<a href="/dawson">DAWSON</a> page or email '
            '<a href="mailto:dawson.support@ustaxcourt.gov?subject=Assistance%20for%20Dawson"> dawson.support@ustaxcourt.gov</a>.<br>'
            '<span class="spacing-fix"></span>'
            "Be sure to include your case docket number in your email. For all other questions contact the Office of the Clerk of Court at "
            '(<a style="text-decoration: underline;" href="tel:+2025210700">202) 521-0700</a>.'
        )
        footer.save()
        logger.info("Successfully updated Footer settings.")

    def run(self):
        """Update the footer as an execution script"""
        command_name = "Footer update for homepage redesign"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.update()
            execution_log_text = "Footer updated for homepage redesign"
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = execution_log_text
            script_entry.save()

        except Footer.DoesNotExist:
            error_msg = "Footer settings not found in database. Cannot update non-existent footer."
            logger.error(error_msg)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {error_msg}"
            script_entry.save()
            raise

        except DatabaseError as e:
            error_msg = f"Database error occurred while updating footer: {str(e)}"
            logger.error(error_msg)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Database Error:</strong> {error_msg}"
            script_entry.save()
            raise

        except ValidationError as e:
            error_msg = f"Validation error occurred while saving footer: {str(e)}"
            logger.error(error_msg)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = (
                f"<strong>Validation Error:</strong> {error_msg}"
            )
            script_entry.save()
            raise

        except Exception as e:
            error_msg = (
                f"Unexpected error during footer update: {type(e).__name__} - {str(e)}"
            )
            logger.error(error_msg)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = (
                f"<strong>Unexpected Error:</strong> {error_msg}"
            )
            script_entry.save()
            raise
