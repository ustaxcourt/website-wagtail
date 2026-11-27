"""Sandbox-only data fix for the DAWSON guides already created there.

The guide initializers only fill empty pages, so guides created by an earlier
deploy keep their old content. This applies the review feedback to them once:
phases collapsed by default and the updated pay.gov link. It lives on the
sandbox branch only and is not part of any story branch.
"""

import logging
from html import escape

from wagtail.models import Page

from home.management.commands.pages.page_initializer import PageInitializer
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)

SLUGS = (
    "dawson-how-to-search-for-a-case",
    "dawson-how-to-search-for-an-order",
    "dawson-how-to-view-dashboard",
    "dawson-how-to-pay-filing-fee",
)
OLD_PAY_GOV_URL = "https://www.pay.gov/public/home"
NEW_PAY_GOV_URL = (
    "https://www.pay.gov/public/search/agencyforms?agencyFilters=United+States+Tax+Court"
    "&searchCategory=PAYMENT&searchType=AGENCYPAYMENT&agencyId=1392"
)


class SandboxDawsonGuidesFixup(PageInitializer):
    SCRIPT_NAME = "SANDBOX: Collapse DAWSON guide phases and update pay.gov link"

    def create(self):
        for slug in SLUGS:
            page = Page.objects.filter(slug=slug).first()
            if page is None or not isinstance(page.specific, PetitionerExperiencePage):
                logger.info(f"- {slug} not found; nothing to fix.")
                continue
            page = page.specific
            body = page.body.get_prep_value()
            for block in body:
                if block["type"] != "detailed_timeline":
                    continue
                value = block["value"]
                for phase in value["phases"]:
                    phase["value"]["default_to_open"] = False
                if value.get("introduction"):
                    value["introduction"] = value["introduction"].replace(
                        f'href="{OLD_PAY_GOV_URL}"',
                        f'href="{escape(NEW_PAY_GOV_URL)}"',
                    )
            page.body = body
            page.save_revision().publish()
            logger.info(f"- Updated {slug}.")

    def run(self):
        if ExecuteScript.command_exists(self.SCRIPT_NAME):
            return 0
        script_entry = ExecuteScript.create_script(self.SCRIPT_NAME)
        try:
            self.create()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = "Sandbox DAWSON guides updated."
            script_entry.save()
        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
