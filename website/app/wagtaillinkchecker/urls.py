from __future__ import absolute_import, unicode_literals

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="wagtaillinkchecker"),
    path("settings/", views.settings, name="wagtaillinkchecker_settings"),
    path("scan/", views.run_scan, name="wagtaillinkchecker_runscan"),
    path("scan/<int:scan_pk>/", views.scan, name="wagtaillinkchecker_scan"),
    path("scan/<int:scan_pk>/delete/", views.delete, name="wagtaillinkchecker_delete"),
]
