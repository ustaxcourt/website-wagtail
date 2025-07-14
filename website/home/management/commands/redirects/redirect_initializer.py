from wagtail.contrib.redirects.models import Redirect
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


class RedirectInitializer:
    def __init__(self):
        self.logger = logger

    def create_redirect(self, old_path, new_path, is_permanent=True, site=None):
        """
        Create a redirect if it doesn't already exist

        Args:
            old_path (str): The path to redirect from
            new_path (str): The path to redirect to
            is_permanent (bool): Whether this is a permanent (301) or temporary (302) redirect
            site (wagtail.models.Site, optional): The Wagtail site to associate the redirect with

        Returns:
            Redirect: The redirect object (created or updated)
        """
        try:
            redirect, created = Redirect.objects.get_or_create(
                old_path=old_path,
                defaults={
                    "redirect_link": new_path,
                    "is_permanent": is_permanent,
                },
            )

            # If the redirect exists but target is outdated, update it
            if not created:
                updated = False
                if redirect.redirect_link != new_path:
                    redirect.redirect_link = new_path
                    updated = True
                if redirect.is_permanent != is_permanent:
                    redirect.is_permanent = is_permanent
                    updated = True
                if site and redirect.site != site:
                    redirect.site = site
                    updated = True
                if updated:
                    redirect.save()
                    logger.info(f"Updated redirect: {old_path} → {new_path}")
                else:
                    logger.info(
                        f"- Redirect from '{old_path}' already exists and is up to date."
                    )
            else:
                if site:
                    redirect.site = site
                    redirect.save()
                logger.info(f"Created redirect: {old_path} → {new_path}")

            return redirect

        except (ValidationError, IntegrityError) as e:
            logger.warning(f"Error creating/updating redirect for '{old_path}': {e}")
            return None
