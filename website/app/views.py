# your_app/views.py
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse


def custom_logout_view(request):
    # Log out from Django application first
    logout(request)

    # Construct Azure AD logout URL
    # Replace with your actual Azure AD tenant ID and client ID
    # and ensure this matches your Azure AD app registration's logout redirect URIs
    tenant_id = settings.SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID
    post_logout_redirect_uri = request.build_absolute_uri(
        reverse("wagtailadmin_login")
    )  # Or your custom login/logged-out page

    # This URL might vary slightly based on Azure AD configuration
    azure_ad_logout_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/logout?"
        f"post_logout_redirect_uri={post_logout_redirect_uri}"
        # You might also need a state parameter for Azure AD logout,
        # but typically it's optional for logout
    )

    return redirect(azure_ad_logout_url)
