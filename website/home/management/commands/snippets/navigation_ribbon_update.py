from home.models import NavigationRibbon, NavigationRibbonLink, IconCategories
from home.models.utils.execute_script import ExecuteScript
import logging

logger = logging.getLogger(__name__)

ribbon_snippet_name = "Guidance for Petitioners Ribbon"


class NavigationRibbonUpdater:
    def __init__(self):
        self.logger = logger

    def update(self):
        if not NavigationRibbon.objects.filter(name=ribbon_snippet_name).exists():
            logger.info(
                "Guidance for Petitioners Navigation Ribbon does not exist. Cannot update."
            )
            return

        logger.info("Updating the Guidance for Petitioners Navigation Ribbon.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name=ribbon_snippet_name
        ).first()

        links = [
            {
                "title": "Guidance for Self-Represented Petitioners",
                "icon": IconCategories.SIGNPOST,
                "url": "/petitioners-guidance",
                "sort_order": 0,
            },
            {
                "title": "Process and Timeline",
                "icon": IconCategories.TIMELINE,
                "url": "/petitioners-timeline",
                "sort_order": 1,
            },
            {
                "title": "Prepare to File",
                "icon": IconCategories.NOTES,
                "url": "/petitioners-prepare-to-file",
                "sort_order": 2,
            },
            {
                "title": "Forms",
                "icon": IconCategories.FORMS,
                "url": "/petitioners-forms",
                "sort_order": 3,
            },
            {
                "title": "Help",
                "icon": IconCategories.HELP,
                "url": "/petitioners-help",
                "sort_order": 4,
            },
            {
                "title": "DAWSON LOG-IN",
                "icon": IconCategories.DAWSON,
                "url": "https://app.dawson.ustaxcourt.gov/login",
                "sort_order": 5,
            },
        ]

        old_links = NavigationRibbonLink.objects.filter(
            navigation_ribbon=navigation_ribbon
        )
        for old_link in old_links:
            old_link.delete()

        for link in links:
            link = NavigationRibbonLink(
                navigation_ribbon=navigation_ribbon,
                title=link["title"],
                icon=link["icon"],
                url=link["url"],
                sort_order=link["sort_order"],
            )
            link.save()

        self.model = navigation_ribbon

    def run(self):
        """Update the Guidance for Petitioners Navigation Ribbon as an execution script"""
        command_name = "Guidance for Petitioners Navigation Ribbon update for Petition Experience redesign"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.update()
            execution_log_text = "Guidance for Petitioners Navigation Ribbon updated for Petition Experience redesign"
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = execution_log_text
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
