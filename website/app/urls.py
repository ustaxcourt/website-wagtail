import boto3
import logging
from botocore.exceptions import ClientError
from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from django.shortcuts import redirect, render
from django.urls import re_path


def all_legacy_documents_redirect(request, filename):
    logger = logging.getLogger(__name__)
    logger.warning(f"Attempting to redirect original URL: {request.get_full_path()}")

    # Initialize S3 client
    s3 = boto3.client(
        "s3",
        region_name="us-east-1",
    )

    # Construct the key
    prefix = "documents/"
    possible_key = f"{prefix}{filename}"

    try:
        # Check if object exists
        s3.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=possible_key)

        # If it exists, redirect to S3 URL
        s3_url = f"{settings.MEDIA_URL}{possible_key}"
        return redirect(s3_url)
    except ClientError as e:
        # Handle object not found error specifically
        if e.response["Error"]["Code"] == "404":
            return render(request, "404.html", status=404)
        else:
            logger.warning(
                f"Unsuccessful attempt to redirect original URL: {request.get_full_path()}"
            )
            # Unexpected error - raise for visibility
            raise


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
