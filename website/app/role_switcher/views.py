from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import RoleSwitchForm, RevertRoleForm

User = get_user_model()

SESSION_ORIGINAL_GROUPS_KEY = 'original_groups_pks'
SESSION_ORIGINAL_IS_SUPERUSER_KEY = 'original_is_superuser'
SESSION_IS_ASSUMING_ROLE_KEY = 'is_assuming_role'
SESSION_ASSUMED_ROLE_NAME_KEY = 'assumed_role_name'

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser) # Only superusers can access this page
def switch_role_view(request):
    user = request.user
    context = {
        'is_assuming_role': request.session.get(SESSION_IS_ASSUMING_ROLE_KEY, False),
        'assumed_role_name': request.session.get(SESSION_ASSUMED_ROLE_NAME_KEY, None),
        'title': "Switch User Role for Testing"
    }

    if request.method == 'POST':
        if 'assume_role' in request.POST:
            form = RoleSwitchForm(request.POST)
            if form.is_valid():
                if request.session.get(SESSION_IS_ASSUMING_ROLE_KEY, False):
                    messages.error(request, "You are already assuming a role. Revert first.")
                    return redirect(reverse('switch_role'))

                selected_group = form.cleaned_data['role']

                # Store original state
                original_groups_pks = list(user.groups.all().values_list('pk', flat=True))
                request.session[SESSION_ORIGINAL_GROUPS_KEY] = original_groups_pks
                request.session[SESSION_ORIGINAL_IS_SUPERUSER_KEY] = user.is_superuser
                request.session[SESSION_ASSUMED_ROLE_NAME_KEY] = selected_group.name

                # Apply new role
                user.groups.clear()
                user.groups.add(selected_group)
                user.is_superuser = False # Explicitly remove superuser for testing non-superuser roles
                user.is_staff = True # Ensure they can still access admin if the role is for admin panel testing
                user.save()

                request.session[SESSION_IS_ASSUMING_ROLE_KEY] = True
                messages.success(request, f"You are now assuming the role: {selected_group.name}. Your superuser status has been temporarily removed.")
                return redirect(reverse('wagtailadmin_home')) # Redirect to Wagtail dashboard or a relevant page

        elif 'revert_role' in request.POST:
            revert_form = RevertRoleForm(request.POST) # For CSRF
            if revert_form.is_valid(): # Effectively just checks CSRF
                if not request.session.get(SESSION_IS_ASSUMING_ROLE_KEY, False):
                    messages.warning(request, "You are not currently assuming a role.")
                    return redirect(reverse('switch_role'))

                original_groups_pks = request.session.get(SESSION_ORIGINAL_GROUPS_KEY, [])
                original_is_superuser = request.session.get(SESSION_ORIGINAL_IS_SUPERUSER_KEY, False)

                user.groups.clear()
                if original_groups_pks:
                    original_groups = Group.objects.filter(pk__in=original_groups_pks)
                    user.groups.set(original_groups)
                user.is_superuser = original_is_superuser
                user.is_staff = True # Superusers are typically staff
                user.save()

                # Clear session keys
                request.session.pop(SESSION_ORIGINAL_GROUPS_KEY, None)
                request.session.pop(SESSION_ORIGINAL_IS_SUPERUSER_KEY, None)
                request.session.pop(SESSION_IS_ASSUMING_ROLE_KEY, None)
                request.session.pop(SESSION_ASSUMED_ROLE_NAME_KEY, None)

                messages.success(request, "Your original permissions have been restored.")
                return redirect(reverse('switch_role'))

    # For GET request or if form is invalid
    context['role_switch_form'] = RoleSwitchForm()
    context['revert_role_form'] = RevertRoleForm()
    return render(request, 'app/templates/switch_role.html', context) # Adjust template path