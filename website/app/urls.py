import logging
import os

from django.conf import settings

from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path, include
from django.urls import re_path
from django.views.generic import TemplateView, RedirectView

from search import views as search_views
from app.admin_local.views import LocalLoginView
from app import alarm_test_views
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.documents.models import Document
from wagtail_transfer import urls as wagtailtransfer_urls


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
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain",
            extra_context={"ENVIRONMENT": getattr(settings, "ENVIRONMENT", "")},
        ),
        name="robots_file",
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/images/icons/favicon.ico", permanent=True),
        name="favicon",
    ),
    path("django-admin/", admin.site.urls),
    path("admin-tools/role-switcher/", include("app.role_switcher.urls")),
    path(
        "admin/local-login/", LocalLoginView.as_view(), name="wagtailadmin_local_login"
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
    path(
        "definitions-search/",
        search_views.definitions_search,
        name="definitions_search",
    ),
    path("wagtail-transfer/", include(wagtailtransfer_urls)),
    path("wagtaillinkchecker/", include("app.wagtaillinkchecker.urls")),
]

# Redirects localhost:8000/admin to local-login
if getattr(settings, "ENVIRONMENT", "") == "local":
    # Ensure our override is evaluated before Wagtail's admin/login
    urlpatterns.insert(
        0,
        path(
            "admin/login/",
            RedirectView.as_view(url="/admin/local-login/", permanent=False),
            name="wagtailadmin_login",
        ),
    )

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # /local-login/ in dev redirects to the real admin/local-login
    urlpatterns.insert(
        0,
        path(
            "local-login/",
            RedirectView.as_view(url="/admin/local-login/", permanent=False),
        ),
    )

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Only include debug_toolbar URLs if the app is installed
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("__debug__/", include("debug_toolbar.urls")),
        ]

urlpatterns = urlpatterns + [
    path("alarm-test/", alarm_test_views.alarm_test_index, name="alarm_test_index"),
    path(
        "alarm-test/trigger-5xx/", alarm_test_views.trigger_5xx, name="alarm_test_5xx"
    ),
    path(
        "alarm-test/trigger-404/", alarm_test_views.trigger_404, name="alarm_test_404"
    ),
    path(
        "alarm-test/trigger-rds-error/",
        alarm_test_views.trigger_rds_error,
        name="alarm_test_rds",
    ),
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
