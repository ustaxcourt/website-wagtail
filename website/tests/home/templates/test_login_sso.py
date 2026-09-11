"""Tests for the Court SSO control on the Wagtail admin login page.

Regression coverage for WAG-1401: ``social-auth-app-django`` 6.x makes the
``social:begin`` view POST-only (``@require_POST``), so the SSO control must
submit a POST form rather than link to the endpoint with a plain anchor.
"""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

BEGIN_URL = reverse("social:begin", args=["azuread-tenant-oauth2"])


@pytest.fixture
def renderable_admin(settings):
    # The admin base template's build-info context processor requires this.
    settings.GITHUB_SHA = "0000000"
    # Render static asset URLs without needing a collected manifest.
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }


class TestLoginPageSsoControl:
    def test_sso_control_is_a_post_form_to_social_begin(self, client, renderable_admin):
        response = client.get(reverse("wagtailadmin_login"))
        assert response.status_code == 200

        content = response.content.decode()
        assert f'action="{BEGIN_URL}"' in content
        assert 'method="post"' in content
        # The CSRF token is required for the POST form to be accepted.
        assert "csrfmiddlewaretoken" in content

    def test_sso_control_does_not_link_to_social_begin_with_a_get(
        self, client, renderable_admin
    ):
        response = client.get(reverse("wagtailadmin_login"))
        content = response.content.decode()

        assert f'href="{BEGIN_URL}"' not in content


class TestSocialBeginMethodContract:
    """Guards the assumption that forced us to use a POST form."""

    def test_get_is_rejected(self, client):
        assert client.get(BEGIN_URL).status_code == 405

    def test_post_is_accepted_and_redirects_to_the_identity_provider(
        self, client, settings
    ):
        settings.SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY = (
            "not-a-real-key"  # pragma: allowlist secret
        )
        settings.SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = (
            "not-a-real-secret"  # pragma: allowlist secret
        )
        settings.SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID = "not-a-real-tenant"

        response = client.post(BEGIN_URL)

        assert response.status_code == 302
        assert "login.microsoftonline.com" in response["Location"]
