from wagtail.contrib.redirects.models import Redirect
from django.core.exceptions import ValidationError


class RedirectInitializer:
    def __init__(self, logger):
        self.logger = logger

    def create_redirect(self, old_path, new_path, is_permanent=True):
        """
        Create a redirect if it doesn't already exist

        Args:
            old_path (str): The path to redirect from
            new_path (str): The path to redirect to
            is_permanent (bool): Whether this is a permanent (301) or temporary (302) redirect
        """
        if Redirect.objects.filter(old_path=old_path).exists():
            self.logger.write(f"- Redirect from '{old_path}' already exists.")
            return

        try:
            redirect = Redirect.objects.create(
                old_path=old_path, redirect_link=new_path, is_permanent=is_permanent
            )
            self.logger.write(f"Created redirect: {old_path} → {new_path}")
            return redirect
        except ValidationError as e:
            self.logger.write(f"Error creating redirect: {e}")
            return None
