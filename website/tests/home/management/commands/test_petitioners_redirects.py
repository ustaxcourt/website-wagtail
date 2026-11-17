from django.test import TestCase, RequestFactory
from django.http import HttpResponseNotFound
from wagtail.contrib.redirects.models import Redirect
from wagtail.contrib.redirects.middleware import RedirectMiddleware
from wagtail.models import Locale, Page, Site

from home.management.commands.redirects.petitioners_redirect_initializer import (
    PetitionersRedirectInitializer,
)


class TestPetitionersRedirectBehavior(TestCase):
    """Black box tests to verify that configured redirects work correctly."""

    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        petitioners_page = Page(title="Petitioners", slug="petitioners")
        petitioners_start_page = Page(
            title="Petitioners Start", slug="petitioners-start"
        )
        petitioners_before_page = Page(
            title="Petitioners Before", slug="petitioners-before"
        )
        petitioners_during_page = Page(
            title="Petitioners During", slug="petitioners-during"
        )
        petitioners_after_page = Page(
            title="Petitioners After", slug="petitioners-after"
        )
        petitioners_guidance_page = Page(
            title="Petitioners Guidance", slug="petitioners-guidance"
        )
        home_page.add_child(instance=petitioners_page)
        home_page.add_child(instance=petitioners_start_page)
        home_page.add_child(instance=petitioners_before_page)
        home_page.add_child(instance=petitioners_during_page)
        home_page.add_child(instance=petitioners_after_page)
        home_page.add_child(instance=petitioners_guidance_page)

        # Ensure redirects are created before testing
        initializer = PetitionersRedirectInitializer()
        initializer.create()

    def _test_redirect(self, old_path, expected_new_path):
        """Helper method to test redirect behavior."""
        # First check if the redirect exists in the database
        redirect = Redirect.objects.filter(old_path=old_path).first()
        self.assertIsNotNone(
            redirect, f"Redirect should exist in database for {old_path}"
        )
        expected_page_id = Page.objects.get(slug=expected_new_path[1:-1]).id
        self.assertEqual(redirect.redirect_page_id, expected_page_id)

        # Test the redirect middleware directly
        request = self.factory.get(old_path)
        middleware = RedirectMiddleware(lambda _: None)

        # Simulate a 404 response for the middleware to process
        mock_response = HttpResponseNotFound()

        # Process the request through the middleware
        response = middleware.process_response(request, mock_response)

        # Check that the middleware returns a redirect
        self.assertEqual(response.status_code, 301)  # Permanent redirect
        self.assertEqual(response.url, expected_new_path)

    def test_petitioners_redirect(self):
        """Test that /petitioners redirects to /petitioners-guidance."""
        self._test_redirect("/petitioners", "/petitioners-guidance/")

    def test_petitioners_start_redirect(self):
        """Test that /petitioners-start redirects to /petitioners-guidance."""
        self._test_redirect("/petitioners-start", "/petitioners-guidance/")

    def test_petitioners_before_redirect(self):
        """Test that /petitioners-before redirects to /petitioners-guidance."""
        self._test_redirect("/petitioners-before", "/petitioners-guidance/")

    def test_petitioners_during_redirect(self):
        """Test that /petitioners-during redirects to /petitioners-guidance."""
        self._test_redirect("/petitioners-during", "/petitioners-guidance/")

    def test_petitioners_after_redirect(self):
        """Test that /petitioners-after redirects to /petitioners-guidance."""
        self._test_redirect("/petitioners-after", "/petitioners-guidance/")

    def test_redirect_behavior_with_query_parameters(self):
        """Test that redirects work with query parameters (query params are not preserved by default)."""
        request = self.factory.get("/petitioners?test=value")
        middleware = RedirectMiddleware(lambda _: None)
        mock_response = HttpResponseNotFound()
        response = middleware.process_response(request, mock_response)

        self.assertEqual(response.status_code, 301)
        # Note: Wagtail redirects do not preserve query parameters by default
        self.assertEqual(response.url, "/petitioners-guidance/")
