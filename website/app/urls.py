import boto3
import logging
import os
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

    # Remove the .pdf extension if present
    base_filename, ext = os.path.splitext(filename)
    if ext.lower() != ".pdf":
        logger.warning(f"Unexpected file extension: {ext}")
        return render(request, "404.html", status=404)

    # Initialize S3 client
    s3 = boto3.client("s3", region_name="us-east-1")

    # Prefix to search for files like "test.pdf" and "test_1234.pdf"
    prefix = "documents/"
    full_search = f"{prefix}{base_filename}"

    try:
        # List objects that match the prefix
        response = s3.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=full_search
        )

        contents = response.get("Contents", [])

        # Only include PDF files that start with the base name
        matched_keys = [
            obj["Key"]
            for obj in contents
            if obj["Key"].startswith(full_search) and obj["Key"].endswith(".pdf")
        ]

        # Check if the number of responses is not 1
        if len(matched_keys) != 1:
            logger.warning(
                f"Found non-singular matches for: {filename}, matches found: {matched_keys}"
            )
            return render(request, "404.html", status=404)

        s3_key = matched_keys[0]
        expected_key = f"{prefix}{filename}"  # This includes '.pdf'

        # Now check that it is the expected key
        if s3_key != expected_key:
            logger.warning(
                f"Found non-specific match for: {filename}, match found: {s3_key}"
            )

        s3_url = f"{settings.DOCUMENT_REDIRECT_URL}{prefix}{filename}"
        return redirect(s3_url)

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        request_id = e.response.get("ResponseMetadata", {}).get("RequestId", "Unknown")

        logger.error(
            f"S3 ClientError occurred - Code: {error_code}, Message: {error_message}, Request ID: {request_id}"
        )
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
