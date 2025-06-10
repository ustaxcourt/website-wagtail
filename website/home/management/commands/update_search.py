from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from wagtail.contrib.search_promotions.models import SearchPromotion, Query
from wagtail.models import Page

# The data is now in a more structured JSON format.
# This is easier to read and maintain than a CSV string.
PROMOTIONS_DATA = [
    {
        "terms": ["Taxpayer", "Petitioner"],
        "results": [
            "https://ustaxcourt.gov/petitioners.html",
            "https://ustaxcourt.gov/petitioners-glossary.html",
        ],
    },
    {
        "terms": ["What is a petitioner", "Am I a petitioner"],
        "results": [
            "https://ustaxcourt.gov/petitioners-start.html",
            "https://ustaxcourt.gov/petitioners-glossary.html",
        ],
    },
    {
        "terms": ["Notice of deficiency", "notice"],
        "results": [
            "https://ustaxcourt.gov/petitioners-start.html",
            "https://ustaxcourt.gov/petitioners-glossary.html",
        ],
    },
    {
        "terms": ["Notice of determination"],
        "results": [
            "https://ustaxcourt.gov/petitioners-start.html",
            "https://ustaxcourt.gov/petitioners-glossary.html",
        ],
    },
    {
        "terms": ["Notice of certification"],
        "results": ["https://ustaxcourt.gov/petitioners-start.html"],
    },
    {
        "terms": ["Start a case"],
        "results": [
            "https://ustaxcourt.gov/petitioners-start.html",
            "https://ustaxcourt.gov/dawson.html",
        ],
    },
    {
        "terms": ["What is DAWSON", "DAWSON", "Register for DAWSON"],
        "results": [
            "https://ustaxcourt.gov/dawson-faqs-basics.html",
            "https://ustaxcourt.gov/dawson.html",
        ],
    },
    {
        "terms": ["How to efile", "eFile", "efile"],
        "results": [
            "https://ustaxcourt.gov/efile-a-petition.html",
            "https://ustaxcourt.gov/dawson.html",
        ],
    },
    {
        "terms": ["Electronic access", "eAccess"],
        "results": [
            "https://ustaxcourt.gov/dawson-faqs-account-management.html",
            "https://ustaxcourt.gov/dawson.html",
        ],
    },
    {
        "terms": ["How to get a DAWSON account"],
        "results": [
            "https://ustaxcourt.gov/dawson-faqs-account-management.html",
            "https://ustaxcourt.gov/dawson.html",
        ],
    },
    {
        "terms": ["Fee", "Fees", "Filing fee"],
        "results": [
            "https://ustaxcourt.gov/fees-and-charges.html",
            "https://ustaxcourt.gov/dawson.html",
        ],
    },
    {
        "terms": ["places of trial", "trial locations", "courthouse", "trial sessions"],
        "results": [
            "https://ustaxcourt.gov/fees-and-charges.html",
            "https://ustaxcourt.gov/dawson.html",
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
            "https://ustaxcourt.gov/dpt-cities",
            "https://ustaxcourt.gov/petitioners-during/",
        ],
    },
    {
        "terms": ["Judge", "Judges", "Judge[name]", "[name of judge]"],
        "results": [
            "https://ustaxcourt.gov/judges",
            "https://ustaxcourt.gov/press-releases",
            "https://ustaxcourt.gov/directory",
        ],
    },
    {
        "terms": ["Urda", "Judge Urda", "Chief Judge", "Chief Judge Urda"],
        "results": [
            "https://ustaxcourt.gov/judges/51/urda/",
            "https://ustaxcourt.gov/press-releases/",
            "https://ustaxcourt.gov/directory/",
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
            "https://ustaxcourt.gov/files/documents/04252024.pdf",
            "https://ustaxcourt.gov/press-releases",
            "https://ustaxcourt.gov/directory",
        ],
    },
    {
        "terms": ["Rules", "Tax Court Rules", "Amendments"],
        "results": ["https://ustaxcourt.gov/rules/"],
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
            "https://ustaxcourt.gov/pamphlets/",
        ],
    },
    {
        "terms": [
            "Practitioner",
            "Tax Court Bar",
            "Attorney Admissions",
            "Admission Application",
        ],
        "results": ["https://ustaxcourt.gov/practitioners/"],
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
            "https://ustaxcourt.gov/transcripts-and-copies/",
            "https://ustaxcourt.gov/pamphlets/",
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
            "https://ustaxcourt.gov/employment/",
            "https://ustaxcourt.gov/employment/law-clerk-program/",
        ],
    },
    {
        "terms": ["Customer support", "Support", "Help", "Feedback", "Questions"],
        "results": ["https://ustaxcourt.gov/contact"],
    },
]


class Command(BaseCommand):
    help = "Creates or updates search promotions."

    def get_page_from_url(self, full_url):
        """
        Takes a full URL, extracts the slug, and retrieves the corresponding Page object.
        Example: "https://example.com/about-us.html#section" -> slug "about-us"
        """
        if not full_url:
            return None

        try:
            path = urlparse(full_url).path
            filename = path.split("/")[-1]
            slug = filename.rsplit(".html", 1)[0]

            page = Page.objects.get(slug=slug)
            return page
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"  -> WARNING: Page with derived slug '{slug}' from URL '{full_url}' not found."
                )
            )
            return None
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  -> ERROR: Could not process URL '{full_url}': {e}")
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
                page = self.get_page_from_url(url)
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
