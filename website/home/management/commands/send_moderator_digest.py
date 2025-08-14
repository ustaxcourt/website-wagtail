import os
import boto3
from typing import Optional, Dict, Any, List, Set

from django.core.management.base import BaseCommand
from django.template import loader
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from wagtail.models import Revision, TaskState, Page
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.contenttypes.models import ContentType


User = get_user_model()


def safe_parse_dt(value):
    """
    Accepts a datetime or ISO string; returns timezone-aware datetime or None.
    """
    if not value:
        return None
    if isinstance(value, str):
        dt = parse_datetime(value)
    else:
        dt = value
    if not dt:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt


def build_edit_url(obj, domain_name: Optional[str]) -> Optional[str]:
    """
    Return an absolute admin edit URL for a Page or Snippet-like object.
    Tries both args/kwargs forms for snippet route to support different Wagtail versions.
    """
    try:
        if isinstance(obj, Page):
            path = reverse("wagtailadmin_pages:edit", args=[obj.pk])
        else:
            ct = ContentType.objects.get_for_model(obj.__class__)
            try:
                path = reverse(
                    "wagtailsnippets:edit", args=[ct.app_label, ct.model, obj.pk]
                )
            except NoReverseMatch:
                path = reverse(
                    "wagtailsnippets:edit",
                    kwargs={
                        "app_label": ct.app_label,
                        "model_name": ct.model,
                        "pk": obj.pk,
                    },
                )
    except Exception:
        return None

    if domain_name:
        return f"https://{domain_name}{path}"
    return path


class Command(BaseCommand):
    help = "Sends a daily digest of pages and snippets awaiting moderation."

    def handle(self, *args, **options):
        # 1. Dynamically get emails of users in the "Moderators" group
        try:
            moderator_group = Group.objects.get(name="Moderators")
            moderator_emails: Set[str] = {
                u.email for u in moderator_group.user_set.all() if u.email
            }
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

        # 2) Collect objects (pages + snippets) currently in moderation
        target_statuses = ["needs_changes", "in_progress"]
        revisions_qs = (
            Revision.objects.filter(
                task_states__workflow_state__status__in=target_statuses
            )
            .select_related("content_type", "user")
            .distinct()
        )

        items: List[Dict[str, Any]] = []
        now = timezone.now()

        for rev in revisions_qs:
            ct = rev.content_type
            model = ct.model_class()
            if not model:
                continue

            # Load the concrete object
            try:
                obj = model.objects.get(pk=rev.object_id)
            except model.DoesNotExist:
                continue

            # Skip Wagtail root page
            if isinstance(obj, Page) and getattr(obj, "depth", None) == 1:
                continue

            # Latest revision: prefer model.revisions, else fall back to current rev
            latest_revision = None
            try:
                if hasattr(obj, "revisions"):
                    latest_revision = obj.revisions.order_by("-created_at").first()
            except Exception:
                pass
            if latest_revision is None:
                latest_revision = rev

            rev_content = latest_revision.content if latest_revision else {}

            # ----- NEW: note and review_by (+ helpers) -----
            note = rev_content.get("note") or getattr(obj, "note", None)

            review_by = safe_parse_dt(
                rev_content.get("review_by") or getattr(obj, "review_by", None)
            )
            is_overdue = bool(review_by and review_by <= now)
            days_until_review = None if not review_by else (review_by - now).days

            # Collect comments
            if isinstance(obj, Page):
                live_rev = getattr(obj, "live_revision", None)
                revs_since_publish = (
                    obj.revisions.all()
                    if hasattr(obj, "revisions")
                    else Revision.objects.none()
                )
                if live_rev:
                    revs_since_publish = revs_since_publish.filter(
                        created_at__gt=live_rev.created_at
                    )
                comments_qs = (
                    TaskState.objects.filter(revision__in=revs_since_publish)
                    .exclude(comment__isnull=True)
                    .exclude(comment__exact="")
                    .order_by("started_at")
                    .values_list("comment", flat=True)
                    .distinct()
                )
            else:
                comments_qs = (
                    TaskState.objects.filter(revision=latest_revision)
                    .exclude(comment__isnull=True)
                    .exclude(comment__exact="")
                    .order_by("started_at")
                    .values_list("comment", flat=True)
                    .distinct()
                )
            comments = list(comments_qs)

            # Title / Requested by / Date requested (template reads these via latest_revision too)
            title = getattr(obj, "title", None) or rev_content.get("title") or str(obj)

            # Status from the most recent task state for this object
            recent_ts = (
                TaskState.objects.filter(
                    revision__content_type=ct,
                    revision__object_id=str(obj.pk),
                    workflow_state__status__in=target_statuses,
                )
                .select_related("workflow_state")
                .order_by("-started_at")
                .first()
            )
            status_label = (
                recent_ts.workflow_state.get_status_display()
                if recent_ts
                and recent_ts.workflow_state
                and hasattr(recent_ts.workflow_state, "get_status_display")
                else "In Progress"
            )

            edit_url = build_edit_url(obj, domain_name)
            if edit_url is None and not isinstance(obj, Page):
                self.stdout.write(
                    self.style.WARNING(
                        f"Could not reverse snippet edit URL for {ct.app_label}.{ct.model} id={obj.pk}"
                    )
                )

            items.append(
                {
                    "obj": obj,
                    "is_page": isinstance(obj, Page),
                    "title": title,
                    "latest_revision": latest_revision,
                    "comments": comments,
                    "edit_url": edit_url,
                    "status": status_label,
                    # fields expected by your HTML:
                    "note": note,
                    "review_by": review_by,
                    "is_overdue": is_overdue,
                    "days_until_review": days_until_review,
                }
            )

        if not items:
            self.stdout.write(
                self.style.SUCCESS("No items are currently awaiting moderation.")
            )
            return

        # 3) Render
        context = {
            "items": items,  # your template iterates 'items'
            "site_url": domain_name,  # used in footer link
        }
        email_html = loader.get_template("mail/moderation_digest.html").render(context)

        # 4) Send via SES
        client = boto3.client("ses", region_name=os.getenv("AWS_REGION", "us-east-1"))
        try:
            response = client.send_email(
                Destination={"ToAddresses": recipient_emails},
                Message={
                    "Body": {"Html": {"Charset": "UTF-8", "Data": email_html}},
                    "Subject": {
                        "Charset": "UTF-8",
                        "Data": "Wagtail Daily Moderator Digest",
                    },
                },
                Source=f"noreply@{domain_name}" if domain_name else "noreply@localhost",
            )
            self.stdout.write(
                self.style.SUCCESS(f"Email sent! Message ID: {response['MessageId']}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error sending email: {e}"))
