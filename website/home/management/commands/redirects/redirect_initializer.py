from wagtail.contrib.redirects.models import Redirect
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

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
    {
        "old_path": "/dawson_faqs.html",
        "new_path": "/dawson-faqs-basics",
        "is_permanent": True,
    },
    {
        "old_path": "/tou.html",
        "new_path": "/dawson-tou",
        "is_permanent": True,
    },
    {
        "old_path": "/resources/ropp/Rule-27_Amended_03202023.pdf",
        "new_path": "/files/documents/rule-27.pdf",
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

    def create(self, old_path, new_path, is_permanent=True):
        """
        Create a single redirect if it doesn't already exist

        Args:
            old_path (str): The path to redirect from
            new_path (str): The path to redirect to
            is_permanent (bool): Whether this is a permanent (301) or temporary (302) redirect
        """
        if Redirect.objects.filter(old_path=old_path).exists():
            self.logger.info(f"- Redirect from '{old_path}' already exists.")
            return

        try:
            Redirect.objects.create(
                old_path=old_path,
                redirect_link=new_path,
                is_permanent=is_permanent,
            )
            self.logger.info(f"Created redirect from '{old_path}' → '{new_path}'")
        except ValidationError as e:
            self.logger.info(f"Error creating redirect for '{old_path}': {e}")

    def create_redirect(self):
        """
        Create all redirects from the REDIRECTS configuration
        """
        self.logger.info("Initializing redirects...")
        for redirect in REDIRECTS:
            old_path = redirect["old_path"]
            new_path = redirect["new_path"]
            is_permanent = redirect["is_permanent"]
            self.create(old_path, new_path, is_permanent)
