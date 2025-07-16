import os
import re
from wagtail.contrib.redirects.models import Redirect
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

STATIC_PDF_REDIRECTS = [
    {
        "old_path": "/files/documents/complete-rules-2005.pdf",
        "new_path": "/files/documents/complete-rules.pdf",
        "is_permanent": True,
    },
    {
        "old_path": "/files/documents/taxcourt-rules-v2.pdf",
        "new_path": "/files/documents/rules.pdf",
        "is_permanent": True,
    },
]


def get_rule_pdf_redirects():
    """
    Return static + dynamically inferred rule PDF redirects.
    Scan a directory for amended rule PDF filenames and generate redirect mappings.
    Redirects files like:
    /files/documents/Rule-1_Amended_20230315.pdf → /files/documents/rule-1.pdf
    """
    pdf_redirects = STATIC_PDF_REDIRECTS.copy()

    rule_pdf_pattern = re.compile(r"^(Rule-\d+)_Amended_\d{8}\.pdf$", re.IGNORECASE)
    RULES_DIR = os.getenv("RULE_PDF_SCAN_PATH", "home/management/documents")

    logger.info(f"Looking for rule PDFs in: {os.path.abspath(RULES_DIR)}")

    if os.path.exists(RULES_DIR):
        for filename in os.listdir(RULES_DIR):
            if filename.lower().endswith(".pdf"):
                match = rule_pdf_pattern.match(filename)
                if match:
                    base_rule = match.group(1).lower()
                    old_path = f"/files/documents/{filename}"
                    new_path = f"/files/documents/{base_rule}.pdf"
                    pdf_redirects.append(
                        {
                            "old_path": old_path,
                            "new_path": new_path,
                            "is_permanent": True,
                        }
                    )
    else:
        logger.warning(
            f"Rule PDF directory not found: {RULES_DIR}. Skipping rule PDF redirects."
        )

    return pdf_redirects


REDIRECTS = [
    {
        "old_path": "/vacancy_announcements",
        "new_path": "/employment/vacancy-announcements",
        "is_permanent": True,
    },
    {
        "old_path": "/vacancy_announcements.html",
        "new_path": "/employment/vacancy-announcements",
        "is_permanent": True,
    },
    {
        "old_path": "/judges_recruiting.html",
        "new_path": "/employment/judges-recruiting",
        "is_permanent": True,
    },
    {
        "old_path": "/taxpayers_before.html",
        "new_path": "/petitioners-before",
        "is_permanent": True,
    },
    {
        "old_path": "/internship_programs.html",
        "new_path": "/employment/internship-programs",
        "is_permanent": True,
    },
    {
        "old_path": "/law_clerk_program.html",
        "new_path": "/employment/law-clerk-program",
        "is_permanent": True,
    },
    {
        "old_path": "/index.html",
        "new_path": "/",
        "is_permanent": True,
    },
    {
        "old_path": "/press_release_archives.html",
        "new_path": "/press-releases/archives",
        "is_permanent": True,
    },
]

LEGACY_URLS = [
    "/administrative_orders.html",
    "/case_procedure.html",
    "/case_related_forms.html",
    "/citation_and_style_manual.html",
    "/clinics.html",
    "/clinics_academic.html",
    "/clinics_academic_non_law_school.html",
    "/clinics_calendar_call.html",
    "/clinics_chief_counsel.html",
    "/clinics_nonacademic.html",
    "/dashboard.html",
    "/dawson.html",
    "/dawson_account_petitioner.html",
    "/dawson_account_practitioner.html",
    "/dawson_faqs.html",
    "/dawson_faqs_account_management.html",
    "/dawson_faqs_basics.html",
    "/dawson_faqs_case_management.html",
    "/dawson_faqs_login.html",
    "/dawson_faqs_searches_public_access.html",
    "/dawson_faqs_training_and_support.html",
    "/dawson_tou.html",
    "/dawson_user_guides.html",
    "/definitions.html",
    "/directory.html",
    "/documents_eligible_for_efiling.html",
    "/dpt_cities.html",
    "/efile_a_petition.html",
    "/employment.html",
    "/fees_and_charges.html",
    "/find_a_case.html",
    "/find_an_opinion.html",
    "/find_an_order.html",
    "/forms_instructions.html",
    "/history.html",
    "/holidays.html",
    "/judges.html",
    "/jcdp.html",
    "/jcdp_orders_issued.html",
    "/merging_files.html",
    "/mission.html",
    "/notice_regarding_privacy.html",
    "/notices_of_rule_amendments.html",
    "/pamphlets.html",
    "/pay_filing_fee.html",
    "/petitioners.html",
    "/petitioners_about.html",
    "/petitioners_after.html",
    "/petitioners_before.html",
    "/petitioners_during.html",
    "/petitioners_glossary.html",
    "/petitioners_start.html",
    "/practitioners.html",
    "/press_releases.html",
    "/release_notes.html",
    "/remote_proceedings.html",
    "/reports_and_statistics.html",
    "/rules.html",
    "/rules_comments.html",
    "/transcripts_and_copies.html",
    "/trial_sessions.html",
    "/update_contact_information.html",
    "/zoomgov.html",
    "/zoomgov_getting_ready.html",
    "/zoomgov_the_basics.html",
    "/zoomgov_zoomgov_proceedings.html",
]

for old_path in LEGACY_URLS:
    if old_path.endswith(".html"):
        cleaned_path = old_path.replace(".html", "").replace("_", "-")
        new_path = cleaned_path + "/"
        REDIRECTS.append(
            {
                "old_path": old_path,
                "new_path": new_path,
                "is_permanent": True,
            }
        )


class RedirectInitializer:
    def __init__(self):
        self.logger = logger

    def normalize_path(self, path: str) -> str:
        return "/" + path.strip().lstrip("/").rstrip("/")

    def create_redirect(self, old_path=None, new_path=None, is_permanent=True):
        """
        Create a redirect if it doesn't already exist

        Args:
            old_path (str): The path to redirect from
            new_path (str): The path to redirect to
            is_permanent (bool): Whether this is a permanent (301) or temporary (302) redirect
        """
        if old_path and new_path:
            redirects = [
                {
                    "old_path": self.normalize_path(old_path),
                    "new_path": new_path,
                    "is_permanent": is_permanent,
                }
            ]
        else:
            redirects = REDIRECTS + get_rule_pdf_redirects()
        logger.info("Initializing redirects...")

        for redirect in redirects:
            old_path = self.normalize_path(redirect["old_path"])
            new_path = redirect["new_path"]
            is_permanent = redirect["is_permanent"]
            if Redirect.objects.filter(old_path=old_path).exists():
                logger.info(f"- Redirect from '{old_path}' already exists.")
                continue
            else:
                try:
                    Redirect.objects.create(
                        old_path=old_path,
                        redirect_link=new_path,
                        is_permanent=is_permanent,
                    )
                    logger.info(f"Created redirect from '{old_path}' → '{new_path}'")
                except ValidationError as e:
                    logger.info(f"Error creating redirect for '{old_path}': {e}")
