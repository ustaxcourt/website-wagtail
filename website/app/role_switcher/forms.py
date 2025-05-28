from django import forms
from django.contrib.auth.models import Group

class RoleSwitchForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="--- Select a Role to Assume ---",
        label="Assume Role",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class RevertRoleForm(forms.Form):
    # This is a dummy form, primarily for the CSRF token and button
    pass