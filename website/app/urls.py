import logging
import os
from django.contrib import admin
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import include, path, re_path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.documents.models import Document


def all_legacy_documents_redirect(request, filename):
    logger = logging.getLogger(__name__)
    logger.warning(f"Attempting to redirect original URL: {request.get_full_path()}")

    # Remove the .pdf extension if present
    base_filename, ext = os.path.splitext(filename)
    if ext.lower() != ".pdf":
        logger.warning(f"Unexpected file extension: {ext}")
        return render_legacy_404(request, filename)

    # Find documents where the filename starts with the base name
    possible_matches = Document.objects.filter(file__icontains=base_filename)

    print("DEBUG: possible_matches =", possible_matches)
    

    # Filter down to .pdf files that start with the base filename
    matched_docs = [
        doc
        for doc in possible_matches
        if doc.filename.lower().endswith(".pdf")
        and os.path.splitext(doc.filename)[0].startswith(base_filename)
    ]

    print("DEBUG: matched_docs =", matched_docs)

    number_of_matches = len(matched_docs)

    print("DEBUG: number_of_matches =", number_of_matches)

    # Redirect if there is a single match and it is exact (ignoring case)
    if number_of_matches == 1:
        matched_doc = matched_docs[0]
        print("DEBUG: first filename =", getattr(possible_matches[0], "filename", "MISSING"))
        if matched_doc.filename.lower() == filename.lower():
            logger.info(
                f"Successfully redirecting legacy resource request for: {filename}"
                )
            return redirect(matched_doc.file.url)
        else:
            logger.warning(
                f"Found non-exact match for: {filename}, match found: {matched_doc.filename}"
            )
    
    # Log requests with no matches or multiple matches
    if(number_of_matches == 0):
        logger.warning(
            f"No matches for: {filename}"
        )
    else:
        logger.warning(
            f"Found multiple matches for: {filename}, matches found: {[doc.filename for doc in matched_docs]}"
        )

    # Not found or ambiguous matches result in 404
    return render_legacy_404(request, filename)

def render_legacy_404(request, filename=None):
    """
    Shared 404 renderer for legacy document redirects.
    Optionally takes filename for future customization/logging.
    """
    return render(request, "404.html", status=404)

urlpatterns = [
    path("sitemap.xml", sitemap),
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    re_path(
        r"^resources/(?:.*/)?(?P<filename>[^/]+\.pdf)$",
        all_legacy_documents_redirect,
        name="all_legacy_documents_redirect",
    ),
    path("documents/", include(wagtaildocs_urls)),
    path("", include("social_django.urls", namespace="social")),
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
