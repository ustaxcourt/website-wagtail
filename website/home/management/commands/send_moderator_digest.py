import os
import boto3
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings
# Import Group and User models
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from wagtail.models import Revision, TaskState, Page

# Get the currently active User model
User = get_user_model()

class Command(BaseCommand):
    help = 'Sends a daily digest of pages awaiting moderation.'

    def handle(self, *args, **options):
        # 1. Dynamically get emails of users in the "Moderators" group
        try:
            moderator_group = Group.objects.get(name='Moderators')
            moderator_users = moderator_group.user_set.all()
            # Use a set for automatic duplicate handling
            moderator_emails = {user.email for user in moderator_users if user.email}
        except Group.DoesNotExist:
            self.stdout.write(self.style.WARNING('"Moderators" group not found. Sending to default email only.'))
            moderator_emails = set()

        # Convert set to list for the boto3 client
        recipient_emails = list(moderator_emails)

        if not recipient_emails:
            self.stdout.write(self.style.ERROR('No recipient emails found. Aborting.'))
            return
            
        self.stdout.write(f"Found {len(recipient_emails)} recipient(s).")

        # You can get this from the Wagtail Site model for more dynamic sites
        site_url = os.getenv("DOMAIN_NAME")
        self.stdout.write(self.style.SUCCESS(f'Site url: {site_url}'))

        # 2. Query for pages in moderation
        pages_awaiting_moderation_ids = (
            Revision.objects.filter(task_states__status=TaskState.STATUS_IN_PROGRESS)
            .values('object_id')
            .distinct()
        )

        pages = Page.objects.filter(id__in=pages_awaiting_moderation_ids)

        if not pages.exists():
            self.stdout.write(self.style.SUCCESS('No pages are currently awaiting moderation.'))
            return

        # 3. Prepare email context and render the template
        context = {
            'pages': pages,
            'site_url': site_url,
        }
        
        email_html = loader.get_template('mail/moderation_digest.html').render(context)

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
                Source="noreply@mmiest-moore-sandbox-web.ustaxcourt.gov",
            )
            self.stdout.write(self.style.SUCCESS(f"Email sent! Message ID: {response['MessageId']}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error sending email: {e}"))