from __future__ import print_function

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render

from django.utils.translation import gettext_lazy as _

from .forms import SitePreferencesForm
from .models import SitePreferences, Scan
from .pagination import paginate
from .scanner import broken_link_scan

from wagtail.admin import messages
from wagtail.models import Site


def scan(request, scan_pk):
    scan = get_object_or_404(Scan, pk=scan_pk)

    return render(request, "wagtaillinkchecker/scan.html", {"scan": scan})


def index(request):
    site = Site.find_for_request(request)
    scans = Scan.objects.filter(site=site).order_by("-scan_started")

    paginator, page = paginate(request, scans)

    return render(
        request,
        "wagtaillinkchecker/index.html",
        {"page": page, "paginator": paginator, "scans": scans},
    )


def delete(request, scan_pk):
    scan = get_object_or_404(Scan, pk=scan_pk)

    if request.method == "POST":
        scan.delete()
        messages.success(request, _("The scan results were successfully deleted."))
        return redirect("wagtaillinkchecker")

    return render(
        request,
        "wagtaillinkchecker/delete.html",
        {
            "scan": scan,
        },
    )


def settings(request):
    site = Site.find_for_request(request)
    instance, created = SitePreferences.objects.get_or_create(site=site)
    form = SitePreferencesForm(instance=instance)
    form.instance.site = site

    if request.method == "POST":
        instance = SitePreferences.objects.filter(site=site).first()
        form = SitePreferencesForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _("Link checker settings have been updated."))
            return redirect("wagtaillinkchecker_settings")
        else:
            messages.error(
                request, _("The form could not be saved due to validation errors")
            )
    else:
        form = SitePreferencesForm(instance=instance)

    return render(
        request,
        "wagtaillinkchecker/settings.html",
        {
            "form": form,
        },
    )


def run_scan(request):
    site = Site.find_for_request(request)
    broken_link_scan(site)

    return redirect("wagtaillinkchecker")
