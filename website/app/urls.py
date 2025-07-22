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
from wagtail.contrib.redirects.models import Redirect
from django.http import HttpResponsePermanentRedirect
from wagtail.documents.views import serve as wagtail_serve


def all_legacy_documents_redirect(request, filename):
    logger = logging.getLogger(__name__)
    logger.warning(f"Attempting to redirect original URL: {request.get_full_path()}")

    # First check for database redirects
    logger.warning(f"Checking for database redirects for path: {request.path}")
    redirect_entry = Redirect.objects.filter(old_path__iexact=request.path).first()

    if redirect_entry:
        logger.warning(
            f"Found redirect entry: {redirect_entry.old_path} -> {redirect_entry.redirect_link}"
        )
        logger.warning(f"Redirect site: {redirect_entry.site}")
        logger.warning(f"Redirect is_permanent: {redirect_entry.is_permanent}")

        redirect_target = redirect_entry.redirect_link

        current_path = request.path.rstrip("/").lower()
        redirect_path = redirect_target.rstrip("/").lower()
        logger.warning(f"Checking current path: {current_path}")
        logger.warning(f"Checking Redirect path: {redirect_path}")

        # Stronger check — stop redirecting if we're already on the target
        if current_path == redirect_path:
            logger.warning(f"Preventing redirect loop for: {request.path}")
            return render_404_util(request)

        # Additional loop prevention: check if we're redirecting to the same filename
        current_filename = os.path.basename(current_path)
        redirect_filename = os.path.basename(redirect_path)
        logger.warning(f"Checking current filename: {current_filename}")
        logger.warning(f"Checking Redirect filename: {redirect_filename}")

        if current_filename.lower() == redirect_filename.lower():
            logger.warning(
                f"Preventing filename redirect loop: {current_filename} -> {redirect_filename}"
            )
            return render_404_util(request)

        logger.warning(f"Database redirect: {current_path} to: {redirect_path}")
        return HttpResponsePermanentRedirect(redirect_target)

    # Remove the extension if present
    base_filename, ext = os.path.splitext(filename)

    # Find documents where the filename matches (case-insensitive)
    possible_matches = Document.objects.filter(file__icontains=base_filename)

    # Filter down to files with same extension that start with the base filename
    matched_docs = [
        doc
        for doc in possible_matches
        if doc.filename.lower().endswith(ext.lower())
        and os.path.splitext(doc.filename.lower())[0] == base_filename.lower()
    ]

    if len(matched_docs) == 1:
        matched_doc = matched_docs[0]

        logger.info(f"✅ Serving document directly via Wagtail: {matched_doc.filename}")
        return wagtail_serve.serve(request, matched_doc.id, matched_doc.filename)
    # Log requests with no matches or multiple matches
    if len(matched_docs) == 0:
        logger.warning(f"No document matches for: {filename}")
    else:
        logger.warning(
            f"Multiple document matches for: {filename}, matches: {[doc.filename for doc in matched_docs]}"
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
        name="all_legacy_documents_redirect",
    ),
    path("admin/", include(wagtailadmin_urls)),
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

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
