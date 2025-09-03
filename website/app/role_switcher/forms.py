from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from wagtail.users.forms import (
    UserCreationForm as WagtailUserCreationForm,
    UserEditForm as WagtailUserEditForm,
)

User = get_user_model()


class RoleSwitchForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="--- Select a Role to Assume ---",
        label="Assume Role",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class RevertRoleForm(forms.Form):
    # This is a dummy form, primarily for the CSRF token and button
    pass


# -------------------------------------------------------
# Wagtail user forms: SSO-only, no password fields shown
# -------------------------------------------------------
class SSOOnlyUserCreationForm(WagtailUserCreationForm):
    """
    Wagtail 'Add user' form without password fields.
    New users get an unusable password so they cannot log in with credentials.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove any password fields (e.g., password1/password2)
        for name in list(self.fields):
            if name.startswith("password"):
                self.fields.pop(name, None)

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        # Ensure they cannot authenticate with username/password
        user.set_unusable_password()
        if commit:
            user.save()
            self.save_m2m()
        return user


class SSOOnlyUserEditForm(WagtailUserEditForm):
    """
    Wagtail 'Edit user' form without password fields.
    Password management should be handled explicitly by an admin if ever needed.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in list(self.fields):
            if name.startswith("password"):
                self.fields.pop(name, None)
