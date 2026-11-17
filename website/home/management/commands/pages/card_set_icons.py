import logging

from home.management.commands.pages.page_initializer import PageInitializer
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)


class CardSetIconsInitializer(PageInitializer):
    """Seeds icon SVGs used as Card Set button icons (WAG-1338) so editors
    have them available in the document chooser without a manual upload."""

    def __init__(self):
        super().__init__()

    def create(self):
        self.load_document_from_documents_dir(
            subdirectory=None,
            filename="download_icon.svg",
            title="Download",
        )

    def run(self):
        """Seed Card Set icon documents as an execution script"""
        command_name = "Card Set icon documents for Petitioner Experience redesign"
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.create()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = (
                "Card Set icon documents created for Petitioner Experience redesign"
            )
            script_entry.save()
        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
