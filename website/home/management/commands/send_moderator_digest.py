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
        site_url = os.getenv("DOMAIN_NAME")
        self.stdout.write(self.style.SUCCESS(f"Site url: {site_url}"))

        # 2. Query for pages in moderation
        pages_awaiting_moderation_ids = (
            Revision.objects.filter(task_states__status=TaskState.STATUS_IN_PROGRESS)
            .values_list(
                "object_id", flat=True
            )  # Change: Use values_list to get a flat list of IDs
            .distinct()
        )

        pages = Page.objects.filter(
            id__in=[int(id) for id in pages_awaiting_moderation_ids]
        )

        if not pages.exists():
            self.stdout.write(
                self.style.SUCCESS("No pages are currently awaiting moderation.")
            )
            return  # TODO: Check with Jenna - do we want an email even if no pages awaiting moderation

        # 3. Prepare email context and render the template
        context = {
            "pages": pages,
            "site_url": site_url,
        }

        email_html = loader.get_template("mail/moderation_digest.html").render(context)

        # 4. Send the email
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
                Source="noreply@mmiest-moore-sandbox-web.ustaxcourt.gov",  # TODO: Update to automatically generate rather than hard-coding
            )
            self.stdout.write(
                self.style.SUCCESS(f"Email sent! Message ID: {response['MessageId']}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error sending email: {e}"))
