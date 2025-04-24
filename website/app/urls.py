import boto3
from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from django.shortcuts import redirect
from django.urls import re_path


def tc_report_redirect(request, path):
    s3_url = f"{settings.MEDIA_URL}documents/{path}"
    return redirect(s3_url)

def all_legacy_documents_redirect(request, filename):
    s3_url = f"{settings.MEDIA_URL}documents/{filename}"
    return redirect(s3_url)
#     # Initialize S3 client
#     s3 = boto3.client(
#         's3',
#         region_name="us-east-1",
#     )

# #TODO: get this name into secrets, or locate it
#     bucket_name = "miest-moore-sandbox-ustc-website-assets"

#     # Search for the filename in the documents/ prefix
#     prefix = "documents/"
#     possible_key = f"{prefix}{filename}"

#     try:
#         # Check if object exists
#         s3.head_object(Bucket=bucket_name, Key=possible_key)
#         s3_url = f"{settings.MEDIA_URL}{possible_key}"
#         return redirect(s3_url)
#     except s3.exceptions.ClientError as e:
#         if e.response['Error']['Code'] == "404":
#             return HttpResponseNotFound(f"Document '{filename}' not found.")
#         else:
#             raise  # For unexpected errors


urlpatterns = [
    path("sitemap.xml", sitemap),
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    # Special pattern for resources/ropp/tc-reports
    re_path(
        r"^resources/ropp/tc-reports/(?P<path>.*)$",
        tc_report_redirect,
        name="tc_report_redirect",
    ),
    # Special pattern for other documents - check if we have file by whatever name and redirect to it, this story is not uploading files, 
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
