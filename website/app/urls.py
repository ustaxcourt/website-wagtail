import logging
import os
import re
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
from django.http import HttpResponsePermanentRedirect
from wagtail.contrib.redirects.models import Redirect


def all_legacy_documents_redirect(request, filename, doc_id=None):
    logger = logging.getLogger(__name__)
    logger.warning(f"Attempting to redirect original URL: {request.get_full_path()}")

    # Updated pattern to extract rule number even with suffixes
    canonical_pattern = re.compile(r"^rule[-_]?(\d+)", re.IGNORECASE)
    match = canonical_pattern.match(filename)

    normalized_filename = None
    normalized_path = None

    if match:
        rule_number = match.group(1)
        normalized_filename = f"rule-{rule_number}.pdf"
        normalized_path = f"/files/documents/{normalized_filename}"
        if filename.lower() != normalized_filename.lower():
            logger.info(f"Redirecting variant filename: {filename} → {normalized_path}")
            return HttpResponsePermanentRedirect(normalized_path)

    # Now safe to use filename directly
    request_path = "/" + request.path.lstrip("/").lower().rstrip("/")
    redirect_entry = Redirect.objects.filter(old_path__iexact=request_path).first()
    if redirect_entry:
        logger.info(f"Matched Wagtail redirect for: {request_path}")
        return HttpResponsePermanentRedirect(redirect_entry.redirect_link)

    redirect_entry = Redirect.objects.filter(old_path__iendswith=filename).first()
    if redirect_entry:
        logger.info(f"Matched Wagtail redirect for: {filename}")
        return HttpResponsePermanentRedirect(redirect_entry.redirect_link)

    # Remove the extension if present
    base_filename, ext = os.path.splitext(filename)

    # Find documents where the filename starts with the base name
    possible_matches = Document.objects.filter(file__icontains=base_filename)

    # Filter down to files with same extension that start with the base filename
    matched_docs = [
        doc
        for doc in possible_matches
        if doc.filename.lower().endswith(ext)
        and os.path.splitext(doc.filename)[0].startswith(base_filename)
    ]

    number_of_matches = len(matched_docs)

    # Redirect if there is a single match and it is exact (ignoring case)
    if number_of_matches == 1:
        matched_doc = matched_docs[0]
        if matched_doc.filename.lower() == filename.lower():
            logger.info(
                f"Successfully redirecting legacy resource request for: {filename}"
            )
            return redirect(matched_doc.file.url)
        else:
            # Log non-exact match and render 404
            logger.warning(
                f"Found non-exact match for: {filename}, match found: {matched_doc.filename}"
            )
            return render_404_util(request)

    # Log requests with no matches or multiple matches
    if number_of_matches == 0:
        logger.warning(f"No matches for: {filename}")
    else:
        logger.warning(
            f"Found multiple matches for: {filename}, matches found: {[doc.filename for doc in matched_docs]}"
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

urlpatterns += [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
