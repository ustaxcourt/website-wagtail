"""
Management command that supports the scheduled publishing Cypress test
(cypress/e2e/local_wag_1411_scheduled_publishing.cy.ts). For local testing only.

    python manage.py scheduled_publishing_test_page               # create draft page
    python manage.py scheduled_publishing_test_page --status      # print live/expired state
    python manage.py scheduled_publishing_test_page --fast-forward go-live
    python manage.py scheduled_publishing_test_page --fast-forward expiry
    python manage.py scheduled_publishing_test_page --delete

``--fast-forward`` moves the page's scheduled time to one minute ago, so the
next ``python manage.py publish_scheduled`` run acts on it without the test
having to wait for the real date.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from wagtail.models import Page, Revision, Site

from home.models import EnhancedStandardPage

SLUG = "scheduled-publishing-test"
TITLE = "Scheduled Publishing Test Page"


class Command(BaseCommand):
    help = "Create/inspect/fast-forward/delete the scheduled publishing test page."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--delete", action="store_true")
        group.add_argument("--status", action="store_true")
        group.add_argument("--fast-forward", choices=["go-live", "expiry"])

    def handle(self, *args, **options):
        if options["delete"]:
            page = self._find_page()
            if page is not None:
                page.delete()
            self.stdout.write("Deleted scheduled publishing test page (if it existed).")
            return

        if options["status"]:
            page = self._get_page()
            self.stdout.write(f"PAGE_STATUS live={page.live} expired={page.expired}")
            return

        if options["fast_forward"]:
            self._fast_forward(self._get_page(), options["fast_forward"])
            return

        self._create()

    def _home_page(self):
        # The default site's root, so the page is served at /<SLUG>/.
        return Site.objects.get(is_default_site=True).root_page

    def _find_page(self):
        # Slugs are only unique among siblings, so only look directly under
        # the home page; a same-slug page elsewhere must never be touched.
        return self._home_page().get_children().filter(slug=SLUG).first()

    def _get_page(self):
        page = self._find_page()
        if page is None:
            raise CommandError(
                f"No page with slug '{SLUG}' under the home page. Create it first."
            )
        return page

    def _create(self):
        page = self._find_page()
        if page is None:
            page = self._home_page().add_child(
                instance=EnhancedStandardPage(
                    title=TITLE,
                    slug=SLUG,
                    seo_title=TITLE,
                    search_description="Test page for scheduled publishing",
                    live=False,
                )
            )
            page.save_revision()
        self.stdout.write(f"PAGE_ID={page.pk}")

    def _fast_forward(self, page, which):
        past = timezone.now() - timedelta(minutes=1)
        if which == "go-live":
            revisions = Revision.page_revisions.filter(
                object_id=str(page.pk), approved_go_live_at__isnull=False
            )
            if not revisions:
                raise CommandError("Page has no scheduled revision to fast-forward.")
            # Publishing re-reads go_live_at from the revision content and
            # re-schedules if it is still in the future, so move both.
            for revision in revisions:
                revision.approved_go_live_at = past
                revision.content["go_live_at"] = past.isoformat()
                revision.save(update_fields=["approved_go_live_at", "content"])
        else:
            if not page.expire_at:
                raise CommandError("Page has no expiry date to fast-forward.")
            Page.objects.filter(pk=page.pk).update(expire_at=past)
        self.stdout.write(f"Fast-forwarded {which} to {past.isoformat()}.")
