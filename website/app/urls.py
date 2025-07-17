import logging
import os
from django.contrib import admin
from django.conf import settings
from django.shortcuts import render
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.documents.models import Document
from search import views as search_views
from django.http import HttpResponsePermanentRedirect
from home.utils.pdf_redirect_utils import normalize_rule_pdf_filename


logger = logging.getLogger(__name__)


def all_legacy_documents_redirect(request, filename, doc_id=None):
    """
    Custom view to handle redirects for legacy PDF document URLs that are not
    caught by Wagtail's built-in redirect middleware.
    """
    logger.warning(f"Custom redirect handler hit for: {request.get_full_path()}")

    # 1. Attempt dynamic normalization for rule PDFs
    normalized_filename = normalize_rule_pdf_filename(filename)
    if normalized_filename:
        # Construct the expected target path for the normalized file
        target_path = f"/files/documents/{normalized_filename}".lower()

        # Get the current request path, normalized for comparison
        current_request_path = request.path.lower().rstrip("/")

        if current_request_path != target_path:
            logger.info(
                f"Redirecting based on filename normalization: {filename} -> {target_path}"
            )
            return HttpResponsePermanentRedirect(target_path)
        else:
            logger.info(
                f"Request is already for normalized path: {request.get_full_path()}."
            )
            return None

    # Remove the extension if present
    base_filename, ext = os.path.splitext(filename)

    # Find documents where the filename starts with the base name
    possible_matches = Document.objects.filter(file__icontains=base_filename)

    # Filter down to files with same extension that start with the base filename
    matched_docs = [
        doc
        for doc in possible_matches
        if doc.filename.lower().endswith(ext)
        and os.path.splitext(doc.filename)[0]
        .lower()
        .startswith(
            base_filename.lower()
        )  # Ensure base filename comparison is also case-insensitive
    ]

    number_of_matches = len(matched_docs)

    # Redirect if there is a single match and it is exact (ignoring case)
    if number_of_matches == 1:
        matched_doc = matched_docs[0]
        # Only redirect if the current requested filename is *not* exactly the matched document's filename.
        if matched_doc.filename.lower() != filename.lower():
            logger.info(
                f"Successfully redirecting legacy resource request (Document Match): {filename} → {matched_doc.file.url}"
            )
            return HttpResponsePermanentRedirect(matched_doc.file.url)
        else:
            return render_404_util(
                request
            )  # If no redirect, and not a document path handled elsewhere.

    if number_of_matches == 0:
        logger.warning(f"No document matches found for: {filename}. Rendering 404.")
    else:
        logger.warning(
            f"Found multiple document matches for: {filename}, matches: {[doc.filename for doc in matched_docs]}. Rendering 404."
        )

    # If no redirect logic above was applied, render 404
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
    path("admin-tools/role-switcher/", include("app.role_switcher.urls")),
    path("admin/", include(wagtailadmin_urls)),
    re_path(
        r"^files/documents/(?P<filename>[^/]+\.pdf)$",
        all_legacy_documents_redirect,
        name="filename_only_redirect",
    ),
    re_path(
        r"^resources/(?:.*/)?(?P<filename>[^/]+\.pdf)$",
        all_legacy_documents_redirect,
        name="all_legacy_documents_redirect",
    ),
    path(
        "documents/", include(wagtaildocs_urls)
    ),  # Wagtail's default document serving URLs
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

urlpatterns += [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
