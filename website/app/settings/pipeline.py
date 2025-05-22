from django.contrib.auth import get_user_model
# from social_core.exceptions import AuthException # Optional: if you want to stop auth for non-pre-registered users

User = get_user_model() # Best practice to get the User model

def associate_existing_user_by_email(backend, strategy, details, response, user=None, *args, **kwargs):
    """
    If a user is logging in via SSO and is not yet associated with a social account,
    but an account with their email already exists, associate this SSO login
    with that existing user account.
    """
    if user:  # If a user object is already passed in, it means they are already authenticated or associated.
        return {'user': user}

    email = details.get('email')
    if not email:
        # Depending on your IdP, the email might be in a different field e.g. 'upn' for Azure AD
        # You can inspect the 'details' dictionary to confirm
        # email = details.get('upn')
        if not email:
            # If no email is provided by the IdP, you can't link.
            # Decide how to handle: let it proceed (may fail later or create user without email) or raise AuthException
            return None # Or raise AuthException(backend, "Email not provided by SSO provider.")

    # Try to find an existing user with the same email (case-insensitive)
    try:
        # Using __iexact for case-insensitive email matching is crucial
        existing_user = User.objects.get(email__iexact=email)

        # Log that we are associating with an existing user
        print(f"SSO login for {email}: Associating with existing user '{existing_user.username}'.")
        return {
            'user': existing_user,
            'is_new': False  # Important: signals to later pipeline steps that this isn't a brand new social user
        }
    except User.DoesNotExist:
        # No user with this email exists.
        # The pipeline will proceed to 'social_core.pipeline.user.create_user'
        # if it's in your pipeline and no other function stops it.
        # Since you pre-register users, you might consider this an error case if you *only*
        # want pre-registered users to be able to log in.
        # If so, you could uncomment and use:
        # raise AuthException(backend, f"Access Denied: User with email {email} is not pre-registered or email not found.")
        print(f"SSO login for {email}: No existing user found with this email. Pipeline will continue.")
        pass # Let the pipeline continue to try and create a user or other configured steps.

    except User.MultipleObjectsReturned:
        # This should ideally not happen if your emails are unique.
        # If it does, you need a strategy: log it, raise an error, or pick one (e.g., the oldest).
        print(f"CRITICAL: Multiple users found with email {email}. Manual intervention required.")
        # raise AuthException(backend, f"Multiple users found with email {email}. Please contact admin.")
        return None # Or handle more gracefully

    return None # Default return if no specific action taken