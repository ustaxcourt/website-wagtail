import logging
import os
import json
from django.contrib import admin
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents.models import Document
from search import views as search_views
from wagtail.contrib.redirects.models import Redirect
from django.http import Http404


def log_request_debug(request, logger):
    """Helper function to log fully qualified path and formatted request details"""
    # Get fully qualified path including domain
    full_url = request.build_absolute_uri()

    # Format request details
    request_details = {
        "method": request.method,
        "full_url": full_url,
        "path": request.path,
        "get_full_path": request.get_full_path(),
        "query_params": dict(request.GET),
        "headers": {key: value for key, value in request.headers.items()},
        "user": str(request.user) if hasattr(request, "user") else "Anonymous",
        "remote_addr": request.META.get("REMOTE_ADDR"),
        "user_agent": request.META.get("HTTP_USER_AGENT"),
        "referrer": request.META.get("HTTP_REFERER"),
        "host": request.META.get("HTTP_HOST"),
        "scheme": request.scheme,
    }

    logger.warning(f"FULLY QUALIFIED PATH: {full_url}")
    logger.warning(f"FORMATTED REQUEST: {json.dumps(request_details, indent=2)}")


def rules_documents_redirect(request, filename):
    logger = logging.getLogger(__name__)

    # Debug logging: print fully qualified path and formatted request
    log_request_debug(request, logger)

    logger.warning(f"Attempting to redirect original URL: {request.get_full_path()}")

    # Prevent redirect loop if already redirected
    if "redirect" in request.GET:
        logger.warning("Already redirected once, stopping here.")
        raise Http404("Redirect loop prevention triggered")

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

        # Try to find the target document in Wagtail and redirect to its actual file URL
        try:
            doc = Document.objects.get(file__icontains=redirect_filename)
            logger.warning(f"Redirecting to actual file URL for: {redirect_filename}")
            return redirect(f"{doc.file.url}?redirect=1")
        except Document.DoesNotExist:
            logger.warning(f"Document not found for: {redirect_filename}")
            raise Http404("Document not found")

    else:
        logger.warning(
            f"No database redirect found for: {request.path}, checking legacy documents"
        )
        raise Http404("No matching redirect found")


def all_legacy_documents_redirect(request, filename):
    logger = logging.getLogger(__name__)

    # Debug logging: print fully qualified path and formatted request
    log_request_debug(request, logger)

    logger.warning(f"Attempting to redirect original URL: {request.get_full_path()}")

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


def documents_wrapper(request, *args, **kwargs):
    """Wrapper function to log requests to wagtail documents URLs"""
    logger = logging.getLogger(__name__)

    # Debug logging: print fully qualified path and formatted request
    log_request_debug(request, logger)

    logger.warning(f"Documents wrapper called for path: {request.get_full_path()}")

    # Import here to avoid circular imports

    # Get the path after "documents/"
    path_info = request.path_info
    if path_info.startswith("/documents/"):
        remaining_path = path_info[11:]  # Remove "/documents/" prefix

        # Create a new request with the modified path for the wagtail docs handler
        request.path_info = "/" + remaining_path if remaining_path else "/"
        request.path = request.path_info

        # Import wagtail's document serving view
        from wagtail.documents.views import serve

        logger.warning(
            f"Forwarding to wagtail documents handler with path: {request.path}"
        )

        try:
            return serve(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in wagtail documents handler: {str(e)}")
            raise

    # If we somehow get here, return 404
    return render_404_util(request)


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
        r"^resources/(?:.*/)?(?P<filename>[^/]+\.pdf)$",
        all_legacy_documents_redirect,
        name="all_legacy_documents_redirect",
    ),
    re_path(
        r"^files/documents/(?P<filename>[^/]+\.pdf)$",
        rules_documents_redirect,
        name="rules_documents_redirect",
    ),
    re_path(r"^documents/.*", documents_wrapper, name="documents_wrapper"),
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
