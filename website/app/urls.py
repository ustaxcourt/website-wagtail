import logging
import os
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
from wagtail.contrib.redirects.models import Redirect
from django.http import HttpResponsePermanentRedirect
from wagtail.documents.views import serve
from django.urls import resolve
from django.urls.exceptions import Resolver404


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

        # Stronger check — stop redirecting if we're already on the target
        if current_path == redirect_path:
            logger.warning(f"Preventing redirect loop for: {request.path}")
            return render_404_util(request)

        # Additional loop prevention: check if we're redirecting to the same filename
        current_filename = os.path.basename(current_path)
        redirect_filename = os.path.basename(redirect_path)
        if current_filename.lower() == redirect_filename.lower():
            logger.warning(
                f"Preventing filename redirect loop: {current_filename} -> {redirect_filename}"
            )
            return render_404_util(request)

        # Prevent loops where redirect target would be handled by this same function
        # Check if the redirect target matches our URL patterns
        try:
            # Remove domain from redirect_target if it's a full URL
            if redirect_target.startswith(("http://", "https://")):
                from urllib.parse import urlparse

                parsed_url = urlparse(redirect_target)
                target_path = parsed_url.path
            else:
                target_path = redirect_target

            # Try to resolve the target path
            resolved = resolve(target_path)
            if resolved.func == all_legacy_documents_redirect:
                logger.warning(
                    f"Preventing redirect loop - target would trigger same function: {target_path}"
                )
                return render_404_util(request)
        except Resolver404:
            # Target path doesn't match any patterns, safe to redirect
            pass

        logger.warning(f"Database redirect: {current_path} to: {redirect_path}")
        return HttpResponsePermanentRedirect(redirect_target)
    else:
        logger.warning(f"No database redirect found for: {request.path}")
        # Check if there are any similar redirects
        similar_redirects = Redirect.objects.filter(
            old_path__icontains=os.path.basename(request.path)
        )[:5]
        if similar_redirects:
            logger.warning(
                f"Similar redirects found: {[r.old_path for r in similar_redirects]}"
            )
        else:
            logger.warning("No similar redirects found")

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

    number_of_matches = len(matched_docs)

    # Redirect if there is a single match and it is exact (ignoring case)
    if number_of_matches == 1:
        matched_doc = matched_docs[0]
        # Check if we're already serving the correct file to prevent loops
        requested_filename = filename.lower()
        actual_filename = matched_doc.filename.lower()

        if requested_filename != actual_filename:
            logger.warning(f"Document redirect: {filename} -> {matched_doc.filename}")
            return redirect(matched_doc.file.url)
        else:
            logger.warning(f"Exact match found, serving file directly: {filename}")
            # Check if the document file URL would cause a redirect loop
            file_url = matched_doc.file.url
            if (
                file_url.startswith("/files/documents/")
                or "/files/documents/" in file_url
            ):
                # Use Wagtail's document serving to avoid redirect loops
                return serve.serve(request, matched_doc.id, matched_doc.filename)
            else:
                return redirect(file_url)

    # Log requests with no matches or multiple matches
    if number_of_matches == 0:
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
