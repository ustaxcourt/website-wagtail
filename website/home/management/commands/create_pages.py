from django.core.management.base import BaseCommand

from home.management.commands.pages.about_the_court import (
    about_the_court_pages_to_initialize,
)

from home.management.commands.pages.rules_and_guidance import (
    rules_and_guidance_pages_to_initialize,
)

from home.management.commands.pages.efiling_and_case_maintenance import (
    efiling_and_case_maintenance_pages_to_initialize,
)

from home.management.commands.pages.orders_and_opinions import (
    orders_and_opinions_pages_to_initialize,
)

from home.management.commands.pages.home_page import HomePageInitializer
from home.management.commands.pages.redirect_page import RedirectPageInitializer
from home.management.commands.pages.footer import FooterInitializer
from home.management.commands.pages.navigation import NavigationInitializer

from home.management.commands.snippets import snippets_to_initialize
from home.management.commands.redirects.redirect_initializer import RedirectInitializer

from home.management.commands.pages.documents import UnlistedFiles
from home.management.commands.pages.about_the_court import JudgesPageInitializer

# Initialize home and footer first
home_page_initialize = [
    HomePageInitializer,
    FooterInitializer,
    RedirectPageInitializer,
]

# Ensure Home Page is initialized first
pages_to_initialize = home_page_initialize + (
    about_the_court_pages_to_initialize
    + rules_and_guidance_pages_to_initialize
    + orders_and_opinions_pages_to_initialize
    + efiling_and_case_maintenance_pages_to_initialize
)

pages_to_update = [HomePageInitializer, FooterInitializer, JudgesPageInitializer]


class Command(BaseCommand):
    help = "Create initial pages and form records if they don't already exist."

    def handle(self, *args, **options):
        # Initialize redirects first
        initializer = RedirectInitializer()

        redirects = [
            {
                "old_path": "/vacancy_announcements",
                "new_path": "/employment/vacancy-announcements",
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

        legacy_urls = [
            "/administrative_orders.html",
            "/case_procedure.html",
            "/case_related_forms.html",
            "/check_info.html",
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
            "/efiling_and_case_maintenance.html",
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
            "/rules_and_guidance.html",
            "/rules_comments.html",
            "/transcripts_and_copies.html",
            "/trial_sessions.html",
            "/update_contact_information.html",
            "/vacancy_announcements.html",
            "/zoomgov.html",
            "zoomgov_getting_ready.html",
            "zoomgov_the_basics.html",
            "zoomgov_zoomgov_proceedings.html",
        ]

        for old_path in legacy_urls:
            if old_path.endswith(".html"):
                cleaned_path = old_path.replace(".html", "").replace("_", "-")
                new_path = cleaned_path + "/"
                redirects.append(
                    {
                        "old_path": old_path,
                        "new_path": new_path,
                        "is_permanent": True,
                    }
                )

        self.stdout.write("Initializing redirects...")
        for redirect in redirects:
            initializer.create_redirect(
                redirect["old_path"], redirect["new_path"], redirect["is_permanent"]
            )
        self.stdout.write(self.style.SUCCESS("All redirects have been initialized."))

        # Continue with existing initialization
        for snippet_class in snippets_to_initialize:
            snippet_instance = snippet_class()
            snippet_instance.create()

        for page_class in pages_to_initialize:
            page_instance = page_class()
            page_instance.create()

        self.stdout.write(self.style.SUCCESS("All pages have been initialized."))

        # Update pages
        for page_class in pages_to_update:
            page_instance = page_class()
            page_instance.update()

        self.stdout.write(self.style.SUCCESS("All pages have been updated."))

        # Initialize navigation last
        nav_initializer = NavigationInitializer()
        nav_initializer.create()
        self.stdout.write(self.style.SUCCESS("Navigation has been initialized."))

        # Initialize unlisted files
        unlisted_files_initializer = UnlistedFiles()
        unlisted_files_initializer.create()
        self.stdout.write(self.style.SUCCESS("Unlisted files have been initialized."))
