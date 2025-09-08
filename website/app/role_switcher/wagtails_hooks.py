from wagtail import hooks


@hooks.register("register_admin_urls")
def force_passwordless_user_forms():
    """
    On Wagtail 7.0.2 the Users admin uses CreateView/EditView.
    Override their form_class to our password-less forms.
    """
    from .forms import SSOOnlyUserCreationForm, SSOOnlyUserEditForm
    from wagtail.users.views import users as user_views

    # Wagtail 7.0.2: these classes exist
    if hasattr(user_views, "CreateView") and hasattr(user_views, "EditView"):
        user_views.CreateView.form_class = SSOOnlyUserCreationForm
        user_views.EditView.form_class = SSOOnlyUserEditForm

    # We’re not adding URLs here, just returning an empty list to satisfy the hook.
    return []
