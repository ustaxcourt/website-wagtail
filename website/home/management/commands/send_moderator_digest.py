import os
import boto3
from django.core.management.base import BaseCommand
from django.template import loader
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from wagtail.models import Revision, TaskState, Page

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

        # 2. Query for pages in moderation and prepare detailed context
        pages_in_moderation_ids = (
            Revision.objects.filter(
                task_states__workflow_state__status__in=["needs_changes", "in_progress"]
            )
            .values_list("object_id", flat=True)
            .distinct()
        )

        # The object_id is a string, so we convert it to int for the Page query
        pages_qs = Page.objects.filter(
            id__in=[int(id) for id in pages_in_moderation_ids]
        )

        # This list will hold the detailed context for each page
        pages_with_context = []

        for page in pages_qs:
            # Get the latest revision for displaying user and date info
            latest_revision = page.get_latest_revision()

            # Find the last time the page was published to get the full history
            # of the current moderation cycle.
            live_revision = page.live_revision
            revisions_since_publish = page.revisions.all()
            if live_revision:
                revisions_since_publish = revisions_since_publish.filter(
                    created_at__gt=live_revision.created_at
                )

            # Now, get all unique comments from task states on those revisions
            comments = (
                TaskState.objects.filter(revision__in=revisions_since_publish)
                .exclude(comment__isnull=True)
                .exclude(comment__exact="")
                .order_by("started_at")
                .values_list("comment", flat=True)
                .distinct()
            )

            pages_with_context.append(
                {
                    "page": page,
                    "latest_revision": latest_revision,
                    "comments": list(comments),
                }
            )

        if not pages_with_context:
            self.stdout.write(
                self.style.SUCCESS("No items are currently awaiting moderation.")
            )
            return

        # 3. Render the template with the detailed context
        context = {
            "pages": pages_with_context,
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
