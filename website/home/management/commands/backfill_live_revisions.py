from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from wagtail.models import Page as LivePage

REVISION_IMPL = None
REVISION_FIELD_NAME = (
    None  # "content_json" for PageRevision, "content" for generic Revision
)
USE_PAGEREVISION = False

try:
    from wagtail.models import PageRevision  # type: ignore

    REVISION_IMPL = PageRevision
    REVISION_FIELD_NAME = "content_json"
    USE_PAGEREVISION = True
except Exception:
    try:
        from wagtail.models import Revision  # type: ignore

        REVISION_IMPL = Revision
        REVISION_FIELD_NAME = "content"
        USE_PAGEREVISION = False
    except Exception:
        REVISION_IMPL = None


class Command(BaseCommand):
    help = "Backfill a live revision for any live Page that has no live_revision. Drafts remain untouched."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change, do not write.",
        )
        parser.add_argument(
            "--limit", type=int, default=500, help="Max pages to process this run."
        )

    def handle(self, *args, **opts):
        if REVISION_IMPL is None:
            self.stderr.write(
                self.style.ERROR(
                    "Could not import a Wagtail Revision model (PageRevision or Revision). "
                    "Check your Wagtail version and imports."
                )
            )
            return

        dry = opts["dry_run"]
        limit = opts["limit"]

        qs = LivePage.objects.filter(live=True, live_revision__isnull=True).order_by(
            "id"
        )
        if limit:
            qs = qs[:limit]

        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No pages need backfill."))
            return

        self.stdout.write(f"Found {count} live pages without live_revision.")
        self.stdout.write(
            f"Using {'PageRevision' if USE_PAGEREVISION else 'generic Revision'} model."
        )

        with transaction.atomic():
            for page in qs.select_related():
                specific = page.specific
                snapshot = specific.to_json()

                created_at = (
                    page.last_published_at
                    or getattr(page, "first_published_at", None)
                    or timezone.now()
                )

                if dry:
                    self.stdout.write(
                        f"[DRY] Would create live revision for Page(id={page.id}, title={page.title!r}) at {created_at}."
                    )
                    continue

                if USE_PAGEREVISION:
                    # Classic PageRevision (field is content_json)
                    kwargs = {
                        "page_id": page.id,
                        "created_at": created_at,
                        "user": None,
                        "submitted_for_moderation": False,
                        "approved_go_live_at": None,
                        "content_json": snapshot,
                    }
                    rev = REVISION_IMPL.objects.create(**kwargs)
                else:
                    # Generic Revision (field is content)
                    ct = ContentType.objects.get_for_model(specific.__class__)
                    kwargs = {
                        "content_type": ct,
                        "object_id": page.id,
                        "created_at": created_at,
                        "user": None,
                        "approved_go_live_at": None,
                        REVISION_FIELD_NAME: snapshot,
                    }
                    rev = REVISION_IMPL.objects.create(**kwargs)

                # Point the page at this revision as live without touching drafts
                page.live_revision = rev

                # Only set latest_revision_created_at if it's currently null
                if not page.latest_revision_created_at:
                    page.latest_revision_created_at = created_at

                page.save(update_fields=["live_revision", "latest_revision_created_at"])

        self.stdout.write(self.style.SUCCESS("Backfill complete."))
