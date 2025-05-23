from django.contrib.auth import get_user_model

User = get_user_model()

def associate_existing_user_by_email(backend, strategy, details, response, user=None, *args, **kwargs):
    """
    If a user is logging in via SSO and is not yet associated with a social account,
    but an account with their email already exists, associate this SSO login
    with that existing user account.
    """
    if user:
        return {'user': user}

    email = details.get('email')
    if not email:
        if not email:
            return None

    # Try to find an existing user with the same email (case-insensitive)
    try:
        existing_user = User.objects.get(email__iexact=email)

        print(f"SSO login for {email}: Associating with existing user '{existing_user.username}'.")
        return {
            'user': existing_user,
            'is_new': False
        }
    except User.DoesNotExist:
        print(f"SSO login for {email}: No existing user found with this email. Pipeline will continue.")
        pass

    except User.MultipleObjectsReturned:
        print(f"CRITICAL: Multiple users found with email {email}. Manual intervention required.")
        return None

    return None