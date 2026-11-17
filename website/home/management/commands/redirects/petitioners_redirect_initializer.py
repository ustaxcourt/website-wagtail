from wagtail.models import Page
from wagtail.contrib.redirects.models import Redirect
from home.models.utils.execute_script import ExecuteScript
import logging

logger = logging.getLogger(__name__)


class PetitionersRedirectInitializer:
    def __init__(self):
        self.logger = logger

    def create_redirects_from_list(self, slug_list, config):
        errors = []
        successes = 0
        total = 0

        for from_link in slug_list:
            total += 1

            try:
                if Redirect.objects.filter(
                    old_path=from_link, site=config["site"]
                ).exists():
                    successes += 1
                    logger.info(
                        f"- Redirect from '{from_link}' for site '{config['site']}' already exists."
                    )
                    continue

                Redirect.objects.create(
                    old_path=from_link,
                    redirect_page_id=config["to_page_id"],
                    is_permanent=config["permanent"],
                    site=config["site"],
                )
                successes += 1
            except Exception as e:
                logger.error(
                    f"  -> ERROR: An unexpected error occurred when creating redirect '{from_link}' -> Page ID '{config['to_page_id']}': {e}"
                )
                errors.append(
                    f"  -> ERROR: An unexpected error occurred when creating redirect '{from_link}' -> Page ID '{config['to_page_id']}': {e}"
                )

        return {
            "errors": errors,
            "successes": successes,
            "total": total,
        }

    def create(self):
        """
        Create a redirect for the old petitioners pages if they don't already exist
        """

        slugs_to_redirect_from = [
            "/petitioners",
            "/petitioners-start",
            "/petitioners-before",
            "/petitioners-during",
            "/petitioners-after",
        ]
        url_path_to_redirect_to = "/home/petitioners-guidance/"
        page_to_redirect_to = Page.objects.get(url_path=url_path_to_redirect_to)
        if page_to_redirect_to:
            import_summary = self.create_redirects_from_list(
                slugs_to_redirect_from,
                {
                    "to_page_id": page_to_redirect_to.id,
                    "permanent": True,
                    "site": None,
                },
            )
            logger.info("--- Redirect import process complete ---")
            logger.info(
                f"Summary: {import_summary['successes']} redirects imported or already existed, {import_summary['total']} attempted."
            )
            for err in import_summary["errors"]:
                logger.info(f"  {err}")

            if len(import_summary["errors"]) > 0:
                raise Exception(
                    "One or more errors occurred creating redirects for petitioner experience pages. See above."
                )
        else:
            raise Exception(
                f"Unable to find page with url_path='{url_path_to_redirect_to}' to create redirects to."
            )

    def run(self):
        """Create petitioners experience redirects"""
        command_name = "WAG-1412: Create redirects to new petitioners experience pages"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.create()
            execution_log_text = (
                "Petitioners experience redirects created successfully."
            )
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = execution_log_text
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
