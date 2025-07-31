import os
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings

from wagtail.models import Page

class Command(BaseCommand):
    help = 'Sends a daily digest of pages awaiting moderation.'

    def handle(self, *args, **options):
        # 1. Define your moderators
        # Best practice: Store this in settings.py or a database model
        moderator_emails = ['Miriam.Miest-Moore.ctr@ustaxcourt.gov']
        
        # You can get this from the Wagtail Site model for more dynamic sites
        site_url = os.getenv('BASE_URL')
        print(f'Site url{site_url}')

        # 2. Query for pages in moderation
        pages = Page.objects.filter(workflow_state__status='in_progress')

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
        try:
            send_mail(
                subject='Wagtail Moderation Digest',
                message='',  # Plain-text version (can be left blank if sending HTML)
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=moderator_emails,
                html_message=email_html,
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully sent digest for {pages.count()} pages.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error sending email: {e}'))