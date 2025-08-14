import os
import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import loader
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.urls import reverse
from wagtail.models import Revision, Page, Site

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
        # Resolve sender / recipients
        from_email = options.get("from_email") or getattr(
            settings, "DEFAULT_FROM_EMAIL", None
        )
        cli_to_emails = options.get("to_emails") or []

        if cli_to_emails:
            recipient_emails = list({e for e in cli_to_emails if e})
        else:
            settings_recipients = list(
                getattr(settings, "DAILY_DIGEST_RECIPIENTS", []) or []
            )
            if settings_recipients:
                recipient_emails = settings_recipients
        try:
            moderator_group = Group.objects.get(name="Moderators")
            moderator_users = moderator_group.user_set.filter(is_active=True)
            # Use a set for automatic duplicate handling
            moderator_emails = {user.email for user in moderator_users if user.email}
        except Group.DoesNotExist:
            moderator_emails = set()
        # Convert set to list for the boto3 client
        recipient_emails = list(moderator_emails)

        if not recipient_emails:
            self.stdout.write(self.style.ERROR("No recipient emails found. Aborting."))
            return

        self.stdout.write(f"Found {len(recipient_emails)} recipient(s).")

        # Resolve admin base/site URL (settings first, then Sites)
        admin_base = (getattr(settings, "WAGTAILADMIN_BASE_URL", "") or "").rstrip("/")
        if not admin_base:
            try:
                default_site = Site.objects.get(is_default_site=True)
                scheme = (
                    "https"
                    if default_site.site_name
                    and "dev" not in (default_site.hostname or "")
                    else "http"
                )
                admin_base = f"{scheme}://{default_site.hostname}".rstrip("/")
            except Site.DoesNotExist:
                admin_base = "http://127.0.0.1:8000"
        self.stdout.write(self.style.SUCCESS(f"Admin base: {admin_base}"))

        # 2. Query all in-progress/needs-changes revisions (pages + snippets)
        revisions = (
            Revision.objects.filter(
                task_states__workflow_state__status__in=["needs_changes", "in_progress"]
            )
            .select_related("content_type", "user")
            .prefetch_related("task_states")
        )

        if not revisions.exists():
            self.stdout.write(
                self.style.SUCCESS("No items are currently awaiting moderation.")
            )
            return

        # Build unified items
        items = []
        # Already resolved above

        for rev in revisions:
            try:
                model_class = rev.content_type.model_class()
                obj = model_class.objects.get(pk=rev.object_id)
            except Exception:
                continue

            is_page = isinstance(obj, Page)
            if is_page:
                try:
                    obj = obj.specific
                except Exception:
                    pass

            # Active task state
            try:
                task_state = (
                    rev.task_states.filter(
                        workflow_state__status__in=["needs_changes", "in_progress"]
                    ).first()
                    or rev.task_states.first()
                )
            except Exception:
                task_state = None

            # Title
            try:
                title = obj.get_admin_display_title()
            except Exception:
                title = str(obj)

            # Edit URL
            try:
                if is_page:
                    relative = reverse("wagtailadmin_pages:edit", args=[obj.pk])
                else:
                    app_label = rev.content_type.app_label
                    model_name = rev.content_type.model
                    relative = reverse(
                        "wagtailsnippets:edit", args=[app_label, model_name, obj.pk]
                    )
                edit_url = f"{admin_base}{relative}" if admin_base else relative
            except Exception:
                edit_url = admin_base or "#"

            # Review-by: prefer revision content then model field
            review_by = None
            if isinstance(rev.content, dict):
                raw = rev.content.get("review_by")
                if raw:
                    review_by = parse_datetime(raw) if isinstance(raw, str) else raw
            if not review_by:
                review_by = getattr(obj, "review_by", None)

            # Overdue / days until
            is_overdue = False
            days_until_review = None
            if review_by:
                aware = (
                    timezone.make_aware(review_by)
                    if timezone.is_naive(review_by)
                    else review_by
                )
                is_overdue = aware <= timezone.now()
                days_until_review = (aware - timezone.now()).days

            # Status & comment
            status_label = "In progress"
            comment = None
            if task_state:
                try:
                    status_label = (
                        task_state.workflow_state.get_status_display()
                        if getattr(task_state, "workflow_state", None)
                        else status_label
                    )
                except Exception:
                    pass
                comment = getattr(task_state, "comment", None)

            # Prefer explicit model/revision note over task_state.comment
            note_value = None
            if isinstance(rev.content, dict):
                note_value = rev.content.get("note")
            if not note_value:
                note_value = getattr(obj, "note", None)
            display_comment = note_value or comment

            # Requested by / created at
            requested_by = None
            if rev.user:
                requested_by = (
                    getattr(rev.user, "get_full_name", lambda: "")()
                    or rev.user.username
                )
            created_at = rev.created_at

            items.append(
                {
                    "is_page": is_page,
                    "live": getattr(obj, "live", None),
                    "title": title,
                    "edit_url": edit_url,
                    "status": status_label,
                    "requested_by": requested_by,
                    "user": rev.user,
                    "created_at": created_at,
                    "comment": display_comment,
                    "review_by": review_by,
                    "is_overdue": is_overdue,
                    "days_until_review": days_until_review,
                }
            )

        # Sort by deadline (None last)
        items.sort(key=lambda it: (it["review_by"] is None, it["review_by"] or 0))

        # 3. Render the template with unified items
        context = {"items": items}
        email_html = loader.get_template("mail/moderation_digest.html").render(context)

        if options.get("dry_run"):
            self.stdout.write(self.style.WARNING("Dry run: not sending email."))
            self.stdout.write(email_html)
            return

        # 4. Send the email using AWS SES
        ses_region = (
            getattr(settings, "AWS_SES_REGION_NAME", None)
            or os.getenv("AWS_SES_REGION_NAME")
            or "us-east-1"
        )
        client = boto3.client("ses", region_name=ses_region)
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
                Source=(
                    from_email
                    or f"noreply@{(admin_base or 'localhost').split('://')[-1]}"
                ),
            )
            self.stdout.write(
                self.style.SUCCESS(f"Email sent! Message ID: {response['MessageId']}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error sending email: {e}"))
