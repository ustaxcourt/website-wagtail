from django.conf import settings
from django.core.management.base import BaseCommand
from wagtail.contrib.search_promotions.models import SearchPromotion, Query
from wagtail.models import Page

# The data is now in a more structured JSON format.
# This is easier to read and maintain than a CSV string.
PROMOTIONS_DATA = [
    {
        "terms": ["Taxpayer", "Petitioner"],
        "results": [
            "petitioners",
            "petitioners-glossary",
        ],
    },
    {
        "terms": ["What is a petitioner", "Am I a petitioner"],
        "results": [
            "petitioners-start",
            "petitioners-glossary",
        ],
    },
    {
        "terms": ["Notice of deficiency", "notice"],
        "results": [
            "petitioners-start",
            "petitioners-glossary",
        ],
    },
    {
        "terms": ["Notice of determination"],
        "results": [
            "petitioners-start",
            "petitioners-glossary",
        ],
    },
    {
        "terms": ["Notice of certification"],
        "results": ["petitioners-start"],
    },
    {
        "terms": ["Start a case"],
        "results": [
            "petitioners-start",
            "dawson",
        ],
    },
    {
        "terms": ["What is DAWSON", "DAWSON", "Register for DAWSON"],
        "results": [
            "dawson-faqs-basics",
            "dawson",
        ],
    },
    {
        "terms": ["How to efile", "eFile", "efile"],
        "results": [
            "efile-a-petition",
            "dawson",
        ],
    },
    {
        "terms": ["Electronic access", "eAccess"],
        "results": [
            "dawson-faqs-account-management",
            "dawson",
        ],
    },
    {
        "terms": ["How to get a DAWSON account"],
        "results": [
            "dawson-faqs-account-management",
            "dawson",
        ],
    },
    {
        "terms": ["Fee", "Fees", "Filing fee"],
        "results": [
            "fees-and-charges",
            "dawson",
        ],
    },
    {
        "terms": ["places of trial", "trial locations", "courthouse", "trial sessions"],
        "results": [
            "fees-and-charges",
            "dawson",
        ],
    },
    {
        "terms": [
            "places of trial",
            "trial locations",
            "courthouse",
            "trial sessions",
            "Trial Sessions",
            "Trials",
            "Proceedings",
            "Remote proceedings",
        ],
        "results": [
            "dpt-cities",
            "petitioners-during",
        ],
    },
    {
        "terms": ["Judge", "Judges"],
        "results": [
            "judges",
            "press-releases",
            "directory",
        ],
    },
    {
        "terms": ["Urda", "Judge Urda", "Chief Judge", "Chief Judge Urda"],
        "results": [
            "https://ustaxcourt.gov/judges/51/urda/",
            "press-releases",
            "directory",
        ],
    },
    {
        "terms": [
            "Charles Jeane",
            "Charles G. Jeane",
            "Clerk of the Court",
            "Clerk",
            "clerk of court",
        ],
        "results": [
            f"{settings.BASE_URL}/files/documents/04252024.pdf",
            "press-releases",
            "directory",
        ],
    },
    {
        "terms": ["Rules", "Tax Court Rules", "Amendments"],
        "results": ["rules"],
    },
    {
        "terms": ["Orders", "Today's Orders", "Judge Ruling", "Ruling"],
        "results": ["https://dawson.ustaxcourt.gov/todays-orders"],
    },
    {
        "terms": [
            "Opinion",
            "Today's Opinions",
            "Judge Ruling",
            "Memorandum Opinion",
            "Docket",
        ],
        "results": [
            "https://dawson.ustaxcourt.gov/todays-opinions",
            "pamphlets",
        ],
    },
    {
        "terms": [
            "Practitioner",
            "Tax Court Bar",
            "Attorney Admissions",
            "Admission Application",
        ],
        "results": ["practitioners"],
    },
    {
        "terms": [
            "Transcripts & Copies",
            "Transcripts",
            "Copies",
            "Document",
            "Documents",
        ],
        "results": [
            "transcripts-and-copies",
            "pamphlets",
        ],
    },
    {
        "terms": [
            "Employment",
            "Jobs",
            "Law Clerk Program",
            "Internships",
            "Vacancy Announcement",
        ],
        "results": [
            "employment",
            "law-clerk-program",
        ],
    },
    {
        "terms": ["Customer support", "Support", "Help", "Feedback", "Questions"],
        "results": ["contact"],
    },
]


class Command(BaseCommand):
    help = "Creates or updates search promotions."

    def get_page_from_slug(self, text):
        if not text:
            return None

        try:
            page = Page.objects.get(slug=text)
            return page
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"  -> WARNING: Page with derived slug '{text}' not found."
                )
            )
            return None

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to update search promotions from JSON data...")

        for i, item in enumerate(PROMOTIONS_DATA):
            search_terms = item.get("terms", [])
            result_urls = item.get("results", [])

            if not search_terms or not result_urls:
                continue

            self.stdout.write(
                self.style.HTTP_INFO(f"\nProcessing entry {i+1}: Terms {search_terms}")
            )

            # Find all page objects first
            promoted_pages = []
            for url in result_urls:
                page = self.get_page_from_slug(url)
                if page:
                    promoted_pages.append(page)

            if not promoted_pages:
                self.stdout.write(
                    self.style.WARNING(
                        "  -> No valid pages found for this entry. Skipping."
                    )
                )
                continue

            # Associate each search term with the found pages
            for term in search_terms:
                clean_term = term.strip()
                if not clean_term:
                    continue

                # Get or create the Query object, using lowercase to avoid case-sensitivity issues
                query, created = Query.objects.get_or_create(
                    query_string=clean_term.lower()
                )
                action_str = "Created" if created else "Found existing"
                self.stdout.write(f"  - {action_str} query for: '{clean_term}'")

                # Create/update a promotion for each page with the correct sort order
                for sort_order, page in enumerate(promoted_pages):
                    SearchPromotion.objects.update_or_create(
                        query=query,
                        page=page,
                        defaults={
                            "sort_order": sort_order,
                            "description": f"{page.search_description}: {page.title}",
                        },
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    -> Linked to '{page.title}' as result #{sort_order + 1}."
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS("\nFinished updating all search promotions.")
        )
