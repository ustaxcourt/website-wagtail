import os
import boto3
from django.core.management.base import BaseCommand
from django.template import loader
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from wagtail.models import Revision, TaskState, Page
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

User = get_user_model()


class Command(BaseCommand):
    help = "Sends a daily digest of pages awaiting moderation."

    def add_arguments(self, parser):
        parser.add_argument(
            "--from",
            dest="from_email",
            help="SES-verified From email address",
        )
        parser.add_argument(
            "--to",
            dest="to_emails",
            action="append",
            help="Recipient email address (can specify multiple times)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Render the email but do not send",
        )

    def handle(self, *args, **options):
        # 1. Dynamically get emails of users in the "Moderators" group
        try:
            moderator_group = Group.objects.get(name="Moderators")
            moderator_users = moderator_group.user_set.all()
            # Use a set for automatic duplicate handling
            moderator_emails = {user.email for user in moderator_users if user.email}
        except Group.DoesNotExist:
            self.stdout.write(self.style.WARNING('"Moderators" group not found.'))
            return

        # Convert set to list for the boto3 client
        recipient_emails = list(moderator_emails)

        if not recipient_emails:
            self.stdout.write(self.style.ERROR("No recipient emails found. Aborting."))
            return

        self.stdout.write(f"Found {len(recipient_emails)} recipient(s).")

        # You can get this from the Wagtail Site model for more dynamic sites
        domain_name = os.getenv("DOMAIN_NAME")

        # 2. Query for all objects (pages + snippets) in moderation and prepare detailed context
        revisions_qs = (
            Revision.objects.filter(
                task_states__workflow_state__status__in=["needs_changes", "in_progress"]
            )
            .select_related("content_type")
            .distinct()
        )

        # Group object ids by content type
        content_type_to_ids = {}
        for rev in revisions_qs.only("content_type", "object_id"):
            ct = rev.content_type
            if ct_id := getattr(ct, "id", None):
                content_type_to_ids.setdefault(ct_id, set()).add(rev.object_id)

        # Build a unified list of items
        items = []

        for ct_id, object_ids in content_type_to_ids.items():
            content_type = ContentType.objects.get_for_id(ct_id)
            model_class = content_type.model_class()
            if not model_class:
                continue

            # Cast ids correctly
            cast_ids = []
            for oid in object_ids:
                try:
                    cast_ids.append(int(oid))
                except (TypeError, ValueError):
                    # Non-integer PKs aren't expected here, skip if encountered
                    continue

            queryset = model_class.objects.filter(pk__in=cast_ids)

            # Exclude Wagtail root page if ever present
            if issubclass(model_class, Page):
                queryset = queryset.exclude(depth=1)

            for obj in queryset:
                # Get the latest revision for displaying user and date info
                latest_revision = getattr(obj, "get_latest_revision", None)
                latest_revision = (
                    latest_revision() if callable(latest_revision) else None
                )

                # Resolve review_by and note from latest revision, fallback to model
                revision_content = latest_revision.content if latest_revision else {}
                review_by_raw = revision_content.get("review_by") or getattr(
                    obj, "review_by", None
                )
                review_by = (
                    parse_datetime(review_by_raw)
                    if isinstance(review_by_raw, str)
                    else review_by_raw
                )
                if review_by and timezone.is_naive(review_by):
                    review_by = timezone.make_aware(review_by)

                is_overdue = bool(review_by and review_by <= timezone.now())
                days_until_review = (
                    (review_by - timezone.now()).days if review_by else None
                )

                note = revision_content.get("note") or getattr(obj, "note", None)

                # Find the last time the object was published to get the full history
                # of the current moderation cycle (pages only)
                comments = []
                if isinstance(obj, Page):
                    live_revision = obj.live_revision
                    revisions_since_publish = obj.revisions.all()
                    if live_revision:
                        revisions_since_publish = revisions_since_publish.filter(
                            created_at__gt=live_revision.created_at
                        )
                    comments = (
                        TaskState.objects.filter(revision__in=revisions_since_publish)
                        .exclude(comment__isnull=True)
                        .exclude(comment__exact="")
                        .order_by("started_at")
                        .values_list("comment", flat=True)
                        .distinct()
                    )
                else:
                    # For non-pages, collect comments from the latest revision task states
                    if latest_revision:
                        comments = (
                            TaskState.objects.filter(revision=latest_revision)
                            .exclude(comment__isnull=True)
                            .exclude(comment__exact="")
                            .order_by("started_at")
                            .values_list("comment", flat=True)
                            .distinct()
                        )

                # Build admin edit URL
                try:
                    if isinstance(obj, Page):
                        edit_path = reverse("wagtailadmin_pages:edit", args=[obj.pk])
                    else:
                        edit_path = reverse(
                            "wagtailsnippets:edit",
                            args=[content_type.app_label, content_type.model, obj.pk],
                        )
                    edit_url = (
                        f"https://{domain_name}{edit_path}"
                        if domain_name
                        else edit_path
                    )
                except Exception:
                    edit_url = None

                items.append(
                    {
                        "obj": obj,
                        "is_page": isinstance(obj, Page),
                        "title": getattr(obj, "title", str(obj)),
                        "latest_revision": latest_revision,
                        "comments": list(comments),
                        "review_by": review_by,
                        "is_overdue": is_overdue,
                        "days_until_review": days_until_review,
                        "note": note,
                        "edit_url": edit_url,
                    }
                )

        if not items:
            self.stdout.write(
                self.style.SUCCESS("No items are currently awaiting moderation.")
            )
            return

        # 3. Render the template with the detailed context
        context = {
            "items": items,
            "site_url": domain_name,
        }

        email_html = loader.get_template("mail/moderation_digest.html").render(context)

        # 4. Send the email using AWS SES
        client = boto3.client("ses", region_name="us-east-1")
        try:
            response = client.send_email(
                Destination={
                    "ToAddresses": recipient_emails,
                },
                Message={
                    "Body": {
                        "Html": {
                            "Charset": "UTF-8",
                            "Data": email_html,
                        }
                    },
                    "Subject": {
                        "Charset": "UTF-8",
                        "Data": "Wagtail Daily Moderator Digest",
                    },
                },
                Source=f"noreply@{domain_name}",
            )
            self.stdout.write(
                self.style.SUCCESS(f"Email sent! Message ID: {response['MessageId']}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error sending email: {e}"))
