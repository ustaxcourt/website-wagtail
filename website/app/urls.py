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
from django.http import JsonResponse
import uuid
from social_django.utils import psa
from app import views as custom_auth_views
from django.contrib.auth import logout  # Import logout for direct use in test logout


logger = logging.getLogger(__name__)


@psa("social:begin")
def debug_oauth_start(request):
    """Debug view to inspect session state before a potential OAuth start."""

    logger.info("=== DEBUG: OAuth Start Session Inspection ===")
    logger.info(f"DEBUG: Session key (start): {request.session.session_key}")
    logger.info(f"DEBUG: Session contents (start): {dict(request.session)}")
    logger.info(f"DEBUG: Request cookies (start): {dict(request.COOKIES)}")

    # Force session creation if not exists, for a clean test
    if not request.session.session_key:
        request.session.create()
        request.session.save()
        logger.info(
            f"DEBUG: Created new session (forced): {request.session.session_key}"
        )
        logger.info(
            f"DEBUG: Session contents after force create: {dict(request.session)}"
        )

    # Manually set a test state to see if it persists after a redirect
    test_state_value = "debug_manual_state_" + str(uuid.uuid4())[:8]
    request.session["test_oauth_state_manual"] = test_state_value
    request.session.save()  # Force save the session

    logger.info(f"DEBUG: Set manual test state in session: {test_state_value}")
    logger.info(f"DEBUG: Session after setting manual state: {dict(request.session)}")
    logger.info(f"DEBUG: Session modified flag: {request.session.modified}")

    return JsonResponse(
        {
            "session_key_at_start": request.session.session_key,
            "session_contents_at_start": dict(request.session),
            "message": "Session state logged. Now try to initiate SSO from the login page.",
            "instructions": "After viewing this, go to /admin/login/ and click your SSO button. Check logs for debug messages.",
        }
    )


def test_session(request):
    """Test view to check if sessions are working and persist across requests."""
    logger.info("=== DEBUG: Test Session View ===")
    if "test_value" not in request.session:
        request.session["test_value"] = str(uuid.uuid4())
        request.session.save()
        logger.info(
            f"DEBUG: test_value set for first time: {request.session['test_value']}"
        )
    else:
        logger.info(
            f"DEBUG: test_value already exists: {request.session['test_value']}"
        )

    logger.info(f"DEBUG: Session key: {request.session.session_key}")
    logger.info(f"DEBUG: Session contents: {dict(request.session)}")
    logger.info(f"DEBUG: Request cookies: {dict(request.COOKIES)}")
    logger.info(f"DEBUG: Session modified: {request.session.modified}")
    logger.info(f"DEBUG: Session accessed: {request.session.accessed}")

    return JsonResponse(
        {
            "session_key": request.session.session_key,
            "test_value": request.session.get("test_value"),
            "session_items": dict(request.session),
            "cookies": dict(request.COOKIES),
            "session_modified": request.session.modified,
            "session_accessed": request.session.accessed,
        }
    )


def test_logout_redirect_view(request):
    """A simple view to test the logout and redirect."""
    logger.info("DEBUG: test_logout_redirect_view called.")
    logout(request)
    logger.info("DEBUG: Session cleared by logout.")
    logger.info(
        f"DEBUG: Session key after logout: {request.session.session_key}"
    )  # This might be None or a new session key
    logger.info(f"DEBUG: Session contents after logout: {dict(request.session)}")

    # Instead of immediate redirect to Azure AD, redirect to a simple page
    # where the user can then click the SSO button for the second login attempt.
    # This helps isolate if the issue is in the redirect *after* logout
    # or during the *new* login initiation.
    return render(
        request,
        "logged_out_test.html",
        {"message": "You have been logged out. Please try SSO login again."},
    )


def all_legacy_documents_redirect(request, filename):
    logger = logging.getLogger(__name__)
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
    path("documents/", include(wagtaildocs_urls)),
    path("", include("social_django.urls", namespace="social")),
    path("test-session/", test_session, name="test_session"),
    path("debug-oauth-start/", debug_oauth_start, name="debug_oauth_start"),
    path("search/", search_views.search, name="search"),
    path(
        "admin/logout/",
        custom_auth_views.custom_logout_view,
        name="wagtailadmin_logout",
    ),
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
