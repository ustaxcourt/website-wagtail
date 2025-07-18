import logging
import os
import csv
from django.contrib import admin
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.documents.models import Document
from search import views as search_views
from pathlib import Path

# --- Static mapping loaded from CSV ---
CSV_REDIRECTS = {}


def load_redirect_map_from_csv():
    csv_filename = "0060_update_rules_documents.csv"
    csv_path = Path(__file__).resolve().parent / csv_filename

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            for current_title, source_filename, new_title in reader:
                # Store legacy filename (case-insensitive) -> new document title
                CSV_REDIRECTS[source_filename.strip().lower()] = new_title.strip()
        print(f"[Redirects] Loaded {len(CSV_REDIRECTS)} entries from CSV.")
    except Exception as e:
        print(f"[Redirects] Failed to load CSV redirect map: {e}")


# Load once on startup
load_redirect_map_from_csv()


def all_legacy_documents_redirect(request, filename):
    logger = logging.getLogger(__name__)
    logger.warning(f"Attempting to redirect original URL: {request.get_full_path()}")

    normalized_filename = filename.strip().lower()

    # Step 1: Check if filename is in the CSV redirect map
    new_title = CSV_REDIRECTS.get(normalized_filename)

    if new_title:
        try:
            matched_doc = Document.objects.get(title__iexact=new_title)
            logger.info(f"Redirecting '{filename}' → '{matched_doc.file.url}'")
            return redirect(matched_doc.file.url)
        except Document.DoesNotExist:
            logger.error(f"Document with title '{new_title}' not found.")
        except Exception as e:
            logger.error(f"Unexpected error redirecting '{filename}': {e}")
        return render_404_util(request)

    # Step 2: Fallback to old logic (if needed)
    logger.warning(f"No CSV match for: {filename}. Falling back to fuzzy search.")
    base_filename, ext = os.path.splitext(filename)
    possible_matches = Document.objects.filter(file__icontains=base_filename)

    matched_docs = [
        doc
        for doc in possible_matches
        if doc.filename.lower().endswith(ext)
        and os.path.splitext(doc.filename)[0].startswith(base_filename)
    ]

    # Redirect if there is a single match and it is exact (ignoring case)
    if len(matched_docs) == 1:
        matched_doc = matched_docs[0]
        if matched_doc.filename.lower() == filename.lower():
            logger.info(
                f"Successfully redirecting legacy resource request for: {filename}"
            )
            return redirect(matched_doc.file.url)
        logger.warning(f"Non-exact match found: {matched_doc.filename}")
        return render_404_util(request)

    # Log requests with no matches or multiple matches
    if len(matched_docs) == 0:
        logger.warning(f"No matches for: {filename}")
    else:
        logger.warning(
            f"Multiple matches for: {filename} → {[doc.filename for doc in matched_docs]}"
        )

    # Not found or multiple matches result in 404
    return render_404_util(request)


# Exists for testing purposes only
def render_404_util(request):
    return render(request, "404.html", status=404)


urlpatterns = [
    path("sitemap.xml", sitemap),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_file",
    ),
    path("django-admin/", admin.site.urls),
    path(
        "admin-tools/role-switcher/", include("app.role_switcher.urls")
    ),  # Or your app's urls, adjust path as desired
    re_path(
        r"^files/documents/(?P<filename>[^/]+\.pdf)$",
        all_legacy_documents_redirect,
        name="legacy_documents_redirect_files",
    ),
    # Redirect for legacy /resources/...
    re_path(
        r"^resources/(?:.*/)?(?P<filename>[^/]+\.pdf)$",
        all_legacy_documents_redirect,
        name="all_legacy_documents_redirect",
    ),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("", include("social_django.urls", namespace="social")),
    path("search/", search_views.search, name="search"),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
