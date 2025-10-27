from django.contrib import messages

from django.urls import reverse
from wagtail.models import Page
from django.http import HttpResponseRedirect


def add_entry_above_view(request, sort_order, page_id):
    try:
        page = Page.objects.get(id=page_id)

        # If the page has unpublished changes, get the latest revision.
        # Otherwise, use the live, specific page.
        if page.has_unpublished_changes:
            home_page = page.get_latest_revision_as_object()
        else:
            home_page = page.specific

        target_entry = home_page.entries.get(sort_order=sort_order)
        target_entry.add_entry_above_me(sort_order=sort_order, request=request)

        messages.success(request, "New entry added above the selected entry.")

        # Redirect back to the editor
        url = reverse("wagtailadmin_pages:edit", args=(home_page.id,))
        return HttpResponseRedirect(f"{url}#inline_child_entries-{sort_order}")

    except Page.DoesNotExist:
        messages.error(request, "The page was not found.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
