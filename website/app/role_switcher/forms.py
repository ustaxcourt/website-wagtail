from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from wagtail.users.forms import (
    UserCreationForm as WagtailUserCreationForm,
    UserEditForm as WagtailUserEditForm,
)

User = get_user_model()


# ---- Role switcher forms (unchanged) ----
class RoleSwitchForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="--- Select a Role to Assume ---",
        label="Assume Role",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class RevertRoleForm(forms.Form):
    pass


class SSOOnlyUserCreationForm(WagtailUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in list(self.fields):
            if name.lower().startswith("password"):
                self.fields.pop(name, None)

    def clean(self):
        # bypass UserCreationForm password validation
        return forms.ModelForm.clean(self)

    def save(self, commit=True):
        # bypass parent save() (expects password1)
        user = forms.ModelForm.save(self, commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
            self.save_m2m()
        return user


class SSOOnlyUserEditForm(WagtailUserEditForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in list(self.fields):
            if name.lower().startswith("password"):
                self.fields.pop(name, None)
