from django.test import TestCase, RequestFactory
from django.http import HttpResponseNotFound
from wagtail.contrib.redirects.models import Redirect
from wagtail.contrib.redirects.middleware import RedirectMiddleware

from home.management.commands.redirects.redirect_initializer import (
    RedirectInitializer,
    REDIRECTS,
)


class TestRedirectBehavior(TestCase):
    """Black box tests to verify that configured redirects work correctly."""

    def setUp(self):
        self.factory = RequestFactory()

        # Ensure redirects are created before testing
        initializer = RedirectInitializer()
        initializer.create_redirects()

    def _test_redirect(self, old_path, expected_new_path):
        """Helper method to test redirect behavior."""
        # First check if the redirect exists in the database
        redirect = Redirect.objects.filter(old_path=old_path).first()
        self.assertIsNotNone(
            redirect, f"Redirect should exist in database for {old_path}"
        )
        self.assertEqual(redirect.redirect_link, expected_new_path)

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

    def test_vacancy_announcements_redirect(self):
        """Test that /vacancy_announcements redirects to /employment/vacancy-announcements."""
        self._test_redirect(
            "/vacancy_announcements", "/employment/vacancy-announcements"
        )

    def test_vacancy_announcements_html_redirect(self):
        """Test that /vacancy_announcements.html redirects to /employment/vacancy-announcements."""
        self._test_redirect(
            "/vacancy_announcements.html", "/employment/vacancy-announcements"
        )

    def test_judges_recruiting_redirect(self):
        """Test that /judges_recruiting.html redirects to /employment/judges-recruiting."""
        self._test_redirect("/judges_recruiting.html", "/employment/judges-recruiting")

    def test_taxpayers_before_redirect(self):
        """Test that /taxpayers_before.html redirects to /petitioners-before."""
        self._test_redirect("/taxpayers_before.html", "/petitioners-before")

    def test_internship_programs_redirect(self):
        """Test that /internship_programs.html redirects to /employment/internship-programs."""
        self._test_redirect(
            "/internship_programs.html", "/employment/internship-programs"
        )

    def test_law_clerk_program_redirect(self):
        """Test that /law_clerk_program.html redirects to /employment/law-clerk-program."""
        self._test_redirect("/law_clerk_program.html", "/employment/law-clerk-program")

    def test_index_html_redirect(self):
        """Test that /index.html redirects to /."""
        self._test_redirect("/index.html", "/")

    def test_press_release_archives_redirect(self):
        """Test that /press_release_archives.html redirects to /press-releases/archives."""
        self._test_redirect("/press_release_archives.html", "/press-releases/archives")

    def test_dawson_faqs_redirect(self):
        """Test that /dawson_faqs.html redirects to /dawson-faqs-basics."""
        self._test_redirect("/dawson_faqs.html", "/dawson-faqs-basics")

    def test_tou_redirect(self):
        """Test that /tou.html redirects to /dawson-tou."""
        self._test_redirect("/tou.html", "/dawson-tou")

    def test_sample_legacy_url_redirects(self):
        """Test that sample legacy URLs are redirected correctly."""
        # Test a few legacy URLs that should be transformed
        test_cases = [
            ("/administrative_orders.html", "/administrative-orders/"),
            ("/case_procedure.html", "/case-procedure/"),
            ("/citation_and_style_manual.html", "/citation-and-style-manual/"),
            ("/dawson_faqs_basics.html", "/dawson-faqs-basics/"),
            ("/employment.html", "/employment/"),
        ]

        for old_path, expected_new_path in test_cases:
            with self.subTest(old_path=old_path):
                self._test_redirect(old_path, expected_new_path)

    def test_all_configured_redirects_work(self):
        """Test that all configured redirects in REDIRECTS list work correctly."""
        for redirect_config in REDIRECTS:
            old_path = redirect_config["old_path"]
            expected_new_path = redirect_config["new_path"]

            with self.subTest(old_path=old_path):
                self._test_redirect(old_path, expected_new_path)

    def test_non_configured_paths_return_404(self):
        """Test that paths not in the redirect configuration return 404."""
        non_existent_paths = [
            "/non_existent_path.html",
            "/another_fake_path",
            "/random_legacy_file.html",
        ]

        for path in non_existent_paths:
            with self.subTest(path=path):
                # Test that non-configured paths don't have redirects
                redirect = Redirect.objects.filter(old_path=path).first()
                self.assertIsNone(
                    redirect, f"No redirect should exist for non-configured path {path}"
                )

                # Test that middleware doesn't create redirects for non-existent paths
                request = self.factory.get(path)
                middleware = RedirectMiddleware(lambda _: None)
                mock_response = HttpResponseNotFound()
                response = middleware.process_response(request, mock_response)

                # Should return the original 404 response
                self.assertEqual(response.status_code, 404)

    def test_redirect_behavior_with_query_parameters(self):
        """Test that redirects work with query parameters (query params are not preserved by default)."""
        request = self.factory.get("/vacancy_announcements?test=value")
        middleware = RedirectMiddleware(lambda _: None)
        mock_response = HttpResponseNotFound()
        response = middleware.process_response(request, mock_response)

        self.assertEqual(response.status_code, 301)
        # Note: Wagtail redirects do not preserve query parameters by default
        self.assertEqual(response.url, "/employment/vacancy-announcements")
