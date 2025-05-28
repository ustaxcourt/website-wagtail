from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required # Changed decorator
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import RoleSwitchForm, RevertRoleForm

User = get_user_model()

# Session Keys
SESSION_ORIGINAL_GROUPS_KEY = 'original_groups_pks'
SESSION_ORIGINAL_IS_SUPERUSER_KEY = 'original_is_superuser'
SESSION_ORIGINAL_IS_STAFF_KEY = 'original_is_staff' # Added to store original staff status
SESSION_IS_ASSUMING_ROLE_KEY = 'is_assuming_role'
SESSION_ASSUMED_ROLE_NAME_KEY = 'assumed_role_name'

@login_required # Changed from @user_passes_test(is_superuser)
def switch_role_view(request):
    user = request.user # This is request.user, its attributes might change during the request if user.save() is called
    
    # Get current state from session
    is_currently_assuming_role = request.session.get(SESSION_IS_ASSUMING_ROLE_KEY, False)
    # This flag is True if the user *was* a superuser before they initiated the current switch
    was_originally_superuser_when_switched = request.session.get(SESSION_ORIGINAL_IS_SUPERUSER_KEY, False)

    if request.method == 'POST':
        if 'assume_role' in request.POST:
            # --- Logic for a user trying to assume a new role ---
            # Condition: Only users who are *currently* (in DB) superusers and *not already assuming a role* can initiate.
            if not (user.is_superuser and not is_currently_assuming_role):
                messages.error(request, "Only active superusers who are not currently assuming another role can initiate a switch.")
                return redirect(reverse('switch_role'))

            form = RoleSwitchForm(request.POST)
            if form.is_valid():
                selected_group = form.cleaned_data['role']

                # Store original state (at this point, user.is_superuser is True)
                request.session[SESSION_ORIGINAL_GROUPS_KEY] = list(user.groups.all().values_list('pk', flat=True))
                request.session[SESSION_ORIGINAL_IS_SUPERUSER_KEY] = user.is_superuser # Should be True
                request.session[SESSION_ORIGINAL_IS_STAFF_KEY] = user.is_staff # Store original staff status

                # Apply new role by modifying the user object
                current_user_in_db = User.objects.get(pk=user.pk) # Get a fresh instance to modify
                current_user_in_db.groups.clear()
                current_user_in_db.groups.add(selected_group)
                current_user_in_db.is_superuser = False # Explicitly remove superuser status
                current_user_in_db.is_staff = True      # Ensure they can still access admin if the role is admin-related
                current_user_in_db.save()
                
                # Update session to reflect the new state
                request.session[SESSION_IS_ASSUMING_ROLE_KEY] = True
                request.session[SESSION_ASSUMED_ROLE_NAME_KEY] = selected_group.name
                messages.success(request, f"You are now assuming the role: {selected_group.name}. Your superuser status has been temporarily removed.")
                # It's important that request.user reflects the changes for the rest of this request if needed,
                # but Django's auth middleware usually updates request.user on subsequent requests.
                # For immediate effect on request.user in this same request after save, re-fetch or update manually if critical.
                # However, redirecting is usually fine.
                return redirect(reverse('wagtailadmin_home'))
            else:
                # Form is invalid, will fall through to render GET with form errors
                # Ensure 'can_initiate_new_switch' is set correctly for this case too
                pass


        elif 'revert_role' in request.POST:
            # --- Logic for a user trying to revert to their original permissions ---
            # Condition: Must be currently assuming a role AND must have been a superuser when they first switched.
            if not (is_currently_assuming_role and was_originally_superuser_when_switched):
                messages.error(request, "Revert action is not applicable or not permitted for your account.")
                return redirect(reverse('wagtailadmin_home')) # Or 'switch_role' if preferred

            revert_form = RevertRoleForm(request.POST) # For CSRF
            if revert_form.is_valid():
                original_groups_pks = request.session.get(SESSION_ORIGINAL_GROUPS_KEY, [])
                
                current_user_in_db = User.objects.get(pk=user.pk) # Get a fresh instance
                current_user_in_db.is_superuser = request.session.get(SESSION_ORIGINAL_IS_SUPERUSER_KEY, False) # Restore
                current_user_in_db.is_staff = request.session.get(SESSION_ORIGINAL_IS_STAFF_KEY, False) # Restore

                current_user_in_db.groups.clear()
                if original_groups_pks:
                    original_groups = Group.objects.filter(pk__in=original_groups_pks)
                    current_user_in_db.groups.set(original_groups)
                current_user_in_db.save()

                # Clear all relevant session keys
                for key in [SESSION_ORIGINAL_GROUPS_KEY, SESSION_ORIGINAL_IS_SUPERUSER_KEY,
                            SESSION_ORIGINAL_IS_STAFF_KEY, SESSION_IS_ASSUMING_ROLE_KEY,
                            SESSION_ASSUMED_ROLE_NAME_KEY]:
                    request.session.pop(key, None)

                messages.success(request, "Your original permissions have been restored.")
                return redirect(reverse('switch_role'))
            else:
                # Invalid revert form (e.g. CSRF), will fall through
                pass

    # --- GET request handling (or POST with invalid form) ---
    # Determine if the current user (in their DB state) can initiate a new switch
    # user.is_superuser here refers to the user's current DB state for this request
    can_initiate_new_switch = user.is_superuser and not is_currently_assuming_role

    context = {
        'is_assuming_role': is_currently_assuming_role,
        'assumed_role_name': request.session.get(SESSION_ASSUMED_ROLE_NAME_KEY, None),
        'title': "Switch User Role for Testing",
        'can_initiate_new_switch': can_initiate_new_switch,
        # Only provide the form if they can initiate a switch
        'role_switch_form': RoleSwitchForm() if can_initiate_new_switch else None,
        'revert_role_form': RevertRoleForm(), # Always needed for CSRF if button is shown
    }

    # If it was a POST request with an invalid assume_role form, add the form with errors to context
    if request.method == 'POST' and 'assume_role' in request.POST and not form.is_valid():
        context['role_switch_form'] = form # Pass the form with errors

    return render(request, 'switch_role.html', context)
